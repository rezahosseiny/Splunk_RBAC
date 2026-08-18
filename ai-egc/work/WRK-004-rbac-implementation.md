---
id: WRK-004
type: work
title: Phase 4 — implement RBAC in Splunk
status: open
created: 2026-08-18
owner: Reza Hosseiny
---

# WRK-004 — Phase 4: RBAC implementation

Gated on WRK-003. Requires Splunk admin credentials in `config/.env`.

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
