---
id: ADR-006
type: decision
title: RBAC scenarios are derived from an explicit test-coverage matrix
status: accepted
created: 2026-08-18
owner: Reza Hosseiny
supersedes: null
superseded_by: null
---

# ADR-006 — RBAC scenarios derived from a test-coverage matrix

## Context

The project's purpose is to prove *every aspect* of the RBAC model
works. A role catalog designed only to mirror Tri-State's org chart
will not do that: if no two roles differ in exactly one bundle, a
generator bug that mis-composes bundles is invisible; if no two roles
have overlapping index sets, Splunk's union semantics are never
exercised; if all roles share a runtime envelope, the quota MAX rule is
never observed.

## Options considered

1. Design roles to mirror the expected production population, and test
   whatever that happens to cover.
2. Design roles from a coverage matrix: enumerate every model behavior
   the strategy asserts, then define the minimum role set that makes
   each behavior observable — biased toward realistic populations where
   the matrix leaves a free choice.

## Decision

Option 2. The bundle and role catalog is designed to make each of the
following observable, and every row must be traceable to at least one
behavioral test:

**Composition semantics**
- Differential pairs: role pairs differing in exactly one bundle, one
  pair per bundle category (`pr_data_*`, `pr_search_*`, `pr_feat_*`,
  `pr_workspace_*`), proving each category's effect is independent.
- Union of index access: two data bundles with overlapping index sets
  in one role, proving union rather than replacement or conflict.
- Union of capabilities across multiple `pr_feat_*` bundles.
- MAX of quotas: two search-related bundles with differing quota values
  in one role, proving Splunk takes the maximum, not the last or least.
- Bundle reuse: at least one bundle imported by two or more roles (also
  the strategy's own reuse test).

**Boundary enforcement**
- Sensitivity wall: a role permitted Class 3 data and denied Class 4/5,
  proving class separation.
- Compliance isolation: a role denied a regulated index it is otherwise
  domain-eligible for.
- Silent denial: `index=*` as a constrained user returns only permitted
  indexes; a denied index named explicitly returns zero events.
- Sensitive capability tier: sensitive capabilities present in exactly
  one `pr_feat_admin_*` chain and absent from every routine role.
- Built-in role isolation: no `pr_*`/`rl_*` imports admin, power, user,
  or can_delete; built-in roles unmodified.
- One role per user: every test user resolves to exactly one `rl_*`.
- Empty workspace stanza: `pr_workspace_*` grants no index, capability,
  or quota; app visibility comes only from app metadata.
- Service account discipline: an `rl_svc_*` role on the constrained
  search envelope.

**Detection efficacy**
- Each of the seven standing detections runs clean on a healthy
  environment and fires on an injected violation, with the environment
  restored afterwards.

Coverage is recorded in `catalog/coverage_matrix.yaml`, mapping each
behavior to the roles and tests that exercise it. A static test fails
the build if any row has no test, so coverage cannot silently regress.

## Rationale

This inverts the usual order — tests are normally written against a
design — because the deliverable here is assurance, not a role catalog.
Designing the role set so that each asserted behavior has an observable
consequence is what makes "we tested the model" a defensible claim. The
cost is a handful of roles that exist for coverage rather than for a
real population; they are marked as such.

## Consequences

- The role catalog is somewhat larger than the production population
  would require; coverage-only roles are labelled and excluded from any
  production-intent export.
- The matrix is a maintained artifact: a new strategy assertion means a
  new matrix row, which means a new test.
- Bundle counts stay within the strategy's sizing targets, or the
  overage is justified against the necessity, reuse, and composition
  tests; a static test warns when a target is exceeded.

## Approval

Approved by Reza Hosseiny, 2026-08-18 — blanket approval of INT-001 and ADR-001 through ADR-010, given in session by the decision authority. Recorded, not granted, by the AI participant.
