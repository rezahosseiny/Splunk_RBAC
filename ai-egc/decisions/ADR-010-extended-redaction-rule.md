---
id: ADR-010
type: decision
title: Redaction extended to every personal identifier in event content
status: accepted
created: 2026-08-18
owner: Reza Hosseiny
supersedes: null
superseded_by: null
---

# ADR-010 — Extended redaction rule

## Context

ADR-009 established the redaction rule but covered email addresses only, and
noted that other personal data in event content was unhandled. Reza directed
that the rule be extended.

Scanning the export's 63 MB of event content found substantially more than
addresses:

| Identifier | Occurrences | Where |
|---|---|---|
| email address | 74,236 | o365, oracle, osnix, azure_ad |
| public IPv4 | 39,723 | o365 client IPs, oracle, palo_alto |
| Windows domain SID | 17,329 (885 distinct) | o365 mailbox activity |
| internal FQDN | 5,070 (568 distinct hosts) | osnix, vmware, o365, aruba |
| private IPv4 | 4,088 | oracle, osnix, aruba |
| IPv6 | 3,439 | o365, oracle |
| domain-qualified account | 839 | nps_server, palo_alto, vmware, snare |
| MAC address | 502 | oracle, aruba, forescout, infoblox |
| person name | ~900 distinct | userDisplayName, FileOwner, and others |
| phone number | 17 | o365, forescout, azure_ad |

## Decision

Extend `catalog/redaction.yaml` to twelve rules, each independently
switchable, all deterministic and format-preserving, all replacing into
ranges reserved by RFC so no redacted value can implicate a real asset:
email, domain account, Windows SID, GUID, device hash, MAC, IPv6, IPv4,
phone, personal-name field, account-name field, and internal hostname.
(The domain-qualified account rule covers the `<domain>\<account>` form.)

Four design decisions inside that are worth stating.

**Preserve what identifies nothing.** Well-known SIDs (`S-1-5-10` and
similar, 447 occurrences), loopback and link-local addresses, and vendor
hostnames are kept. They are platform constants, not people; redacting
them would destroy meaning and protect nobody.

**Preserve the public/private distinction.** Private addresses are
replaced inside `10.0.0.0/8` and public ones inside `198.18.0.0/15`, so
internal-versus-external traffic still reads correctly after redaction.

**Identify names by field, not by shape.** Value shape produces false
positives — `Location` holding "Message Body" and `ApplicationDisplayName` holding
"Microsoft Office" both look like names. An
explicit field allowlist is precise. A dictionary carrying `Address`
alongside `Name` is additionally treated as a recipient object, so its
`Name` is a person; elsewhere `Name` stays readable. `displayName` is
redacted in place but is not propagated corpus-wide, because it also
holds values like "Active Directory".

**Learn identity literals from the corpus, then match them anywhere.**
Chasing syntaxes failed repeatedly: the same fact appeared as JSON, as
`key="value"`, as an XML element body, as a Windows `Account Name:`
label, and inside prose in an email subject line. Instead a first pass
collects hostnames, person names, and account names, and the second pass
replaces those literals wherever they occur. Cheap generic candidate
patterns are confirmed against the learned sets, so cost does not grow
with the number of learned values. This is what finally covered
`Subject: "RE: <name> shared a file"`.

## Verification

`tools/verify_redaction.py`, run over 27 generated files and all 31,108
events: **clean**. Also confirmed:

- **Structure preserved.** All 26,467 JSON events valid before and
  after, 0 broken. JSON events are decoded, redacted value by value, and
  re-encoded, which removes escape hazards entirely.
- **Deterministic.** Redacting twice yields identical output, so
  `make rebuild` reproduces byte-identical data.
- **Readability retained.** "Active Directory" (60), `S-1-5-10` (447),
  `127.0.0.1` (241), and `OUTLOOK.EXE` (6,242) all survive.

## The finding that shaped this record

**A pattern-based audit cannot detect its own blind spot.** The rule
audit reported "clean" while an independent search for known-real values
found four live leaks: Kerberos machine accounts carrying `$` (excluded
from the address pattern), host labels containing `_`, GUIDs preceded by
`_` where `\b` does not match because both characters are word
characters, and JSON nested inside a JSON string. The audit missed all
four because it used the same patterns as the redaction it was checking.

Consequently verification has two independent layers, and the second is
the load-bearing one: a plain substring search for known-real values.
Non-sensitive markers live in `catalog/redaction.yaml`; specific
identifiers live in `config/forbidden_literals.txt`, which is gitignored
so those values are not themselves committed, with an `.example` file
committed in its place.

Three further bugs were found and fixed by the same means:

- The replacement `\user_…` inside a JSON string produced an invalid
  `\u` escape and corrupted 12 events. The value-by-value JSON path
  removes the whole class of hazard.
- The qualified and bare forms of one hostname produced two different
  pseudonyms, because one digested the FQDN and the other the label.
- The field-name pattern lacked a boundary, so `displayName` matched
  inside `ApplicationDisplayName` and redacted a product name. Running
  the verifier against this project's own records is what surfaced it.

## Consequences

- Redacting the full export takes about 30 seconds in two passes. The
  learning pass means the seeder must read the corpus before writing
  any of it.
- Bare hostnames are replaced only when that host also appears qualified
  somewhere in the corpus, and must be at least five characters. A host
  that only ever appears bare and unqualified is not covered.
- Person names in free-text prose are covered only when the same name was
  learned from a structured field.
- A hit from the forbidden-literal layer is a redaction defect to fix in
  the rules, never a reason to extend the literal list.
- Over-redaction is possible and accepted: `displayName` sometimes holds
  a computer or service name. Since the RBAC model is indifferent to
  event content, the cost is cosmetic; each rule can be disabled.
- The rules cover the identifiers found in this export. A new export can
  introduce a new shape, which is exactly what the literal layer and the
  mapping-gap report exist to surface.

## Approval

Approved by Reza Hosseiny, 2026-08-18 — blanket approval of INT-001 and ADR-001 through ADR-010, given in session by the decision authority. Recorded, not granted, by the AI participant.
