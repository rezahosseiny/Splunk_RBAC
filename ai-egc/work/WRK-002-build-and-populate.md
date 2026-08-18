---
id: WRK-002
type: work
title: Phase 2 — build governed indexes in Splunk and populate sample data
status: in-progress
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
