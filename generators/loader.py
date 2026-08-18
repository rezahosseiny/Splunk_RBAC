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

    FILES = ("taxonomy", "mapping", "indexes", "business_units", "redaction")

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
        self.errors = []
        self._validate()

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
