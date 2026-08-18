# Start Here

**Framework:** AI-EGC Framework<br>
**Author:** Reza Hosseiny<br>
**Version:** 0.3.1

## Project

**Splunk RBAC Test Harness** — an automated build-and-test environment that
proves the RBAC model defined in Tri-State's Splunk Strategy 2.0 (see
`strategy/Splunk_Strategy_2.0.md`, § Role-Based Access Control) on a
standalone dev Splunk instance, before it is trusted in production.

## Framework

AI-EGC Framework (see `manifest.yaml` for the pinned versions and
portable source contract). Framework behavior comes from that resolved
framework source, not copied tools or schemas in this project. The project
repository remains authoritative for project records; AI participants are
bounded and replaceable.

## Authority boundary

Decision authority: **Reza Hosseiny** (see `manifest.yaml`).

AI participants may NOT, under any circumstances:

- approve, accept, or promote any record (proposals only)
- change authority boundaries or this file's rules
- edit approved records (supersede instead)
- deploy to or modify any Splunk environment other than the standalone
  dev instance at /opt/splunk on this VM
- modify the strategy documents under `strategy/` (they are the
  normative spec; changes are Reza's alone)
- commit secrets, credentials, or unsanitized production data to
  version control, or push this repository to any remote without
  explicit approval
- hand-edit generated `build/` output, or use Splunk Web UI for RBAC
  configuration (change the catalog and regenerate instead)

## Reading order

1. `manifest.yaml` — what versions and profile this project follows
2. `state.yaml` — current state, active work, next authorized action
3. `ROADMAP.md` — the five phases, what each ends with, and where we are
4. `controls/` — if present, read each applicable authoritative control;
   unknown identity never grants a scoped permission
5. `decisions/` — what has been decided and approved (in ID order)
6. `work/` and `handoff/current.md` — what is in flight

Generated capsules, upgrade briefs, validator reports, and tool logs belong in
the external runtime workspace reported by the installed framework tool's
`runtime .` command; they are not project records unless explicitly promoted
into a governed record.

## Session close (material sessions)

Update `state.yaml` (state, active work, next action) and
`handoff/current.md` (what happened, what's mid-flight, what's next).
If a successor would act differently without knowing it — record it.
