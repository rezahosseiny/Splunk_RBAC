---
id: ADR-008
type: decision
title: Phase 1 input decisions — coverage, sources, ES indexes, ambiguous feeds
status: accepted
created: 2026-08-18
owner: Reza Hosseiny
supersedes: null
superseded_by: null
---

# ADR-008 — Phase 1 input decisions

## Context

Profiling `sample_data/Splunk_Sample_data.csv` raised four questions
that had to be settled before the governed schema could be proposed.
Each was put to the decision authority with options and a
recommendation on 2026-08-18.

## Decisions

**D1 — Coverage fixtures: add them.** The export covers Classes 2, 3,
and 5 and effectively only the `non` compliance driver, with no Class 4
(`ctl`/OT/ICS) and no Class 1 data. Synthetic coverage fixtures are
added for the missing cells so the model's sensitivity walls and
compliance isolation are testable. The RBAC model is indifferent to
event content, so synthetic events prove the boundary as well as real
ones; fixtures are built so a real OT export can later replace them
through the same mapping with no rework.

**D2 — Source policy: rewrite to governed values, plus quarantine
coverage, plus a durable mapping document.** Sources are rewritten to
governed `tag:tag:tag` values on ingest, and a deliberately
non-compliant subset is routed to `ops_non_inf_bad_s` so the strategy's
Quarantine Protocol and access to quarantined data are both exercised.

Reza added a standing requirement: the legacy→governed mapping is to be
kept as a document, refreshed on every production sample import,
because remediating the real estate against the strategy is planned
follow-on work. The mapping document is therefore a project deliverable
in its own right, not a byproduct. It collapses ephemeral portions of
legacy values into patterns — which is both what remediation needs (the
pattern is what gets fixed, not the individual value) and what keeps
per-run identifiers such as the Azure tenant ID out of the document.

**D3 — Enterprise Security internal indexes: govern, exempt from
naming.** `notable`, `risk`, `threat_activity`, `cim_modactions`,
`endpoint_summary`, `gia_summary`, and `summary` keep their existing
names under a recorded `naming_exception: vendor_mandated` flag with
justification and owner, because ES resolves these names internally in
correlation searches, data models, and macros. They are otherwise fully
governed: class, compliance driver, owners, membership in data bundles,
and coverage in expectations. RBAC access to them is tested; the naming
rule is skipped with a recorded reason.

**D4 — Ambiguous feeds: proceed on best judgment; synthetic data
acceptable.** Reza directed that the index, source, and sourcetype
values for ambiguous feeds be proposed on best judgment rather than
deferred for owner confirmation, and that synthetic data may stand in
where real data is unclear or absent. Applied as follows:

- `ers` is ES Entity Risk Score machinery (`search_name="Risk - EWA
  Entity Risk Score Calculation"`, ESCU detections,
  `ers_execution_id`) and `dlx_kpi` is detection coverage/health KPIs
  (`coverage`, `confidence`, `performance`, `detection_id`). Both are
  ES-internal summary feeds and take the D3 treatment.
- `oracle` splits: Oracle Cloud Infrastructure audit and logging to an
  operational-class index, and Oracle identity/MFA events to the
  Class 5 identity index. Keeping them together would put Class 5
  identity data in a Class 3 index, which the strategy's segregation
  rule prohibits.
- The 117 `oracle` sourcetypes collapse to a small stable set. The
  sprawl is caused by the sourcetype being assigned from the API
  operation name (105 distinct `com.oraclecloud.*` values) and from MFA
  factor names (`TOTP`, `SMS`, `PHONE_CALL`), which breaches the
  standard's stability requirement.
- Four truncated sourcetype values (`com.orac`, `com.or`,
  `com.oracle`, `com.oraclecl`, 26 events) plus two unidentified ones
  (`work`, `recovery`, 13 events) are routed to the quarantine index.
  The truncation is a genuine upstream parsing defect and is recorded
  in the remediation document.

## Findings for Tri-State, surfaced while applying D2

These are production defects the mapping exposed. None blocks this
project; all belong in the remediation programme.

- **Employee email addresses are being written into the `source` field
  of the Oracle feed.** Roughly 15 distinct named individuals appear as
  source values. This breaches the source standard three times over —
  the value is per-event rather than stable, it identifies a person
  rather than a feed, and it puts personal data into metadata that is
  visible to anyone who can search the index at all, regardless of
  event-level controls. It also cuts against the strategy's own
  Privacy & Data Minimization section. Fixing it is an input-layer
  change: source should be the stable feed identifier
  (`api:oracle:idcs:audit`), with the acting user kept in an event
  field where field-level controls apply.
- **Hostnames are embedded in `osnix` source paths** (186 patterns of
  the form `/data/logs/<fqdn>/<logfile>.log`). Host belongs in the
  `host` field, not in `source`.
- **Corrupted source values exist**, for example
  `/data/logs/{host}/#000#000#000@#002#003.log` — control characters in
  a file path, indicating a broken input stanza.
- **Truncated sourcetype values** in the Oracle feed (`com.or`,
  `com.orac`, `com.oracle`, `com.oraclecl`), consistent with a
  field-extraction or transform writing a clipped value.

Because of the first finding, `tools/resolve_mapping.py` refuses to
write the remediation document if any email address, fully-qualified
hostname, or GUID survives pattern collapsing. Sanitization of a
committed deliverable is enforced by the tool rather than left to
review discipline. The verbatim profile
(`reports/mapping_worksheet.md`) keeps raw values for diagnosis and
stays gitignored.

## Consequences

- A finding for the strategy, not this project: Strategy 2.0 has no
  exception class for vendor-mandated index names. The same gap applies
  to `_audit`, `_internal`, and ITSI indexes. Candidate for 2.1.
- A second finding: the `_l` retention tier is inconsistent in
  Strategy 2.0 — § Retention Suffix says 3 years total, while the
  retention table says 90 days hot plus 3 years cold plus 3 years
  frozen archive, described as 7 years total. The catalog encodes
  searchable retention (hot plus cold) as `frozenTimePeriodInSecs` and
  records the archive period separately, with the discrepancy flagged
  as an open question rather than silently resolved.
- Because PCI is represented by a real feed (`thales_hsm`, best-guess
  classification), the synthetic fixtures reduce to Class 4 OT
  (regulated and non-regulated) and Class 1 public.

## Approval

Approved by Reza Hosseiny, 2026-08-18 — blanket approval of INT-001 and ADR-001 through ADR-010, given in session by the decision authority. Recorded, not granted, by the AI participant.
