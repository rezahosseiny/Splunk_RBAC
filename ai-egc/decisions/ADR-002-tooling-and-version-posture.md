---
id: ADR-002
type: decision
title: Tooling — Python 3 + pytest + requests + PyYAML, plain REST, version-agnostic
status: accepted
created: 2026-08-18
owner: Reza Hosseiny
supersedes: null
superseded_by: null
---

# ADR-002 — Tooling and version posture

## Context

The harness needs catalog parsing, conf generation, REST-driven
deployment/verification, and an assertion framework. The dev VM runs
Splunk Enterprise 10.4.1 at /opt/splunk (confirmed 2026-08-18); the
production version may differ.

## Options considered

1. splunk-sdk (Python SDK) for all Splunk interaction.
2. Plain `requests` against the Splunk REST API.
3. Shell + Splunk CLI only.

## Decision

Python 3 + pytest + requests + PyYAML. Plain REST calls via a thin
wrapper (`deploy/splunk_api.py`); no splunk-sdk dependency. Splunk CLI
(`splunk add oneshot`) is permitted where REST is awkward (one-shot
data seeding). Code is kept version-agnostic across Splunk 9.x/10.x:
no version-specific endpoints or response-shape assumptions.

## Rationale

splunk-sdk adds a dependency whose version coupling works against the
version-agnostic requirement; the REST endpoints used here
(authorization, authentication, apps, search jobs) are stable across
releases. pytest gives fixtures, parametrization, and skip semantics
that map naturally onto per-role/per-user test matrices.

## Consequences

- One small wrapper to maintain (session login, GET/POST, JSON mode).
- Behavioral tests must skip cleanly, with a clear message, when
  credentials/config are absent (so static tests always run anywhere).

## Approval

Approved by Reza Hosseiny, 2026-08-18 — blanket approval of INT-001 and ADR-001 through ADR-010, given in session by the decision authority. Recorded, not granted, by the AI participant.
