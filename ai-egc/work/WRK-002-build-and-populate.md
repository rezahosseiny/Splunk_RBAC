---
id: WRK-002
type: work
title: Phase 2 — build governed indexes in Splunk and populate sample data
status: completed
created: 2026-08-18
owner: Reza Hosseiny
---

# WRK-002 — Phase 2: build and populate

WRK-001 approved 2026-08-18; this phase is now active.

## Objective

Create the governed indexes on the dev instance and load the sample
export into them, entirely by script and repeatably.

## Work

- `generators/loader.py` — catalog loading, referential integrity, the
  naming regexes, and the effective-permission helpers (capabilities,
  index patterns, allowed indexes, quota MAX, workspace apps).
- `generators/build.py` — render `tristate_indexes`: `indexes.conf`
  from the catalog and retention tiers (`frozenTimePeriodInSecs` =
  total days × 86400; paths under `$SPLUNK_DB`; single-tier deviation
  commented) and `props.conf` per sourcetype (TZ, TIME_FORMAT where
  known, `SHOULD_LINEMERGE=false`).
- `deploy/splunk_api.py` — thin REST wrapper (session login, GET/POST,
  JSON output mode, TLS verification from settings).
- `deploy/deploy.sh` — idempotent app sync, removal of apps no longer
  generated, refresh or restart.
- `deploy/seed_data.py` — split any export by target governed
  index/sourcetype using `catalog/mapping.yaml`, rewrite source per the
  Phase 1 source policy, apply `tools/redact.py` to event content before
  ingestion (ADR-009), ingest, then verify landed counts by admin search.
  No per-feed logic.
- `deploy/teardown.sh` — remove generated apps, test users, and
  catalog-defined indexes.
- Makefile targets per ADR-007.

## Acceptance criteria

1. `make build && make deploy` creates every governed index on the dev
   instance, with retention matching the catalog.
2. `make seed` lands the export into the governed indexes; verified
   event counts per index match the export's counts, and re-running it
   does not duplicate events.
3. Splunk reports no conf errors after deploy; `_internal` shows no
   index-related warnings for the generated app.
4. **No real email address is searchable anywhere in Splunk after
   seeding** (ADR-009). Verified by searching the seeded indexes for the
   production mail domain over all time and asserting zero events; the
   seeder itself refuses to ingest content in which an address survived.
5. `make teardown && make rebuild` returns to a passing populated state
   from a clean instance, and reproduces byte-identical pseudonyms.

## Evidence (on completion)

`reports/seed_verification.md` (per-index expected vs landed counts),
deploy log, and the generated `build/apps/tristate_indexes` tree.

## Progress — 2026-08-18

**Written and working offline:**

- `generators/loader.py` — catalog loading, the naming regexes, mapping
  resolution, retention computation, and validation. Every tool imports it, so
  the rules exist once. `make validate` clean: 35 indexes, 33 legacy feeds,
  3 fixtures, 25 units.
- `generators/build.py` — renders `tristate_indexes` (indexes.conf, props.conf,
  app.conf, local.meta). Version is stamped from a catalog content hash, so it
  changes on every catalog change without anyone remembering to bump it.
  Output: 35 indexes, 112 sourcetypes.
- `generators/make_fixtures.py` — deterministic synthetic events for the three
  coverage fixtures (500 events). No clock and no RNG, so a rebuild reproduces
  them byte-identically.
- `deploy/splunk_api.py` — REST wrapper, plain requests, version-agnostic.
- `deploy/seed_data.py` — resolves, redacts, groups, and streams. Verified
  offline: 31,108 export events plus 500 fixture events resolve into 156
  destinations with redaction clean, then it stops with an actionable message
  about missing credentials.
- `deploy/deploy_rest.py`, `deploy/deploy.sh`, `deploy/teardown.py`,
  `deploy/teardown.sh` — both deployment paths and the catalog-scoped teardown.
- `Makefile`, `requirements.txt`, `config/settings.yaml`, `config/.env.example`.

`make offline` runs validate, fixtures, profile, build, and the redaction
verification end to end and passes.

**Blocked on two inputs only Reza can supply (ADR-011):**

1. Splunk admin credentials in `config/.env`. Needed by deploy, seed, and
   verification. `make connect` confirms them.
2. Nothing else, if the default REST deployment path is used. If the filesystem
   sync path is preferred instead, write access to `/opt/splunk/etc/apps` — the
   directory is owned by `splunk:splunk` and `sudo` needs a password.

Acceptance criteria 1 through 5 are all instance-side and cannot be evidenced
until credentials exist. Everything up to the instance boundary is done.

## Deferred note on timestamp hints

102 of the 112 governed sourcetypes have no recorded TZ or TIME_FORMAT and rely
on Splunk auto-detection. `build.py` lists them on every run rather than
silently defaulting. Auto-detection is adequate for a test harness, but each one
is a real props.conf decision for production onboarding, and the list is the
work item for that.

## Completion — 2026-08-18

All acceptance criteria met against the live instance (Splunk 10.4.1,
localhost.localdomain).

| Criterion | Result |
|---|---|
| Every governed index exists with catalog retention | 35 of 35 present |
| Seeded counts match the export | 31,608 expected, 31,608 landed, **zero mismatches across all 35 indexes** |
| Re-seeding does not duplicate | verified: a second `make seed` is a no-op on an unchanged fingerprint |
| No real identifier searchable in Splunk | mail domain, tenant ID, domain SID, and known employee names all return 0 hits; `example.invalid` pseudonyms present, proving redaction ran rather than data being absent |
| Clean-instance rebuild returns to a passing state | demonstrated: teardown removed 34 indexes and their data, deploy recreated all 35, seed matched exactly |

Evidence: `reports/seed_verification.md`, `reports/resolved_inventory.json`,
`build/apps/tristate_indexes/`.

## Five defects found and fixed while proving it

None of these would have surfaced without insisting the counts match exactly.
Each is the kind of failure that passes a smoke test and corrupts every
behavioural assertion downstream.

1. **Stanzas created disabled.** The generic `configs/conf-<file>` endpoint
   creates a new stanza disabled unless told otherwise. All 35 indexes existed
   and silently accepted nothing — Splunk logged `INDEXER_MISSING_INDEX` per
   event and dropped 31,608 of them. Deployment now writes every stanza
   explicitly enabled.
2. **Index creation is not hot-reloadable.** splunkd logged "reload is not safe
   since a path has been changed" and the new indexes stayed inert. Deployment
   now restarts splunkd through the management API.
3. **The restart wait was a false positive.** The old process keeps answering for
   several seconds after a restart is accepted, so polling for "up" immediately
   succeeded against the process that was about to die, and deployment reported
   a restart that had not happened. It now waits for the port to go down first,
   then to come back.
4. **Line merging inflated counts.** `SHOULD_LINEMERGE=false` on every
   sourcetype means one event per line, so multi-line Windows XML and
   ActiveDirectory events arrived as many events each — `res_non_sec_iam_ad_m`
   showed 792 where 20 were expected. Seeding now flattens each event to one
   line.
5. **Undated events merged into their predecessor.** Some exported events have
   an empty leading timestamp and begin `, search_name=...`; the time is in the
   export's `_time` column but not in `_raw`. Splunk cannot date such a line and
   merges it into the previous event, so 20 arrived as 1. Seeding now prefixes
   the event's own `_time` when the text does not already start with one.

Two smaller corrections: teardown must delete an index in its **owning app's
namespace** (Splunk rejects a cross-app delete), and must never touch an index
Splunk itself provides — `summary` ships with Splunk and is owned by the system
context, so the catalog now marks it `provided_by: splunk` and neither defines
nor deletes it.

## Carried into Phase 3

- 102 of 112 governed sourcetypes have no recorded TZ or TIME_FORMAT and rely on
  auto-detection. `build.py` lists them every run. Adequate here; each is a real
  props.conf decision for production onboarding.
- Flattening multi-line events is a harness decision, not a production one.
  Production needs a per-sourcetype LINE_BREAKER, which needs onboarding
  knowledge of each feed.
