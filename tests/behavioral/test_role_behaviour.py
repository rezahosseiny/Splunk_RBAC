"""Behavioural tests: what the live instance grants each role.

Every assertion compares observed Splunk behaviour against
`catalog/expectations.yaml`, which is written by hand. Nothing here derives an
expected value from the bundle definitions the generator reads, because that
would let a generator fault agree with itself and pass.

Two adjustments are applied, both recorded in `catalog/taxonomy.yaml` under
`platform_floors` and explained in ADR-014:

- Splunk 10.4.1 grants five capabilities to every user regardless of role, and no
  role configuration revokes them. The expected set is therefore the catalog's
  grant PLUS that recorded floor — and nothing else, so an unexplained sixth
  still fails.
- Some quota values are raised to a platform minimum, and `srchTimeWin: 0` reads
  back as `-1`.
"""

import pytest

from tests.conftest import context_of

pytestmark = pytest.mark.behavioral


def search_window(catalog, role):
    """A time range that fits inside the role's own srchTimeWin.

    A role with srchTimeWin set refuses a search spanning longer than that, so an
    all-time search makes such a role look as though it reaches nothing. The
    service account has a 24-hour window; the seeded data is all within one day,
    so a window just inside the role's limit sees everything it should.
    """
    limit = catalog.effective_quota(
        "srchTimeWin", catalog.computed_quotas(role).get("srchTimeWin", 0))
    if not limit or limit < 0:
        return "0", "+1d"
    hours = max(1, int(limit / 3600) - 1)
    return f"-{hours}h", "now"


def reachable(session, catalog=None, role=None):
    """Indexes this user can actually search, with the event count in each.

    One tstats over index=* answers both halves of the question: which indexes
    the user reaches, and how much is in them. Splunk returns nothing for an
    index the user cannot reach, so absence here IS the silent denial the
    strategy relies on.
    """
    earliest, latest = ("0", "+1d") if catalog is None else \
        search_window(catalog, role)
    rows = session.search("| tstats count where index=* by index",
                          earliest=earliest, latest=latest)
    return {row["index"]: int(row["count"]) for row in rows}


def test_roles(catalog, user_sessions):
    """Each user holds exactly one Business Role, and it is the right one."""
    for role, session in sorted(user_sessions.items()):
        context = context_of(session)
        assert context["roles"] == [role], (
            f"{context['username']} holds {context['roles']}, expected "
            f"exactly [{role}] — the one-role-per-user convention")


def test_capabilities(catalog, user_sessions):
    """Each role's capability set matches exactly. No extra, none missing."""
    problems = []
    for role, session in sorted(user_sessions.items()):
        live = context_of(session)["capabilities"]
        expected = set(catalog.expected_live_capabilities(role))
        extra, missing = sorted(live - expected), sorted(expected - live)
        if extra or missing:
            problems.append(f"{role}: extra={extra} missing={missing}")
    assert not problems, "\n  ".join(problems)


def test_platform_capability_floor_unchanged(catalog, user_sessions):
    """The recorded platform floor still describes the platform.

    Separate from test_capabilities on purpose. If an upgrade widens the floor,
    every role gains a capability nobody granted, and that must fail loudly here
    rather than be absorbed into each role's expected set.
    """
    recorded = catalog.platform_capability_floor()
    for capability in sorted(recorded):
        holders = [role for role, session in user_sessions.items()
                   if capability in context_of(session)["capabilities"]]
        assert len(holders) == len(user_sessions), (
            f"{capability} is recorded as a platform floor but only "
            f"{len(holders)} of {len(user_sessions)} roles hold it; the record "
            f"is now wrong")

    # Nothing beyond the record may reach every role.
    common = set.intersection(*[context_of(s)["capabilities"]
                                for s in user_sessions.values()])
    unearned = {c for c in common
                if any(c not in catalog.computed_capabilities(r)
                       for r in user_sessions)}
    assert unearned == recorded, (
        f"the platform floor has changed: newly universal={sorted(unearned - recorded)}, "
        f"no longer universal={sorted(recorded - unearned)}")


def test_data_access(catalog, user_sessions, seeded_counts):
    """Each role reaches exactly the indexes it must, and no others."""
    problems = []
    for role, session in sorted(user_sessions.items()):
        expect = catalog.expects[role]
        allowed = set(expect["allowed_indexes"])
        live = reachable(session, catalog, role)

        # Only indexes holding data can be observed, so compare within that set.
        observable = {name for name in allowed if seeded_counts.get(name)}
        unreachable = sorted(observable - set(live))
        if unreachable:
            problems.append(f"{role}: cannot reach {unreachable}, but the "
                            f"expectations allow them and they hold data")

        leaked = sorted(set(live) - allowed)
        if leaked:
            problems.append(f"{role}: reaches {leaked}, which the expectations "
                            f"do not allow")

        # Counts must match what was seeded, not merely be non-zero.
        for name in sorted(observable & set(live)):
            if live[name] != seeded_counts[name]:
                problems.append(f"{role}: {name} returned {live[name]} events, "
                                f"{seeded_counts[name]} were seeded")
    assert not problems, "\n  ".join(problems)


def test_data_access_denied_is_silent(catalog, user_sessions, seeded_counts):
    """A denied index named explicitly returns zero events, not an error.

    The wildcard test above proves the index is absent from index=*. This proves
    the other half: naming it directly is refused silently. A model that denied
    the wildcard but answered the named search would pass a weaker test.
    """
    for role, session in sorted(user_sessions.items()):
        for name in catalog.expects[role].get("must_not_reach", []):
            if not seeded_counts.get(name):
                continue                      # nothing to leak
            earliest, latest = search_window(catalog, role)
            rows = session.search(f"search index={name} | head 1 | stats count",
                                  earliest=earliest, latest=latest)
            count = int(rows[0]["count"]) if rows else 0
            assert count == 0, (
                f"{role} reached {name}, which its expectations forbid; "
                f"{count} events returned")


def test_quotas(catalog, admin, user_sessions):
    """Each role's runtime envelope matches the catalog, or its recorded floor."""
    problems = []
    for role in sorted(user_sessions):
        content = admin.get(
            f"/services/authorization/roles/{role}")["entry"][0]["content"]
        for key, value in sorted(catalog.computed_quotas(role).items()):
            if key in (catalog.taxonomy["platform_floors"]
                       .get("unsupported_attributes") or {}):
                continue                      # not stored on this release
            live = content.get(f"imported_{key}")
            expected = catalog.effective_quota(key, value)
            if live != expected:
                problems.append(f"{role}.{key}: live={live} expected={expected}")
    assert not problems, "\n  ".join(problems)


def test_quota_maximum_across_bundles(catalog, admin):
    """A quota is the MAXIMUM of each attribute, taken attribute by attribute.

    rl_cov_search holds pr_search_basic (5 jobs, 500 MB) and pr_search_burst
    (20 jobs, 200 MB). The result must be 20 jobs and 500 MB — one value from
    each bundle. Three wrong rules give three distinguishable wrong answers:
    last-wins gives 200 MB, least-wins gives 5 jobs, and taking the more
    generous bundle wholesale cannot produce this pair at all.
    """
    content = admin.get(
        "/services/authorization/roles/rl_cov_search")["entry"][0]["content"]
    assert content.get("imported_srchJobsQuota") == 20, (
        "the job quota should come from pr_search_burst")
    assert content.get("imported_srchDiskQuota") == 500, (
        "the disk quota should come from pr_search_basic")


def test_app_visibility(catalog, user_sessions):
    """Each role sees its workspace apps and no others."""
    problems = []
    for role, session in sorted(user_sessions.items()):
        expect = catalog.expects[role]
        visible = {entry["name"] for entry in
                   session.get("/services/apps/local",
                               params={"count": 0})["entry"]}
        for app in catalog.expected_visible_apps(role):
            if app not in visible:
                problems.append(f"{role}: cannot see {app}")
        for app in expect.get("hidden_apps") or []:
            if app in visible:
                problems.append(f"{role}: can see {app}, which is hidden for it")
    assert not problems, "\n  ".join(problems)


def test_workspace_bundle_grants_nothing_else(catalog, admin, user_sessions):
    """A workspace bundle changes app visibility and nothing else.

    rl_cov_workspace differs from rl_cov_base by one workspace bundle. Its index
    set, capability set, and quotas must be identical, which is what proves the
    empty stanza is correct rather than merely harmless.
    """
    base, work = "rl_cov_base", "rl_cov_workspace"
    assert (context_of(user_sessions[base])["capabilities"]
            == context_of(user_sessions[work])["capabilities"]), (
        "the workspace bundle changed the capability set")
    assert (reachable(user_sessions[base], catalog, base)
            == reachable(user_sessions[work], catalog, work)), (
        "the workspace bundle changed index access")
    for key in ("srchJobsQuota", "srchDiskQuota", "srchTimeWin"):
        a = admin.get(f"/services/authorization/roles/{base}")["entry"][0]
        b = admin.get(f"/services/authorization/roles/{work}")["entry"][0]
        assert a["content"].get(f"imported_{key}") == \
            b["content"].get(f"imported_{key}"), (
            f"the workspace bundle changed {key}")


def test_differential_pairs(catalog, admin, user_sessions):
    """Each coverage role differs from the control in exactly one dimension."""
    base = "rl_cov_base"
    base_caps = context_of(user_sessions[base])["capabilities"]
    base_idx = set(reachable(user_sessions[base], catalog, base))

    # A data bundle changes index access only.
    assert context_of(user_sessions["rl_cov_data"])["capabilities"] == base_caps
    assert set(reachable(user_sessions["rl_cov_data"], catalog,
                         "rl_cov_data")) > base_idx

    # A feature bundle changes capabilities only.
    feat_caps = context_of(user_sessions["rl_cov_feat"])["capabilities"]
    assert feat_caps > base_caps
    assert feat_caps - base_caps == {"output_file"}
    assert set(reachable(user_sessions["rl_cov_feat"], catalog,
                         "rl_cov_feat")) == base_idx

    # Overlapping data bundles union rather than replace.
    overlap = set(reachable(user_sessions["rl_cov_overlap"], catalog,
                            "rl_cov_overlap"))
    assert overlap > base_idx, (
        "overlapping index sets did not union; if the last bundle won, the "
        "result would be smaller than the control's")


def test_builtin_roles_unmodified(catalog, admin):
    """No built-in role was modified, and none imports a project bundle."""
    builtin = catalog.taxonomy["builtin_roles"]
    for name in builtin:
        entry = admin.get(
            f"/services/authorization/roles/{name}")["entry"][0]
        imported = set(entry["content"].get("imported_roles") or [])
        project = {r for r in imported if r.startswith(("pr_", "rl_"))}
        assert not project, f"built-in role {name} imports {sorted(project)}"
        assert entry["acl"].get("app") != "tristate_rbac", (
            f"built-in role {name} is defined in this project's app")

    # And no project role imports a built-in.
    for role in catalog.role_list:
        entry = admin.get(
            f"/services/authorization/roles/{role['name']}")["entry"][0]
        imported = set(entry["content"].get("imported_roles") or [])
        assert not imported & set(builtin), (
            f"{role['name']} imports a built-in role")


def test_no_project_role_outside_the_rbac_app(catalog, admin):
    """Nothing this project defines lives outside its deployment app.

    The strategy prohibits UI-driven RBAC changes because they land in
    etc/system/local, which is per-member and outside version control. This is
    the same question the drift detection asks, asserted directly.
    """
    rows = admin.search(
        "| rest /servicesNS/-/-/configs/conf-authorize "
        "| eval app='eai:acl.app' "
        "| search title=role_rl_* OR title=role_pr_* "
        "| search NOT app=tristate_rbac | table title app",
        earliest="0", latest="now")
    assert not rows, f"project roles defined outside tristate_rbac: {rows}"
