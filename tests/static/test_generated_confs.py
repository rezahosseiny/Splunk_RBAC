"""Static tests on the generated app tree.

These read what the generator produced, not what the catalog says. A generator
that drops a stanza, or writes a permission the catalog never asked for, is
invisible to a catalog-only check.
"""

import os
import re

import pytest


def parse_conf(path):
    """Parse a Splunk .conf into {stanza: {key: value}}."""
    stanzas, current = {}, None
    with open(path, encoding="utf-8") as handle:
        for raw in handle:
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("[") and line.endswith("]"):
                current = line[1:-1]
                stanzas.setdefault(current, {})
            elif current is not None and "=" in line:
                key, _, value = line.partition("=")
                stanzas[current][key.strip()] = value.strip()
    return stanzas


@pytest.fixture(scope="module")
def authorize(build_dir):
    path = os.path.join(build_dir, "tristate_rbac", "local", "authorize.conf")
    assert os.path.exists(path), "authorize.conf was not generated"
    return parse_conf(path)


def test_generated_confs(catalog, authorize, build_dir):
    """Every stanza round-trips to the catalog, and holds only what it should."""
    for name in catalog.bundle_by_name:
        assert f"role_{name}" in authorize, f"bundle {name} has no stanza"
    for role in catalog.role_list:
        assert f"role_{role['name']}" in authorize, (
            f"role {role['name']} has no stanza")

    # A Business Role stanza holds importRoles and nothing else.
    for role in catalog.role_list:
        stanza = authorize[f"role_{role['name']}"]
        assert set(stanza) == {"importRoles"}, (
            f"{role['name']} stanza holds {sorted(stanza)}; a Business Role "
            f"must carry no permission of its own")
        imported = stanza["importRoles"].split(";")
        assert imported == role["bundles"], (
            f"{role['name']} imports {imported}, catalog says {role['bundles']}")

    # A workspace stanza is empty. This is the half that must grant nothing.
    for bundle in catalog.bundle_groups["workspace"]:
        assert authorize[f"role_{bundle['name']}"] == {}, (
            f"{bundle['name']} stanza is not empty")

    # A data bundle's index list round-trips.
    for bundle in catalog.bundle_groups["data"]:
        stanza = authorize[f"role_{bundle['name']}"]
        assert stanza["srchIndexesAllowed"].split(";") == \
            bundle["indexes_allowed"], bundle["name"]

    # A search bundle writes each capability as enabled, plus its envelope.
    for bundle in catalog.bundle_groups["search"]:
        stanza = authorize[f"role_{bundle['name']}"]
        for capability in bundle["capabilities"]:
            assert stanza.get(capability) == "enabled", (
                f"{bundle['name']}.{capability}")
        for key, value in bundle["envelope"].items():
            assert stanza.get(key) == str(value), f"{bundle['name']}.{key}"

    # No stanza imports a built-in role.
    builtin = set(catalog.taxonomy["builtin_roles"])
    for stanza, values in authorize.items():
        imported = set((values.get("importRoles") or "").split(";")) - {""}
        assert not imported & builtin, f"{stanza} imports a built-in role"


def test_roleMap_template(catalog, build_dir):
    """The identity-provider mapping has exactly one role on each line.

    Text only. Live SAML behaviour needs an identity provider this environment
    does not have, so this checks the contract rather than the behaviour.
    """
    path = os.path.join(build_dir, "tristate_rbac", "local",
                        "authentication.conf.template")
    assert os.path.exists(path), "the roleMap template was not generated"
    with open(path, encoding="utf-8") as handle:
        lines = [l.strip() for l in handle
                 if l.strip() and not l.startswith("#")]
    assert lines[0] == "[roleMap_SAML]"

    mapped = {}
    for line in lines[1:]:
        group, _, role = line.partition("=")
        group, role = group.strip(), role.strip()
        assert group.startswith("GRP_splunk_"), line
        assert ";" not in role and "," not in role, (
            f"{line}: exactly one role must appear on the right")
        assert role.startswith("rl_"), (
            f"{line}: only a Business Role may be mapped; direct assignment of "
            f"a pr_* bundle is prohibited")
        assert group == f"GRP_splunk_{role}", line
        mapped[role] = group

    # Population roles are mapped; coverage roles have no production population.
    population = {r["name"] for r in catalog.role_list
                  if r.get("purpose") != "coverage"}
    assert set(mapped) == population, (
        f"unmapped population roles: {sorted(population - set(mapped))}; "
        f"unexpected: {sorted(set(mapped) - population)}")


def test_detections_generated(catalog, build_dir):
    """All seven detections exist, are scheduled, and alert on a result."""
    path = os.path.join(build_dir, "tristate_rbac", "local",
                        "savedsearches.conf")
    stanzas = parse_conf(path)
    expected = {
        "al_rbac_multi_role_assignment",
        "al_rbac_direct_bundle_assignment",
        "al_rbac_sensitive_capability_sprawl",
        "al_rbac_destructive_capability_check",
        "al_rbac_configuration_drift",
        "al_rbac_sensitive_role_chain_membership",
        "al_rbac_capability_catalog_change",
    }
    assert set(stanzas) == expected, (
        f"missing: {sorted(expected - set(stanzas))}; "
        f"unexpected: {sorted(set(stanzas) - expected)}")
    for name, values in stanzas.items():
        assert values.get("search"), f"{name} has no search"
        assert values.get("enableSched") == "1", f"{name} is not scheduled"
        assert values.get("disabled") == "0", f"{name} is disabled"
        assert values.get("cron_schedule"), f"{name} has no schedule"


def test_workspace_apps_generated(catalog, build_dir):
    """A workspace is a two-file construct, and both halves must exist."""
    for bundle in catalog.bundle_groups["workspace"]:
        for app in bundle["apps"]:
            meta = os.path.join(build_dir, app, "metadata", "local.meta")
            assert os.path.exists(meta), f"{app} has no local.meta"
            with open(meta, encoding="utf-8") as handle:
                text = handle.read()
            # The grant must name the workspace role, or the role reaches nothing.
            assert f"read : [ {bundle['name']} ]" in text, (
                f"{app} does not grant read to {bundle['name']}")
            assert "write : [ rl_platform_admin ]" in text, (
                f"{app} does not restrict write to the platform administrator")
            view = os.path.join(app, "default", "data", "ui", "views")
            assert os.path.isdir(os.path.join(build_dir, view)), (
                f"{app} has no view, so app visibility cannot be observed")


def test_rbac_app_write_restricted(build_dir):
    """Write access to the RBAC app is restricted.

    The strategy makes this the technical enforcement of the rule that RBAC is
    changed only through this app and never through Splunk Web.
    """
    path = os.path.join(build_dir, "tristate_rbac", "metadata", "local.meta")
    with open(path, encoding="utf-8") as handle:
        text = handle.read()
    match = re.search(r"access\s*=\s*(.+)", text)
    assert match, "no access line in the RBAC app metadata"
    assert "write : [ admin ]" in match.group(1), (
        f"write access is not restricted: {match.group(1)}")


def test_indexes_conf_retention(catalog, build_dir):
    """Each index carries the retention its name encodes."""
    path = os.path.join(build_dir, "tristate_indexes", "local", "indexes.conf")
    stanzas = parse_conf(path)
    for entry in catalog.index_list:
        name = entry["name"]
        if name in catalog.provided:
            assert name not in stanzas, (
                f"{name} is provided by Splunk and must not be redefined")
            continue
        assert name in stanzas, f"{name} has no stanza"
        expected = catalog.frozen_seconds(name)
        if expected:
            assert stanzas[name].get("frozenTimePeriodInSecs") == str(expected), (
                f"{name}: retention does not match the catalog")
