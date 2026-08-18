---
id: WRK-004
type: work
title: Phase 4 — implement RBAC in Splunk
status: completed
created: 2026-08-18
owner: Reza Hosseiny
---

# WRK-004 — Phase 4: RBAC implementation

WRK-003 approved 2026-08-18. This phase is active. Credentials are in
`config/.env`.

## Objective

Generate and deploy the full RBAC configuration to the dev instance as
apps, with no UI edits and nothing written to `etc/system/local/`.

## Work

- `tristate_rbac/local/authorize.conf` — every `pr_*` bundle and `rl_*`
  role. Data bundles: `srchIndexesAllowed` (semicolon-separated),
  `srchIndexesDefault`, optional `srchFilter`. Search bundles:
  `<cap> = enabled` plus envelope attributes. Feature bundles:
  capabilities only. Workspace bundles: empty stanza with an explanatory
  comment. Roles: `importRoles` only.
- `tristate_rbac/local/authentication.conf.template` — SAML roleMap,
  exactly one `GRP_splunk_<role> = <role>` line per Business Role. Not
  deployed on the test VM (ADR-003).
- `tristate_rbac/local/savedsearches.conf` — the seven detections as
  `al_rbac_*` saved searches: multi-role assignment, direct bundle
  assignment, sensitive capability sprawl, destructive capability check,
  configuration drift, sensitive role chain membership, capability
  catalog change.
- `tristate_rbac/metadata/local.meta` — write restricted to platform
  admins (the strategy's technical enforcement of the no-UI-edits rule).
- `tristate_rbac/default/app.conf` — version stamped from VERSION or a
  catalog hash, incremented on every change.
- One app per `pr_workspace_*` bundle: `app.conf`, `local.meta` granting
  read to the workspace role and write to `rl_platform_admin`, a nav
  file, and a placeholder dashboard so visibility is testable.
- `deploy/create_users.py` — recreate each test user with exactly one
  role; random passwords to `config/test_user_credentials.json`.
- `deploy/capability_inventory.py` — dump the capability catalog to a
  dated JSON under `reports/` and diff against the previous baseline,
  supporting the strategy's upgrade triage process.

## Acceptance criteria

1. `make deploy && make users` leaves every bundle, role, user, and
   workspace app live on the instance; roles and capabilities resolve as
   the catalog defines.
2. `etc/system/local/authorize.conf` contains no project stanzas.
3. All seven detections exist and are runnable.
4. A capability baseline for Splunk 10.4.1 is captured.
5. Built-in roles are unmodified (verified against a pre-deploy
   snapshot).

## Evidence (on completion)

Deploy log, `reports/capability_baseline_<date>.json`, a role/bundle
listing pulled live from REST, and confirmation of an empty
`etc/system/local/authorize.conf`.

## Deployed and verified — 2026-08-18

| Item | Result |
|---|---|
| Bundles live | 29 of 29 |
| Business Roles live | 15 of 15 |
| Test users | 15 created, each holding exactly one role |
| Detections | 7 of 7 deployed as `al_rbac_*` |
| Apps | 6 of 6: tristate_indexes, tristate_rbac, and 4 workspaces |
| Built-in roles | unmodified; no bundle or role imports one |
| Index sets | every role matches the catalog exactly |
| Quotas | every role matches the catalog, or its recorded platform floor |
| Capability sets | all 15 users reconcile against the grant plus the recorded floor |

**The quota MAXIMUM rule is proven on the live platform.** `rl_cov_search`
resolves to `imported_srchJobsQuota = 20` from `pr_search_burst` and
`imported_srchDiskQuota = 500` from `pr_search_basic`. Neither bundle supplies
both, so the result cannot be explained by any rule other than a per-attribute
maximum.

## Four platform findings (ADR-014)

Phase 4's real product. None is a catalog fault; all four limit what the strategy
can claim, and none would have been visible without asking a real user.

1. **A capability floor no role configuration can remove.** All five of
   `schedule_rtsearch`, `list_all_objects`, `run_mcollect`, `run_collect`, and
   `edit_own_objects` reach every user. Two — `run_collect` and `run_mcollect` —
   are in this strategy's sensitive AND destructive tiers. Explicit
   `= disabled` was tried on an imported bundle and on the directly held role;
   neither revoked anything. **The sensitive-tier isolation the strategy
   requires is therefore not achievable for those two on Splunk 10.4.1.**
2. **`srchMaxTime` is not stored.** The write is accepted and the attribute
   comes back absent, so a search-duration limit is not available through RBAC.
3. **Quota floors.** `srchJobsQuota` cannot go below 3 and `rtSrchJobsQuota`
   cannot go below 6, for any positive value. A service-account envelope
   narrower than three concurrent searches is not achievable.
4. **`srchTimeWin: 0` reads back as `-1`.** The same intent in two
   representations, so a naive comparison reports a false mismatch.

The floors are recorded in `catalog/taxonomy.yaml` as measured facts rather than
folded into the expectations. Folding them in would make every test pass and hide
that two sensitive capabilities reach every user, which is the most important
thing this phase found.

## Three deployment defects fixed

1. **Empty stanzas were skipped**, so no `pr_workspace_*` role deployed at all —
   the exact half-implemented workspace the strategy warns about, created by the
   deployer. An empty stanza is what a workspace bundle IS.
2. **Only `local/*.conf` was pushed.** Fifteen files — every `metadata/local.meta`,
   every dashboard, every nav file — were skipped silently, so the workspace
   access grants never reached the instance. The path now pushes views and nav
   through the UI endpoint, applies `local.meta` as object ACLs, and NAMES
   anything it cannot deploy.
3. **Attribute-level drift was never reconciled.** `upsert` set the keys present
   in the file and never removed one that had gone, so a capability dropped from
   a bundle would stay granted for ever with no report showing it.
   `authorize.conf` stanzas are now replaced rather than merged.

A fourth is recorded as a limitation, not fixed: the lookup-table-files endpoint
needs the file staged on the Splunk filesystem first, which the API path cannot
do. The capability baseline is embedded in its detection's SPL instead, which
also stops the detection comparing against a stale lookup.

## Acceptance criteria

1. Every bundle, role, user, and workspace app live and resolving as the catalog
   defines. — **met**, with the platform floors recorded.
2. `etc/system/local/authorize.conf` holds no project stanzas. — **met**; every
   role reports `app=tristate_rbac`.
3. All seven detections exist and are runnable. — **met**.
4. A capability baseline for Splunk 10.4.1 captured. — **met**.
5. Built-in roles unmodified. — **met**.

Phase 5 must now run the detections and prove each fires on injection. Note that
`al_rbac_destructive_capability_check` will report 14 of 15 roles, correctly,
because of finding 1.
