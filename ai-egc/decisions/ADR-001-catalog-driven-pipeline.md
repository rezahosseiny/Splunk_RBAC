---
id: ADR-001
type: decision
title: Catalog-driven pipeline with an independent expectations layer
status: accepted
created: 2026-08-18
owner: Reza Hosseiny
supersedes: null
superseded_by: null
---

# ADR-001 — Catalog-driven pipeline with an independent expectations layer

## Context

The strategy mandates config-as-code, prohibits UI edits, and requires
versioned app deployment. The harness must prove the RBAC model works —
it must not certify its own bugs: if behavioral tests asserted values
computed from the same catalog the generator consumes, a generator bug
would pass its own test.

## Options considered

1. Hand-written Splunk confs plus hand-written tests (no generator).
2. Generator from a YAML catalog; tests derive expected values from the
   same catalog.
3. Generator from a YAML catalog; behavioral tests assert against an
   independent, human-written expectations file.

## Decision

Option 3. `catalog/*.yaml` is the single source of truth →
`generators/build.py` renders `build/apps/` (tristate_rbac,
tristate_indexes, one app per `pr_workspace_*` bundle) →
`deploy/deploy.sh` pushes to the dev instance → two test layers:

- **Static** (offline, pre-deploy): catalog integrity, naming rules,
  single-concern bundle rules, sensitive-capability isolation,
  generated-conf round-tripping.
- **Behavioral** (live REST, per test user): driven exclusively by
  `catalog/expectations.yaml`, a human-written statement of what each
  role must and must not be able to do. Never derived from
  bundles/roles at test time.

A dedicated static test cross-checks expectations against the
catalog-computed effective sets, so any disagreement surfaces as a
conscious decision rather than a silent assumption.

## Rationale

Option 1 abandons the automation requirement. Option 2 self-certifies
generator bugs. Option 3 costs a hand-maintained expectations file per
role and buys genuine assurance.

## Consequences

- `catalog/expectations.yaml` must be updated by hand for every role
  change; the cross-check test enforces that it happens.
- `build/` output is never hand-edited; regenerate from the catalog.
- Drift from `etc/system/local/` is a detectable violation, not a
  workflow.

## Approval

Approved by Reza Hosseiny, 2026-08-18 — blanket approval of INT-001 and ADR-001 through ADR-010, given in session by the decision authority. Recorded, not granted, by the AI participant.
