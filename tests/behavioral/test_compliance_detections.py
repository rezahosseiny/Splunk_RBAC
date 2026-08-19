"""The seven standing detections, and proof that each one can fire.

Running a detection on a healthy environment and seeing nothing proves very
little: a detection that can never fire looks identical. Each test here therefore
injects the violation the detection exists to catch, asserts the detection
reports it, and reverts.

Every injection reverts in a `finally` block, and a session-scoped check at the
end asserts the environment is clean again. A test that leaves a violation behind
would make every later test suspect.
"""

import urllib.parse

import pytest

pytestmark = pytest.mark.behavioral

DETECTIONS = [
    "al_rbac_multi_role_assignment",
    "al_rbac_direct_bundle_assignment",
    "al_rbac_sensitive_capability_sprawl",
    "al_rbac_destructive_capability_check",
    "al_rbac_configuration_drift",
    "al_rbac_sensitive_role_chain_membership",
    "al_rbac_capability_catalog_change",
]

# Returns rows on a healthy environment by design: it is recertification
# evidence for the sensitive tier, not a violation report.
EVIDENCE_DETECTIONS = {"al_rbac_sensitive_role_chain_membership"}

APP = "tristate_rbac"


def spl_of(admin, name):
    entry = admin.get(f"/servicesNS/nobody/{APP}/saved/searches/"
                      f"{urllib.parse.quote(name)}")["entry"][0]
    return entry["content"]["search"]


def run(admin, name, spl=None):
    return admin.search(spl or spl_of(admin, name),
                        earliest="-24h", latest="now")


def set_role_capabilities(admin, role, capabilities):
    """Replace a role's capability list through the roles endpoint.

    The generic conf endpoint accepts the write but the roles endpoint does not
    reflect it until a reload, so an injection made that way appears to fail. The
    object endpoint applies immediately, which is what an injection test needs.
    """
    payload = [("capabilities", c) for c in sorted(capabilities)] or \
        [("capabilities", "")]
    admin.post(f"/servicesNS/nobody/{APP}/authorization/roles/"
               f"{urllib.parse.quote(role)}", data=payload)


@pytest.fixture(scope="module")
def all_detections_present(admin):
    """Every detection exists before any of them is exercised."""
    names = {entry["name"] for entry in
             admin.get(f"/servicesNS/nobody/{APP}/saved/searches",
                       params={"count": 0})["entry"]}
    missing = [d for d in DETECTIONS if d not in names]
    assert not missing, f"detections not deployed: {missing}"
    return names


def test_compliance_detections(admin, all_detections_present):
    """All seven run, and each behaves correctly on a healthy environment."""
    for name in DETECTIONS:
        rows = run(admin, name)
        if name in EVIDENCE_DETECTIONS:
            assert rows, (f"{name} returned nothing; it should report the "
                          f"sensitive role chain holders as evidence")
        else:
            assert not rows, f"{name} reports a violation: {rows[:4]}"


def test_injection_multi_role_assignment(admin, catalog,
                                         all_detections_present):
    """Give a user a second Business Role and watch the detection catch it."""
    name = "al_rbac_multi_role_assignment"
    username, first = "t_noc_operator", "rl_noc_operator"
    second = "rl_cov_base"
    path = f"/services/authentication/users/{username}"
    try:
        admin.post(path, data=[("roles", first), ("roles", second)])
        rows = run(admin, name)
        assert any(r.get("title") == username for r in rows), (
            f"{name} did not report {username} holding two roles: {rows}")
    finally:
        admin.post(path, data={"roles": first})
    assert not run(admin, name), "the environment was not restored"


def test_injection_direct_bundle_assignment(admin, all_detections_present):
    """Assign a Privilege Bundle straight to a user."""
    name = "al_rbac_direct_bundle_assignment"
    username, proper = "t_noc_operator", "rl_noc_operator"
    path = f"/services/authentication/users/{username}"
    try:
        admin.post(path, data={"roles": "pr_data_ops_infra"})
        rows = run(admin, name)
        assert any(r.get("title") == username for r in rows), (
            f"{name} did not report the direct bundle assignment: {rows}")
    finally:
        admin.post(path, data={"roles": proper})
    assert not run(admin, name), "the environment was not restored"


def test_injection_sensitive_capability_sprawl(admin, catalog,
                                               all_detections_present):
    """Add a sensitive capability to a routine bundle."""
    name = "al_rbac_sensitive_capability_sprawl"
    bundle, capability = "pr_feat_dashboards", "edit_user"
    original = catalog.bundle_by_name[bundle]["capabilities"]
    try:
        set_role_capabilities(admin, bundle, list(original) + [capability])
        rows = run(admin, name)
        assert any(r.get("title") == bundle for r in rows), (
            f"{name} did not report {capability} on {bundle}: {rows}")
    finally:
        set_role_capabilities(admin, bundle, original)
    assert not run(admin, name), "the environment was not restored"


def test_injection_destructive_capability_check(admin, catalog,
                                                all_detections_present):
    """Give a Business Role outside the allow-list a destructive capability."""
    name = "al_rbac_destructive_capability_check"
    role, capability = "rl_noc_operator", "delete_by_keyword"
    assert role not in catalog.taxonomy["destructive_capability_allowlist"]
    try:
        set_role_capabilities(admin, role, [capability])
        rows = run(admin, name)
        assert any(r.get("title") == role for r in rows), (
            f"{name} did not report {capability} on {role}: {rows}")
    finally:
        set_role_capabilities(admin, role, [])
    assert not run(admin, name), "the environment was not restored"


def test_injection_configuration_drift(admin, all_detections_present):
    """Define a project role outside the deployment app.

    This is what a Splunk Web edit produces: a stanza in an app that is not the
    versioned deployment app.
    """
    name = "al_rbac_configuration_drift"
    stanza, foreign_app = "role_rl_drift_probe", "search"
    path = (f"/servicesNS/nobody/{foreign_app}/configs/conf-authorize/"
            f"{stanza}")
    created = False
    try:
        admin.post(f"/servicesNS/nobody/{foreign_app}/configs/conf-authorize",
                   data={"name": stanza, "srchIndexesAllowed": "main"})
        created = True
        rows = run(admin, name)
        assert any(r.get("title") == stanza for r in rows), (
            f"{name} did not report the drifted stanza: {rows}")
    finally:
        if created:
            admin.delete(path)
    assert not run(admin, name), "the environment was not restored"


def test_injection_sensitive_role_chain_membership(admin, catalog,
                                                  all_detections_present):
    """Add a holder to a sensitive role chain and watch the evidence change.

    This detection reports evidence rather than a violation, so the injection is
    a new holder appearing rather than the search turning from empty to full.
    """
    name = "al_rbac_sensitive_role_chain_membership"
    username, proper = "t_cov_base", "rl_cov_base"
    sensitive = "rl_platform_admin"
    before = {r.get("title") for r in run(admin, name)}
    assert username not in before
    path = f"/services/authentication/users/{username}"
    try:
        admin.post(path, data={"roles": sensitive})
        after = {r.get("title") for r in run(admin, name)}
        assert username in after, (
            f"{name} did not report the new holder of {sensitive}: {after}")
    finally:
        admin.post(path, data={"roles": proper})
    assert {r.get("title") for r in run(admin, name)} == before, (
        "the environment was not restored")


def test_injection_capability_catalog_change(admin, catalog,
                                             all_detections_present):
    """Simulate an upgrade adding a capability.

    Splunk's capability catalog cannot be changed from outside, so the injection
    runs the detection against a baseline with one capability removed. That is
    exactly what an upgrade looks like to this search: the live catalog holds
    something the baseline does not.
    """
    name = "al_rbac_capability_catalog_change"
    spl = spl_of(admin, name)
    assert not run(admin, name, spl), "the baseline already disagrees"

    victim = "search"
    assert f'{victim},' in spl or f',{victim},' in spl, (
        f"{victim} is not in the embedded baseline")
    tampered = spl.replace(f",{victim},", ",", 1)
    rows = run(admin, name, tampered)
    reported = {r.get("capability"): r.get("change") for r in rows}
    assert reported.get(victim) == "added", (
        f"{name} did not report {victim} as added against a baseline missing "
        f"it: {rows}")

    # Nothing was changed on the instance, so nothing needs reverting: the
    # tampering was applied to a copy of the search string.
    assert not run(admin, name), "the deployed detection was altered"


def test_environment_is_clean_after_injection(admin, all_detections_present):
    """Every detection is quiet again once the injections have reverted."""
    still_firing = []
    for name in DETECTIONS:
        if name in EVIDENCE_DETECTIONS:
            continue
        if run(admin, name):
            still_firing.append(name)
    assert not still_firing, (
        f"these detections still report a violation, so an injection was not "
        f"reverted: {still_firing}")
