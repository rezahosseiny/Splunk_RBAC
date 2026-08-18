---
id: WRK-005
type: work
title: Phase 5 — automated test suites and reporting
status: open
created: 2026-08-18
owner: Reza Hosseiny
---

# WRK-005 — Phase 5: automated tests and reporting

Gated on WRK-004.

## Objective

Prove, automatically and repeatably, that the deployed RBAC model
behaves as the strategy specifies, and report the result in a form that
serves as both engineering signal and audit evidence.

## Static suite (offline, pre-deploy)

- catalog integrity: no loader errors
- naming: indexes match the governed schema with codes registered in the
  taxonomy and a valid retention suffix; sourcetypes and sources are
  lowercase `tag:tag:tag` within the tag limit; roles and bundles match
  their prefixes; service roles match `rl_svc_*`
- bundle single-concern rules: data bundles carry no capabilities or
  envelope; search bundles carry only search-execution capabilities plus
  envelope; feature bundles carry capabilities and no search-execution
  capabilities; workspace bundles carry nothing
- sensitive capabilities appear only in `pr_feat_admin_*` bundles that
  are flagged sensitive with a governance block
- role composition: bundles only, no built-in imports, one role per user
- expectations cross-check against catalog-computed effective sets
- generated confs round-trip to the catalog; `rl_*` stanzas contain only
  `importRoles`; the roleMap template has exactly one role per line
- sizing: warn, not fail, when bundle counts exceed the strategy targets
- mapping and manifest: every sample feed resolves to catalog entries
- coverage: every ADR-006 behavior has at least one test (fails if not)

## Behavioral suite (live REST, per test user)

Driven exclusively by `catalog/expectations.yaml`; skips cleanly with a
clear message when credentials are absent.

- data access: per user, permitted indexes return their seeded counts and
  denied indexes return zero events; `index=*` returns only permitted
  indexes
- capabilities: `current-context` capability set equals expectations
  exactly (full set equality, not subset)
- roles: each user's role list is exactly their one `rl_*` role
- quotas: effective quota attributes match expectations, including the
  MAX-across-bundles cases
- app visibility: expected apps visible, hidden apps absent
- detections: each of the seven runs clean on the healthy environment;
  then, per detection, inject the corresponding violation, assert it
  fires, and revert under `try`/`finally` so the environment ends clean

## Reporting

`make test` writes `reports/junit-static.xml`,
`reports/junit-behavioral.xml`, `reports/test_summary.md` (pass/fail by
suite, a per-role behavioral results table, and detection
injection outcomes), and `reports/coverage_matrix.md`.

## Acceptance criteria

1. `make test` passes on the deployed environment.
2. Every one of the seven detections is proven to fire on injection, and
   the environment verifies clean afterwards.
3. No coverage-matrix row lacks a test.
4. `make rebuild` from a clean instance ends with a full passing run,
   demonstrating reproducibility.
5. The reports are self-explanatory to a reader who has not seen the
   repository.

## Evidence (on completion)

`reports/test_summary.md`, both JUnit files,
`reports/coverage_matrix.md`, and a clean-instance `make rebuild`
transcript.
