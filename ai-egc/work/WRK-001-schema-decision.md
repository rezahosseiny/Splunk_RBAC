---
id: WRK-001
type: work
title: Phase 1 — decide governed index, sourcetype, and source schema
status: completed
created: 2026-08-18
owner: Reza Hosseiny
---

# WRK-001 — Phase 1: schema decision

The four input decisions were taken on 2026-08-18 and are recorded in
ADR-008. A complete best-judgment mapping proposal now exists and is
verified against the sample export; it awaits Reza's review.

## Objective

Decide the governed index, sourcetype, and source values for the
Tri-State estate represented by `sample_data/Splunk_Sample_data.csv`,
and the legacy→governed mapping that makes the decision executable.

## Scope of decision

- Governed index name per legacy index, per the strategy schema
  `[class]_[compliance]_[domain]_[content]_[optional_detail]_[retention]`.
- New three-letter `content` codes to be registered in the taxonomy
  (the strategy makes `content`, `domain`, and `compliance` definable by
  the Data Governance Council).
- Governed sourcetype per legacy sourcetype, in `tag:tag:tag` form.
- Source policy: rewrite to governed values on ingest, or preserve
  legacy values (ADR-005 recommends rewrite).
- Legacy indexes requiring split (one legacy index → several governed
  indexes) or merge.
- Disposition of Enterprise Security internal indexes (`notable`,
  `risk`, `summary`, `cim_modactions`, `endpoint_summary`,
  `gia_summary`, `threat_activity`) and of unidentified feeds
  (`ers`, `dlx_kpi`).
- Coverage fixtures for the empty cells of the class × compliance
  matrix — at minimum a Class 4 `ctl_cip_ics_*` OT feed and one
  regulated index — without which the model's sensitivity walls and
  compliance isolation cannot be tested (ADR-005).

## Acceptance criteria

1. `catalog/mapping.yaml` covers every legacy index and sourcetype in
   the export, with no unresolved flags. — **met**, 0 gaps over 31,108
   events.
2. `catalog/taxonomy.yaml` registers every code in use, and every index
   carries a class, compliance driver, retention tier, description, and
   named owners. — **met**; ownership recommendations in
   `catalog/indexes.yaml`, drawn from `catalog/business_units.yaml`.
3. Every governed index name, sourcetype, and source passes the
   strategy naming rules; the quarantine index `ops_non_inf_bad_s`
   exists. — **met**, validation clean.
4. The class × compliance matrix has no empty cell that a planned RBAC
   scenario needs. — **met**: all five classes and three compliance
   drivers (`non`, `cip`, `pci`) are represented.
5. Reza has reviewed the proposed classifications. — **met**,
   approved 2026-08-18.
6. `make validate` passes. — deferred to WRK-002, which introduces the
   Makefile; the equivalent checks pass today via
   `python -m tools.resolve_mapping` (zero gaps, clean naming) and
   `python -m tools.verify_redaction` (clean).

## Derivation note

`indexes.yaml`, `sourcetypes.yaml`, and `sources.yaml` were originally
planned as separate catalog files. They are instead **derived** from
`mapping.yaml` plus `taxonomy.yaml`, because hand-maintaining them
alongside the mapping would store the same decision twice and breach
ADR-007's one-decision-one-file rule. Only ownership cannot be derived,
so `catalog/owners.yaml` exists for that alone. This refines ADR-007's
decision-file table.

## Evidence (on completion)

`catalog/mapping.yaml`, `catalog/taxonomy.yaml`, `catalog/owners.yaml`,
`docs/source_remediation_map.md`, `reports/mapping_worksheet.md`, and
the `tools/resolve_mapping.py` run showing zero mapping gaps and clean
naming validation.
