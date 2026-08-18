What this project is

An automated test harness for the RBAC model in Tri-State's Splunk Strategy 2.0 (full document: docs/Splunk_Strategy_2.0.md  the # Role-Based Access Control (RBAC) section is the normative spec for everything here). Owner: Reza Hosseiny (reza.hosseiny@tristategt.org), VP Technical Services.

Goal: on a standalone Splunk instance on a Linux dev VM, automatically build a test environment (indexes, sourcetypes, RBAC roles, test users, sample data) from a YAML catalog, then run automated tests proving the RBAC strategy works as designed. Maximum automation is an explicit requirement.

The RBAC model in one paragraph

Business Roles (rl_*) are assigned to users (1 per user, no exceptions) and contain ONLY importRoles  no permissions of their own. They compose single-concern Privilege Bundles (pr_*): pr_data_* (index access only), pr_search_* (search-execution caps + runtime envelope/quotas), pr_feat_* (all other capabilities), pr_workspace_* (empty stanza; app access granted in each workspace app's metadata/local.meta). Splunk unions permissions across imported roles and takes MAX of quotas. Sensitive capabilities (list in catalog/taxonomy.yaml) may exist only in pr_feat_admin_* bundles. Built-in roles (admin/power/user/can_delete) are never modified or imported. All config deploys as an app (tristate_rbac); UI edits are prohibited; drift from etc/system/local/ is a detectable violation. Seven standing compliance detections are defined in the strategy §Compliance monitoring  they must be implemented as saved searches AND asserted by pytest (including violation-injection tests proving each detection fires).

Architecture / data flow
catalog/*.yaml  generators/build.py  build/apps/*  deploy/deploy.sh  Splunk VM
                        
        tests/static (offline, pre-deploy)      tests/behavioral (live REST, per test user)

Key principle: catalog/expectations.yaml is an INDEPENDENT, human-written statement of what each role must/must not be able to do. Behavioral tests compare live Splunk behavior against expectations, never against values derived from bundles/roles (that would self-certify generator bugs). A static test cross-checks expectations against the catalog-computed effective sets so disagreements surface as conscious decisions.

Decisions already made
Repo lives at /Codes/Splunk_RBAC on the Linux dev VM; user works in VS Code.
Test auth: local test users, one per rl_* role (users.yaml). Production SAML GRP_splunk_<rl_*> 1:1 mapping is covered by static tests on a generated authentication.conf template only. (LDAP container deferred.)
Standalone instance: use etc/apps/ instead of prod etc/shcluster/apps/ / etc/manager-apps/  deviation documented in README.
Python + pytest + requests; PyYAML for catalog. Splunk version not yet confirmed  keep code version-agnostic (plain REST, no splunk-sdk).
Test-user passwords: generated at deploy time by deploy/create_users.py, written to config/test_user_credentials.json (gitignored), consumed by behavioral tests. Admin creds come from config/.env (see .env.example).
Catalog entries marked example: true are placeholders from the strategy doc's own examples. They make the pipeline runnable today and will be REPLACED in a mapping workshop when Reza provides sanitized production samples (index/source/sourcetype lists + events). Synthetic sample files (45 events across 4 feeds) exist so end-to-end runs work now.
Decisions will be made together with Reza per his "ai-egc" framework  details not yet provided. ASK about it before running the mapping workshop.
Repo status

DONE (review before trusting, but these are complete):

README.md  layout, quick start, deviations table, workflow
Makefile  targets: validate, build, test-static, deploy, users, seed, test-behavioral, test, capability-baseline, clean, all
requirements.txt, .gitignore, config/settings.yaml, config/.env.example
catalog/  all 8 files (taxonomy, indexes, sourcetypes, sources, bundles, roles, users, expectations). 5 roles, 14 bundles, 5 indexes incl. quarantine ops_non_inf_bad_s. Expectations filled for all 5 roles.
sample_data/  README, manifest.yaml, 4 synthetic .log files
generators/loader.py  catalog loading, referential-integrity checks, regexes (INDEX_NAME_RE, SANDBOX_INDEX_RE, TAG_NAME_RE, ROLE_RE, BUNDLE_RE), helpers: effective_capabilities / effective_index_patterns / effective_allowed_indexes (fnmatch) / effective_quotas (MAX rule) / workspace_apps
docs/Splunk_Strategy_2.0.md  the reference document

TODO (specs below; nothing else written yet):

generators/__init__.py (empty) and generators/build.py  orchestrator. python -m generators.build [--validate-only]. Fail loudly on catalog.errors. Render into build/apps/:
tristate_rbac/local/authorize.conf  every pr_* bundle and rl_* role. Bundle rendering per category: data  srchIndexesAllowed (semicolon- separated), srchIndexesDefault, optional srchFilter; search  caps as <cap> = enabled + envelope attrs verbatim; feat  caps only; workspace  empty stanza [role_pr_workspace_x] with a comment. Roles  importRoles = bundle1;bundle2;... only.
tristate_rbac/local/authentication.conf.template  SAML roleMap with one GRP_splunk_<role> = <role> line per rl_* (static-test target; not deployed on the test VM).
tristate_rbac/local/savedsearches.conf  the 7 compliance detections (SPL against _audit, _internal, | rest /services/authorization/roles and | rest /services/admin/users): multi_role_assignment, direct_bundle_assignment, sensitive_capability_sprawl, destructive_capability_check, configuration_drift, sensitive_role_chain_membership, capability_catalog_change. Naming per strategy: prefix al_ (alerts), e.g. al_rbac_multi_role_assignment.
tristate_rbac/metadata/local.meta  write restricted to platform admins.
tristate_rbac/default/app.conf  version stamped from a VERSION file or catalog hash (strategy: version incremented every change).
tristate_indexes/local/indexes.conf  from catalog indexes + retention tiers in taxonomy (frozenTimePeriodInSecs = total_days*86400; homePath/ coldPath/thawedPath under $SPLUNK_DB; comment hot/cold split  single VM has one storage tier).
tristate_indexes/local/props.conf  per sourcetype: TZ, TIME_FORMAT where given, SHOULD_LINEMERGE=false.
One workspace app per pr_workspace_* bundle (from its apps: list): default/app.conf, metadata/local.meta with access = read : [ <bundle> ], write : [ rl_platform_admin ], export = system, plus a trivial default/data/ui/nav/default.xml and one placeholder dashboard so app visibility is testable.
deploy/  splunk_api.py (thin requests wrapper: session login, GET/POST with verify from settings, JSON output mode); deploy.sh (idempotent: rsync build/apps  $SPLUNK_HOME/etc/apps, remove previously-deployed apps not in build, restart or debug/refresh, then create_users.py + seed_data.py); teardown.sh (remove apps, test users, test indexes  clean slate); create_users.py (delete+recreate each users.yaml user via /services/authentication/users with exactly one role; random passwords  config/test_user_credentials.json); seed_data.py (per manifest.yaml entry: splunk add oneshot <file> -index ... -sourcetype ... -rename-source ... -host ... via CLI, or HEC per settings; verify counts land via admin search after ingest); capability_inventory.py (dump /services/authorization/capabilities to a dated JSON under reports/; diff vs previous baseline  supports the strategy's upgrade triage process).
tests/static/ (+ tests/conftest.py making repo root importable, a session-scoped catalog fixture, and running build once):
test_catalog_integrity: catalog.errors empty
test_naming: every index matches INDEX_NAME_RE with codes existing in taxonomy; retention suffix valid; sourcetypes/sources match TAG_NAME_RE (25 tags, lowercase); roles match ROLE_RE; bundles match BUNDLE_RE; service-account roles match rl_svc_*
test_bundle_concerns: data bundles have no capabilities/envelope; search bundle caps  search_execution_capabilities; feat bundles have caps only and none in search_execution_capabilities; workspace bundles have neither caps nor indexes nor envelope
test_sensitive_caps: sensitive caps appear only in bundles named pr_feat_admin_* AND flagged sensitive:true with a governance block; roles importing them are flagged sensitive:true
test_roles_composition: every role has bundles only (no capabilities/indexes keys); no built-in roles imported; every user has exactly one role; service accounts default pr_search_constrained unless justified
test_expectations_consistency: for each role, expectations allowed_indexes == catalog effective_allowed_indexes; denied  allowed == ; capabilities == effective_capabilities; quotas == effective_quotas; visible_apps == workspace_apps
test_generated_confs: parse build/apps authorize.conf (configparser with strict=False or hand parser  Splunk conf  INI); every stanza round-trips to the catalog; rl_* stanzas contain only importRoles; roleMap template has exactly one role per line
test_sizing: warn (not fail) when bundle counts leave taxonomy sizing_targets  use pytest.warns/warnings
test_manifest: every manifest sample file exists, nonempty, and its index/sourcetype/source exist in the catalog
tests/behavioral/ (skip cleanly with a clear message if config/.env or credentials file missing). Fixtures: admin session + per-user sessions from test_user_credentials.json. Expected event counts per index computed from manifest + line counts. Tests, all driven by expectations.yaml:
test_data_access: as each user, search index=<ix> | stats count over all-time returns the seeded count for allowed, and 0 events for denied (Splunk silently returns nothing for unauthorized indexes); also index=* must return only allowed indexes' events
test_capabilities: /services/authentication/current-context capabilities == expectations (assert full set equality)
test_roles: user's roles list == exactly [their rl_* role]
test_quotas: /services/authorization/roles/<rl_*> effective quota attrs match expectations
test_app_visibility: /services/apps/local as user  visible_apps present, hidden_apps absent
test_compliance_detections: each of the 7 saved searches exists and runs clean on the healthy environment; then INJECTION: e.g. temporarily add a second role to a user  al_rbac_multi_role_assignment returns it  revert (use try/finally; environment must end clean); assign a pr_* to a user directly  detection fires  revert
Optional later: GitHub Actions/pre-commit for static tests; LDAP container for roleMap behavioral coverage; Splunk in Docker for CI behavioral runs.
Conventions
Never hand-edit build/ output; change the catalog and regenerate.
Never use Splunk Web UI for RBAC config on the VM (mirrors production rule).
Any new index/sourcetype/source goes through the catalog with owner fields.
Keep code version-agnostic across Splunk 9.x; no splunk-sdk dependency.
Line length and style: plain PEP8, no framework beyond pytest.
Immediate next steps (in order)
Finish generators/build.py + __init__.py; make build must produce the three app trees from the current example catalog.
Write static tests; make test-static green.
Write deploy scripts; run on the VM against real $SPLUNK_HOME.
Write behavioral tests; make test-behavioral green on the VM.
THEN: mapping workshop with Reza  replace example: true entries with real sanitized production feeds (he will supply index/source/sourcetype lists + sample events; ask him for the ai-egc framework details first).
Re-run everything; iterate on bundle/role design against real data.
Also known (environment)
Original strategy docs live in D:\Agentic\Splunk on Reza's Windows machine and in the claude.ai "Splunk" project (claude/Splunk_Strategy_2.0.md).
Splunk_Strategy_2.0.md = v1.0 with the RBAC section replaced by the overhauled version from Splunk_RBAC_Strategy_Section.docx (2026-08-18). Figure 1 (layered RBAC diagram) referenced at Splunk_Strategy_media/rbac_figure1.png (not copied into this repo).
Two known v1.0-inherited loose ends outside RBAC scope: an open "Cribl or other ingestion control?" question in §Ingestion Plane, and a Long Term retention inconsistency (3 years in §Retention Suffix vs 7 years total in the retention table). Not blockers for this project.
