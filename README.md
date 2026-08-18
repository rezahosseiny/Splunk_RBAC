# Splunk RBAC Test Harness

| Field | Value |
|---|---|
| **Document** | README |
| **Location in Repo** | `README.md` |
| **Author** | Reza Hosseiny |
| **Status** | Approved |
| **Last Updated** | 2026-08-18 |
| **Covers** | What this repository is, where each document is, and the quickest route to a working environment. |

This repository proves that the Role-Based Access Control model in Tri-State's
Splunk Strategy 2.0 works, before Tri-State builds it in production.

A YAML catalog holds every decision. Generators render the Splunk apps from that
catalog. Deploy scripts push the apps to a Splunk instance and load sample data.
Two test suites then compare the live behaviour against the strategy.

The normative specification is `strategy/Splunk_Strategy_2.0.md`, section
**Role-Based Access Control**.

## Quick start

```bash
pip install -r requirements.txt
cp config/.env.example config/.env     # then set the Splunk credentials
make offline                           # validate, generate, build, check redaction
make connect                           # confirm the credentials
make deploy                            # create the indexes; Splunk restarts
make seed                              # load the sample data
```

Run `make help` for every command.

## Documents

| Document | Purpose |
|---|---|
| [`docs/DESIGN.md`](docs/DESIGN.md) | The architecture, the design rules, and the reason for each |
| [`docs/USER_GUIDE.md`](docs/USER_GUIDE.md) | How to operate, change, and troubleshoot the harness |
| [`ai-egc/ROADMAP.md`](ai-egc/ROADMAP.md) | The five phases and the current position |
| [`ai-egc/START_HERE.md`](ai-egc/START_HERE.md) | The governance framework and the reading order |
| [`docs/source_remediation_map.md`](docs/source_remediation_map.md) | Each legacy value and the governed value that replaces it |

## Layout

| Path | Content |
|---|---|
| `catalog/` | Every decision. The only source of truth. |
| `generators/` | Catalog loader and the app generators |
| `deploy/` | Deployment, seeding, and teardown |
| `tools/` | Profiling, mapping resolution, and redaction |
| `strategy/` | The strategy documents |
| `ai-egc/` | Governance records: intent, decisions, work items, roadmap |
| `docs/` | Design, user guide, and the remediation deliverable |
| `build/`, `reports/` | Generated output. Never edit. Not committed. |

## Governance

This project follows the AI-EGC Framework. Start at
[`ai-egc/START_HERE.md`](ai-egc/START_HERE.md). Decision authority is Reza
Hosseiny. Every decision is recorded in `ai-egc/decisions/` with its reason and
its consequences.
