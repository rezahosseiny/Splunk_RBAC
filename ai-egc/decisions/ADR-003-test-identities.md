---
id: ADR-003
type: decision
title: Test identities — local users, one per Business Role; SAML covered statically
status: accepted
created: 2026-08-18
owner: Reza Hosseiny
supersedes: null
superseded_by: null
---

# ADR-003 — Test identities

## Context

Behavioral tests must exercise Splunk *as each user population*.
Production uses SAML with `GRP_splunk_<rl_*>` IdP groups mapped 1:1 to
Business Roles; the dev VM has no IdP.

## Options considered

1. Stand up an LDAP container and test the roleMap live.
2. Local Splunk test users, one per `rl_*` role; cover the IdP mapping
   with static tests on a generated authentication.conf template.

## Decision

Option 2. `catalog/users.yaml` defines one local test user per `rl_*`
role, each holding exactly that one role. `deploy/create_users.py`
deletes and recreates them at deploy time with random passwords written
to `config/test_user_credentials.json` (gitignored). Admin credentials
come from `config/.env` (gitignored; `.env.example` committed). The
generator renders `authentication.conf.template` with exactly one
`GRP_splunk_<role> = <role>` line per Business Role; static tests
assert its shape. An LDAP container is deferred as an optional later
addition.

## Rationale

Local users test the thing that matters here — Splunk-side RBAC
enforcement per role — without dragging an IdP into the dev loop. The
roleMap convention is a text contract, checkable statically.

## Consequences

- The one-role-per-user invariant is asserted both statically
  (users.yaml) and behaviorally (live roles list per user).
- Live SAML behavior (group changes, multi-group users) is untested
  until an IdP-backed environment exists; documented as a known gap.

## Approval

Approved by Reza Hosseiny, 2026-08-18 — blanket approval of INT-001 and ADR-001 through ADR-010, given in session by the decision authority. Recorded, not granted, by the AI participant.
