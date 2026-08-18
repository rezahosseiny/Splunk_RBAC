# Design

| Field | Value |
|---|---|
| **Document** | Design |
| **Location in Repo** | `docs/DESIGN.md` |
| **Author** | Reza Hosseiny |
| **Status** | Approved |
| **Last Updated** | 2026-08-18 |
| **Covers** | The purpose of the harness, its architecture, the design rules it obeys, and why each rule exists. |

> This document uses ASD-STE100 Simplified Technical English. Sentences are
> short. Each sentence gives one item of information. The active voice is used.

---

## 1. Purpose

The Splunk Strategy 2.0 defines a Role-Based Access Control (RBAC) model. This
project proves that the model works before Tri-State builds it in production.

The harness does three things:

1. It builds a complete test environment from a catalog. The environment has
   indexes, roles, privilege bundles, test users, and sample data.
2. It tests the environment against the strategy.
3. It reports the result as evidence.

The normative specification is `strategy/Splunk_Strategy_2.0.md`, section
**Role-Based Access Control**. If this document and the strategy disagree, the
strategy is correct.

## 2. The RBAC model in brief

The model has two layers of Splunk role.

**Business Roles (`rl_*`)** are given to users. Each user has one Business Role
and no more. A Business Role holds no permissions. It only imports Privilege
Bundles.

**Privilege Bundles (`pr_*`)** each grant one kind of access. There are four
categories:

| Category | Grants | Holds |
|---|---|---|
| `pr_data_*` | Index access | `srchIndexesAllowed`, `srchIndexesDefault`, optional `srchFilter` |
| `pr_search_*` | Search execution and runtime limits | `search`, `rtsearch`, `schedule_search`, and the quota attributes |
| `pr_feat_*` | All other capabilities | Splunk capabilities |
| `pr_workspace_*` | Access to a set of apps | Nothing. The stanza is empty. App metadata grants the access. |

A bundle in one category must not hold attributes of another category. This
rule makes the bundles composable.

Splunk calculates the permissions of a user as the **union** of all roles in the
chain. Splunk calculates the quotas as the **maximum** across the chain.

## 3. Architecture

```
  catalog/*.yaml
        │
        │  generators/loader.py            reads and validates the catalog
        ▼
  generators/build.py                      renders the Splunk apps
        │
        ▼
  build/apps/                              tristate_indexes, tristate_rbac,
        │                                  one app per workspace
        ├──────────────────────────────┐
        ▼                              ▼
  deploy/deploy.sh                deploy/deploy_rest.py
  (filesystem sync)               (management API)
        │                              │
        └──────────────┬───────────────┘
                       ▼
              Splunk dev instance
                       │
        ┌──────────────┴───────────────┐
        ▼                              ▼
  deploy/seed_data.py            tests/behavioral
  (sample data, redacted)        (live REST, one session per test user)

  tests/static                    runs offline, before any deployment
```

### 3.1 Data flow for the sample data

1. `tools/profile_sample_data.py` reports what a production export contains.
2. `tools/resolve_mapping.py` applies `catalog/mapping.yaml` to the export. It
   reports any value that no rule classifies.
3. `deploy/seed_data.py` resolves each event, applies the redaction rules, and
   sends the event to its governed index.

## 4. Design rules

Each rule below has a reason. The reason is the part that matters. A rule
without a reason becomes a habit, and a habit gets broken when it is
inconvenient.

### 4.1 The catalog is the only source of truth

Every decision is in exactly one file. To change a decision, edit that file and
run the pipeline again. Do not edit a script. Do not edit a `.conf` file. Do not
change Splunk directly.

| Decision | File |
|---|---|
| Legacy to governed mapping | `catalog/mapping.yaml` |
| Codes, retention tiers, capability tiers, sizing targets | `catalog/taxonomy.yaml` |
| Index register: description and owners | `catalog/indexes.yaml` |
| Business units that can hold ownership | `catalog/business_units.yaml` |
| Redaction rules | `catalog/redaction.yaml` |
| Bundles and roles (Phase 3) | `catalog/bundles.yaml`, `catalog/roles.yaml` |
| Test users (Phase 3) | `catalog/users.yaml` |
| Expectations (Phase 3) | `catalog/expectations.yaml` |

**Reason:** this makes a change of mind cheap. It also makes the reason for
every configuration item findable.

### 4.2 The expectations are independent

`catalog/expectations.yaml` states what each role must be able to do, and what
each role must not be able to do. A person writes this file by hand. No tool
generates it.

**Reason:** if the expectations came from the same catalog that the generator
reads, then a fault in the generator would appear in both. The tests would agree
with the fault and pass. The suite would prove nothing.

A static test compares the expectations against the values calculated from the
catalog. A disagreement is then a decision to make, not a silent difference.

> A parallel catalog in `raw_files/catalog` has an `expectations.yaml` file with
> the header `GENERATED from the mapping proposal`. Do not copy that file. Its
> own comment claims that it is independent. It is not.

### 4.3 The role catalog is designed for observation

The role set makes each asserted behaviour observable. This is the opposite of
the usual order: normally a person writes tests against a design.

The rules are in `ai-egc/decisions/ADR-006-coverage-matrix-driven-rbac.md`. The
principal ones are:

- Two roles must differ by exactly one bundle, for each of the four categories.
  This proves that each category acts independently.
- One role must hold two data bundles with index sets that overlap. This proves
  the union behaviour.
- One role must hold two bundles with different quota values. This proves the
  maximum behaviour.
- One role must be denied a regulated index that it is otherwise eligible for.
  This proves compliance isolation.

**Reason:** if no two roles differ by one bundle, a generator that composes
bundles incorrectly is invisible. If all roles share one runtime envelope, the
maximum rule is never seen.

### 4.4 Generated output is disposable

`build/` and `reports/` are always regenerated. Never edit them. They are not
authoritative for anything.

Splunk-side state is also reproducible from the catalog. A difference between
Splunk and the catalog is a fault, not a state to keep.

### 4.5 Every entry point is idempotent

Each `make` target is safe to run again at any time. Two exceptions are
deliberate:

- `make seed` refuses to run if the inputs changed since the last load.
  Seeding is not incremental. It sends every event that it resolves. To send
  again on top of existing data would double every count. Use `make reseed`
  instead. That target purges, deploys, and then seeds.
- `make teardown` and `make reseed` remove data. This is their purpose.

### 4.6 Redaction is enforced, not requested

The production export holds personal data. It holds employee mail addresses,
client IP addresses, Windows domain SIDs, internal host names, and person names.

`catalog/redaction.yaml` defines twelve rules. `tools/redact.py` applies them.
Every tool that reads an export uses that one module.

Each replacement has two properties:

- It is **deterministic**. The same input always gives the same output. A
  reload therefore reproduces the same pseudonyms. A random replacement would
  break reproducibility and make the expected values unstable.
- It is **format-preserving**. A redacted event is still valid JSON. It still
  parses. Replacements go only into address ranges that the RFCs reserve, so a
  redacted value can never point to a real host or mailbox.

Verification has two layers:

1. A **rule audit**. It applies the same patterns. It finds a failure to run the
   redaction, and a value left outside its reserved range.
2. A **forbidden-literal search**. It looks for known real values as plain text.

The second layer is the one that matters. A pattern cannot find its own blind
spot. The rule audit reported "clean" while four real leaks were present. A
literal search found all four. Details are in
`ai-egc/decisions/ADR-010-extended-redaction-rule.md`.

**A hit from the second layer is a fault in the rules. Do not add the value to
the literal list to make the report clean.**

### 4.7 Deviations from the strategy are recorded, not hidden

The test environment is one standalone instance. The strategy assumes a
clustered production platform. Each difference is recorded:

| Strategy expects | This environment does | Record |
|---|---|---|
| Apps distributed by the search head cluster deployer | Apps in `etc/apps` | ADR-004 |
| Index apps under `etc/manager-apps` | The same app under `etc/apps` | ADR-004 |
| Tiered storage for hot and cold | One storage tier | ADR-004 |
| SAML users from the corporate identity provider | Local test users, one for each role | ADR-003 |
| A filesystem sync to deploy | The management API, because the app directory belongs to the `splunk` user | ADR-011 |

## 5. Naming

An index name encodes its governance:

```
[class]_[compliance]_[domain]_[content]_[optional_detail]_[retention]
```

Each code has three letters. `catalog/taxonomy.yaml` registers every code.
`catalog/indexes.yaml` also states these fields for each index. The two must
agree, and a static check enforces this.

**Reason for the repetition:** the register is then readable without the reader
decoding a name. The check prevents the copy from drifting.

Two exceptions exist:

- **A vendor-mandated name.** Splunk Enterprise Security resolves names such as
  `notable` and `risk` inside its own correlation searches and data models. To
  rename them breaks the application. These indexes carry
  `naming_exception: vendor_mandated`. The exception excuses the index name
  only. The sourcetypes and sources are still checked.
- **An index that Splunk provides.** `summary` ships with Splunk. The catalog
  governs who can search it. The catalog must not create it, change it, or
  delete it. It carries `provided_by: splunk`.

> Strategy 2.0 defines no exception class for a vendor-mandated name. This is a
> gap. It also applies to `_audit`, `_internal`, and the ITSI indexes. It is a
> candidate for Strategy 2.1.

## 6. Ownership

Each index has two owners:

- The **business owner** is accountable for data quality, continued business
  need, and approval of access requests.
- The **technical owner** owns the system that produces the data. That owner is
  accountable for data correctness and for notice of change.

`catalog/business_units.yaml` registers the 25 units that can hold ownership.
Only a code from that file is valid in the index register.

The two roles are often held by different units. Windows security event logs are
an example. Sec Cyber is the business owner, because Sec Cyber uses the data. IT
Infrastructure is the technical owner, because IT Infrastructure operates the
hosts.

**Reason:** this puts the access decision with the unit that understands the
need. It puts the correctness decision with the unit that operates the system.

## 7. Coverage fixtures

The production sample covers data Classes 2, 3, and 5. It covers only the `non`
compliance driver. It holds no Class 4 (Control/OT) data and no Class 1 data.

Without Class 4 data, the harness cannot test OT isolation. Without a regulated
index, the harness cannot test compliance isolation. These two controls are the
principal purpose of the model.

The catalog therefore adds three synthetic fixtures:

| Index | Stands in for |
|---|---|
| `ctl_cip_ics_scd_s` | Class 4 SCADA telemetry under NERC CIP |
| `ctl_non_ics_hst_m` | Class 4 data that is not regulated, to compare with the above |
| `pub_non_app_wea_s` | Class 1 public data |

The RBAC model does not examine event content. Only the index, the sourcetype,
and the source have an effect. A synthetic event therefore proves the boundary
as well as a real event.

A real OT export can replace a fixture. Add a `legacy_indexes` entry that
targets the same index. No other change is needed.

## 8. Known limitations

| Limitation | Effect |
|---|---|
| A bare host name is replaced only if the same host also appears with its domain somewhere in the corpus. | A host that appears only in its short form is not redacted. |
| A person name in free text is replaced only if the same name was learned from a structured field. | A name that appears only in prose is not redacted. |
| Seeding flattens each event to one line. | The harness gives correct event counts. Production needs a `LINE_BREAKER` for each sourcetype instead. |
| 102 of 112 governed sourcetypes have no `TZ` or `TIME_FORMAT`. | Splunk detects the timestamp automatically. Each one is a real decision for production onboarding. `make build` lists them. |
| Neither deployment method uses the cluster deployer. | The distribution mechanism is not tested. |
| The identity provider mapping is tested only as text. | Live SAML behaviour is not tested. |

## 9. Related documents

| Document | Purpose |
|---|---|
| `docs/USER_GUIDE.md` | How to operate the harness |
| `ai-egc/ROADMAP.md` | The five phases and the current position |
| `ai-egc/decisions/` | Every decision, with its reason and its consequences |
| `docs/source_remediation_map.md` | The legacy to governed crosswalk, for the remediation programme |
| `strategy/Splunk_Strategy_2.0.md` | The normative specification |
