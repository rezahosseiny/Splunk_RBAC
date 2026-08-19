"""Static tests on the catalog itself. No Splunk instance needed.

These run before anything is deployed. A fault caught here costs a rebuild; the
same fault caught after deployment costs a restart and a reseed.
"""

import re

import pytest

from generators import loader


def test_catalog_integrity(catalog):
    """The catalog is internally consistent."""
    assert catalog.errors == [], (
        "catalog has errors:\n  " + "\n  ".join(catalog.errors))


def test_naming(catalog):
    """Every name obeys the strategy's naming standard."""
    problems = []
    for entry in catalog.index_list:
        name = entry["name"]
        if entry.get("naming_exception"):
            # The exception excuses the index NAME only.
            assert entry["naming_exception"] in catalog.taxonomy[
                "naming_exception_classes"], name
            continue
        fields = catalog.decode(name)
        assert fields, f"index {name} does not match the schema"
        for field, table in (("data_class", "classes"),
                             ("compliance", "compliance"),
                             ("domain", "domains"), ("content", "content")):
            if fields[field] not in catalog.taxonomy[table]:
                problems.append(f"{name}: {field} code {fields[field]!r} "
                                f"is not registered")
        if fields["retention"] not in catalog.taxonomy["retention"]:
            problems.append(f"{name}: retention {fields['retention']!r}")

    for name in catalog.bundle_by_name:
        if not loader.BUNDLE_RE.match(name):
            problems.append(f"bundle {name} does not match pr_<category>_<name>")
    for role in catalog.role_list:
        if not loader.ROLE_RE.match(role["name"]):
            problems.append(f"role {role['name']} does not match rl_<name>")
    assert not problems, "\n  ".join(problems)


def test_bundle_concerns(catalog):
    """A bundle holds only what its own category permits.

    This is what makes bundles composable: any data bundle must combine with any
    search, feature, and workspace bundle without one silently affecting another.
    """
    permitted = {
        "data": {"indexes_allowed", "indexes_default", "srch_filter"},
        "search": {"capabilities", "envelope"},
        "feat": {"capabilities"},
        "workspace": {"apps"},
    }
    for category, group in catalog.bundle_groups.items():
        for bundle in group:
            held = {key for key in ("indexes_allowed", "indexes_default",
                                    "srch_filter", "capabilities", "envelope",
                                    "apps") if bundle.get(key)}
            extra = held - permitted[category]
            assert not extra, (f"{bundle['name']} ({category}) holds {extra}, "
                               f"which belongs to another category")

    search_exec = set(catalog.taxonomy["search_execution_capabilities"])
    for bundle in catalog.bundle_groups["search"]:
        assert set(bundle["capabilities"]) <= search_exec, bundle["name"]
    for bundle in catalog.bundle_groups["feat"]:
        assert not set(bundle["capabilities"]) & search_exec, (
            f"{bundle['name']} holds a search-execution capability, which "
            f"belongs in a pr_search_* bundle")

    # A workspace bundle must grant nothing but app access. That is what makes
    # the empty stanza correct rather than merely harmless.
    for bundle in catalog.bundle_groups["workspace"]:
        for key in ("capabilities", "indexes_allowed", "envelope"):
            assert not bundle.get(key), f"{bundle['name']} holds {key}"


def test_sensitive_caps(catalog):
    """A sensitive capability lives only in a flagged pr_feat_admin_* bundle."""
    for name, bundle in catalog.bundle_by_name.items():
        held = set(bundle.get("capabilities", [])) & catalog.sensitive_caps
        if not held:
            continue
        assert name.startswith("pr_feat_admin_"), (
            f"{name} holds sensitive capabilities {sorted(held)}")
        assert bundle.get("sensitive"), f"{name} is not flagged sensitive"
        assert bundle.get("governance"), f"{name} has no governance block"

    allowlist = set(catalog.taxonomy["destructive_capability_allowlist"])
    destructive = set(catalog.taxonomy["destructive_capabilities"])
    for role in catalog.role_list:
        held = set(catalog.computed_capabilities(role["name"])) & destructive
        if held:
            assert role["name"] in allowlist, (
                f"{role['name']} holds {sorted(held)} but is not in the "
                f"destructive-capability allow-list")

    # Separation of duties: no role may both administer and destroy.
    for role in catalog.role_list:
        caps = set(catalog.computed_capabilities(role["name"]))
        assert not ({"edit_user", "edit_roles"} & caps and destructive & caps), (
            f"{role['name']} can both change roles and destroy data")


def test_roles_composition(catalog):
    """A Business Role composes bundles and holds nothing directly."""
    builtin = set(catalog.taxonomy["builtin_roles"])
    for role in catalog.role_list:
        for key in ("capabilities", "indexes_allowed", "envelope", "apps"):
            assert not role.get(key), f"{role['name']} holds {key} directly"
        assert role.get("bundles"), f"{role['name']} imports nothing"
        assert not set(role["bundles"]) & builtin, (
            f"{role['name']} imports a built-in role")
        for bundle in role["bundles"]:
            assert bundle in catalog.bundle_by_name, (
                f"{role['name']} imports unknown bundle {bundle}")

    # One user per role, and one role per user.
    by_role = {}
    for user in catalog.user_list:
        assert user["role"] not in by_role, (
            f"role {user['role']} has two test users")
        by_role[user["role"]] = user["username"]
    assert set(by_role) == set(catalog.role_by_name), (
        "every role needs exactly one test user; missing: "
        f"{sorted(set(catalog.role_by_name) - set(by_role))}")

    # A service account defaults to the constrained envelope.
    for role in catalog.role_list:
        if loader.SVC_ROLE_RE.match(role["name"]):
            names = [b["name"] for b in
                     catalog.role_bundles(role["name"], "search")]
            assert names == ["pr_search_constrained"] or role.get(
                "wider_envelope_justification"), (
                f"{role['name']} needs pr_search_constrained or a written "
                f"justification for a wider envelope")


def test_expectations_consistency(catalog):
    """The hand-written expectations agree with the composed bundles.

    This is the check that makes the expectations trustworthy. If they were
    generated from the bundles, this comparison would always agree and would
    prove nothing; because they are written by hand, a disagreement means either
    the composition or the recorded intent is wrong.
    """
    problems = []
    for name in sorted(catalog.role_by_name):
        expect = catalog.expects.get(name)
        assert expect, f"{name} has no expectations entry"
        assert expect.get("intent"), f"{name} records no intent"
        for label, stated, computed in (
                ("allowed_indexes", expect["allowed_indexes"],
                 catalog.computed_indexes(name)),
                ("capabilities", expect["capabilities"],
                 catalog.computed_capabilities(name)),
                ("visible_apps", expect["visible_apps"],
                 catalog.computed_workspace_apps(name))):
            if set(stated) != set(computed):
                problems.append(
                    f"{name}.{label}: stated-only={sorted(set(stated)-set(computed))} "
                    f"bundles-only={sorted(set(computed)-set(stated))}")
        for key, value in catalog.computed_quotas(name).items():
            if expect["quotas"].get(key) != value:
                problems.append(f"{name}.quotas.{key}: stated "
                                f"{expect['quotas'].get(key)}, bundles give "
                                f"{value}")
    assert not problems, "\n  ".join(problems)


def test_capability_names_exist(catalog):
    """Every capability the catalog grants exists on the target release.

    Not hypothetical: three names the strategy gives do not exist on Splunk
    10.4.1, and Splunk rejects an unknown capability rather than ignoring it.
    """
    import json
    import os
    path = os.path.join(loader.ROOT, "reports", "capability_baseline.json")
    if not os.path.exists(path):
        pytest.skip("no capability baseline — run `make capability-baseline`")
    with open(path, encoding="utf-8") as handle:
        available = set(json.load(handle))
    problems = []
    for name, bundle in sorted(catalog.bundle_by_name.items()):
        for capability in bundle.get("capabilities", []):
            if capability not in available:
                problems.append(f"{name}: {capability!r} does not exist")
    for group in ("sensitive_capabilities", "destructive_capabilities"):
        for capability in catalog.taxonomy.get(group) or []:
            if capability not in available:
                problems.append(f"taxonomy.{group}: {capability!r}")
    assert not problems, "\n  ".join(problems)


def test_sizing(catalog):
    """Bundle counts stay inside the strategy's targets.

    A warning, not a failure: the strategy permits growth with justification.
    """
    outside = []
    for category, group in catalog.bundle_groups.items():
        target = catalog.taxonomy["sizing_targets"].get(f"pr_{category}")
        if target and not target["min"] <= len(group) <= target["max"]:
            outside.append(f"pr_{category}: {len(group)} bundles, target "
                           f"{target['min']}-{target['max']}")
    if outside:
        pytest.skip("sizing outside target (permitted with justification): "
                    + "; ".join(outside))


def test_mapping_covers_the_samples(catalog):
    """Every value in every sample export resolves through the mapping."""
    import csv
    import glob
    import os
    import sys as _sys
    csv.field_size_limit(_sys.maxsize)
    exports = sorted(glob.glob(os.path.join(loader.ROOT, "sample_data",
                                            "*.csv")))
    if not exports:
        pytest.skip("no sample export to check")
    gaps = set()
    for path in exports:
        with open(path, newline="", encoding="utf-8", errors="replace") as fh:
            for row in csv.DictReader(fh):
                index = (row.get("index") or "").strip()
                if not index:
                    continue
                st = (row.get("sourcetype") or "").strip()
                if catalog.rule_for(index, st) is None:
                    gaps.add((index, st))
    assert not gaps, ("unmapped pairs:\n  "
                      + "\n  ".join(f"{i} / {s}" for i, s in sorted(gaps)))


def test_coverage_matrix_is_complete(catalog):
    """Every asserted behaviour names a test, and every named test exists.

    The second half matters as much as the first: a row naming a test that was
    renamed or deleted looks covered and is not.

    The check reads the test SOURCE rather than what pytest collected, so it is
    valid whether the whole suite runs or only one directory. Relying on
    collection made it fail whenever the static suite ran alone, which would
    have trained everyone to ignore it.
    """
    import glob
    import os
    import re as _re
    defined = set()
    for path in glob.glob(os.path.join(loader.ROOT, "tests", "**", "test_*.py"),
                          recursive=True):
        with open(path, encoding="utf-8") as handle:
            defined.update(_re.findall(r"^def (test_\w+)", handle.read(),
                                       _re.M))
    named = set()
    for row in catalog.coverage_matrix["behaviours"]:
        assert row.get("tests"), f"{row['id']} names no test"
        assert row.get("observable_because"), (
            f"{row['id']} does not say why it is observable")
        named.update(row["tests"])
    missing = sorted(named - defined)
    assert not missing, ("the coverage matrix names tests that do not exist: "
                         + ", ".join(missing))
