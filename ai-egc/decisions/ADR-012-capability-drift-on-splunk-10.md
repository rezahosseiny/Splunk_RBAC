---
id: ADR-012
type: decision
title: Capability names in the strategy do not all exist on Splunk 10.4.1
status: accepted
created: 2026-08-18
owner: Reza Hosseiny
supersedes: null
superseded_by: null
---

# ADR-012 — Capability drift on Splunk 10.4.1

## Context

The strategy's Sensitive capability tier names eleven capabilities. Before
writing the bundles, the capability catalog was captured from the instance
(`tools/capability_inventory.py`, 216 capabilities on Splunk 10.4.1).

Three of the eleven names do not exist on that release:

| Strategy name | Status on 10.4.1 |
|---|---|
| `edit_indexes` | Does not exist. The capability is named `indexes_edit`. |
| `edit_indexes_allinternal` | Does not exist. `indexes_edit` covers it. |
| `clean_indexes` | Does not exist, and has no equivalent. |

A bundle written from the strategy text verbatim would therefore fail to
deploy — Splunk rejects an unknown capability rather than ignoring it.

This is the drift the strategy's own upgrade triage process exists to catch. It
was caught before the first bundle was written, rather than at deployment,
because the baseline was taken first.

## Options considered

1. Keep the strategy's names and let Phase 4 fail, then correct.
2. Correct the names in the catalog, and record the correction.
3. Correct the names silently.

## Decision

Option 2. `catalog/taxonomy.yaml` now names only capabilities verified to exist
on the target release. `edit_indexes` becomes `indexes_edit`. The two names with
no equivalent move to a new `sensitive_capabilities_absent_on_target` block, so
their absence is a recorded fact rather than a silent omission.

Four capabilities are also added to the sensitive tier, each marked
`addition: true`: `edit_storage_passwords`, `edit_user_seed`,
`edit_upload_and_index`, and `run_mcollect`. Each grants credential
modification or arbitrary index writes, which is what the strategy's own
definition of the tier describes.

`schedule_rtsearch` is added to `search_execution_capabilities`. The strategy
names three; this one governs whether a real-time search may be scheduled,
which is how a search runs and therefore that category's concern. It is recorded
as an addition, and the validator rejected `pr_search_advanced` until it was
registered — which is how the question surfaced.

`make capability-baseline` captures the catalog, diffs it against the previous
dated baseline, and verifies that every capability the catalog grants exists.
A static test does the same check offline.

## Rationale

Silent correction would leave the strategy and the implementation disagreeing,
with no record of which is right. Recording it makes the next reader's question
answerable: the implementation is correct for 10.4.1, and the strategy text
needs an amendment.

Keeping the absent names in a separate block matters more than it appears.
`clean_indexes` has no equivalent, so the control the strategy intended — the
ability to gate index data removal by capability — is not available on this
release. Deleting the name would hide that; recording it makes the gap
reviewable.

## Consequences

- **A finding for Strategy 2.1.** The Sensitive capability tier list needs
  correcting. Capability names must be verified against a target release, not
  quoted from memory.
- The strategy's `clean_indexes` control cannot be enforced by capability on
  10.4.1. Index data removal happens through the REST API or the CLI, which
  `indexes_edit` and `delete_by_keyword` gate instead.
- The catalog is now release-specific in one respect. An upgrade requires
  `make capability-baseline` and a review of the diff, which is what the
  strategy's triage process already requires.
- Every capability name in the catalog is verified: 27 distinct capabilities
  across 29 bundles, all present on the instance.

## Approval

Approved by Reza Hosseiny, 2026-08-18. ADR-013 records the five review decisions taken the same day.
