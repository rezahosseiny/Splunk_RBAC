---
id: WRK-005
type: work
title: Phase 5 — automated test suites and reporting
status: completed
created: 2026-08-18
owner: Reza Hosseiny
---

# WRK-005 — Phase 5: automated tests and reporting

WRK-004 complete. Both suites written, passing, and reporting.

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

## Complete — 2026-08-18

**37 tests, all passing. 31 behaviours proven. All 7 detections proven to fire.**

| Suite | Tests | Result |
|---|---:|---|
| Static (offline) | 16 | pass |
| Behavioural (live, per test user) | 21 | pass |

`make rebuild` from a clean instance ends green, which demonstrates
reproducibility rather than asserting it: teardown, deploy, users, seed, and both
suites, in one command.

## Every detection is proven to fire

Each of the seven is quiet on a healthy environment AND reports its violation
when one is injected, with the environment verified clean afterwards. That second
half is the point: a detection that cannot fire looks exactly like one with
nothing to find.

The injections: a second Business Role on a user; a bundle assigned directly to a
user; a sensitive capability added to a routine bundle; a destructive capability
on a role outside the allow-list; a role stanza created in a foreign app, which
is what a Splunk Web edit produces; a new holder added to a sensitive role chain;
and for the capability-catalog change, the detection run against a baseline with
one capability removed, which is what an upgrade looks like to that search.

## Reporting

`make test` writes `reports/junit-static.xml`, `reports/junit-behavioral.xml`,
and `reports/test_summary.md`. The summary lists each behaviour and whether it
was proven, each detection and whether it fired, and the platform limits that
bound the result — so a reader knows what the pass actually covers. It is the
work-item evidence, produced by the pipeline rather than assembled by hand.

## Four test defects found and fixed

Each would have produced a false result rather than an obvious failure.

1. **An all-time search made a constrained role look empty.** `rl_svc_siem_ingest`
   has a 24-hour `srchTimeWin`, and Splunk refuses a search spanning longer than
   that, so the role appeared to reach none of its six indexes. The test now
   derives its window from the role's own limit. Read carelessly, the original
   failure looked like a data-access defect.
2. **The injection mechanism did not apply.** Writing a capability through the
   generic conf endpoint is accepted but not reflected by the roles endpoint until
   a reload, so two injections appeared to fail and the detections looked broken.
   Injections now use the roles object endpoint, which applies immediately.
3. **The coverage-completeness check depended on what pytest collected**, so it
   failed whenever the static suite ran alone. It now reads the test source, which
   is valid under any selection. A check that fails for the wrong reason trains
   everyone to ignore it.
4. **The redaction audit checked format rather than reachability.** It flagged the
   test-user addresses in `catalog/users.yaml`, which are already at the reserved
   `example.invalid` domain and cannot reach anyone. It now treats any address at
   that domain as safe, which is the property that matters.

## One product finding (ADR-014 Finding E)

`rl_platform_admin` sees all four workspace apps rather than the one its bundle
grants, because `admin_all_objects` bypasses object ACLs and app visibility is an
ACL. Flagged as a risk in ADR-013, now confirmed. Recorded in the expectations as
`additional_visible_apps` with a required reason, rather than by widening
`visible_apps` — a reader comparing this role with the others would otherwise
conclude the boundary holds for everyone.

## Acceptance criteria

1. `make test` passes on the deployed environment. — **met**, 37 of 37.
2. Every detection proven to fire on injection, environment clean afterwards. —
   **met**, all seven.
3. No coverage-matrix row lacks a test. — **met**, and the check now also fails
   if the matrix names a test that does not exist.
4. `make rebuild` from a clean instance ends green. — **met**.
5. The reports are self-explanatory to a reader who has not seen the repository.
   — **met**: `reports/test_summary.md` names each behaviour, each detection, and
   the platform limits bounding the result.

## Evidence

`reports/test_summary.md`, `reports/junit-static.xml`,
`reports/junit-behavioral.xml`, `reports/coverage_matrix.md`.
