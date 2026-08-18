# Handoff — current

**Framework:** AI-EGC Framework<br>
**Author:** Reza Hosseiny<br>
**Version:** 0.3.1

> Overwritten at each material session close; history lives in Git.

## Where things stand

Lifecycle is **build**. **WRK-001 (Phase 1) is complete and approved.**
**WRK-002 (Phase 2 — build and populate) is the active phase.**

Reza gave blanket approval of INT-001 and ADR-001 through ADR-010 in session on
2026-08-18, and directed that the project move to Phase 2. All ten decision
records are `accepted`; INT-001 is `approved`. The approvals are recorded, not
granted, by the AI participant — the authority boundary in START_HERE stands.

The roadmap now has its own record: [`ROADMAP.md`](../ROADMAP.md), added to the
reading order in START_HERE. It carries all five phases, which are decision
gates versus execution runs, what each phase ends with, and what lies beyond
the roadmap.

The repository was committed and pushed for the first time on 2026-08-18.

**Roadmap (Reza, 2026-08-18, ADR-005):** five phases — schema decision,
build and populate, RBAC scenario design, RBAC implementation,
automated tests and reporting. WRK-001..005 map one-to-one. Phases 1
and 3 are decision gates; 2, 4, and 5 run to completion without
check-ins.

**Decisions taken this session (ADR-008), all four via session Q&A:**

- D1 add synthetic coverage fixtures for the empty class cells
- D2 rewrite sources to governed values, plus quarantine coverage, plus
  a durable accumulating mapping document (Reza's standing requirement —
  remediating the real estate is planned follow-on work)
- D3 govern ES-internal indexes but exempt their names
  (`naming_exception: vendor_mandated`)
- D4 proceed on best judgment for ambiguous feeds; synthetic data
  acceptable

## Phase 1 result — verified, awaiting review

`catalog/mapping.yaml` maps all 31,108 events with **zero gaps** into
**29 governed indexes** (20 governed-name, 9 vendor-name-exempt),
naming validation clean. Coverage spans all five classes and three
compliance drivers:

| class | compliance | indexes |
|---|---|---|
| pub | non | pub_non_app_wea_s (fixture) |
| ent | non | ent_non_app_col_o365_m, ent_non_app_itm_m |
| ops | non | ndl, lin, win, vmw, dns, stg, ocl, bad (8) |
| ctl | cip | ctl_cip_ics_scd_s (fixture) |
| ctl | non | ctl_non_ics_hst_m (fixture) |
| res | non | iam, fwl, edr, nac, dlp, win (6) |
| res | pci | res_pci_sec_hsm_l (thales_hsm, best guess) |

Notable consolidations and splits: arista + aruba + cisco + f5 collapse
into `ops_non_inf_ndl_m`; `oracle` splits into OCI infrastructure and
Class 5 identity with 117 sourcetypes collapsing to 4; `nps_server`
splits host monitoring from RADIUS identity; `o365` splits Defender
incidents into the EDR index; 39 events quarantined.

## Code written this session

- `tools/profile_sample_data.py` — facts-only profiler, re-runnable
  against any export; writes `reports/mapping_worksheet.md`.
- `tools/resolve_mapping.py` — applies the mapping, reports unmapped
  values as gaps, validates every governed name, and writes
  `docs/source_remediation_map.md` (695 patterns, the D2 deliverable).
  Verified that it catches malformed sources: temporarily reverting one
  slug template produced 3 naming problems, restoring it cleaned them.
  Ephemeral fragments collapse to `{guid}`/`{timestamp}`/`{digits}`, so
  the Azure tenant ID does not appear anywhere in the document —
  confirmed by grep.
- `catalog/taxonomy.yaml`, `catalog/mapping.yaml`, `catalog/owners.yaml`,
  `catalog/business_units.yaml`, `catalog/redaction.yaml`.
- `tools/redact.py` and `tools/verify_redaction.py` — the redaction rule and
  its two-layer verification.

## Ownership model

`catalog/business_units.yaml` registers Reza's 25 business units with a code,
group, and scope. `catalog/owners.yaml` assigns each index a business owner
(accountable for data quality, business need, and access approvals) and a
technical owner (owns the originating system). The split is deliberate: it puts
access decisions with the unit that understands the need and correctness
decisions with the unit that runs the system — so Windows security logs are
owned by Sec Cyber but technically owned by IT Infrastructure.

15 of the 25 units own an index today. The 10 that do not — Physical Security,
Telecom Engineering, Telecom Maintenance, IT Field Services, Facilities,
Finance & Accounting, Human Resources, Safety, Legal, Technology Office — have
no data in this export. That is itself a finding: Physical Security in
particular looks like a real gap, since access-control events (Protege GX)
were seen arriving inside the Windows/Snare feed rather than in an index of
their own.

## Mid-flight

Nothing partially done. WRK-001 needs Reza's review and the owner
fields; no generator, deploy, or test code exists yet.

## Next session should

Collect from Reza, then run WRK-002 straight through:

1. Review `catalog/mapping.yaml`. The classifications most worth
   challenging: `thales_hsm` as `pci` (it carries the only real
   compliance-isolation test), the `o365` and `oracle` splits, whether
   `azure`/`o365` Defender data belongs with EDR, and whether
   consolidating four network vendors into one index is the access
   boundary he wants.
2. Review `catalog/indexes.yaml` — the governed index register: 30 indexes,
   each with a description and a recommended business and technical owner from
   the 25 units in `catalog/business_units.yaml`, flagged 23 high / 6 medium /
   1 low. Review the 7 non-high ones, confirm the rest in passing.
3. Register — or reject — the 12 proposed three-letter content codes in
   `taxonomy.yaml` (stg, vmw, ocl, iam, edr, nac, dlp, hsm, col, itm,
   hst, wea); these need Data Governance Council registration.
4. Settle the `_l` retention inconsistency flagged in `taxonomy.yaml`
   (Strategy 2.0 says both 3 years and 7 years total).
5. Pin the framework source in `manifest.yaml`.

Then WRK-002: loader, generator, deploy, and seeding. Splunk admin
credentials in `config/.env` are needed before Phase 4, not Phase 2.

## Production defects found (see ADR-008 Findings)

Worth Reza's attention independently of this project:

1. **Employee email addresses are in the `source` field of the Oracle
   feed** — ~15 named individuals. Personal data in metadata visible to
   anyone who can search the index, and a triple breach of the source
   standard.

   Reza's response (ADR-009): a project-wide redaction rule, not a
   per-tool fix. `catalog/redaction.yaml` states the policy,
   `tools/redact.py` implements it, and every tool that reads an export
   uses it — including the seeder, which is the larger exposure, since
   ingesting the export would otherwise copy real addresses into the dev
   instance. Default mode replaces each address with a stable pseudonym
   at the reserved domain `example.invalid`
   (`user_48eccef0@example.invalid`), preserving cardinality and
   correlation; a `sentinel` mode using `redacted@email.com` is
   available. Enforcement is a guard: generated output is audited and
   writing is refused if an address survived — verified end to end.

   Reza then directed the rule be extended (ADR-010). It now covers
   twelve identifier classes found by scanning the 63 MB of event
   content: addresses, IPv4 and IPv6, Windows domain SIDs (17,329
   occurrences), internal hostnames (568 distinct), MAC addresses,
   domain-qualified accounts, phone numbers, person names, and accounts.
   `tools/verify_redaction.py` reports clean over 27 generated files and
   all 31,108 events, with all 26,467 JSON events still valid and output
   byte-identical across runs.

   **The load-bearing lesson:** the pattern-based audit reported "clean"
   while four real leaks were present, because it used the same patterns
   as the redaction it was checking. An independent substring search for
   known-real values found them. Verification therefore has two layers,
   and the literal layer is the one that catches pattern gaps. A hit
   there is a redaction defect to fix in the rules, never a reason to
   extend the literal list.
2. Hostnames embedded in `osnix` source paths (186 patterns), and
   hostnames in `_raw` across 568 distinct assets.
3. A corrupted source path containing control characters.
4. Truncated sourcetype values in the Oracle feed.
5. Account name and domain arrive in separate fields
   (`accountName` beside `domainName`), so neither is an address — worth
   knowing when writing CIM field mappings.

Two findings for Strategy 2.1, outside this project's scope: the
missing exception class for vendor-mandated index names, and the `_l`
retention contradiction.




## Review against the parallel catalog in raw_files/catalog

A catalog built independently by another AI sits in `raw_files/catalog`
(mapping, indexes, sourcetypes, sources, taxonomy, bundles, roles, users,
expectations). Reviewed 2026-08-18. Two changes were adopted, one problem in it
must not be copied, and its RBAC layer is a useful head start for WRK-003.

**Adopted from it — all five changes applied 2026-08-18**

1. `linux_secure` now maps to a new Class 5 index `res_non_sec_lin_l` instead of
   `ops_non_inf_lin_m`. Their catalog made this split and mine did not, which was
   inconsistent with the oswin/oswinsec split I had already applied — Linux
   authentication data is security data. A real defect in my mapping.
2. `catalog/indexes.yaml` replaces `owners.yaml`, in their list format: one
   entry per index carrying the description the strategy's Data Catalog
   mandates, the decoded name fields, both owners, and the contributing
   production feeds. The decoded fields are redundant with the name by design —
   the register reads on its own, and a static test asserts they agree with the
   name and taxonomy so a disagreement fails the build.
3. Volume-aware retention: ESXi moves to `ops_non_inf_vmw_s` and Windows host
   monitoring splits out to `ops_non_inf_whm_s`, both high-volume and low
   forensic value. Forescout NAC moves to `_m` — Class 5 does not imply long
   hold, only regulated data and audit trails do.
4. Identity granularity: the merged `res_non_sec_iam_l` splits per provider —
   `iam_aad_l`, `iam_ad_m`, `iam_okt_l`, `iam_oci_l`, `iam_nps_l` — so a role
   can be scoped to one IdP or granted all with `res_non_sec_iam_*`.
5. `raw_files/catalog/` is now gitignored, since their mapping.yaml carries the
   Azure tenant ID, an internal hostname, and the mail domain.

Storage and network stay merged: SAN and NAS, and the four network vendors,
have identical access requirements, and the strategy only calls for separate
indexes where access controls or retention differ.

Index count is now 35 (23 governed-name, 9 vendor-name-exempt, 3 fixtures),
still zero mapping gaps and clean naming validation.

**Do not copy: their expectations.yaml is generated.** Its header says
"GENERATED from the mapping proposal" while its own comment claims to be an
"INDEPENDENT statement". A generated expectations file cannot detect a generator
bug — it self-certifies, which is exactly what ADR-001 exists to prevent.
Expectations must be authored by hand, against the strategy and the business
need, never emitted from the same catalog the generator reads.

**Also worth knowing**

- Their `mapping.yaml` contains the Azure tenant ID (7 occurrences), an internal
  hostname, and the mail domain. `raw_files/` is not gitignored, so committing it
  as-is would put those in git history.
- Their catalog has no `ctl_*` and no `pub_*` index, so OT isolation, NERC CIP
  scoping, and the public tier are untestable in it (what ADR-008 D1 fixes).
- Their role catalog has no clean differential pairs, and no role composes two
  search bundles, so Splunk's quota-MAX rule is never exercised — the gap
  ADR-006 exists to close.
- Their wildcard data bundle `pr_data_ops_inf` (`ops_non_inf_*`) sweeps in the
  quarantine index, granting NOC operators data that failed onboarding and may
  contain misrouted sensitive content. Worth avoiding in WRK-003.
