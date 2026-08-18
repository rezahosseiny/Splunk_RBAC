---
id: ADR-013
type: decision
title: Phase 3 — the bundle, role, and expectations catalog
status: accepted
created: 2026-08-18
owner: Reza Hosseiny
supersedes: null
superseded_by: null
---

# ADR-013 — The bundle, role, and expectations catalog

## Context

Phase 3 decides the RBAC catalog. ADR-006 set the constraint: the role set must
make every behaviour the strategy asserts *observable*, and not merely mirror the
expected user population.

## Decision

**29 bundles, all inside the strategy's sizing targets.**

| Category | Count | Target |
|---|---|---|
| `pr_data_*` | 12 | 8–12 |
| `pr_search_*` | 4 | 3–4 |
| `pr_feat_*` | 9 | 6–10 |
| `pr_workspace_*` | 4 | 3–6 |

**15 roles.** Nine are population roles: `rl_soc_t1`, `rl_soc_t2`,
`rl_it_engineer`, `rl_noc_operator`, `rl_ot_engineer`,
`rl_compliance_auditor`, `rl_platform_admin`, `rl_data_custodian`, and the
service account `rl_svc_siem_ingest`. Six are coverage roles, marked
`purpose: coverage` and excluded from any production-intent export.

**15 test users, one per role**, which is what makes the one-role-per-user rule
testable.

**29 behaviours in the coverage matrix**, each recording why it is observable.

Six decisions inside that deserve their reasons stated.

### 1. Index patterns wildcard the retention suffix, and only that

`pr_data_ops_infra` grants `ops_non_inf_ndl_*`, `ops_non_inf_lin_*`, and six
more. One pattern for each content code, with the trailing `_s`/`_m`/`_l`
replaced by `*`.

Two failure modes pull in opposite directions, and this granularity avoids both.

**An explicit list breaks on a retention change.** All 26 governed index stems
are currently unique, so moving one index from `_m` to `_l` would silently drop
it from every bundle that named it. The bundle would still validate, the
deployment would still succeed, and a role would quietly lose access.

**A broad wildcard over-grants.** `ops_non_inf_*` reads as "the operational
estate" but also matches `ops_non_inf_bad_s`, the quarantine index. Quarantine
holds data that failed onboarding, which by definition was not classified and may
contain misrouted sensitive content. That pattern would hand it to every NOC
operator as a side effect nobody read closely. `res_non_sec_*` behaves the same
way: it pulls all five identity indexes into a bundle meant for security
telemetry.

Wildcarding only the suffix survives a retention change and still names what it
grants. Quarantine needs its own pattern, `ops_non_inf_bad_*`, which is what
makes granting it a decision.

The parallel catalog in `raw_files/catalog` grants `ops_non_inf_*`, and its own
comment says "incl. quarantine" — so the grant was noticed and accepted rather
than missed, which is worse.

### 2. The quota test uses an asymmetric pair

`pr_search_basic` gives 5 jobs and 500 MB. `pr_search_burst` gives 20 jobs and
200 MB. `rl_cov_search` holds both, so the effective values must be **20 jobs and
500 MB** — one from each bundle.

The asymmetry is the point. If the bundles were simply "small" and "large", a
rule that took the more generous bundle wholesale would give the right answer for
the wrong reason. Here, three wrong rules give three distinguishable wrong
answers: last-wins gives 200 MB, least-wins gives 5 jobs, and
more-generous-bundle-wins cannot be stated at all.

### 3. Coverage roles share one control

`rl_cov_base` holds one bundle from each category. Each other coverage role
differs from it by **exactly one bundle**, recorded in `differs_from_base_by`,
and a validator rejects a role whose actual difference does not match what it
claims.

Without such a pair, a generator that mis-composes bundles is invisible: every
role would differ in several ways at once, and a failure could not be attributed
to a category.

The parallel catalog has no such pair. `rl_soc_t1` and `rl_soc_t2` differ in the
search bundle *and* three feature bundles, so a difference in behaviour cannot be
attributed. It also gives every role exactly one search bundle, so the quota
maximum rule is never exercised at all.

### 4. Two admin bundles, not one

`pr_feat_admin_platform` holds user and role administration.
`pr_feat_admin_data` holds index modification and data destruction. No role holds
both.

`rl_platform_admin` can change roles but cannot delete data.
`rl_data_custodian` can delete data but cannot change roles, so it cannot grant
itself anything. Neither account can reconfigure the platform and then destroy
the record of having done so.

### 5. Expectations are written from intent

`catalog/expectations.yaml` records an `intent` sentence for each role, then the
index set, capability set, quotas, and app visibility that follow from it. Each
role also names the `must_not_reach` boundaries that carry meaning, and the two
admin roles name `must_not_hold` capabilities.

The file is hand written. A static test compares it against the composition
computed from the bundles, and a disagreement is a decision rather than a silent
difference. That check was verified to work by breaking it deliberately in two
ways: a wrong quota and an omitted index were both reported.

The parallel catalog's expectations file carries the header
`GENERATED from the mapping proposal` while its own comment claims to be
independent. A generated expectations file agrees with a generator fault by
construction.

### 6. Coverage roles are marked, not disguised

Six of fifteen roles exist for observation rather than for a population. They
carry `purpose: coverage`, and the validator requires every role to be named by a
coverage-matrix row so that nothing exists without a stated reason.

## Decisions taken in review, 2026-08-18

Reza settled five open items. Each is now reflected in the catalog.

1. **Wildcard granularity: retention suffix only.** As described above.
2. **Keep all six coverage roles.** Full attribution is worth six roles and six
   test users. The strategy's own reasoning applies: new Business Roles are
   cheap, new bundles are not.
3. **Keep the two-role administrative split.** `rl_platform_admin` and
   `rl_data_custodian` stay separate. Where one person must hold both, that is an
   exception under the strategy's exception process, and the one-role-per-user
   rule makes it visible.
4. **SOC tier 2 also reaches PCI scope.** A senior analyst investigating a
   payment or cryptographic incident needs the HSM logs, and requiring an
   exception for each such incident would make the exception routine. Tier 1 and
   the service account remain denied, and they hold the same class and domain as
   tier 2, so the compliance boundary is still observable — BOUND-03 now rests on
   that pair.
5. **`schedule_rtsearch` is granted to no role.** The strategy's list of three
   search-execution capabilities stands unamended. A scheduled real-time search
   is the most expensive object a user can create, and the strategy's own content
   standards discourage real-time panels in favour of scheduled reports and
   accelerated data models. Ad-hoc real time stays available through `rtsearch`,
   bounded by `rtSrchJobsQuota`. Recorded in `taxonomy.yaml` under
   `capabilities_granted_to_no_role`, so the absence is a decision and not an
   oversight.

## Consequences

- Fifteen test users must be created and their credentials managed. Phase 4 does
  this.
- The catalog is larger than the production population needs. That is the price
  of attribution: a failure points at one category.
- `pr_data_sec_host_triage` overlaps two other data bundles deliberately. It is
  realistic — an analyst triaging a host needs both the security and the
  operational logs — but its purpose in the catalog is to make the union
  behaviour observable with overlapping sets.
- `admin_all_objects` in `pr_feat_admin_platform` bypasses knowledge-object
  ACLs. It does not expand index access, which `srchIndexesAllowed` governs, but
  the expectations for `rl_platform_admin` assert its index set explicitly so
  that a change in that behaviour would be caught.
- Phase 5 must implement every test named in the coverage matrix. A row without a
  test fails the build.

## Approval

Approved by Reza Hosseiny, 2026-08-18. ADR-013 records the five review decisions taken the same day.
