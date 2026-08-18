#!/usr/bin/env python3
"""Catalog loading, validation, and mapping resolution.

The single place the catalog is read and interpreted. Every tool and generator
imports from here, so the naming rules, the mapping semantics, and the
effective-permission helpers exist once.

    from generators import loader
    cat = loader.Catalog()
    cat.errors          # [] when the catalog is internally consistent
    cat.retention("ops_non_inf_lin_m")
    cat.resolve("aruba", "aruba:stm", "udp:5010")
"""

import fnmatch
import os
import re

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CATALOG_DIR = os.path.join(ROOT, "catalog")

# [class]_[compliance]_[domain]_[content]_[optional_detail]_[retention]
INDEX_NAME_RE = re.compile(
    r"^(?P<data_class>[a-z]{3})_(?P<compliance>[a-z]{3})_(?P<domain>[a-z]{3})_"
    r"(?P<content>[a-z]{3})(?:_(?P<detail>[a-z0-9_]+?))?_(?P<retention>[sml])$"
)
SANDBOX_INDEX_RE = re.compile(r"^tmp_[a-z0-9_]+_s$")
TAG_NAME_RE = re.compile(r"^[a-z0-9_\-\.]+(?::[a-z0-9_\-\.]+)*$")
ROLE_RE = re.compile(r"^rl_[a-z0-9_]+$")
SVC_ROLE_RE = re.compile(r"^rl_svc_[a-z0-9_]+$")
BUNDLE_RE = re.compile(r"^pr_(data|search|feat|workspace)_[a-z0-9_]+$")
MAX_TAGS = 5
SECONDS_PER_DAY = 86400


def slug(value):
    """Lowercase and reduce to characters the tag format permits."""
    value = re.sub(r"[^a-z0-9_.\-]+", "_", value.lower())
    return re.sub(r"[_\-]{2,}", "_", value).strip("_.-")


def render(template, sourcetype, source):
    """Expand a mapping template against one observed (sourcetype, source)."""
    return (template
            .replace("{tail_lower}", sourcetype.rsplit(":", 1)[-1].lower())
            .replace("{st_lower}", sourcetype.lower())
            .replace("{src_tail_lower}", source.rsplit(":", 1)[-1].lower())
            .replace("{src_lower}", source.lower())
            .replace("{src_tail_slug}", slug(source.rsplit(":", 1)[-1]))
            .replace("{src_slug}", slug(source)))


class Catalog:
    """The loaded catalog, with validation and resolution."""

    FILES = ("taxonomy", "mapping", "indexes", "business_units",
             "redaction", "bundles", "roles", "users", "expectations",
             "coverage_matrix")

    def __init__(self, catalog_dir=CATALOG_DIR):
        self.dir = catalog_dir
        for name in self.FILES:
            path = os.path.join(catalog_dir, f"{name}.yaml")
            with open(path, encoding="utf-8") as handle:
                setattr(self, name, yaml.safe_load(handle))

        self.units = self.business_units["units"]
        self.index_list = self.indexes["indexes"]
        self.index_by_name = {e["name"]: e for e in self.index_list}
        self.legacy = self.mapping["legacy_indexes"]
        self.fixtures = self.mapping.get("coverage_fixtures", {})
        # Indexes Splunk itself provides: governed for access, never defined
        # or removed by this project.
        self.provided = {e["name"] for e in self.index_list
                         if e.get("provided_by")}
        self.name_exempt = {
            name for name, entry in self.legacy.items()
            if entry.get("naming_exception")
        }

        self.bundle_groups = {
            "data": self.bundles.get("data_bundles") or [],
            "search": self.bundles.get("search_bundles") or [],
            "feat": self.bundles.get("feature_bundles") or [],
            "workspace": self.bundles.get("workspace_bundles") or [],
        }
        self.bundle_by_name = {b["name"]: b for group in
                               self.bundle_groups.values() for b in group}
        self.bundle_category = {b["name"]: cat for cat, group in
                                self.bundle_groups.items() for b in group}
        self.role_list = self.roles["roles"]
        self.role_by_name = {r["name"]: r for r in self.role_list}
        self.user_list = self.users["users"]
        self.expects = self.expectations["expectations"]
        self.sensitive_caps = set(self.taxonomy["sensitive_capabilities"])
        self.search_exec_caps = set(
            self.taxonomy["search_execution_capabilities"])

        self.errors = []
        self.warnings = []
        self._validate()
        self._validate_rbac()

    # ---- decoding -------------------------------------------------------

    def decode(self, index_name):
        """Return the fields an index name encodes, or None if exempt/invalid."""
        match = INDEX_NAME_RE.match(index_name)
        return match.groupdict() if match else None

    def retention(self, index_name):
        """The retention tier record for an index, or None."""
        fields = self.decode(index_name)
        if not fields:
            entry = self.index_by_name.get(index_name, {})
            suffix = (entry.get("retention") or "").lstrip("_")
            return self.taxonomy["retention"].get(suffix)
        return self.taxonomy["retention"][fields["retention"]]

    def frozen_seconds(self, index_name):
        """frozenTimePeriodInSecs — searchable days, not the archive period."""
        tier = self.retention(index_name)
        if not tier:
            return None
        return int(tier["searchable_days"]) * SECONDS_PER_DAY

    # ---- mapping resolution --------------------------------------------

    def rule_for(self, legacy_index, legacy_sourcetype):
        """First mapping rule whose glob matches, or None."""
        entry = self.legacy.get(legacy_index)
        if not entry:
            return None
        for rule in entry.get("rules", []):
            if fnmatch.fnmatchcase(legacy_sourcetype, rule["match"]):
                return rule
        return None

    def resolve(self, legacy_index, legacy_sourcetype, legacy_source):
        """Governed (index, sourcetype, source) for one observed triple.

        Returns None when no rule matches — a mapping gap, reported rather
        than silently absorbed.
        """
        rule = self.rule_for(legacy_index, legacy_sourcetype)
        if rule is None:
            return None
        return {
            "index": rule["index"],
            "sourcetype": render(rule["sourcetype"], legacy_sourcetype,
                                 legacy_source),
            "source": render(rule["source"], legacy_sourcetype, legacy_source),
            "quarantine_reason": rule.get("quarantine_reason"),
        }

    def target_indexes(self):
        """Every governed index the catalog can route data into."""
        names = {rule["index"]
                 for entry in self.legacy.values()
                 for rule in entry["rules"]}
        return sorted(names | set(self.fixtures))

    # ---- effective permissions ------------------------------------------
    #
    # Phase 3 adds the bundle and role helpers here, once bundles.yaml and
    # roles.yaml exist. Writing them before the files they read would be
    # guesswork.

    def effective_allowed_indexes(self, patterns):
        """Expand index patterns against the catalog's index set."""
        allowed = set()
        for pattern in patterns:
            for name in self.index_by_name:
                if fnmatch.fnmatchcase(name, pattern):
                    allowed.add(name)
        return sorted(allowed)

    def role_bundles(self, role_name, category=None):
        """The bundles a role imports, optionally of one category."""
        role = self.role_by_name.get(role_name) or {}
        names = role.get("bundles", [])
        if category:
            names = [n for n in names
                     if self.bundle_category.get(n) == category]
        return [self.bundle_by_name[n] for n in names if n in self.bundle_by_name]

    def computed_indexes(self, role_name):
        """Union of the index sets of the role's data bundles."""
        patterns = []
        for bundle in self.role_bundles(role_name, "data"):
            patterns += bundle.get("indexes_allowed", [])
        return self.effective_allowed_indexes(patterns)

    def computed_capabilities(self, role_name):
        """Union of the capabilities of the role's search and feature bundles."""
        caps = set()
        for category in ("search", "feat"):
            for bundle in self.role_bundles(role_name, category):
                caps.update(bundle.get("capabilities", []))
        return sorted(caps)

    def computed_quotas(self, role_name):
        """Per-attribute MAXIMUM across the role's search bundles.

        Splunk resolves each quota attribute independently, so a role holding
        two bundles can take its job quota from one and its disk quota from the
        other. Taking the values of whichever bundle looks more generous would
        give a different, wrong answer.
        """
        quotas = {}
        for bundle in self.role_bundles(role_name, "search"):
            for key, value in (bundle.get("envelope") or {}).items():
                quotas[key] = max(quotas.get(key, value), value)
        return quotas

    def computed_workspace_apps(self, role_name):
        """Apps the role's workspace bundles grant."""
        apps = set()
        for bundle in self.role_bundles(role_name, "workspace"):
            apps.update(bundle.get("apps", []))
        return sorted(apps)

    def role_is_sensitive(self, role_name):
        """True when any bundle in the chain is flagged sensitive."""
        return any(b.get("sensitive")
                   for b in self.role_bundles(role_name))

    # ---- RBAC validation -------------------------------------------------

    def _warn(self, message):
        self.warnings.append(message)

    def _validate_rbac(self):
        self._check_bundle_concerns()
        self._check_sensitive_isolation()
        self._check_role_composition()
        self._check_users()
        self._check_expectations()
        self._check_coverage_matrix()
        self._check_sizing()

    def _check_bundle_concerns(self):
        """Each bundle must hold only what its category permits."""
        for name, bundle in sorted(self.bundle_by_name.items()):
            category = self.bundle_category[name]
            if not BUNDLE_RE.match(name):
                self._err(f"bundle {name}: does not match pr_<category>_<name>")
            elif not name.startswith(f"pr_{category}_"):
                self._err(f"bundle {name}: listed under {category} bundles but "
                          f"named for another category")
            has = {k for k in ("indexes_allowed", "indexes_default",
                               "srch_filter", "capabilities", "envelope",
                               "apps") if bundle.get(k)}
            permitted = {
                "data": {"indexes_allowed", "indexes_default", "srch_filter"},
                "search": {"capabilities", "envelope"},
                "feat": {"capabilities"},
                "workspace": {"apps"},
            }[category]
            for key in sorted(has - permitted):
                self._err(f"bundle {name}: category {category} must not hold "
                          f"'{key}'")
            if category == "data":
                for index in bundle.get("indexes_allowed", []):
                    if not any(fnmatch.fnmatchcase(n, index)
                               for n in self.index_by_name):
                        self._err(f"bundle {name}: index pattern {index!r} "
                                  f"matches no registered index")
            if category == "search":
                extra = set(bundle.get("capabilities", [])) - self.search_exec_caps
                if extra:
                    self._err(f"bundle {name}: holds non-search-execution "
                              f"capabilities {sorted(extra)}")
            if category == "feat":
                overlap = set(bundle.get("capabilities", [])) & self.search_exec_caps
                if overlap:
                    self._err(f"bundle {name}: holds search-execution "
                              f"capabilities {sorted(overlap)}, which belong in "
                              f"a pr_search_* bundle")
            if category == "workspace":
                if not bundle.get("apps"):
                    self._err(f"bundle {name}: grants no app")

    def _check_sensitive_isolation(self):
        """A sensitive capability may live only in a flagged pr_feat_admin_*."""
        for name, bundle in sorted(self.bundle_by_name.items()):
            held = set(bundle.get("capabilities", [])) & self.sensitive_caps
            if not held:
                continue
            if not name.startswith("pr_feat_admin_"):
                self._err(f"bundle {name}: holds sensitive capabilities "
                          f"{sorted(held)} but is not a pr_feat_admin_* bundle")
            if not bundle.get("sensitive"):
                self._err(f"bundle {name}: holds sensitive capabilities but is "
                          f"not flagged sensitive: true")
            if not bundle.get("governance"):
                self._err(f"bundle {name}: sensitive bundle has no governance "
                          f"block")
        for role in self.role_list:
            chain_sensitive = self.role_is_sensitive(role["name"])
            if chain_sensitive and not role.get("sensitive"):
                self._err(f"role {role['name']}: imports a sensitive bundle but "
                          f"is not flagged sensitive: true")
            if role.get("sensitive") and not chain_sensitive:
                self._err(f"role {role['name']}: flagged sensitive but imports "
                          f"no sensitive bundle")
        allowlist = set(self.taxonomy.get("destructive_capability_allowlist", []))
        destructive = set(self.taxonomy["destructive_capabilities"])
        for role in self.role_list:
            held = set(self.computed_capabilities(role["name"])) & destructive
            if held and role["name"] not in allowlist:
                self._err(f"role {role['name']}: holds destructive capabilities "
                          f"{sorted(held)} but is not in "
                          f"destructive_capability_allowlist")

    def _check_role_composition(self):
        """A role composes bundles and holds nothing directly."""
        builtin = set(self.taxonomy["builtin_roles"])
        for role in self.role_list:
            name = role["name"]
            if not ROLE_RE.match(name):
                self._err(f"role {name}: does not match rl_<name>")
            for key in ("capabilities", "indexes_allowed", "envelope", "apps"):
                if role.get(key):
                    self._err(f"role {name}: holds '{key}' directly; a Business "
                              f"Role must only compose bundles")
            if not role.get("bundles"):
                self._err(f"role {name}: imports no bundle")
            for bundle in role.get("bundles", []):
                if bundle in builtin:
                    self._err(f"role {name}: imports built-in role {bundle}")
                elif bundle not in self.bundle_by_name:
                    self._err(f"role {name}: imports unknown bundle {bundle}")
            if role.get("service_account") and not SVC_ROLE_RE.match(name):
                self._err(f"role {name}: flagged service_account but does not "
                          f"match rl_svc_*")
            if SVC_ROLE_RE.match(name):
                search_names = [b["name"] for b in
                                self.role_bundles(name, "search")]
                if search_names != ["pr_search_constrained"] \
                        and not role.get("wider_envelope_justification"):
                    self._err(f"role {name}: a service account defaults to "
                              f"pr_search_constrained; a wider envelope needs "
                              f"wider_envelope_justification")
            # An ambiguous quota combination: 0 means "no limit" for these two
            # attributes, so a numeric maximum against a non-zero value is not
            # the semantic maximum.
            for key in ("srchTimeWin", "srchMaxTime"):
                values = [(b.get("envelope") or {}).get(key)
                          for b in self.role_bundles(name, "search")]
                values = [v for v in values if v is not None]
                if 0 in values and any(v > 0 for v in values):
                    self._warn(f"role {name}: combines {key}=0 (no limit) with a "
                               f"non-zero value; the numeric maximum is not the "
                               f"semantic maximum, so state the intent")

    def _check_users(self):
        """One user per role, one role per user."""
        prefix = self.users.get("username_prefix", "")
        seen = {}
        for user in self.user_list:
            username, role = user.get("username"), user.get("role")
            if prefix and not username.startswith(prefix):
                self._err(f"user {username}: does not start with {prefix!r}")
            if role not in self.role_by_name:
                self._err(f"user {username}: unknown role {role}")
            if role in seen:
                self._err(f"role {role}: has more than one test user "
                          f"({seen[role]}, {username})")
            seen[role] = username
        for name in sorted(self.role_by_name):
            if name not in seen:
                self._err(f"role {name}: has no test user, so its behaviour "
                          f"cannot be tested")

    def _check_expectations(self):
        """Cross-check the hand-written expectations against the composition.

        This is the check ADR-001 exists for. A disagreement means either the
        composition is wrong or the recorded intent is wrong. Both are findings.
        """
        for name in sorted(self.role_by_name):
            expect = self.expects.get(name)
            if not expect:
                self._err(f"role {name}: no entry in expectations.yaml")
                continue
            if not expect.get("intent"):
                self._err(f"expectations {name}: no intent recorded")

            for label, stated, computed in (
                    ("allowed_indexes", expect.get("allowed_indexes"),
                     self.computed_indexes(name)),
                    ("capabilities", expect.get("capabilities"),
                     self.computed_capabilities(name)),
                    ("visible_apps", expect.get("visible_apps"),
                     self.computed_workspace_apps(name))):
                if stated is None:
                    self._err(f"expectations {name}: no {label}")
                    continue
                extra = sorted(set(stated) - set(computed))
                missing = sorted(set(computed) - set(stated))
                if extra:
                    self._err(f"expectations {name}: {label} states {extra} "
                              f"which the bundles do not grant")
                if missing:
                    self._err(f"expectations {name}: {label} omits {missing} "
                              f"which the bundles do grant")

            stated_q = expect.get("quotas") or {}
            computed_q = self.computed_quotas(name)
            for key in sorted(set(stated_q) | set(computed_q)):
                if stated_q.get(key) != computed_q.get(key):
                    self._err(f"expectations {name}: quota {key} stated "
                              f"{stated_q.get(key)}, bundles give "
                              f"{computed_q.get(key)}")

            reachable = set(self.computed_indexes(name))
            for index in expect.get("must_not_reach", []):
                if index not in self.index_by_name:
                    self._err(f"expectations {name}: must_not_reach names "
                              f"unknown index {index}")
                elif index in reachable:
                    self._err(f"expectations {name}: must_not_reach lists "
                              f"{index} but the bundles grant it")
            held = set(self.computed_capabilities(name))
            for capability in expect.get("must_not_hold", []):
                if capability in held:
                    self._err(f"expectations {name}: must_not_hold lists "
                              f"{capability} but the bundles grant it")
            all_apps = set(self.expectations.get("workspace_apps_all", []))
            hidden = set(expect.get("hidden_apps") or [])
            visible = set(expect.get("visible_apps") or [])
            if visible & hidden:
                self._err(f"expectations {name}: apps in both visible_apps and "
                          f"hidden_apps: {sorted(visible & hidden)}")
            unaccounted = all_apps - visible - hidden
            if unaccounted:
                self._err(f"expectations {name}: workspace apps in neither list: "
                          f"{sorted(unaccounted)}")

    def _check_coverage_matrix(self):
        """Every behaviour must name real roles, and every role must be used."""
        rows = self.coverage_matrix["behaviours"]
        ids = [row["id"] for row in rows]
        if len(ids) != len(set(ids)):
            self._err("coverage_matrix: duplicate behaviour ids")
        used = set()
        for row in rows:
            for key in ("behaviour", "strategy_basis", "observable_because",
                        "tests"):
                if not row.get(key):
                    self._err(f"coverage_matrix {row['id']}: no {key}")
            if not row.get("tests"):
                self._err(f"coverage_matrix {row['id']}: no test covers this "
                          f"behaviour")
            for role in row.get("roles", []):
                if role == "all":
                    used.update(self.role_by_name)
                elif role not in self.role_by_name:
                    self._err(f"coverage_matrix {row['id']}: unknown role {role}")
                else:
                    used.add(role)
        for name, role in sorted(self.role_by_name.items()):
            if name not in used:
                self._err(f"role {name}: named by no coverage-matrix row, so "
                          f"nothing states what it demonstrates")
            if role.get("purpose") == "coverage" and \
                    not role.get("differs_from_base_by") and \
                    name != "rl_cov_base" and \
                    "overlap" not in name:
                self._warn(f"role {name}: a coverage role should record "
                           f"differs_from_base_by")

        # A differential pair must differ by exactly one bundle.
        base = self.role_by_name.get("rl_cov_base")
        if base:
            base_bundles = set(base["bundles"])
            for role in self.role_list:
                target = role.get("differs_from_base_by")
                if not target:
                    continue
                difference = set(role["bundles"]) ^ base_bundles
                if difference != {target}:
                    self._err(f"role {role['name']}: records "
                              f"differs_from_base_by={target} but differs from "
                              f"rl_cov_base by {sorted(difference)}")

    def _check_sizing(self):
        """Warn, never fail, when a category leaves the strategy's target."""
        for category, group in sorted(self.bundle_groups.items()):
            target = self.taxonomy["sizing_targets"].get(f"pr_{category}")
            if not target:
                continue
            count = len(group)
            if not target["min"] <= count <= target["max"]:
                self._warn(f"pr_{category}: {count} bundles, outside the "
                           f"strategy target of {target['min']}-{target['max']}")

    # ---- validation -----------------------------------------------------

    def _err(self, message):
        self.errors.append(message)

    def _validate(self):
        tax = self.taxonomy
        # Every index in the register must be reachable from the mapping,
        # and every mapping target must be registered.
        targets = set(self.target_indexes())
        registered = set(self.index_by_name)
        for name in sorted(targets - registered):
            self._err(f"index {name}: routed to by mapping but not registered "
                      f"in indexes.yaml")
        for name in sorted(registered - targets):
            self._err(f"index {name}: registered in indexes.yaml but no "
                      f"mapping rule or fixture routes to it")

        for entry in self.index_list:
            name = entry["name"]
            if not entry.get("description"):
                self._err(f"index {name}: no description")
            for field in ("owner_business", "owner_technical"):
                unit = entry.get(field)
                if not unit:
                    self._err(f"index {name}: no {field}")
                elif unit not in self.units:
                    self._err(f"index {name}: {field} '{unit}' is not a unit "
                              f"in business_units.yaml")

            fields = self.decode(name)
            if fields is None:
                if not entry.get("naming_exception"):
                    self._err(f"index {name}: does not match the naming schema "
                              f"and declares no naming_exception")
                elif entry["naming_exception"] not in tax[
                        "naming_exception_classes"]:
                    self._err(f"index {name}: unregistered naming_exception "
                              f"'{entry['naming_exception']}'")
                continue

            # The register restates what the name encodes; they must agree.
            for field, table in (("data_class", "classes"),
                                 ("compliance", "compliance"),
                                 ("domain", "domains"),
                                 ("content", "content")):
                if fields[field] not in tax[table]:
                    self._err(f"index {name}: {field} code "
                              f"'{fields[field]}' not registered in "
                              f"taxonomy.{table}")
                if entry.get(field) != fields[field]:
                    self._err(f"index {name}: {field} is "
                              f"{entry.get(field)!r} but the name encodes "
                              f"{fields[field]!r}")
            if entry.get("retention") != f"_{fields['retention']}":
                self._err(f"index {name}: retention is "
                          f"{entry.get('retention')!r} but the name encodes "
                          f"'_{fields['retention']}'")
            if fields["detail"] and entry.get("detail") != fields["detail"]:
                self._err(f"index {name}: detail is {entry.get('detail')!r} "
                          f"but the name encodes {fields['detail']!r}")

        # Mapping rules must be complete and target registered indexes.
        for legacy, entry in self.legacy.items():
            if not entry.get("rules"):
                self._err(f"legacy index {legacy}: no rules")
            for rule in entry.get("rules", []):
                for key in ("match", "index", "sourcetype", "source"):
                    if key not in rule:
                        self._err(f"legacy index {legacy}: rule missing "
                                  f"'{key}'")

        # Fixtures must declare what they stand in for.
        for name, fixture in self.fixtures.items():
            for key in ("reason", "sourcetype", "source", "events"):
                if key not in fixture:
                    self._err(f"fixture {name}: missing '{key}'")

        if self.mapping.get("source_policy") != "rewrite":
            self._err("mapping.yaml: source_policy must be 'rewrite' "
                      "(ADR-008 D2)")
        quarantine = self.mapping.get("quarantine_index")
        if quarantine not in registered:
            self._err(f"mapping.yaml: quarantine_index {quarantine!r} is not "
                      f"a registered index")


def main():
    """Validate the catalog and report."""
    import sys
    catalog = Catalog()
    print(f"catalog: {len(catalog.index_list)} indexes, "
          f"{len(catalog.legacy)} legacy feeds, "
          f"{len(catalog.fixtures)} coverage fixtures, "
          f"{len(catalog.units)} business units")
    counts = {c: len(g) for c, g in sorted(catalog.bundle_groups.items())}
    print(f"rbac:    {sum(counts.values())} bundles "
          f"({', '.join(f'{c}={n}' for c, n in counts.items())}), "
          f"{len(catalog.role_list)} roles, {len(catalog.user_list)} users, "
          f"{len(catalog.coverage_matrix['behaviours'])} covered behaviours")
    sensitive = [r["name"] for r in catalog.role_list
                 if catalog.role_is_sensitive(r["name"])]
    print(f"         sensitive role chains: {', '.join(sensitive) or 'none'}")
    if catalog.warnings:
        print(f"\n{len(catalog.warnings)} WARNINGS:")
        for warning in catalog.warnings:
            print(f"  {warning}")
    if catalog.errors:
        print(f"\n{len(catalog.errors)} ERRORS:")
        for error in catalog.errors:
            print(f"  {error}")
        return 1
    print("validation: clean")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
