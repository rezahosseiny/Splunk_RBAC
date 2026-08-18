---
id: ADR-007
type: decision
title: Reproducibility and automation contract
status: accepted
created: 2026-08-18
owner: Reza Hosseiny
supersedes: null
superseded_by: null
---

# ADR-007 — Reproducibility and automation contract

## Context

Two standing requirements from the decision authority: the environment
must be reproducible — new sample data must be importable, and changed
schema or RBAC decisions must be re-implementable by script rather than
by hand — and the work must run with minimal interruption and
reasonable token cost.

Both are architectural, not procedural: they are satisfied by where
decisions are stored and how the pipeline is invoked, not by discipline.

## Options considered

1. Scripts that do the work, with decisions embedded in the scripts.
2. Declarative decision files consumed by idempotent scripts, with a
   single rebuild entry point.

## Decision

Option 2, with the following contract.

**Every decision lives in exactly one declarative file.** Changing a
decision means editing that file and re-running; it never means editing
a script, a conf, or Splunk itself.

| Decision | File |
|---|---|
| Legacy → governed index/sourcetype/source mapping | `catalog/mapping.yaml` |
| Codes, retention tiers, sensitive capabilities, sizing targets | `catalog/taxonomy.yaml` |
| Governed index register: description and ownership | `catalog/indexes.yaml` |
| Business units that can hold ownership | `catalog/business_units.yaml` |
| Redaction rules applied to every export value | `catalog/redaction.yaml` |
| Bundle and role catalog | `catalog/bundles.yaml`, `catalog/roles.yaml` |
| Test users | `catalog/users.yaml` |
| Independent per-role expectations | `catalog/expectations.yaml` |
| Behaviors that must be covered | `catalog/coverage_matrix.yaml` |

**Generated output is disposable.** `build/` and `reports/` are
regenerated, never hand-edited, and are not authoritative for anything.
Splunk-side state (apps, indexes, users) is likewise reproducible from
the catalog; drift is a defect, not a state to preserve.

**Idempotent entry points.** Each is safe to re-run at any time:

| Command | Effect |
|---|---|
| `make profile` | re-profile sample exports into the mapping worksheet |
| `make validate` | catalog integrity and referential checks, offline |
| `make build` | render `build/apps/` from the catalog |
| `make deploy` | sync apps to the instance, remove apps no longer generated, refresh |
| `make users` | recreate test users and credentials |
| `make seed` | (re-)ingest sample data into governed indexes |
| `make test` | static + behavioral suites with reports |
| `make rebuild` | teardown, then the whole chain end to end |
| `make teardown` | remove generated apps, test users, and test indexes |

**New sample data** is a drop-in: add the export to `sample_data/`,
`make profile` to see what it contains and what it violates, extend
`catalog/mapping.yaml` for anything new, then `make reseed`. Seeding is
keyed on the mapping, so it never contains per-feed logic.

**Changed schema or RBAC decisions** are `make rebuild`. Because
expectations are independent (ADR-001), a changed role forces a
conscious expectations edit; the cross-check test fails otherwise.

**Interruption and token economy.**

- Bulk data work is done by deterministic scripts that emit compact
  summaries and write detail to `reports/`; large inputs are never read
  into conversation context. (The 34,801-line export was profiled into a
  35-line summary.)
- Decisions are batched into one approval gate per phase — five gates
  for the whole roadmap — each presented as a prepared proposal to amend
  rather than a set of open questions.
- Test results are files (JUnit XML plus a markdown summary), reviewed
  by exception: failures and coverage gaps are surfaced, passes are
  counted.
- Execution phases run to completion without check-ins; work stops only
  at a gate, on a genuine ambiguity, or on a destructive action.

**Reporting.** `make test` writes `reports/junit-*.xml`,
`reports/test_summary.md` (pass/fail by suite, per-role behavioral
results, detection injection outcomes), and
`reports/coverage_matrix.md` (each asserted behavior and the tests
covering it). These reports are the completion evidence required for
work items, so evidence is produced by the pipeline rather than
assembled by hand.

> Amended 2026-08-18: `sourcetypes.yaml` and `sources.yaml` were dropped —
> sourcetype and source values are decided in `mapping.yaml`, and restating them
> would store one decision twice. `owners.yaml` was folded into
> `indexes.yaml`, which now holds the two fields an index name cannot encode:
> its description and its owners.

## Rationale

Storing each decision in exactly one declarative file is what makes
"change our minds cheaply" true rather than aspirational, and an
idempotent rebuild is what makes reproducibility verifiable — if
`make rebuild` from a clean instance produces a passing environment,
reproducibility is demonstrated rather than asserted. Tying reports to
work-item evidence removes the usual duplicated effort between proving
something works and recording that it works.

## Consequences

- Any per-feed special case that cannot be expressed in `mapping.yaml`
  is a contract violation and must be fixed by extending the mapping
  schema, not by branching in a script.
- `make rebuild` is destructive to the test environment by design; it is
  scoped to generated apps, test users, and catalog-defined indexes, and
  it never touches Splunk internal indexes or built-in roles.
- Reproducibility from a clean instance is itself an acceptance
  criterion, exercised at least once before project close.

## Approval

Approved by Reza Hosseiny, 2026-08-18 — blanket approval of INT-001 and ADR-001 through ADR-010, given in session by the decision authority. Recorded, not granted, by the AI participant.
