---
id: INT-001
type: intention
title: Prove the Splunk Strategy 2.0 RBAC model with an automated test harness
status: approved
created: 2026-08-18
owner: Reza Hosseiny
supersedes: null
superseded_by: null
---

# INT-001 — Purpose

**Framework:** AI-EGC Framework<br>
**Author:** Reza Hosseiny<br>
**Version:** 0.3.1

## Why this project exists

The RBAC section of Tri-State's Splunk Strategy 2.0 defines a layered
access-control model: `rl_*` Business Roles (one per user, importRoles
only) composed from single-concern `pr_*` Privilege Bundles
(`pr_data_*`, `pr_search_*`, `pr_feat_*`, `pr_workspace_*`), with a
sensitive-capability tier, a prohibition on UI edits and built-in-role
reuse, and seven standing compliance detections.

Before the production build (Strategy Roadmap Phases 3–5), Tri-State
needs machine-verified evidence that this model works as designed —
that bundle composition, permission union and quota MAX behavior,
sensitive-capability isolation, workspace app visibility, and every
compliance detection behave exactly as the strategy specifies.

This project builds that evidence: on a standalone Splunk instance on
the Linux dev VM, it generates the entire RBAC environment (indexes,
roles, bundles, test users, seeded data) from a YAML catalog and proves
its behavior with automated static and behavioral test suites. Maximum
automation is an explicit requirement. Beneficiaries: Reza Hosseiny and
the Splunk Platform team.

## What success looks like

1. `make all` on the dev VM validates the catalog, generates the app
   trees (`tristate_rbac`, `tristate_indexes`, workspace apps), deploys
   them to /opt/splunk, creates test users, seeds sample data, and both
   test suites pass.
2. The static suite (offline) proves the catalog and generated confs
   conform to the strategy's structural rules: naming, single-concern
   bundles, sensitive-capability isolation, one-role-per-user
   composition, and the SAML roleMap template.
3. The behavioral suite (live REST, per test user) proves observed
   Splunk behavior matches `catalog/expectations.yaml` — an independent
   human-written statement of what each role must and must not be able
   to do (data access, capabilities, quotas, app visibility).
4. All seven compliance detections deploy as `al_rbac_*` saved
   searches, run clean on a healthy environment, and each is proven to
   fire via violation injection, with the environment restored clean
   afterwards.
5. The placeholder catalog entries are replaced with real Tri-State
   feeds (mapping workshop over `sample_data/Splunk_Sample_data.csv`),
   and all suites re-run green against the real catalog.

## Out of scope

- Production or clustered deployment (SHC deployer, manager-apps
  paths); the standalone deviations are documented, not eliminated.
- Live SAML/LDAP integration testing — the IdP mapping is covered by
  static tests on a generated authentication.conf template only.
- Non-RBAC sections of the strategy (topology, ingestion pipeline,
  retention operations, app development standards) except where the
  RBAC model depends on them (index naming, entity naming).
- Splunk version certification beyond the dev instance (code stays
  version-agnostic, plain REST, no splunk-sdk).

## Approval

Approved by Reza Hosseiny, 2026-08-18 — blanket approval of INT-001 and ADR-001 through ADR-010, given in session by the decision authority. Recorded, not granted, by the AI participant.
