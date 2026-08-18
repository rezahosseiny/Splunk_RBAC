# Roadmap

**Framework:** AI-EGC Framework<br>
**Author:** Reza Hosseiny<br>
**Version:** 0.3.1

Set by the decision authority on 2026-08-18. The reasoning behind the
sequencing is in [`decisions/ADR-005-real-data-first-sequencing.md`](decisions/ADR-005-real-data-first-sequencing.md);
each phase's objective, acceptance criteria, and required evidence are in its
work item. This file is the single view of the whole route and where we are on
it.

Current position is authoritative in [`state.yaml`](state.yaml).

## Shape

Five phases, real data first. Phases 1 and 3 are **decision gates** — they end
when the decision authority confirms the proposal. Phases 2, 4, and 5 are
**execution runs** — they proceed to completion without check-ins and end when
their evidence exists.

```
  1 Schema          2 Build &         3 RBAC            4 RBAC            5 Tests &
    decision    ->    populate    ->    scenarios   ->    implement   ->    reporting
  ────────────      ────────────      ────────────      ────────────      ────────────
  decision gate     execution         decision gate     execution         execution
  WRK-001           WRK-002           WRK-003           WRK-004           WRK-005
```

The dependency that shapes everything: Phase 3 needs Phase 1's index taxonomy
to exist, but Phase 1's index list must already satisfy Phase 3's coverage
matrix — otherwise the mapping finishes and only then reveals that the role
pairs needed to observe the model's behaviour cannot be built. See
[`decisions/ADR-006-coverage-matrix-driven-rbac.md`](decisions/ADR-006-coverage-matrix-driven-rbac.md).

## Phases

### Phase 1 — Schema decision (WRK-001) · decision gate

Decide the governed index, sourcetype, and source values for the real
Tri-State estate, and the legacy-to-governed mapping that makes the decision
executable.

**Delivered:** 35 indexes, all 31,108 sample events mapped with zero gaps,
naming validation clean. `catalog/mapping.yaml` (rule-based),
`catalog/indexes.yaml` (index register with descriptions and owners),
`catalog/business_units.yaml`, `catalog/taxonomy.yaml`,
`catalog/redaction.yaml`, and the profiling, resolution, and
redaction-verification tools. Approved 2026-08-18.

### Phase 2 — Build and populate (WRK-002) · execution

Create the governed indexes on the dev instance and load the sample export into
them, entirely by script and repeatably. Catalog loader, generator, REST
wrapper, idempotent deploy, redacting seeder, teardown, and the Makefile entry
points.

**Ends when:** every governed index exists on the instance with catalog
retention, seeded event counts match the export, re-seeding does not duplicate,
no real identifier is searchable in Splunk, and a clean-instance rebuild returns
to a passing populated state.

### Phase 3 — RBAC scenario design (WRK-003) · decision gate

Decide the Privilege Bundle and Business Role catalog such that every behaviour
the strategy asserts is observable — differential role pairs per bundle
category, overlapping index sets to observe union, differing quotas to observe
MAX, sensitive-capability isolation, a service-account role, and the
independently authored expectations file.

**Ends when:** the coverage matrix has no row without a role that makes it
observable, and the decision authority confirms the catalog.

### Phase 4 — RBAC implementation (WRK-004) · execution

Generate and deploy the full RBAC configuration as apps: `authorize.conf` for
every bundle and role, the SAML roleMap template, the seven compliance
detections, workspace apps with their metadata grants, restricted app write
access, test users, and the capability baseline.

**Ends when:** every bundle, role, user, and workspace app is live and resolves
as the catalog defines, `etc/system/local/authorize.conf` holds no project
stanzas, and built-in roles are provably unmodified.

### Phase 5 — Automated tests and reporting (WRK-005) · execution

Static suite offline against catalog and generated confs; behavioural suite
live per test user against `catalog/expectations.yaml`; all seven detections
proven to fire by violation injection with the environment restored clean.
Machine-readable and human-readable reports that double as work-item evidence.

**Ends when:** `make test` passes, every detection is proven to fire, no
coverage row lacks a test, and `make rebuild` from a clean instance ends green.

## After the roadmap

Out of scope for these five phases but on the horizon: replacing the three
synthetic coverage fixtures with real OT and public-tier exports; remediating
the production estate against the strategy using
`docs/source_remediation_map.md`; CI for the static suite; an IdP-backed
environment to cover SAML role mapping behaviourally; and a clustered test
environment to cover the distribution mechanics the standalone deviations leave
untested (ADR-004).

## Findings raised for Strategy 2.1

Neither blocks this project; both are recorded in ADR-008.

- No exception class exists for vendor-mandated index names, which Enterprise
  Security, ITSI, and the Splunk internal indexes all require.
- The `_l` retention tier is self-contradictory: the Retention Suffix section
  says 3 years total, the retention table says 7.
