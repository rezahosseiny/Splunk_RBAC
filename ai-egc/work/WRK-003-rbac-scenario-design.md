---
id: WRK-003
type: work
title: Phase 3 — decide RBAC scenarios covering every aspect of the model
status: completed
created: 2026-08-18
owner: Reza Hosseiny
---

# WRK-003 — Phase 3: RBAC scenario design

WRK-002 complete. A full catalog proposal now exists and is verified against the composition. Awaiting Reza's review — this is a decision gate.

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

## Proposal delivered — 2026-08-18

`make validate` clean. `make coverage` reports every behaviour covered.
`make capability-baseline` confirms every capability name exists on the target.

| Deliverable | Result |
|---|---|
| `catalog/bundles.yaml` | 29 bundles: 12 data, 4 search, 9 feature, 4 workspace — every category inside the strategy's sizing target |
| `catalog/roles.yaml` | 15 roles: 9 population, 6 coverage |
| `catalog/users.yaml` | 15 test users, one per role |
| `catalog/coverage_matrix.yaml` | 29 behaviours, each recording why it is observable |
| `catalog/expectations.yaml` | All 15 roles, hand written from intent |

Design decisions and their reasons are in ADR-013. The four that matter most:
explicit index lists rather than wildcards, so the quarantine index cannot be
granted by accident; an asymmetric quota pair, so three wrong rules give three
distinguishable wrong answers; coverage roles sharing one control and differing
by exactly one bundle, so a failure can be attributed to a category; and two
admin bundles, so no role can both reconfigure the platform and destroy the
record.

## The cross-check works, and was proven to

The expectations were verified against the composition by breaking the check
deliberately, twice. A wrong quota produced
`expectations rl_cov_search: quota srchJobsQuota stated 5, bundles give 20`. An
omitted index produced `allowed_indexes omits ['ops_non_inf_ndl_m'] which the
bundles do grant`. Both were then restored.

That matters because a cross-check that cannot fail is indistinguishable from no
cross-check, and this one carries the whole independence argument.

## The validator caught the author

`pr_search_advanced` was rejected until `schedule_rtsearch` was registered in
the taxonomy, because the strategy names only three search-execution
capabilities. The capability belongs in that category, but placing it there was a
judgement, and the validator forced it to be recorded as one rather than slipped
in. See ADR-012.

## Acceptance criteria

1. Coverage matrix enumerates every ADR-006 behaviour, mapped to roles. — met, 29 rows.
2. Bundle counts inside the sizing targets. — met, all four categories.
3. Sensitive capabilities only in `pr_feat_admin_*`, flagged, with governance. — met, enforced by the validator.
4. Roles bundles-only, no built-in imports, one role per user. — met, enforced.
5. Expectations complete and authored without deriving from the bundles. — met for all 15 roles.
6. `make validate` passes including the cross-check. — met.
7. Reza has reviewed the catalog. — **met**, approved 2026-08-18 with
   five decisions recorded in ADR-013.

## Evidence

`reports/coverage_matrix.md`, `reports/capability_baseline.json`, and the
`make validate` output.
