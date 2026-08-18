---
id: ADR-014
type: decision
title: Splunk 10.4.1 enforces capability and quota floors the strategy does not anticipate
status: proposed
created: 2026-08-18
owner: Reza Hosseiny
supersedes: null
superseded_by: null
---

# ADR-014 — Platform floors on Splunk 10.4.1

## Context

Phase 4 deployed the catalog and created the fifteen test users. Reading each
user's effective permissions from `/services/authentication/current-context`
produced four results the strategy does not anticipate. All four were measured on
the instance, not inferred.

None is a fault in the catalog. All four limit what the strategy can claim.

## Finding A — a capability floor no role configuration can remove

Every one of the fifteen test users holds capabilities that no bundle grants:

| Capability | Roles that hold it without a grant | In the strategy's tiers |
|---|---:|---|
| `schedule_rtsearch` | 15 of 15 | granted to no role by decision (ADR-013) |
| `list_all_objects` | 15 of 15 | — |
| `run_mcollect` | 15 of 15 | **sensitive and destructive** |
| `run_collect` | 14 of 15 | **sensitive and destructive** |
| `edit_own_objects` | 12 of 15 | — |

All five are held by all fifteen users. The right-hand column counts the roles
whose bundles do not grant the capability, and which hold it anyway.

Measuring this needed a correction worth recording. The first attempt
intersected each user's *unexpected* capabilities and found three, not five,
because a capability a role legitimately grants does not look unexpected for that
role — `run_collect` looked accounted for on `rl_data_custodian`, which is the one
role meant to have it. Comparing each role against its own grant gives the true
figure.

Explicit revocation does not work. `run_collect = disabled` was applied first to
`pr_feat_baseline`, which every role imports, and then directly to
`rl_cov_base`, the role a user holds. Neither removed it from that user's
effective set. Splunk evaluates the chain as a union, so a denial in one role
cannot subtract a grant, and these grants do not originate in a role at all.

**Consequences for the strategy.** The Sensitive capability tier says no routine
bundle contains a sensitive capability, and that sensitive capabilities are
isolated in `pr_feat_admin_*` bundles. On Splunk 10.4.1 that is **not achievable
for `run_collect` and `run_mcollect`**. The NOC operator and the SIEM service
account can write arbitrary data into any index they can reach, and no role
configuration prevents it.

The `al_rbac_destructive_capability_check` detection will therefore report
fourteen of fifteen roles. That is the detection working correctly. Suppressing
it would hide a real exposure; the strategy is explicit that a recurring finding
is a policy gap needing a strategy revision, not an incident to suppress.

## Finding B — `srchMaxTime` is not stored

The catalog sets `srchMaxTime` on every search bundle. Splunk accepts the write
and reports the attribute as absent:

```
pr_search_constrained.srchMaxTime = None
```

The attribute is not a role attribute on this release. Setting it achieves
nothing, and a search-duration limit is not available through RBAC.

## Finding C — quota floors below which a value cannot go

| Attribute | Catalog value | Effective value | Floor |
|---|---:|---:|---:|
| `srchJobsQuota` on `pr_search_constrained` | 2 | 3 | 3 |
| `rtSrchJobsQuota` on `pr_search_advanced` | 4 | 6 | 6 |

The floor applies only to a positive value. Zero is honoured, so "no real-time
searches at all" is achievable while "at most four" is not.

The bundle's own stanza reads back the catalog value, so the write succeeded. The
**effective** value is raised to the floor. The strategy's intent for a service
account — a narrower envelope than a human analyst — cannot go below three
concurrent searches.

## Finding D — `0` and `-1` both mean "no limit"

The catalog writes `srchTimeWin: 0`, the documented value for no limit. Splunk
reports the effective value as `-1`. The two are the same intent in different
representations, so a naive comparison reports a mismatch that is not one.

## Decision

**Record the floors in the catalog as measured facts, and compare against them
explicitly.** `catalog/taxonomy.yaml` gains a `platform_floors` block holding the
capability floor, the quota floors, the unsupported attribute, and the
equivalent representations — each with the release it was measured on and the
date.

The alternative was to fold the floor silently into
`catalog/expectations.yaml`, so that every role's expected capability set simply
included the three universal capabilities. That was rejected. It would make the
tests pass while hiding the fact that two sensitive capabilities are granted to
every user, which is the single most important thing Phase 4 discovered.

The behavioural tests therefore assert:

- each role's capability set equals what the bundles grant **plus** the recorded
  platform floor, and nothing else — so a new unexplained capability still fails;
- the floor itself is unchanged from what is recorded — so a platform upgrade
  that adds to it fails loudly rather than widening access quietly;
- quotas match the catalog **or** the recorded floor where the catalog asks for
  less, and `srchTimeWin: 0` is treated as equal to `-1`.

`srchMaxTime` stays in the catalog, marked as not enforced on this release, so
the intent survives for a release that supports it.

## Consequences

- **Two sensitive capabilities cannot be isolated on Splunk 10.4.1.** Strategy
  2.1 must either drop `run_collect` and `run_mcollect` from the sensitive tier
  with that reasoning recorded, or state that the control is unenforceable on
  this release and rely on audit rather than prevention. This is Reza's decision,
  not the harness's.
- `schedule_rtsearch` cannot be withheld. The ADR-013 decision to grant it to no
  role is not implementable on this release; the decision stands as intent, and
  the floor records why it is not achieved.
- A service-account envelope cannot be narrower than three concurrent searches.
- Any RBAC control that depends on search duration must find another mechanism.
- The floors are release-specific. `make capability-baseline` and the
  behavioural suite both re-measure them, so an upgrade that changes a floor is
  a test failure rather than a surprise.

## Approval

Pending — Reza Hosseiny
