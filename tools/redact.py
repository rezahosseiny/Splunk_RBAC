#!/usr/bin/env python3
"""Redaction enforced on every value taken from a production export.

One rule set, loaded from catalog/redaction.yaml, shared by every tool that
reads an export: the profiler, the mapping resolver, and the data seeder. No
tool implements its own redaction.

Every replacement is deterministic and format-preserving. Deterministic, so the
same input always yields the same output and `make rebuild` reproduces
byte-identical data — a genuinely random replacement would break that.
Format-preserving, so a redacted event is still valid JSON, still parses, and
still reads like the thing it replaced. Replacements land only in ranges
reserved by RFC for documentation or testing.

Operations:

    learn(text)     collect internal hostnames from a corpus. Call over every
                    event before redacting, so bare hostnames are caught as
                    well as qualified ones.
    redact(text)    remove redaction targets. Safe for event content.
    collapse(text)  redact, then reduce ephemeral fragments to patterns. For
                    documents, where the pattern is what remediation acts on.
    audit(text)     list redaction targets that survived. Callers refuse to
                    write output when this is non-empty, so enforcement does
                    not depend on anyone remembering to check.
"""

import hashlib
import ipaddress
import json
import os
import re

import yaml

CATALOG = os.path.join(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))), "catalog")

# The local part allows $ and !: Kerberos machine accounts appear as
# HOST$@REALM and are just as identifying as a mailbox.
# The local part allows $ ! = and ': Kerberos machine accounts appear as
# HOST$@REALM, and O365 encodes some recipients as base32 ending in "==".
EMAIL_RE = re.compile(r"[A-Za-z0-9._%+$!='\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}")
# The separator is captured and re-emitted: inside JSON a real DOMAIN\\account
# is written with two backslashes, and collapsing them would produce an invalid
# escape. The lookahead stops a JSON \\uXXXX escape being mistaken for one.
DOMAIN_ACCOUNT_RE = re.compile(
    r"\b([A-Za-z][A-Za-z0-9_\-]{1,30})(\\{1,2})"
    r"(?!u[0-9a-fA-F]{4})([A-Za-z][A-Za-z0-9._\-$]{1,30})\b")
SID_RE = re.compile(r"\bS-1-\d+(?:-\d+){1,8}\b")
GUID_RE = re.compile(r"(?<![0-9a-fA-F])[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-"
                     r"[0-9a-f]{4}-[0-9a-f]{12}(?![0-9a-fA-F])", re.I)
DEVICE_HASH_RE = re.compile(r"\b[0-9a-f]{32,}\b", re.I)
MAC_RE = re.compile(r"\b(?:[0-9a-f]{2}[:\-]){5}[0-9a-f]{2}\b", re.I)
# Permissive: every candidate is validated with ipaddress before replacement,
# so time strings such as 18:51:07 are left alone rather than mangled.
IPV6_RE = re.compile(r"\b(?:[0-9a-f]{1,4}:){2,7}[0-9a-f]{1,4}\b", re.I)
IPV4_RE = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
PHONE_E164_RE = re.compile(r"(?<![\d.\-])\+\d{10,15}\b")
PHONE_US_RE = re.compile(r"\b(?:\(\d{3}\)\s?|\d{3}[.\-])\d{3}[.\-]\d{4}\b")
# Candidate hostname tokens. Bare hostnames are matched by scanning tokens and
# looking each up in the learned set, rather than by building an alternation of
# 500+ names: the alternation is orders of magnitude slower over a 63 MB corpus.
# Includes . and $ so dotted usernames (a.priestley) and machine accounts
# (HOST$) are seen as one token rather than split into fragments.
HOST_TOKEN_RE = re.compile(r"\b[A-Za-z0-9][A-Za-z0-9_.$\-]{4,62}\b")
# A bare hostname must be at least this long to be replaced, so that a short
# label that doubles as an ordinary word is not rewritten everywhere it appears.
MIN_BARE_HOST = 5
NAME_PSEUDONYM_PREFIX = "person_"
ACCOUNT_PSEUDONYM_PREFIX = "acct_"
# Cheap generic candidates, confirmed against the learned sets. Keeping the
# patterns generic is what stops cost growing with the number of learned values.
NAME_CANDIDATE_RE = re.compile(
    r"\b[A-Z][A-Za-z'\-]{1,20}(?:,[ ]?|[ ])[A-Z][A-Za-z'\-]{1,20}\b")
def _label_pattern(field):
    """Field name to its human-readable label form.

    Windows event narrative writes fields as labels: the field Account_Name
    appears as "Account Name:  value", and TargetUserName as "Target User
    Name:". Splitting on underscores and camelCase boundaries covers both.
    """
    spaced = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", "_", field)
    parts = [p for p in spaced.split("_") if p]
    return r"[ _]?".join(re.escape(p) for p in parts)


XML_DATA_RE = re.compile(
    r"<Data\s+Name=['\"](?P<field>[A-Za-z_][A-Za-z0-9_]*)['\"]\s*>"
    r"(?P<value>[^<]{1,120})</Data>")

# Document-only pattern collapsing.
FQDN_ANY_RE = re.compile(r"\b[A-Za-z0-9][A-Za-z0-9\-]*"
                         r"(?:\.[A-Za-z0-9][A-Za-z0-9\-]*)+"
                         r"\.(?:org|com|net|local|gov|io|edu)\b")
TIMESTAMP_RE = re.compile(r"\d{14,}")
LONG_DIGITS_RE = re.compile(r"\d{5,}")


class Redactor:
    """Applies catalog/redaction.yaml."""

    def __init__(self, config=None):
        if config is None:
            with open(os.path.join(CATALOG, "redaction.yaml"),
                      encoding="utf-8") as handle:
                config = yaml.safe_load(handle)
        self.config = config
        self.salt = str(config.get("salt", "")).encode()

        email = config["email_address"]
        self.mode = email["mode"]
        if self.mode not in ("pseudonym", "sentinel"):
            raise ValueError(
                f"redaction.yaml: email_address.mode must be 'pseudonym' or "
                f"'sentinel', got {self.mode!r}")
        self.sentinel = email["sentinel"]
        self.domain = email["pseudonym_domain"]
        self.prefix = email["pseudonym_prefix"]
        if not self.salt:                       # v1 kept the salt under email
            self.salt = str(email.get("salt", "")).encode()

        self.rules = config.get("rules", {})
        self.internal_domains = tuple(
            d.lower() for d in self._rule("internal_hostname")
            .get("internal_domains", []))
        self.internal_fqdn_re = re.compile(
            r"\b([A-Za-z0-9][A-Za-z0-9_\-]*)((?:\.[A-Za-z0-9_\-]+)*?\.(?:"
            + "|".join(re.escape(d) for d in self.internal_domains)
            + r"))\b", re.I) if self.internal_domains else None

        preserve = config.get("preserve", {})
        self.preserve_v4 = [ipaddress.ip_network(n, strict=False)
                            for n in preserve.get("ipv4", [])]
        self.preserve_v6 = set(str(a) for a in preserve.get("ipv6", []))
        self.well_known_sid_re = re.compile(
            preserve.get("well_known_sid_pattern", r"^$"))

        # One fake domain SID for the whole corpus: in the real data every user
        # shares the AD domain SID and differs only in the RID, so preserving
        # that shape is both more faithful and what lets audit() recognise an
        # already-redacted SID.
        self.sid_domain = "-".join(
            str(x) for x in self._ints("sid-domain-constant", 3, 4))

        name_rule = self._rule("personal_name_field")
        self.name_fields = {f.lower() for f in name_rule.get("fields", [])}
        self.name_learn_fields = {
            f.lower() for f in name_rule.get("learn_globally_from",
                                             name_rule.get("fields", []))}
        self.never_learn = {str(v).strip().lower()
                            for v in name_rule.get("never_learn", [])}
        self.name_field_re = re.compile(
            r'(?<![A-Za-z0-9_])(["\']?)('
            + "|".join(re.escape(f) for f in sorted(name_rule.get("fields", [])))
            + r')\1(\s*[:=]\s*)"([^"]*)"', re.I) if self.name_fields else None

        account_rule = self._rule("account_name_field")
        self.account_fields = {f.lower() for f in account_rule.get("fields", [])}
        self.min_account_length = int(account_rule.get("min_length", 4))

        # "Account Name:  value" as written in Windows event narrative.
        label_fields = sorted(self.account_fields | self.name_learn_fields)
        self.label_re = re.compile(
            r"\b(?:" + "|".join(_label_pattern(f) for f in label_fields)
            + r")\s*:\s{1,4}([A-Za-z0-9._$\-]{4,64}|"
            + r"[A-Z][A-Za-z'\-]{1,20},[ ]?[A-Z][A-Za-z'\-]{1,20})",
            re.I) if label_fields else None

        self.learned_hosts = set()
        self.learned_names = set()
        self.learned_accounts = set()

        self.forbidden_literals = [
            str(v).lower() for v in config.get("forbidden_literals", []) if v]
        literals_file = config.get("forbidden_literals_file")
        if literals_file:
            path = os.path.join(os.path.dirname(CATALOG), literals_file)
            if os.path.exists(path):
                with open(path, encoding="utf-8") as handle:
                    for line in handle:
                        line = line.split("#", 1)[0].strip()
                        if line:
                            self.forbidden_literals.append(line.lower())

        self.own_output_re = re.compile(
            r"^(?:" + re.escape(self.sentinel) + r"|"
            + re.escape(self.prefix) + r"[0-9a-f]{8}@"
            + re.escape(self.domain) + r")$")

    # ---- helpers ---------------------------------------------------------

    def _rule(self, name):
        return self.rules.get(name) or {}

    def _on(self, name):
        return bool(self._rule(name).get("enabled"))

    def _digest(self, value, size=4):
        return hashlib.blake2b(self.salt + value.lower().encode(),
                               digest_size=size).hexdigest()

    def _ints(self, value, count, size=1):
        """Deterministic small integers derived from a value."""
        raw = hashlib.blake2b(self.salt + value.lower().encode(),
                             digest_size=count * size).digest()
        return [int.from_bytes(raw[i * size:(i + 1) * size], "big")
                for i in range(count)]

    # ---- individual replacements ----------------------------------------

    def pseudonym(self, address):
        """A stable made-up address for one real address."""
        return f"{self.prefix}{self._digest(address)}@{self.domain}"

    def _sub_email(self, match):
        address = match.group(0)
        if self.own_output_re.match(address):
            return address
        return (self.sentinel if self.mode == "sentinel"
                else self.pseudonym(address))

    def _sub_domain_account(self, match):
        domain, separator, account = match.group(1, 2, 3)
        if account.startswith(self.prefix):
            return match.group(0)
        return f"{domain}{separator}{self.prefix}{self._digest(account)}"

    def _sub_sid(self, match):
        sid = match.group(0)
        if (self._rule("windows_sid").get("preserve_well_known", True)
                and self.well_known_sid_re.match(sid)):
            return sid
        rid = self._ints(sid, 1, 4)[0]
        return f"S-1-5-21-{self.sid_domain}-{rid}"

    def _sub_guid(self, match):
        h = self._digest(match.group(0), 16)
        return f"{h[:8]}-{h[8:12]}-4{h[13:16]}-a{h[17:20]}-{h[20:32]}"

    def _sub_device_hash(self, match):
        value = match.group(0)
        h = self._digest(value, 32)
        return (h * ((len(value) // len(h)) + 1))[:len(value)]

    def _sub_mac(self, match):
        octets = self._ints(match.group(0), 5)
        sep = "-" if "-" in match.group(0) else ":"
        return sep.join(["02"] + [f"{o:02x}" for o in octets])

    def _sub_ipv6(self, match):
        value = match.group(0)
        if value in self.preserve_v6:
            return value
        try:
            ipaddress.IPv6Address(value)
        except ValueError:
            return value            # not an address, e.g. the time 18:51:07
        h = self._digest(value, 12)
        groups = [h[i:i + 4] for i in range(0, 24, 4)]
        return ":".join(["2001", "db8"] + groups)

    def _sub_ipv4(self, match):
        value = match.group(0)
        try:
            address = ipaddress.ip_address(value)
        except ValueError:
            return value                        # not a real address, e.g. 1.2.3.999
        if any(address in network for network in self.preserve_v4):
            return value
        octets = self._ints(value, 3)
        if address.is_private:
            return f"10.{octets[0]}.{octets[1]}.{octets[2]}"
        # 198.18.0.0/15 — RFC 2544, never routed to a real host.
        return f"198.{18 + (octets[0] & 1)}.{octets[1]}.{octets[2]}"

    def _sub_phone(self, match):
        value = match.group(0)
        last = self._ints(value, 1)[0] % 100
        if value.startswith("+"):
            return f"+15555550{last:02d}"
        if value.startswith("("):
            return f"(555) 555-01{last:02d}"
        sep = "." if "." in value else "-"
        return f"555{sep}555{sep}01{last:02d}"

    def _sub_internal_fqdn(self, match):
        # Digest the host label only, not the whole FQDN, so the qualified and
        # bare forms of one host yield the same pseudonym.
        return f"host-{self._digest(match.group(1))}.{self.domain}"

    def name_pseudonym(self, value):
        """A stable placeholder for one person's name."""
        return f"{NAME_PSEUDONYM_PREFIX}{self._digest(value)}"

    def _sub_name_field(self, match):
        quote, field, sep, value = match.group(1, 2, 3, 4)
        if not value or value.startswith(NAME_PSEUDONYM_PREFIX):
            return match.group(0)
        return f'{quote}{field}{quote}{sep}"{self.name_pseudonym(value)}"'

    def account_pseudonym(self, value):
        """A stable placeholder for one account name."""
        return f"{ACCOUNT_PSEUDONYM_PREFIX}{self._digest(value)}"

    def _sub_learned_token(self, match):
        """Replace a token only when the corpus showed it to be an identity."""
        token = match.group(0)
        lowered = token.lower()
        if lowered in self.learned_hosts:
            return f"host-{self._digest(token)}"
        if lowered in self.learned_accounts:
            return self.account_pseudonym(token)
        return token

    def _sub_learned_name(self, match):
        candidate = match.group(0)
        if candidate.lower() in self.learned_names:
            return self.name_pseudonym(candidate)
        return candidate

    # ---- corpus learning -------------------------------------------------

    def learn(self, text):
        """First pass: collect the identity values this corpus contains.

        Hostnames, person names, and account names are gathered here so that
        redact() can match them as literals wherever they appear — including in
        syntaxes no rule models, such as an XML element body or an email
        subject line.
        """
        if self.internal_fqdn_re and self._on("internal_hostname"):
            for host, _domain in self.internal_fqdn_re.findall(text):
                if len(host) >= MIN_BARE_HOST:
                    self.learned_hosts.add(host.lower())

        if not self._on("learned_literals"):
            return

        stripped = text.strip()
        if stripped[:1] in ("{", "["):
            try:
                self._learn_json(json.loads(stripped))
            except ValueError:
                pass

        if self.name_field_re:
            for _q, field, _s, value in self.name_field_re.findall(text):
                if field.lower() in self.name_learn_fields:
                    self._add_name(value)
        for match in XML_DATA_RE.finditer(text):
            field = match.group("field").lower()
            if field in self.name_learn_fields:
                self._add_name(match.group("value"))
            elif field in self.account_fields:
                self._add_account(match.group("value"))
        if self.label_re:
            for value in self.label_re.findall(text):
                if NAME_CANDIDATE_RE.fullmatch(value.strip()):
                    self._add_name(value)
                else:
                    self._add_account(value)
        for field in self.account_fields:
            for match in re.finditer(
                    r'["\']?' + re.escape(field) + r'["\']?\s*[:=]\s*"([^"]{1,64})"',
                    text, re.I):
                self._add_account(match.group(1))

    def _learn_json(self, node):
        if isinstance(node, dict):
            has_address = any(k.lower() == "address" for k in node)
            for key, value in node.items():
                lower = key.lower()
                if isinstance(value, str):
                    if lower in self.name_learn_fields or (has_address
                                                           and lower == "name"):
                        self._add_name(value)
                    elif lower in self.account_fields:
                        self._add_account(value)
                    elif value.strip()[:1] in ("{", "["):
                        try:
                            self._learn_json(json.loads(value))
                        except ValueError:
                            pass
                else:
                    self._learn_json(value)
        elif isinstance(node, list):
            for item in node:
                self._learn_json(item)

    def _add_name(self, value):
        value = (value or "").strip()
        if not NAME_CANDIDATE_RE.fullmatch(value):
            return
        if value.lower() in self.never_learn:
            return
        self.learned_names.add(value.lower())
        if "," in value:                      # also learn "Given Surname" order
            surname, _, given = value.partition(",")
            flipped = f"{given.strip()} {surname.strip()}"
            if NAME_CANDIDATE_RE.fullmatch(flipped):
                self.learned_names.add(flipped.lower())

    def _add_account(self, value):
        value = (value or "").strip()
        if GUID_RE.fullmatch(value) or value.lower() in self.never_learn:
            return                      # a GUID is not an account name
        if (len(value) >= self.min_account_length
                and re.fullmatch(r"[A-Za-z0-9._$\-]+", value)
                and not value.startswith((ACCOUNT_PSEUDONYM_PREFIX,
                                          self.prefix))):
            self.learned_accounts.add(value.lower())

    def bare_hosts_in(self, text):
        """Learned hostnames appearing bare in this text."""
        return [t for t in HOST_TOKEN_RE.findall(text)
                if t.lower() in self.learned_hosts]

    # ---- public API ------------------------------------------------------

    def redact(self, text):
        """Remove redaction targets. Preserves structure and everything else.

        Order matters: email first, because an address contains a domain that
        the hostname rule would otherwise rewrite; qualified hostnames before
        bare ones; GUIDs before the generic long-hex rule; IPv6 before MAC,
        since an IPv6 address with two-character groups also matches the MAC
        pattern.
        """
        text = EMAIL_RE.sub(self._sub_email, text)
        if self._on("domain_account"):
            text = DOMAIN_ACCOUNT_RE.sub(self._sub_domain_account, text)
        if self._on("windows_sid"):
            text = SID_RE.sub(self._sub_sid, text)
        if self._on("guid"):
            text = GUID_RE.sub(self._sub_guid, text)
        if self._on("device_hash"):
            text = DEVICE_HASH_RE.sub(self._sub_device_hash, text)
        if self._on("ipv6_address"):
            text = IPV6_RE.sub(self._sub_ipv6, text)
        if self._on("mac_address"):
            text = MAC_RE.sub(self._sub_mac, text)
        if self._on("ipv4_address"):
            text = IPV4_RE.sub(self._sub_ipv4, text)
        if self._on("phone_number"):
            text = PHONE_E164_RE.sub(self._sub_phone, text)
            text = PHONE_US_RE.sub(self._sub_phone, text)
        if self._on("personal_name_field") and self.name_field_re:
            text = self.name_field_re.sub(self._sub_name_field, text)
        if self._on("internal_hostname") and self.internal_fqdn_re:
            text = self.internal_fqdn_re.sub(self._sub_internal_fqdn, text)
            # The domain also stands alone as a field value.
            for domain in self.internal_domains:
                text = re.sub(re.escape(domain), self.domain, text,
                              flags=re.I)
        if self.learned_hosts or self.learned_accounts:
            text = HOST_TOKEN_RE.sub(self._sub_learned_token, text)
        if self._on("learned_literals") and self.learned_names:
            text = NAME_CANDIDATE_RE.sub(self._sub_learned_name, text)
        return text

    def redact_event(self, text):
        """Redact one event, preserving its structure.

        JSON events are decoded, redacted value by value, and re-encoded. That
        removes escape-sequence hazards entirely: in decoded form a backslash is
        just a backslash, so no substitution can produce an invalid \\uXXXX or
        break a string. Everything else is redacted as plain text.
        """
        stripped = text.strip()
        if stripped[:1] in ("{", "["):
            try:
                document = json.loads(stripped)
            except ValueError:
                return self.redact(text)
            return json.dumps(self._redact_json(document), ensure_ascii=False)
        return self.redact(text)

    def _redact_json(self, node):
        if isinstance(node, dict):
            result = {}
            # A dict carrying Address alongside Name is a recipient object, so
            # its Name is a person. Elsewhere Name holds things like
            # "Storage Services", which should stay readable.
            has_address = any(k.lower() == "address" for k in node)
            for key, value in node.items():
                if (self._on("account_name_field") and isinstance(value, str)
                        and value and key.lower() in self.account_fields):
                    result[key] = self.account_pseudonym(value)
                elif (self._on("personal_name_field")
                        and isinstance(value, str) and value
                        and (key.lower() in self.name_fields
                             or (has_address and key.lower() == "name"))):
                    result[key] = self.name_pseudonym(value)
                else:
                    result[key] = self._redact_json(value)
            return result
        if isinstance(node, list):
            return [self._redact_json(v) for v in node]
        if isinstance(node, str):
            nested = node.strip()
            if nested[:1] in ("{", "[") and nested[-1:] in ("}", "]"):
                try:
                    inner = json.loads(nested)
                except ValueError:
                    return self.redact(node)
                if isinstance(inner, (dict, list)):
                    return json.dumps(self._redact_json(inner),
                                      ensure_ascii=False)
            return self.redact(node)
        return node

    def collapse(self, text):
        """Redact, then reduce ephemeral fragments to stable patterns."""
        text = self.redact(text)
        placeholders = self.config.get("document_patterns", {})
        for key, pattern in (("fully_qualified_hostname", FQDN_ANY_RE),
                             ("guid", GUID_RE),
                             ("timestamp", TIMESTAMP_RE),
                             ("hash", DEVICE_HASH_RE),
                             ("long_digits", LONG_DIGITS_RE)):
            replacement = placeholders.get(key)
            if replacement:
                text = pattern.sub(replacement, text)
        return text

    def audit(self, text, include_document_patterns=True):
        """List redaction targets that survived. Empty means clean.

        Range-based rather than pattern-based: a value is a leak when it is not
        inside the reserved range its rule replaces into. That is what makes the
        check meaningful — finding an IP address proves nothing, but finding one
        outside 10.0.0.0/8 and 198.18.0.0/15 proves redaction did not run.
        """
        leaks = []

        self._note(leaks, "email address",
                   [a for a in EMAIL_RE.findall(text)
                    if not self.own_output_re.match(a)])

        if self._on("internal_hostname") and self.internal_fqdn_re:
            self._note(leaks, "internal hostname",
                       [h + d for h, d in self.internal_fqdn_re.findall(text)])
            self._note(leaks, "internal hostname (bare)",
                       self.bare_hosts_in(text))

        if self._on("windows_sid"):
            self._note(leaks, "domain SID", [
                s for s in SID_RE.findall(text)
                if not self.well_known_sid_re.match(s)
                and not s.startswith(f"S-1-5-21-{self.sid_domain}-")])

        if self._on("domain_account"):
            self._note(leaks, "domain account",
                       [f"{d}{sep}{a}" for d, sep, a
                        in DOMAIN_ACCOUNT_RE.findall(text)
                        if not a.startswith(self.prefix)])

        if self._on("ipv4_address"):
            self._note(leaks, "IPv4 address",
                       [v for v in IPV4_RE.findall(text)
                        if not self._safe_ipv4(v)])

        if self._on("ipv6_address"):
            self._note(leaks, "IPv6 address",
                       [v for v in IPV6_RE.findall(text)
                        if not self._safe_ipv6(v)])

        if self._on("mac_address"):
            self._note(leaks, "MAC address",
                       [v for v in MAC_RE.findall(text)
                        if not v.lower().startswith("02")])

        if self._on("phone_number"):
            self._note(leaks, "phone number",
                       [v for v in (PHONE_E164_RE.findall(text)
                                    + PHONE_US_RE.findall(text))
                        if "5555550" not in v.replace(" ", "")
                        .replace("-", "").replace("(", "").replace(")", "")
                        .replace(".", "")])

        if self._on("personal_name_field") and self.name_field_re:
            self._note(leaks, "personal name field",
                       [f"{f}={v}" for _q, f, _s, v
                        in self.name_field_re.findall(text)
                        if v and not v.startswith(NAME_PSEUDONYM_PREFIX)])

        if include_document_patterns:
            self._note(leaks, "GUID", GUID_RE.findall(text))

        if self._on("learned_literals"):
            self._note(leaks, "learned person name",
                       [c for c in NAME_CANDIDATE_RE.findall(text)
                        if c.lower() in self.learned_names])
            self._note(leaks, "learned account name",
                       [t for t in HOST_TOKEN_RE.findall(text)
                        if t.lower() in self.learned_accounts])

        leaks.extend(self.verify(text))
        return leaks

    def verify(self, text):
        """Check the forbidden-literal list. Independent of every rule above.

        This is the backstop that catches a pattern gap, which a rule's own
        pattern cannot do. Treat a hit here as a redaction defect, not as a
        reason to extend this list.
        """
        lowered = text.lower()
        return [f"forbidden literal {literal!r}: "
                f"{lowered.count(literal)} occurrences"
                for literal in self.forbidden_literals if literal in lowered]

    def _safe_ipv4(self, value):
        """True when this address is preserved by policy or already redacted."""
        try:
            address = ipaddress.IPv4Address(value)
        except ValueError:
            return True                     # not an address at all
        if any(address in network for network in self.preserve_v4):
            return True
        return (address in ipaddress.ip_network("10.0.0.0/8")
                or address in ipaddress.ip_network("198.18.0.0/15"))

    def _safe_ipv6(self, value):
        if value in self.preserve_v6:
            return True
        try:
            address = ipaddress.IPv6Address(value)
        except ValueError:
            return True                     # a time string, not an address
        return address in ipaddress.ip_network("2001:db8::/32")

    @staticmethod
    def _note(leaks, label, hits):
        unique = sorted(set(hits))
        if unique:
            leaks.append(f"{label}: {len(unique)} distinct, "
                         f"e.g. {unique[0]!r}")


_DEFAULT = None


def default():
    """Process-wide redactor loaded from the catalog."""
    global _DEFAULT
    if _DEFAULT is None:
        _DEFAULT = Redactor()
    return _DEFAULT


if __name__ == "__main__":
    import sys
    redactor = default()
    enabled = [n for n in redactor.rules if redactor._on(n)]
    print(f"email mode={redactor.mode} domain={redactor.domain}", file=sys.stderr)
    print(f"rules enabled: {', '.join(enabled)}", file=sys.stderr)
    lines = sys.stdin.read()
    redactor.learn(lines)
    sys.stdout.write(redactor.redact(lines))
