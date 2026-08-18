# Decisions

**Framework:** AI-EGC Framework<br>
**Author:** Reza Hosseiny<br>
**Version:** 0.3.1

One file per decision: `ADR-001-short-slug.md`, `ADR-002-…`. In the Lite
profile the approval is embedded in the decision record. Approved records
are never edited in substance — supersede with a new record instead.

Copy-paste template:

```markdown
---
id: ADR-001
type: decision
title: <What was decided>
status: proposed        # draft → proposed → accepted (by decision authority)
created: <YYYY-MM-DD>
owner: <OWNER>
supersedes: null
superseded_by: null
---

# ADR-001 — <Title>

## Context
## Options considered
## Decision
## Rationale
## Consequences
## Approval
<Approved by NAME, DATE — or "pending">
```
