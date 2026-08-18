---
id: ADR-011
type: decision
title: Deployment path when the app directory is not writable
status: proposed
created: 2026-08-18
owner: Reza Hosseiny
supersedes: null
superseded_by: null
---

# ADR-011 — Deployment path under restricted filesystem access

## Context

Phase 2 needs to place the generated index app on the dev instance. The
strategy's deployment path — and the one ADR-004 adapted for a standalone
instance — is a filesystem sync into the app directory.

On this VM that path is closed. `/opt/splunk` and `/opt/splunk/etc/apps` are
owned by `splunk:splunk` and mode 755; the working account `reza` cannot write
there, and `sudo` requires a password that an automated run cannot supply. The
management API on port 8089 answers but returns 401, because no credentials
exist yet.

So Phase 2's build and resolution steps run today, and everything that touches
the instance is blocked on access that only the decision authority can grant.

## Options considered

1. **Grant filesystem access** — add `reza` to the `splunk` group, or set an ACL
   on the app directory. Keeps the strategy's deployment path exactly.
2. **Run the deploy step manually** as the splunk user, with automation stopping
   at that boundary.
3. **Deploy through the management API**, letting splunkd write the configuration
   into the app's own local directory. Needs credentials only.

## Decision

Support 1 and 3, and select between them in `config/settings.yaml`
(`deployment.method: rsync | rest`). Default to `rest` on this VM, because it
needs only the credentials that Phase 2 already requires for seeding and
verification, and therefore unblocks the phase without an elevation request.

- `deploy/deploy.sh` is the rsync path: `rsync --delete` per app, so the
  deployed app matches `build/apps` exactly and a stanza dropped from the
  catalog disappears from the instance. It detects the unwritable directory and
  prints both remedies rather than failing obscurely.
- `deploy/deploy_rest.py` is the API path: it parses the generated `.conf`
  files and upserts each stanza into
  `/servicesNS/nobody/<app>/configs/conf-<file>`, creating the app first if
  absent. Idempotent, with `--dry-run` and `--prune` for stanzas the catalog no
  longer generates.

Both consume the same generated output. Neither is a UI edit, and neither writes
to `etc/system/local` — the path the strategy prohibits and whose drift the
configuration-drift detection watches for. The catalog remains the source of
truth in both cases.

## Rationale

The strategy prohibits UI-driven configuration because those changes land in
`etc/system/local`, are per-member, and are outside version control. An API
write into a named app's `local` directory has none of those properties: it is
generated from the catalog, reproducible, and lands where the deployment app
expects. Treating "REST" as equivalent to "UI edit" would confuse the mechanism
with the property the rule protects.

Preferring the API path by default is a judgement about where the friction
should sit: requesting a permission change on a Splunk host is a slower and more
consequential act than supplying credentials the project needs anyway.

## Consequences

- **Phase 2 is blocked on two inputs from Reza**, both of which he alone can
  provide: Splunk admin credentials in `config/.env`, and — only if the rsync
  path is preferred — write access to `/opt/splunk/etc/apps`.
- **Confirmed in practice: a restart is required, not merely possible.**
  splunkd refuses to hot-reload after an index is added ("reload is not safe
  since a path has been changed") and the new index accepts nothing until it
  restarts. `deploy_rest.py --restart` therefore restarts through the management
  API, and `make deploy` always passes it. The restart takes roughly 45 seconds
  on this VM, so deployment is not a fast inner loop.
- Stanzas written through the generic conf endpoint are created **disabled** by
  default; deployment forces them enabled. Without that, every index exists and
  silently drops everything sent to it.
- The API path exercises less of the production deployment mechanism than a
  filesystem sync does. Neither exercises the search head cluster deployer or
  cluster manager bundle validation, which ADR-004 already records as untested
  on a standalone instance.
- `deploy/teardown.py` uses the same API and is scoped by the catalog: it
  removes only the apps this project generates, the indexes the catalog defines,
  and the users the catalog declares, never a Splunk internal index or a
  built-in role.

## Approval

Pending — Reza Hosseiny
