---
id: ADR-005
type: decision
title: Sequencing — real-data schema first, then RBAC, then tests
status: accepted
created: 2026-08-18
owner: Reza Hosseiny
supersedes: null
superseded_by: null
---

# ADR-005 — Sequencing: real-data schema first, then RBAC, then tests

> Revision note (2026-08-18, pre-approval): this record replaces an earlier
> draft that proposed a two-track approach (placeholder catalog first,
> real-data mapping later). The decision authority directed real-data-first
> sequencing. The earlier draft was never approved, so it is revised in
> place rather than superseded.

## Context

`sample_data/Splunk_Sample_data.csv` is a real export from Tri-State's
current Splunk environment (31,108 events, 33 legacy indexes, profiled
by `tools/profile_sample_data.py`). The harness can either be built
against placeholder catalog entries drawn from the strategy's own
examples and retrofitted to real data later, or built against the real
data from the start.

## Options considered

1. **Placeholder-first.** Seed the catalog with `example: true` entries,
   prove the pipeline end to end, then replace with real feeds.
2. **Real-data-first.** Decide the governed index/source/sourcetype
   schema from the sample export, build it in Splunk, then design RBAC
   scenarios against that schema, implement, and test.

## Decision

Option 2, in five phases, each ending in a single approval gate:

1. **Schema decision.** From the sample export and the strategy naming
   standard, decide the governed index, sourcetype, and source values
   and the legacy→governed mapping. Deliverable: `catalog/mapping.yaml`
   plus the taxonomy and data catalog entries.
2. **Build and populate.** Generate and deploy the index app, then
   ingest the sample export into the governed indexes via scripted,
   idempotent seeding.
3. **RBAC scenario design.** Decide the bundle and role catalog such
   that every aspect of the model is exercised, driven by an explicit
   coverage matrix (ADR-006). Deliverable: bundles, roles, users, and
   the independent expectations file.
4. **RBAC implementation.** Generate and deploy `tristate_rbac`, the
   workspace apps, the SAML roleMap template, and the seven compliance
   detections; create test users.
5. **Automated tests and reporting.** Static and behavioral suites,
   including violation-injection proof for each detection, with
   machine-readable and human-readable reports.

Phases 1 and 3 are decision phases (authority: Reza); 2, 4, and 5 are
execution phases. Phase 1's index list must satisfy Phase 3's coverage
matrix — see Consequences.

## Rationale

Placeholder-first spends effort on a catalog that is thrown away, and
worse, it lets RBAC scenarios be designed against a data shape that
does not exist. Real-data-first means every bundle, role, and test is
designed against the estate the model will actually govern. The cost —
Phase 1 blocks everything behind classification decisions — is
mitigated by making Phase 1 a review-and-amend of a prepared proposal
rather than a blank-page workshop.

## Consequences

- **Coverage feedback into Phase 1.** A purely bottom-up mapping of the
  sample yields no Class 1 (`pub`) or Class 4 (`ctl`/OT) indexes and
  effectively only the `non` compliance driver, which leaves the
  model's sensitivity walls and compliance isolation untestable.
  Phase 1 must therefore add representative indexes for the missing
  cells of the class × compliance matrix, seeded with synthetic events
  and clearly marked as coverage fixtures. The RBAC model is indifferent
  to event content; only the index/sourcetype/source metadata matters.
- **Source renaming.** Nearly every source in the export violates the
  standard structurally (bare ports such as `udp:5012`, per-run URLs,
  absolute log paths) — these are input-layer defects, not renaming
  defects. Phase 1 must decide whether seeding rewrites sources to
  governed values (proves the target state) or preserves legacy values
  (reproduces current reality). Proposal: rewrite, and retain the
  profiler's violation report as the production remediation backlog.
- **Missing host column.** The export omits `host`, so the strategy's
  host standard cannot be profiled or tested. A re-export including
  `host` is requested; not a blocker.
- Acceptance requires that no placeholder entries remain in the catalog.
- Data handling: the export contains real internal hostnames and an
  Azure tenant ID. `sample_data/*.csv` and `reports/` are gitignored;
  neither is committed or pushed without an explicit decision.

## Approval

Approved by Reza Hosseiny, 2026-08-18 — blanket approval of INT-001 and ADR-001 through ADR-010, given in session by the decision authority. Recorded, not granted, by the AI participant.
