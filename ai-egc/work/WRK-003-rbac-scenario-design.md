---
id: WRK-003
type: work
title: Phase 3 — decide RBAC scenarios covering every aspect of the model
status: open
created: 2026-08-18
owner: Reza Hosseiny
---

# WRK-003 — Phase 3: RBAC scenario design

Gated on WRK-002. This is a decision phase (authority: Reza).

## Objective

Decide the Privilege Bundle and Business Role catalog such that every
behavior the strategy asserts about the RBAC model is observable, per
the coverage matrix in ADR-006.

## Scope of decision

- `pr_data_*` bundles over the governed index taxonomy, including at
  least one pair with deliberately overlapping index sets (to observe
  union) and a class/compliance boundary that at least one role is
  denied (to observe sensitivity walls).
- `pr_search_*` runtime envelopes, including two with differing quota
  values composable into one role (to observe quota MAX), and the
  `pr_search_constrained` default for service accounts.
- `pr_feat_*` activity bundles, with all sensitive capabilities isolated
  in `pr_feat_admin_*` bundles carrying governance blocks.
- `pr_workspace_*` bundles and the app set each grants.
- `rl_*` Business Roles, including differential pairs (differing in
  exactly one bundle per category), one `rl_svc_*` service account role,
  and one platform admin role.
- Test users, one per role.
- `catalog/expectations.yaml` — written independently of the bundle
  definitions: for each role, the indexes it must and must not reach,
  its exact capability set, its quotas, and its visible and hidden apps.

## Acceptance criteria

1. `catalog/coverage_matrix.yaml` enumerates every ADR-006 behavior,
   each mapped to the roles that make it observable.
2. Bundle counts sit within the strategy's sizing targets, or each
   overage is justified against the necessity, reuse, and composition
   tests.
3. Sensitive capabilities appear only in `pr_feat_admin_*` bundles;
   every role chain including one is flagged sensitive with governance
   metadata.
4. Every role is bundles-only; no built-in role is imported; every user
   holds exactly one role.
5. `catalog/expectations.yaml` is complete for every role and was
   authored without deriving values from the bundle definitions.
6. `make validate` passes, including the expectations cross-check
   (disagreements resolved as conscious decisions, not silent edits).

## Evidence (on completion)

`catalog/bundles.yaml`, `roles.yaml`, `users.yaml`,
`expectations.yaml`, `coverage_matrix.yaml`, and
`reports/coverage_matrix.md`.
