---
id: ADR-009
type: decision
title: Email addresses are redacted from every value taken out of a production export
status: accepted
created: 2026-08-18
owner: Reza Hosseiny
supersedes: null
superseded_by: null
---

# ADR-009 — Email redaction rule

## Context

Applying the mapping surfaced real employee email addresses in the
`source` field of the Oracle feed (ADR-008 Findings). The first
sanitization pass caught them only in the remediation document, and only
because of a manual check. Two problems with that:

- The larger exposure is not the document but the **seeded data**.
  Ingesting the export loads whatever it contains into the dev Splunk
  instance, including addresses in `_raw` from the identity, O365, and
  Azure AD feeds. That is a copy of personal data on a dev VM.
- Enforcement by review discipline fails eventually. It already nearly
  did.

Reza directed that a rule exist to replace any email address with a
made-up address or a fixed redaction value.

## Options considered

1. Redact in each tool as needed.
2. One declarative rule set in the catalog, one shared implementation
   used by every tool, and a guard that refuses to emit output in which
   a redaction target survived.

## Decision

Option 2.

- `catalog/redaction.yaml` holds the rule — the single place the policy
  is stated, per ADR-007.
- `tools/redact.py` implements it. No tool implements its own redaction;
  the profiler, the mapping resolver, and the data seeder all use it.
- Two modes. **`pseudonym`** (the default) replaces each address with a
  stable made-up address at the RFC 2606 reserved domain
  `example.invalid` — for example
  `user_48eccef0@example.invalid`. **`sentinel`** replaces every address
  with one fixed value, `redacted@email.com`.
- Enforcement is a guard, not a habit: generated output is audited
  before it is written, and writing is refused if any address survived.
  Verified end to end — a poisoned input produces a refusal and no file.

Redaction applies to every value taken from an export: documents,
reports, terminal summaries, and the events seeded into Splunk.

## Rationale

**Pseudonym over a single sentinel, as the default.** A sentinel
collapses every user to one identity, so any search grouping by user
sees a single value and the seeded data stops behaving like real data. A
pseudonym keeps cardinality and correlation — the same real address
always yields the same fake one, so a user appearing across the O365,
Azure AD, and Oracle feeds still correlates.

**Deterministic rather than genuinely random.** Random replacement would
make every `make rebuild` produce different data, breaking the
reproducibility contract in ADR-007 and making test expectations
unstable. "Random made-up address" is therefore implemented as
"deterministic, and unrelated to the original".

**A reserved domain.** `email.com` is a real registered domain, so
`redacted@email.com` is a deliverable address belonging to a third
party. `example.invalid` cannot resolve or receive mail. The requested
value is retained as the `sentinel` setting because it was asked for by
name, with the concern recorded in the file; changing the domain is a
one-line edit.

**Case-insensitive.** `Mark.Dreyer@…` and `mark.dreyer@…` are the same
person and map to the same pseudonym.

## Consequences

- Pseudonyms are de-identified, not cryptographically unlinkable: the
  salt is committed so pseudonyms stay stable across machines, which
  means the mapping is reversible by anyone holding both the salt and a
  candidate roster. Adequate for a dev harness; move the salt to
  `config/.env` if unlinkability is required.
- `docs/source_remediation_map.md` is a committed deliverable and is
  audited for addresses, hostnames, and GUIDs.
  `reports/mapping_worksheet.md` is the diagnostic view, is audited for
  addresses only — hostnames stay legible there for diagnosis — and
  remains gitignored.
- WRK-002 gains an acceptance criterion: the seeder applies redaction to
  event content before ingestion, and a behavioral check confirms no
  real address is searchable in Splunk afterwards.
- The rule currently covers email addresses. Other personal data in
  event content (usernames, phone numbers, IP-to-person mappings) is not
  redacted, and the strategy's own Privacy & Data Minimization section
  suggests reviewing whether it should be. Raised, not decided.

## Approval

Approved by Reza Hosseiny, 2026-08-18 — blanket approval of INT-001 and ADR-001 through ADR-010, given in session by the decision authority. Recorded, not granted, by the AI participant.
