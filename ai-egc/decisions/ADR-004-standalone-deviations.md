---
id: ADR-004
type: decision
title: Documented deviations for the standalone dev instance
status: accepted
created: 2026-08-18
owner: Reza Hosseiny
supersedes: null
superseded_by: null
---

# ADR-004 — Documented deviations for the standalone dev instance

## Context

The strategy's authoritative paths assume a clustered production
topology: `etc/shcluster/apps/` distributed by the SHC deployer, and
index apps under `etc/manager-apps/` via the cluster manager. The test
environment is a single standalone instance at /opt/splunk. The
strategy also assumes tiered storage (hot/warm on NVMe, cold on
capacity storage); the VM has one disk tier.

## Options considered

1. Simulate the cluster (multiple instances/containers) to use the
   production paths verbatim.
2. Deploy everything to `etc/apps/` on the standalone instance and
   document each deviation explicitly.

## Decision

Option 2. All generated apps deploy to `$SPLUNK_HOME/etc/apps/`.
Retention renders as `frozenTimePeriodInSecs` (total days × 86400) with
a comment noting that the hot/cold split is not represented on a
single-tier VM. The README carries a deviations table mapping each
production path/behavior to its standalone substitute.

## Rationale

The subject under test is the RBAC model — role composition, index
authorization, capabilities, quotas, detections — none of which changes
between `etc/apps/` and `etc/shcluster/apps/`. Cluster simulation adds
operational surface without adding assurance for the questions asked.

## Consequences

- Distribution mechanics (deployer push, cluster-manager bundle
  validation) remain untested until a clustered test environment
  exists; documented as a known gap.
- The generated app content is production-shaped; only the deploy
  destination differs.

## Approval

Approved by Reza Hosseiny, 2026-08-18 — blanket approval of INT-001 and ADR-001 through ADR-010, given in session by the decision authority. Recorded, not granted, by the AI participant.
