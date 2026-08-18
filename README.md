# Splunk RBAC Test Harness

**Framework:** AI-EGC Framework<br>
**Author:** Reza Hosseiny<br>
**Version:** 0.3.1

Automated build-and-test environment proving the RBAC model in
Tri-State's Splunk Strategy 2.0 on a standalone dev Splunk instance:
a YAML catalog generates the RBAC apps (roles, privilege bundles,
indexes, workspaces, compliance detections), deploy scripts push them
to the instance, and static + behavioral pytest suites verify the model
behaves exactly as the strategy specifies. The normative spec is
`strategy/Splunk_Strategy_2.0.md`, § Role-Based Access Control.

**This project is governed by the AI-EGC Framework** — start at
[`ai-egc/START_HERE.md`](ai-egc/START_HERE.md).
