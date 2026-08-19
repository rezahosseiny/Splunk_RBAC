---
id: ADR-015
type: decision
title: Test-account credentials are shown in the generated report
status: accepted
created: 2026-08-19
owner: Reza Hosseiny
supersedes: null
superseded_by: null
---

# ADR-015 — Credentials in the generated report

## Context

The configuration and test report is required to carry a table of test users with
their roles and their passwords, so a reader can reproduce any result in it
without a second lookup.

That sits against the project's own data-handling discipline. Everything else
built here treats credentials as something to keep out of a document:
`config/.env` and `config/test_user_credentials.json` are gitignored, the
redaction rules exist to stop identifiers reaching a generated file, and the
verification refuses to write a document in which one survived.

## Options considered

1. Show the passwords.
2. Mask them and point to the credentials file.
3. Omit the table.

## Decision

**Show them, with three conditions.**

- The report is written to `reports/`, which is gitignored, so it is not
  committed and does not reach the remote.
- The credential table carries a notice stating that this is a test system, that
  the accounts exist only on the development instance, and that they are
  regenerated on every `make users` run — so a value recorded elsewhere stops
  working.
- `make report-shareable` produces an identical report with the credentials
  masked, for circulation. Verified: zero passwords appear in that copy.

Reza's condition, recorded verbatim in intent: **if this harness is ever promoted
to a production role, the passwords are masked or omitted.**

## Rationale

The accounts protect nothing. They exist on one development instance, hold only
synthetic and redacted data, and are destroyed and recreated by a single command.
Against that, a reader verifying an access claim in the report would otherwise
have to open a second file to do it.

The masked variant is what keeps this from being a one-way decision: the report
can be circulated without the concession, and the moment the accounts guard
anything real, `report-shareable` becomes the only variant produced.

## Consequences

- `reports/rbac_report.md` must not be committed, copied into `docs/`, or attached
  to anything leaving Tri-State. The proprietary notice in its header says so.
- The report becomes stale as a credential source the moment `make users` runs
  again. It states this where the table appears.
- If the harness is promoted, this record is superseded rather than edited, and
  the default flips to masked.

## Approval

Approved by Reza Hosseiny, 2026-08-19, with the production condition recorded
above.
