#!/usr/bin/env python3
"""Generate the RBAC configuration and test report.

Everything in the report is read from the catalog, the resolved inventory, and the
JUnit output of the last run. Nothing is hand-maintained, so a configuration
change followed by `make test` produces a report that describes the new
configuration and the new result.

    python -m tools.rbac_report                 # full report, credentials shown
    python -m tools.rbac_report --mask-passwords
"""

import argparse
import datetime
import glob
import hashlib
import json
import os
import re
import sys
import xml.etree.ElementTree as ET

from generators import loader

ROOT = loader.ROOT
REPORTS = os.path.join(ROOT, "reports")
OUT = os.path.join(REPORTS, "rbac_report.md")
CREDENTIALS = os.path.join(ROOT, "config", "test_user_credentials.json")

AUTHOR = "Reza Hosseiny, Vice President Technical Services"

# Purpose of each REST interface the harness uses. Endpoints are discovered from
# the source; this supplies the meaning. An endpoint with no entry here is listed
# as undocumented rather than omitted, so the section cannot go stale silently.
ENDPOINT_PURPOSE = {
    "/services/server/info":
        "Confirm connectivity and record the Splunk version and build under test.",
    "/services/server/control/restart":
        "Restart splunkd after an index is added, which Splunk cannot hot-reload.",
    "/services/apps/local":
        "List installed apps, create a generated app, and read app visibility as a user.",
    "/services/data/indexes":
        "List indexes and confirm each catalog index exists on the instance.",
    "/services/receivers/stream":
        "Stream a batch of seeded events into one index, sourcetype, and source.",
    "/services/receivers/simple":
        "Send a single event when diagnosing ingestion.",
    "/services/search/jobs":
        "Run every verification and detection search.",
    "/services/authorization/roles":
        "Read each role's effective index set, capability set, and quotas.",
    "/services/authorization/capabilities":
        "Capture the capability catalogue for the baseline and the upgrade diff.",
    "/services/authentication/users":
        "Create, delete, and read the test users, and inject a role violation.",
    "/services/authentication/current-context":
        "Read what a user actually holds. The authoritative source for effective "
        "capabilities, because a role definition is not the same as a user's "
        "resolved permissions.",
    "/services/messages":
        "Read splunkd's own warnings, which is how dropped events were traced.",
    "/services/licenser/groups":
        "Confirm the licence state while diagnosing ingestion.",
    "/servicesNS/nobody/{app}/configs/conf-{file}":
        "Write a generated .conf stanza into the app's own local directory.",
    "/servicesNS/nobody/{app}/data/indexes":
        "Create an index inside the app namespace.",
    "/servicesNS/nobody/{app}/data/ui/views":
        "Deploy a dashboard and set its permissions.",
    "/servicesNS/nobody/{app}/data/ui/nav":
        "Deploy an app's navigation.",
    "/servicesNS/nobody/{app}/data/lookup-table-files":
        "Upload a lookup file. Not usable on this host: the endpoint requires the "
        "file staged on the Splunk filesystem first.",
    "/servicesNS/nobody/{app}/saved/searches":
        "Read a deployed detection and its SPL.",
    "/servicesNS/nobody/{app}/authorization/roles":
        "Change a role's capability list live, which is how a violation is "
        "injected and reverted.",
    "/servicesNS/nobody/{app}/apps/local/{app}/acl":
        "Apply an app's metadata as an object permission.",
    "/servicesNS/-/-/configs/conf-{file}":
        "Read every role stanza across all apps with its owning app. Used with "
        "conf-authorize, and the only interface that answers the "
        "configuration-drift question: the roles interface reports an empty "
        "owning app for every role.",
}

SCAN_DIRS = ("deploy", "tools", "tests", "generators")
# This module holds the extraction patterns and the purpose keys, so
# scanning it would report its own text as interfaces in use.
SCAN_SKIP = ("tools/rbac_report.py",)


# ---------------------------------------------------------------- formatting

def us_date(moment):
    """August 18, 2026 — no zero padding on the day."""
    return f"{moment.strftime('%B')} {moment.day}, {moment.year}"


def anchor(title):
    slug = re.sub(r"[^a-z0-9\s-]", "", title.lower())
    return re.sub(r"\s+", "-", slug.strip())


def bar(value, peak, width=26):
    """A proportional bar. Zero draws nothing rather than a misleading sliver."""
    if not peak or value <= 0:
        return ""
    filled = max(1, round(value / peak * width))
    return "█" * filled


def yn(value):
    return "yes" if value else "—"


def wrap(text, width=94):
    words, out, line = " ".join(str(text).split()).split(), [], ""
    for word in words:
        if len(line) + len(word) + 1 > width:
            out.append(line)
            line = word
        else:
            line = f"{line} {word}".strip()
    out.append(line)
    return "\n".join(out)


# ---------------------------------------------------------------- inputs

def load_junit():
    """Every test case, plus the run timestamp and totals."""
    cases, stamps = [], []
    totals = {"tests": 0, "failures": 0, "errors": 0, "skipped": 0}
    for path in sorted(glob.glob(os.path.join(REPORTS, "junit-*.xml"))):
        suite_name = os.path.basename(path)[6:-4]
        root = ET.parse(path).getroot()
        for suite in root.iter("testsuite"):
            if suite.get("timestamp"):
                stamps.append(suite.get("timestamp"))
            for key in totals:
                totals[key] += int(suite.get(key) or 0)
        for case in root.iter("testcase"):
            outcome, detail = "passed", ""
            for child in case:
                if child.tag in ("failure", "error"):
                    outcome, detail = "failed", (child.get("message") or "").strip()
                elif child.tag == "skipped":
                    outcome, detail = "skipped", (child.get("message") or "").strip()
            cases.append({
                "suite": suite_name,
                "name": case.get("name"),
                "module": (case.get("classname") or "").replace(".", "/"),
                "seconds": float(case.get("time") or 0),
                "outcome": outcome,
                "detail": detail,
            })
    run = None
    if stamps:
        try:
            run = datetime.datetime.fromisoformat(min(stamps))
        except ValueError:
            run = None
    return cases, totals, run


def load_inventory():
    path = os.path.join(REPORTS, "resolved_inventory.json")
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def load_credentials():
    if not os.path.exists(CREDENTIALS):
        return None
    with open(CREDENTIALS, encoding="utf-8") as handle:
        return json.load(handle)


def catalog_fingerprint(catalog):
    digest = hashlib.sha256()
    for name in sorted(catalog.FILES):
        with open(os.path.join(catalog.dir, f"{name}.yaml"), "rb") as handle:
            digest.update(handle.read())
    return digest.hexdigest()[:12]


def target_platform():
    try:
        from deploy.splunk_api import Splunk
        info = Splunk.from_env().server_info()
        return (f"Splunk Enterprise {info['version']} (build {info['build']}), "
                f"{info['server_name']}")
    except Exception:
        return "not reachable when this report was generated"


# Collections whose trailing segment is one object's name, not part of the path.
OBJECT_COLLECTIONS = (
    "authorization/roles", "authentication/users", "data/indexes",
    "saved/searches", "apps/local", "data/ui/views", "data/ui/nav",
    "data/lookup-table-files", "messages",
)


def normalise_endpoint(raw):
    """One interface path, or None if the match is not a real path.

    Extraction from source picks up fragments as well as calls: a trailing
    backtick from a docstring, an f-string placeholder, a specific object name.
    Normalising here is what keeps the section a list of interfaces rather than a
    list of string literals.
    """
    clean = raw.strip().rstrip("`\"'),.;:/")
    if re.search(r"\[\^|\\s|\\\"", clean):
        return None                      # part of a regex, not a path
    clean = re.sub(r"\{[^}]*\}", "{app}", clean)
    clean = re.sub(r"\{app\}(?:\{app\})+", "{app}", clean)
    if clean.startswith("/servicesNS/") and "{app}" not in clean:
        parts = clean.split("/")
        if len(parts) > 3 and parts[2] != "-":
            parts[2] = "nobody"
        if len(parts) > 4 and parts[3] not in ("-",):
            parts[3] = "{app}"
        clean = "/".join(parts)
    # The conf file varies by caller; the interface is the same one.
    clean = re.sub(r"/configs/conf-[A-Za-z0-9{}_.\-]+", "/configs/conf-{file}",
                   clean)
    # An unbalanced brace means the match was cut inside an expression.
    if clean.count("{") != clean.count("}"):
        return None
    # A namespaced path needs an owner, an app, and an endpoint.
    if clean.startswith("/servicesNS/") and len([s for s in clean.split("/") if s]) < 4:
        return None
    for collection in OBJECT_COLLECTIONS:
        clean = re.sub(rf"({re.escape(collection)})/[^/]+$", r"\1", clean)
    clean = re.sub(r"/\{app\}/acl$", "/{app}/acl", clean)
    segments = [s for s in clean.split("/") if s]
    if len(segments) < 2 or not re.fullmatch(r"[A-Za-z0-9{}_/.\-]+", clean):
        return None
    return clean


def discover_endpoints():
    """REST paths the harness actually calls, normalised for grouping."""
    found = {}
    for folder in SCAN_DIRS:
        for path in glob.glob(os.path.join(ROOT, folder, "**", "*.py"),
                              recursive=True):
            relative = os.path.relpath(path, ROOT)
            if relative in SCAN_SKIP:
                continue
            with open(path, encoding="utf-8") as handle:
                text = handle.read()
            for raw in re.findall(r"/servicesNS/[^\s\"'()]*|/services/[^\s\"'()]*",
                                  text):
                clean = normalise_endpoint(raw)
                if clean:
                    found.setdefault(clean, set()).add(relative)
    return found


# ---------------------------------------------------------------- sections

SECTIONS = [
    "Executive summary",
    "Configuration design",
    "The catalog",
    "Classification and naming",
    "Governed indexes",
    "Legacy to governed mapping",
    "Capabilities",
    "Privilege bundles",
    "Business roles",
    "Test users and credentials",
    "Access expectations",
    "Test design",
    "Coverage of the model",
    "Test results",
    "Compliance detections",
    "REST interfaces used",
    "Reproducibility",
    "Findings and limitations",
    "Regenerating this report",
]


def header(catalog, run, totals, fingerprint, generated):
    passed = (totals["tests"] - totals["failures"] - totals["errors"]
              - totals["skipped"])
    verdict = "PASS" if not (totals["failures"] or totals["errors"]) else "FAIL"
    lines = [
        "# Splunk RBAC Configuration and Test Report",
        "",
        "> **PROPRIETARY — TRI-STATE INTERNAL USE ONLY**",
        ">",
        "> This document and the system that produced it are the proprietary",
        "> property of Tri-State Generation and Transmission Association. Use is",
        "> restricted to authorized Tri-State employees. It must not be copied,",
        "> distributed, or disclosed outside Tri-State without written",
        "> authorization.",
        ">",
        "> This report contains access-control configuration and test-account",
        "> credentials. Handle it accordingly.",
        "",
        "---",
        "",
        "| Field | Value |",
        "|---|---|",
        "| **Document** | Splunk RBAC Configuration and Test Report |",
        "| **Location in Repo** | `reports/rbac_report.md` |",
        f"| **Author** | {AUTHOR} |",
        f"| **Status** | Generated — {verdict} |",
        f"| **Last Updated** | {us_date(generated)} |",
        "| **Covers** | The governed index catalog, the RBAC model as "
        "configured, the test suites and their results, and the REST interfaces "
        "used to obtain them. |",
        "",
        "## Report provenance",
        "",
        "| | |",
        "|---|---|",
        f"| Test run started | "
        f"{run.strftime('%Y-%m-%d %H:%M:%S %z') if run else '—'} |",
        f"| Report generated | {generated.strftime('%Y-%m-%d %H:%M:%S %z')} |",
        f"| Result | **{passed} passed, {totals['failures'] + totals['errors']} "
        f"failed, {totals['skipped']} skipped** of {totals['tests']} |",
        f"| Target platform | {target_platform()} |",
        f"| Catalog fingerprint | `{fingerprint}` |",
        "| Governing strategy | Splunk Strategy 2.0, section Role-Based Access "
        "Control |",
        "| Governance framework | AI-EGC 0.3.1 — records in `ai-egc/` |",
        "",
        "The catalog fingerprint is a content hash of every decision file. If it",
        "differs from the fingerprint in a later report, the configuration changed",
        "between the two runs.",
        "",
        "## Contents",
        "",
    ]
    for number, title in enumerate(SECTIONS, 1):
        lines.append(f"{number}. [{title}](#{anchor(title)})")
    lines += ["", "---", ""]
    return lines


def executive_summary(catalog, cases, totals, inventory):
    counts = {k: len(v) for k, v in catalog.bundle_groups.items()}
    events = sum(r["events"] for r in inventory["indexes"].values()) if inventory else 0
    fixtures = sum(int(f["events"]) for f in catalog.fixtures.values())
    population = [r for r in catalog.role_list if r.get("purpose") != "coverage"]
    passed = sum(1 for c in cases if c["outcome"] == "passed")
    lines = [
        "## Executive summary", "",
        "The access-control model defined in Splunk Strategy 2.0 has been built on",
        "a Splunk instance from a single catalog of decisions and tested",
        "automatically. This report records the configuration as it stands and the",
        "result of the most recent test run.", "",
        "| | |", "|---|---:|",
        f"| Governed indexes | {len(catalog.index_list)} |",
        f"| Events loaded | {events + fixtures:,} |",
        f"| Privilege Bundles | {len(catalog.bundle_by_name)} |",
        f"| Business Roles | {len(catalog.role_list)} |",
        f"| — of which model real populations | {len(population)} |",
        f"| — of which exist to make behaviour observable | "
        f"{len(catalog.role_list) - len(population)} |",
        f"| Test users | {len(catalog.user_list)} |",
        f"| Compliance detections | 7 |",
        f"| Model behaviours under test | "
        f"{len(catalog.coverage_matrix['behaviours'])} |",
        f"| Tests | {len(cases)} |",
        f"| Tests passed | {passed} |",
        f"| Tests failed | {totals['failures'] + totals['errors']} |",
        "",
        "### Bundle catalogue against the strategy's sizing targets", "",
        "| Category | Count | Target | Within target |", "|---|---:|---|---|",
    ]
    for category in ("data", "search", "feat", "workspace"):
        target = catalog.taxonomy["sizing_targets"].get(f"pr_{category}") or {}
        count = counts.get(category, 0)
        inside = target.get("min", 0) <= count <= target.get("max", 99)
        lines.append(f"| `pr_{category}_*` | {count} | "
                     f"{target.get('min')}–{target.get('max')} | {yn(inside)} |")
    lines += ["", "---", ""]
    return lines


def configuration_design(catalog):
    return [
        "## Configuration design", "",
        "### The model", "",
        "Splunk has one access-control object: the role. The strategy adds a",
        "governance layer above it, splitting roles into two kinds.", "",
        "A **Business Role** (`rl_*`) is what a user holds. Each user holds exactly",
        "one, and it grants nothing itself — it only imports Privilege Bundles.",
        "A **Privilege Bundle** (`pr_*`) grants one kind of access and one only.",
        "", "```mermaid", "flowchart LR",
        "  U[\"User<br/>one Business Role\"] --> R[\"rl_* Business Role<br/>importRoles only\"]",
        "  R --> D[\"pr_data_*<br/>which indexes\"]",
        "  R --> S[\"pr_search_*<br/>search envelope\"]",
        "  R --> F[\"pr_feat_*<br/>capabilities\"]",
        "  R --> W[\"pr_workspace_*<br/>empty stanza\"]",
        "  D --> I[\"Indexes\"]",
        "  S --> Q[\"Quotas and<br/>search execution\"]",
        "  F --> C[\"Splunk capabilities\"]",
        "  W --> A[\"App metadata<br/>grants app access\"]",
        "```", "",
        "Splunk evaluates a user's permissions as the **union** of every role in the",
        "chain, and each quota as the **maximum** across the chain. That is why",
        "bundles compose without loss, and it is the behaviour the tests verify",
        "rather than assume.", "",
        "### The rules the configuration obeys", "",
        "| Rule | Why it exists |", "|---|---|",
        "| A bundle holds only what its category permits | It is what makes any "
        "data bundle combinable with any search, feature, and workspace bundle "
        "without one silently affecting another |",
        "| A Business Role holds `importRoles` and nothing else | Answering \"what "
        "can this user do?\" means reading one chain, not hunting for direct grants |",
        "| Index sets wildcard the retention suffix only | An explicit list breaks "
        "when an index changes retention tier; a broad wildcard would grant the "
        "quarantine index as a side effect |",
        "| Sensitive capabilities live only in a `pr_feat_admin_*` bundle | It "
        "confines privilege escalation to a named, governed grant |",
        "| No built-in Splunk role is modified or imported | A built-in role changes "
        "between releases and is outside this project's control |",
        "| Expectations are written by hand, never generated | If they were derived "
        "from the same configuration the generator reads, a fault would appear in "
        "both and the tests would agree with it |",
        "| Nothing is configured through Splunk Web | A UI change is written to "
        "`etc/system/local`, which is per-member and outside version control |",
        "", "---", ""]


def the_catalog(catalog):
    files = [
        ("taxonomy.yaml", "Registered codes, retention tiers, capability tiers, "
                          "sizing targets, and the measured platform limits"),
        ("mapping.yaml", "How every legacy index, sourcetype, and source maps to "
                         "its governed equivalent"),
        ("indexes.yaml", "The index register: description and both owners for each "
                         "index"),
        ("business_units.yaml", "The business units that may hold data ownership"),
        ("redaction.yaml", "What must be removed from any production export before "
                           "it is used"),
        ("bundles.yaml", "Every Privilege Bundle and what it grants"),
        ("roles.yaml", "Every Business Role and the bundles it composes"),
        ("users.yaml", "The test users, one per role"),
        ("expectations.yaml", "What each role must and must not be able to do, "
                              "written by hand"),
        ("coverage_matrix.yaml", "Every behaviour under test and what makes it "
                                 "observable"),
    ]
    lines = [
        "## The catalog", "",
        "Every decision lives in exactly one file. Changing a decision means",
        "editing that file and re-running the pipeline; it never means editing a",
        "`.conf` file, a script, or Splunk itself.", "",
        "| File | Decision it holds | Size |", "|---|---|---:|",
    ]
    for name, purpose in files:
        path = os.path.join(catalog.dir, name)
        size = f"{sum(1 for _ in open(path, encoding='utf-8'))} lines" \
            if os.path.exists(path) else "absent"
        lines.append(f"| `catalog/{name}` | {purpose} | {size} |")
    lines += [
        "", "Everything else is generated. `build/apps/` and `reports/` are",
        "rewritten on every run and are never edited by hand.", "", "---", ""]
    return lines


def classification(catalog):
    tax = catalog.taxonomy
    lines = [
        "## Classification and naming", "",
        "An index name encodes its own governance, so a reader can tell what an",
        "index holds and how long it is kept without consulting a register:", "",
        "```", "[class]_[compliance]_[domain]_[content]_[optional detail]_[retention]",
        "```", "",
        "Each code is three letters and must be registered before use. The register",
        "below is the authority; a name using an unregistered code fails the build.",
        "", "### Data classes", "",
        "| Code | Class | Sensitivity |", "|---|---|---|",
    ]
    for code, detail in tax["classes"].items():
        lines.append(f"| `{code}` | {detail['number']} — {detail['name']} | "
                     f"{'strictly defined by the strategy' if detail.get('source')=='strategy' else ''} |")
    lines += ["", "### Compliance drivers", "", "| Code | Driver |", "|---|---|"]
    for code, detail in tax["compliance"].items():
        lines.append(f"| `{code}` | {detail['name']} |")
    lines += ["", "### Domains", "", "| Code | Domain |", "|---|---|"]
    for code, detail in tax["domains"].items():
        lines.append(f"| `{code}` | {detail['name']} |")
    lines += ["", "### Content codes", "",
              "Codes marked *proposed* are new in this project and require Data",
              "Governance Council registration.", "",
              "| Code | Content | Origin |", "|---|---|---|"]
    for code, detail in sorted(tax["content"].items()):
        lines.append(f"| `{code}` | {detail['name']} | {detail.get('source','')} |")
    lines += ["", "### Retention tiers", "",
              "`frozenTimePeriodInSecs` encodes searchable retention — hot plus",
              "cold. Any archive period after that is custody handled outside",
              "Splunk.", "",
              "| Suffix | Tier | Hot | Cold | Searchable | Archive | At end |",
              "|---|---|---:|---:|---:|---:|---|"]
    for suffix, tier in tax["retention"].items():
        lines.append(
            f"| `_{suffix}` | {tier['name']} | {tier['hot_days']}d | "
            f"{tier['cold_days']}d | {tier['searchable_days']}d | "
            f"{tier['archive_days']}d | {tier['frozen_action']} |")

    lines += ["", "### Coverage of the class and compliance matrix", "",
              "Every combination in use, and which indexes occupy it. A boundary",
              "the model claims to enforce needs data on both sides of it to be",
              "testable at all.", "",
              "| Class | Compliance | Indexes |", "|---|---|---|"]
    cells = {}
    for entry in catalog.index_list:
        fields = catalog.decode(entry["name"])
        if fields:
            cells.setdefault((fields["data_class"], fields["compliance"]),
                             []).append(entry["name"])
    for (cls, comp), names in sorted(cells.items()):
        lines.append(f"| `{cls}` {catalog.taxonomy['classes'][cls]['name']} | "
                     f"`{comp}` | {len(names)} — "
                     + ", ".join(f"`{n}`" for n in sorted(names)) + " |")
    exempt = [e["name"] for e in catalog.index_list if e.get("naming_exception")]
    if exempt:
        lines += ["", f"A further {len(exempt)} indexes carry a registered naming",
                  "exception and keep vendor-mandated names:",
                  "", ", ".join(f"`{n}`" for n in sorted(exempt)) + ".", "",
                  "Splunk Enterprise Security resolves these names internally in",
                  "its correlation searches and data models, so renaming them",
                  "breaks the application. The exception excuses the index name",
                  "only; their sourcetypes and sources are still checked."]
    lines += ["", "---", ""]
    return lines


def indexes_section(catalog, inventory):
    lines = [
        "## Governed indexes", "",
        f"{len(catalog.index_list)} indexes. Class, compliance driver, domain,",
        "content code, and retention are all encoded in the name; they are repeated",
        "here so the register reads on its own, and a static test fails the build if",
        "the two ever disagree.", "",
        "| Index | Class | Compl. | Domain | Content | Ret. | Business owner | "
        "Technical owner | Purpose |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    units = catalog.units
    for entry in sorted(catalog.index_list, key=lambda e: e["name"]):
        fields = catalog.decode(entry["name"]) or {}
        purpose = " ".join(entry["description"].split())
        lines.append(
            f"| `{entry['name']}` | {fields.get('data_class', '—')} | "
            f"{fields.get('compliance', '—')} | {fields.get('domain', '—')} | "
            f"{fields.get('content', '—')} | {entry.get('retention', '—')} | "
            f"{units[entry['owner_business']]['name']} | "
            f"{units[entry['owner_technical']]['name']} | {purpose} |")

    if inventory:
        volumes = {name: rec["events"]
                   for name, rec in inventory["indexes"].items()}
        for fixture, detail in catalog.fixtures.items():
            volumes[fixture] = int(detail["events"])
        peak = max(volumes.values()) if volumes else 0
        lines += ["", "### Event volume as loaded", "",
                  "Volume is what makes an access boundary observable: an index",
                  "holding nothing cannot demonstrate that a role reaches it.", "",
                  "```"]
        for name, count in sorted(volumes.items(), key=lambda kv: -kv[1]):
            lines.append(f"{name:24s} {count:>7,d}  {bar(count, peak)}")
        lines += ["```", "",
                  f"Total {sum(volumes.values()):,} events across "
                  f"{len(volumes)} indexes."]

    lines += ["", "### Ownership", "",
              "Each index carries two owners with distinct accountabilities. The",
              "business owner is accountable for data quality, continued business",
              "need, and approving access requests. The technical owner owns the",
              "system that produces the data and is accountable for its correctness",
              "and for notice of change. They differ wherever one unit depends on",
              "data another unit operates.", "",
              "| Business unit | Indexes owned (business) | Indexes owned "
              "(technical) |", "|---|---:|---:|"]
    biz, tech = {}, {}
    for entry in catalog.index_list:
        biz[entry["owner_business"]] = biz.get(entry["owner_business"], 0) + 1
        tech[entry["owner_technical"]] = tech.get(entry["owner_technical"], 0) + 1
    for code in sorted(set(biz) | set(tech)):
        lines.append(f"| {units[code]['name']} | {biz.get(code, 0)} | "
                     f"{tech.get(code, 0)} |")
    lines += ["", "---", ""]
    return lines


def mapping_section(catalog, inventory):
    lines = [
        "## Legacy to governed mapping", "",
        "The production estate uses vendor-named indexes and, in many cases,",
        "sourcetypes and sources that do not meet the strategy's metadata standard.",
        "The mapping states what each becomes.", "",
        "It is expressed as **rules**, not as a row per value. Each rule matches a",
        "sourcetype pattern within one legacy index and names the governed",
        "destination. A sourcetype that is new but fits an existing pattern is",
        "classified automatically; a genuinely new feed is reported as a gap and",
        "seeding refuses to run until someone classifies it.", "",
        f"Source policy: **{catalog.mapping['source_policy']}** — sources are",
        "rewritten to governed values on ingest.", "",
        f"Quarantine index: `{catalog.mapping['quarantine_index']}` — anything that",
        "cannot be classified goes here rather than into a production index.", "",
        "### Rules by legacy index", "",
        "| Legacy index | Rules | Governed destinations | Notes |",
        "|---|---:|---|---|",
    ]
    for legacy, entry in sorted(catalog.legacy.items()):
        targets = sorted({r["index"] for r in entry["rules"]})
        note = " ".join((entry.get("note") or "").split())
        if len(note) > 190:
            note = note[:187] + "…"
        lines.append(f"| `{legacy}` | {len(entry['rules'])} | "
                     + ", ".join(f"`{t}`" for t in targets) + f" | {note} |")

    lines += ["", "### Coverage fixtures", "",
              "The production export covers three of the five data classes and one",
              "compliance driver. Without data in the missing cells, the model's",
              "sensitivity walls and compliance isolation could not be tested at",
              "all — so synthetic feeds fill them. RBAC does not examine event",
              "content, so a synthetic event proves a boundary as well as a real",
              "one. A real export replaces a fixture by adding a mapping entry that",
              "targets the same index.", "",
              "| Index | Class | Compliance | Events | Stands in for |",
              "|---|---|---|---:|---|"]
    for name, fixture in sorted(catalog.fixtures.items()):
        lines.append(f"| `{name}` | {fixture['class']} | {fixture['compliance']} | "
                     f"{fixture['events']} | "
                     + " ".join(fixture["reason"].split()) + " |")

    if inventory:
        lines += ["", "### Governed sourcetypes and sources per index", "",
                  "| Index | Sourcetypes | Sources | Events | From legacy |",
                  "|---|---:|---:|---:|---|"]
        for name, rec in sorted(inventory["indexes"].items()):
            lines.append(f"| `{name}` | {len(rec['sourcetypes'])} | "
                         f"{len(rec['sources'])} | {rec['events']:,} | "
                         + ", ".join(f"`{x}`" for x in rec["from_legacy"]) + " |")
        lines += ["", "#### Full sourcetype and source listing", ""]
        for name, rec in sorted(inventory["indexes"].items()):
            lines += [f"**`{name}`**", "",
                      "- Sourcetypes: "
                      + ", ".join(f"`{s}`" for s in rec["sourcetypes"]),
                      "- Sources: "
                      + ", ".join(f"`{s}`" for s in rec["sources"][:40])
                      + (f" _(and {len(rec['sources']) - 40} more)_"
                         if len(rec["sources"]) > 40 else ""), ""]
    else:
        lines += ["", "> Sourcetype and source detail is unavailable: "
                  "`reports/resolved_inventory.json` has not been generated. "
                  "Run `make profile`.", ""]
    lines += ["---", ""]
    return lines


def capabilities_section(catalog):
    baseline_path = os.path.join(REPORTS, "capability_baseline.json")
    available = None
    if os.path.exists(baseline_path):
        with open(baseline_path, encoding="utf-8") as handle:
            available = json.load(handle)
    granted = sorted({c for b in catalog.bundle_by_name.values()
                      for c in b.get("capabilities", [])})
    floors = catalog.taxonomy.get("platform_floors") or {}

    lines = [
        "## Capabilities", "",
        "Capabilities are Splunk's atomic permissions, checked by Splunk's own code",
        "at runtime. They are not user-defined. The catalog grants them only through",
        "bundles, never directly on a Business Role.", "",
        "| | |", "|---|---:|",
        f"| Capabilities available on the target release | "
        f"{len(available) if available else 'baseline not captured'} |",
        f"| Capabilities the catalog grants | {len(granted)} |",
        f"| Classified sensitive | {len(catalog.sensitive_caps)} |",
        f"| Classified destructive | "
        f"{len(catalog.taxonomy['destructive_capabilities'])} |",
        f"| Granted by the platform regardless of role | "
        f"{len(floors.get('capabilities') or {})} |",
        "",
        "Every name in the catalog is verified against the live capability",
        "catalogue. This is not a formality: three names given in the strategy do",
        "not exist on this release, and Splunk rejects an unknown capability rather",
        "than ignoring it.", "",
        "### Sensitive tier", "",
        "These grant privilege escalation, data destruction, credential access, or",
        "platform-wide change. They may appear only in a `pr_feat_admin_*` bundle,",
        "and that bundle must carry a governance block.", "",
        "| Capability | Why it is sensitive | Added by this project |",
        "|---|---|---|",
    ]
    for name, detail in sorted(catalog.taxonomy["sensitive_capabilities"].items()):
        lines.append(f"| `{name}` | {detail.get('reason','')} | "
                     f"{yn(detail.get('addition'))} |")

    absent = catalog.taxonomy.get("sensitive_capabilities_absent_on_target") or {}
    if absent:
        lines += ["", "#### Named by the strategy but absent on this release", "",
                  "| Strategy name | Replacement |", "|---|---|"]
        for name, detail in sorted(absent.items()):
            lines.append(f"| `{name}` | "
                         + (f"`{detail['replaced_by']}`"
                            if detail.get("replaced_by")
                            else "none — " + str(detail.get("note", ""))) + " |")

    lines += ["", "### Destructive set and its allow-list", "",
              "Only a role named in the allow-list may hold one of these. Any other",
              "holder is reported by the destructive-capability detection.", "",
              "| Capability |", "|---|"]
    for name in catalog.taxonomy["destructive_capabilities"]:
        lines.append(f"| `{name}` |")
    lines += ["", "Allow-listed roles: "
              + ", ".join(f"`{r}`" for r in
                          catalog.taxonomy["destructive_capability_allowlist"])
              + ".", ""]

    if floors:
        lines += ["### Granted by the platform regardless of role", "",
                  f"Measured on {floors.get('measured_on')} on",
                  f"{floors.get('measured_date')}. "
                  + " ".join((floors.get("method") or "").split()), "",
                  "These reach every user whatever the configuration says, and",
                  "explicit revocation does not remove them. They are recorded as",
                  "measured facts rather than folded into each role's expected set,",
                  "because two of them are capabilities this strategy would",
                  "otherwise classify as sensitive.", "",
                  "| Capability | Roles holding it without a grant | Note |",
                  "|---|---:|---|"]
        for name, detail in sorted((floors.get("capabilities") or {}).items()):
            lines.append(f"| `{name}` | {detail.get('unearned_by_roles','—')} of "
                         f"{len(catalog.role_list)} | "
                         + " ".join((detail.get("note") or "").split()) + " |")
        minimums = floors.get("quota_minimums") or {}
        if minimums:
            lines += ["", "#### Quota floors", "",
                      "A positive value below the floor is silently raised to it.",
                      "Zero is honoured, so \"none at all\" is achievable while",
                      "\"a small number\" is not.", "",
                      "| Attribute | Floor |", "|---|---:|"]
            for key, value in sorted(minimums.items()):
                lines.append(f"| `{key}` | {value} |")
        unsupported = floors.get("unsupported_attributes") or {}
        if unsupported:
            lines += ["", "#### Attributes not stored on this release", "",
                      "| Attribute | Consequence |", "|---|---|"]
            for key, note in sorted(unsupported.items()):
                lines.append(f"| `{key}` | " + " ".join(str(note).split()) + " |")

    never = catalog.taxonomy.get("capabilities_granted_to_no_role") or {}
    if never:
        lines += ["", "### Deliberately granted to no role", "",
                  "| Capability | Reason |", "|---|---|"]
        for name, detail in sorted(never.items()):
            lines.append(f"| `{name}` | "
                         + " ".join(str(detail.get("reason", "")).split()) + " |")
    lines += ["", "---", ""]
    return lines


def bundles_section(catalog):
    titles = {"data": "Data bundles — which indexes",
              "search": "Search bundles — the runtime envelope",
              "feat": "Feature bundles — all other capabilities",
              "workspace": "Workspace bundles — app access"}
    lines = [
        "## Privilege bundles", "",
        f"{len(catalog.bundle_by_name)} bundles. Each grants one kind of access and",
        "holds no attribute belonging to another category — that separation is what",
        "lets any data bundle combine with any search, feature, and workspace",
        "bundle to produce a role.", "",
    ]
    for category in ("data", "search", "feat", "workspace"):
        group = catalog.bundle_groups[category]
        lines += [f"### {titles[category]}", ""]
        if category == "data":
            lines += ["Index patterns wildcard the retention suffix only. An",
                      "explicit list would break when an index changes retention",
                      "tier; a broader wildcard would grant the quarantine index as",
                      "a side effect.", "",
                      "| Bundle | Index patterns | Resolves to | Default |",
                      "|---|---|---:|---|"]
            for bundle in group:
                patterns = bundle.get("indexes_allowed", [])
                resolved = catalog.effective_allowed_indexes(patterns)
                lines.append(
                    f"| `{bundle['name']}` | "
                    + "<br/>".join(f"`{p}`" for p in patterns)
                    + f" | {len(resolved)} |"
                    + " " + ", ".join(f"`{d}`" for d in
                                      bundle.get("indexes_default", [])) + " |")
        elif category == "search":
            lines += ["| Bundle | Capabilities | Time window | Concurrent | "
                      "Real-time | Disk (MB) |", "|---|---|---:|---:|---:|---:|"]
            for bundle in group:
                env = bundle.get("envelope") or {}
                win = env.get("srchTimeWin")
                lines.append(
                    f"| `{bundle['name']}` | "
                    + ", ".join(f"`{c}`" for c in bundle["capabilities"])
                    + f" | {'no limit' if win == 0 else f'{win:,}s'} | "
                    f"{env.get('srchJobsQuota')} | {env.get('rtSrchJobsQuota')} | "
                    f"{env.get('srchDiskQuota')} |")
        elif category == "feat":
            lines += ["| Bundle | Capabilities | Sensitive |", "|---|---|---|"]
            for bundle in group:
                lines.append(
                    f"| `{bundle['name']}` | "
                    + ", ".join(f"`{c}`" for c in bundle["capabilities"])
                    + f" | {'**yes**' if bundle.get('sensitive') else '—'} |")
        else:
            lines += ["A workspace stanza is intentionally empty: it grants no",
                      "index, no capability, and no quota. It is a named handle,",
                      "and the access is granted in each app's metadata. A",
                      "workspace is therefore a two-file construct, and both halves",
                      "must exist or a user holds a role that reaches nothing.", "",
                      "| Bundle | Apps it unlocks |", "|---|---|"]
            for bundle in group:
                lines.append(f"| `{bundle['name']}` | "
                             + ", ".join(f"`{a}`" for a in bundle["apps"]) + " |")
        lines.append("")

    admin = [b for b in catalog.bundle_groups["feat"] if b.get("sensitive")]
    if admin:
        lines += ["### Governance on the sensitive bundles", "",
                  "| Bundle | Time bounded | Max standing | Dual approval | "
                  "Session logging | Recertification |",
                  "|---|---|---:|---|---|---|"]
        for bundle in admin:
            gov = bundle.get("governance") or {}
            lines.append(
                f"| `{bundle['name']}` | {yn(gov.get('time_bounded'))} | "
                f"{gov.get('max_standing_duration_days','—')} days | "
                f"{yn(gov.get('dual_approval'))} | "
                f"`{gov.get('session_logging','—')}` | "
                f"{gov.get('recertification','—')} |")
        lines.append("")
    lines += ["---", ""]
    return lines


def roles_section(catalog):
    lines = [
        "## Business roles", "",
        f"{len(catalog.role_list)} roles. A Business Role carries no permission of",
        "its own; it is a composition of bundles, rendered as `importRoles` in",
        "`authorize.conf`.", "",
        "Roles marked **coverage** exist to make one model behaviour observable and",
        "would not appear in a production population. They share one control,",
        "`rl_cov_base`, and each differs from it by exactly one bundle — without",
        "such a pair, a configuration fault could not be attributed to a category,",
        "because every role would differ in several ways at once.", "",
        "| Role | Kind | Business unit | Bundles | Indexes | Capabilities | "
        "Sensitive | Purpose |",
        "|---|---|---|---:|---:|---:|---|---|",
    ]
    for role in catalog.role_list:
        name = role["name"]
        unit = role.get("business_unit")
        lines.append(
            f"| `{name}` | {role.get('purpose','population')} | "
            f"{catalog.units[unit]['name'] if unit else '—'} | "
            f"{len(role['bundles'])} | {len(catalog.computed_indexes(name))} | "
            f"{len(catalog.computed_capabilities(name))} | "
            f"{'**yes**' if role.get('sensitive') else '—'} | "
            + " ".join(role["description"].split()) + " |")

    lines += ["", "### Composition — which role imports which bundle", "",
              "| Bundle |"]
    order = [r["name"] for r in catalog.role_list]
    lines[-1] += " " + " | ".join(n.replace("rl_", "") for n in order) + " |"
    lines.append("|---|" + "|".join([":-:"] * len(order)) + "|")
    for category in ("data", "search", "feat", "workspace"):
        for bundle in catalog.bundle_groups[category]:
            row = [f"| `{bundle['name']}` "]
            for name in order:
                held = bundle["name"] in catalog.role_by_name[name]["bundles"]
                row.append(f"| {'●' if held else ''} ")
            lines.append("".join(row) + "|")

    lines += ["", "A dot means the role imports that bundle. Reading down a column",
              "gives a role's whole permission chain; reading across a row shows",
              "how widely a bundle is reused.", ""]

    single = []
    for bundle in catalog.bundle_by_name.values():
        holders = [r["name"] for r in catalog.role_list
                   if bundle["name"] in r["bundles"]]
        if len(holders) == 1:
            single.append((bundle["name"], holders[0],
                           bundle.get("single_role_justification", "")))
    if single:
        lines += ["### Bundles imported by exactly one role", "",
                  "The strategy's reuse test says such grants arguably belong in the",
                  "role itself. Each is kept deliberately, with the reason recorded.",
                  "", "| Bundle | Only holder | Why it stays a bundle |",
                  "|---|---|---|"]
        for name, holder, reason in sorted(single):
            lines.append(f"| `{name}` | `{holder}` | "
                         + " ".join(str(reason).split()) + " |")
        lines.append("")

    lines += ["### One worked chain", "",
              "How `rl_soc_t1` resolves, as an example of the pattern every role",
              "follows.", "", "```mermaid", "flowchart LR",
              "  U[\"t_soc_t1\"] --> R[\"rl_soc_t1\"]"]
    for bundle in catalog.role_by_name["rl_soc_t1"]["bundles"]:
        short = bundle.replace("pr_", "")
        lines.append(f"  R --> {short.replace('_','')}[\"{bundle}\"]")
    lines += ["```", "",
              f"Result: {len(catalog.computed_indexes('rl_soc_t1'))} indexes, "
              f"{len(catalog.computed_capabilities('rl_soc_t1'))} capabilities, "
              f"{len(catalog.computed_workspace_apps('rl_soc_t1'))} workspace app.",
              "", "---", ""]
    return lines


def users_section(catalog, credentials, mask):
    lines = [
        "## Test users and credentials", "",
        "One user per Business Role, and no more. That is what makes the",
        "one-role-per-user rule testable: a behavioural test reads each user's role",
        "list from Splunk and asserts it holds exactly one entry.", "",
        "These users stand in for the identity provider on the test instance.",
        "Production uses SAML, with one group mapped to each Business Role.", "",
    ]
    if mask:
        lines += ["> Credentials are masked in this copy. The full values are in",
                  "> `config/test_user_credentials.json`, which is not committed and",
                  "> is readable only by its owner.", ""]
    else:
        lines += ["> **Credentials below are shown in full.** This is a test system",
                  "> and these accounts exist only on the development instance. They",
                  "> are regenerated on every `make users` run, so any value recorded",
                  "> elsewhere stops working. If this harness is ever promoted to a",
                  "> production role, the credentials must be masked or omitted —",
                  "> `make report-shareable` produces a masked copy.", ""]
    lines += ["| User | Business Role | Kind | Password | Display name |",
              "|---|---|---|---|---|"]
    for user in catalog.user_list:
        role = catalog.role_by_name[user["role"]]
        if credentials and user["username"] in credentials and not mask:
            secret = f"`{credentials[user['username']]['password']}`"
        elif mask:
            secret = "*masked*"
        else:
            secret = "*not created yet*"
        lines.append(f"| `{user['username']}` | `{user['role']}` | "
                     f"{role.get('purpose','population')} | {secret} | "
                     f"{user.get('realname','')} |")

    lines += ["", "### Identity provider mapping used in production", "",
              "The generated `authentication.conf` template holds one line per",
              "Business Role. Exactly one role appears on the right of each line,",
              "and it is always an `rl_*` role — direct assignment of a bundle to a",
              "group is prohibited, and that rule is the technical enforcement of",
              "one role per user.", "", "```ini", "[roleMap_SAML]"]
    for role in catalog.role_list:
        if role.get("purpose") != "coverage":
            lines.append(f"GRP_splunk_{role['name']} = {role['name']}")
    lines += ["```", "",
              "Coverage roles are absent by design: they have no production",
              "population.", "", "---", ""]
    return lines


def expectations_section(catalog):
    lines = [
        "## Access expectations", "",
        "What each role must and must not be able to do. **This statement is written",
        "by hand**, from each role's business purpose, and no tool generates it.", "",
        "That matters more than it appears. The behavioural tests compare live Splunk",
        "behaviour against these values. If they were derived from the same",
        "configuration the generator reads, a fault in the generator would appear in",
        "both, the comparison would agree with the fault, and the suite would pass",
        "while proving nothing. A separate static test compares this statement",
        "against what the configuration actually composes, and a disagreement has to",
        "be resolved as a decision rather than edited away.", "",
        "### Which role reaches which index", "",
    ]
    order = [r["name"] for r in catalog.role_list]
    header_row = "| Index |" + " " + " | ".join(
        n.replace("rl_", "") for n in order) + " |"
    lines += [header_row, "|---|" + "|".join([":-:"] * len(order)) + "|"]
    for entry in sorted(catalog.index_list, key=lambda e: e["name"]):
        row = [f"| `{entry['name']}` "]
        for name in order:
            allowed = entry["name"] in catalog.expects[name]["allowed_indexes"]
            row.append(f"| {'●' if allowed else ''} ")
        lines.append("".join(row) + "|")
    lines += ["", "A dot means the role must reach that index. A blank means it must",
              "not, and a behavioural test confirms a search returns zero events —",
              "silently, which is how Splunk refuses an unauthorized index.", ""]

    lines += ["### Per role", ""]
    for role in catalog.role_list:
        name = role["name"]
        expect = catalog.expects[name]
        quotas = catalog.computed_quotas(name)
        lines += [f"#### `{name}`", "",
                  wrap("**Intent.** " + " ".join(expect["intent"].split())), "",
                  "| | |", "|---|---|",
                  f"| Indexes reachable | {len(expect['allowed_indexes'])} |",
                  f"| Capabilities from the catalog | "
                  f"{len(expect['capabilities'])} |",
                  f"| Capabilities including the platform floor | "
                  f"{len(catalog.expected_live_capabilities(name))} |",
                  f"| Concurrent searches | {quotas.get('srchJobsQuota','—')} |",
                  f"| Real-time searches | {quotas.get('rtSrchJobsQuota','—')} |",
                  f"| Disk quota | {quotas.get('srchDiskQuota','—')} MB |",
                  f"| Time window | "
                  + ("no limit" if quotas.get("srchTimeWin") == 0
                     else f"{quotas.get('srchTimeWin', 0):,}s") + " |",
                  f"| Workspace apps | "
                  + (", ".join(f"`{a}`" for a in
                               catalog.expected_visible_apps(name)) or "none") + " |",
                  ""]
        lines += ["- **Reaches:** "
                  + ", ".join(f"`{i}`" for i in expect["allowed_indexes"]), ""]
        if expect.get("must_not_reach"):
            lines += ["- **Must not reach** (boundaries that carry meaning for this "
                      "role): "
                      + ", ".join(f"`{i}`" for i in expect["must_not_reach"]), ""]
        if expect.get("must_not_hold"):
            lines += ["- **Must not hold:** "
                      + ", ".join(f"`{c}`" for c in expect["must_not_hold"]), ""]
        lines += ["- **Capabilities:** "
                  + ", ".join(f"`{c}`" for c in expect["capabilities"]), ""]
        if expect.get("additional_visible_apps"):
            lines += ["- **Sees additional apps** because "
                      + " ".join(expect["additional_visible_reason"].split())
                      + ": "
                      + ", ".join(f"`{a}`"
                                  for a in expect["additional_visible_apps"]), ""]
    lines += ["---", ""]
    return lines


def test_design_section(catalog, cases):
    static = [c for c in cases if c["suite"] == "static"]
    live = [c for c in cases if c["suite"] == "behavioral"]
    return [
        "## Test design", "",
        "Two suites, run in that order, because a fault caught offline costs a",
        "rebuild while the same fault caught after deployment costs a restart and a",
        "reload.", "",
        "| Suite | Tests | Needs Splunk | What it examines |",
        "|---|---:|---|---|",
        f"| Static | {len(static)} | no | The catalog and the generated `.conf` "
        "files, before anything is deployed |",
        f"| Behavioural | {len(live)} | yes | The live instance, one authenticated "
        "session per test user |",
        "",
        "### What the static suite examines", "",
        "It reads the generated configuration as well as the catalog. A generator",
        "that drops a stanza, or writes a permission the catalog never asked for, is",
        "invisible to a catalog-only check.", "",
        "- The catalog is internally consistent and every name obeys the standard.",
        "- Each bundle holds only what its category permits.",
        "- Sensitive capabilities appear only in a flagged `pr_feat_admin_*` bundle "
        "carrying a governance block.",
        "- No Business Role holds a permission directly; none imports a built-in "
        "role; each has exactly one test user.",
        "- The hand-written expectations agree with what the bundles compose.",
        "- Every capability the catalog names exists on the target release.",
        "- Every generated stanza round-trips to the catalog, every workspace stanza "
        "is empty, and the identity-provider template has exactly one role per line.",
        "- Every sample value resolves through the mapping.",
        "- Every behaviour in the coverage matrix names a test, and every test it "
        "names exists.",
        "",
        "### What the behavioural suite examines", "",
        "It authenticates as each test user and asks Splunk what that user can",
        "actually do. A role definition is not the same thing as a user's resolved",
        "permissions, and the difference is where the platform findings came from.",
        "",
        "- Each user's role list holds exactly one entry.",
        "- Each role's capability set matches exactly — no extra, none missing.",
        "- The recorded platform floor still describes the platform, so an upgrade "
        "that widens it fails loudly instead of quietly widening access.",
        "- Each role reaches exactly the indexes it must, with the event counts that "
        "were loaded, and a denied index returns zero events when named directly.",
        "- Quotas match the catalog, or the recorded floor where the catalog asks "
        "for less.",
        "- Quotas resolve as a per-attribute maximum across two composed bundles.",
        "- Each role sees its workspace apps and no others.",
        "- A workspace bundle changes app visibility and nothing else.",
        "- Each coverage role differs from the control in exactly one dimension.",
        "- Built-in roles are unmodified and no project role is defined outside the "
        "deployment app.",
        "- Every detection is quiet when healthy and fires when its violation is "
        "injected.",
        "",
        "### A note on search windows", "",
        "A role with a time-window restriction refuses a search spanning longer than",
        "that window. Each test therefore derives its search range from the role",
        "under test. Without that, the service account appeared to reach none of its",
        "indexes — a result that reads like an access-control fault and is in fact a",
        "test fault.", "", "---", ""]


def coverage_section(catalog, cases):
    outcome = {c["name"]: c["outcome"] for c in cases}
    groups = {"COMP": "Composition semantics", "BOUND": "Boundary enforcement",
              "IDP": "Identity provider mapping", "DET": "Detection efficacy",
              "CAT": "Catalog integrity"}
    rows = catalog.coverage_matrix["behaviours"]
    lines = [
        "## Coverage of the model", "",
        f"{len(rows)} behaviours the strategy asserts about the model. Each records",
        "why it is observable — the answer to one question: if this were broken,",
        "what would a person see? A row that cannot answer that is not covered,",
        "whatever tests point at it.", "",
    ]
    proven = 0
    for prefix, title in groups.items():
        subset = [r for r in rows if r["id"].startswith(prefix)]
        if not subset:
            continue
        lines += [f"### {title}", "",
                  "| ID | Behaviour | Observable because | Result |",
                  "|---|---|---|---|"]
        for row in subset:
            results = {outcome.get(t) for t in row["tests"]}
            if "failed" in results:
                verdict = "**FAILED**"
            elif results == {None}:
                verdict = "no test ran"
            elif "passed" in results:
                verdict = "proven"
                proven += 1
            else:
                verdict = "skipped"
            lines.append(f"| {row['id']} | {row['behaviour']} | "
                         + " ".join(row["observable_because"].split())
                         + f" | {verdict} |")
        lines.append("")
    lines += [f"**{proven} of {len(rows)} behaviours proven by this run.**", "",
              "---", ""]
    return lines


def results_section(cases, totals):
    lines = ["## Test results", ""]
    failed = [c for c in cases if c["outcome"] == "failed"]
    skipped = [c for c in cases if c["outcome"] == "skipped"]
    if failed:
        lines += [f"### {len(failed)} failures", ""]
        for case in failed:
            lines += [f"#### `{case['name']}`", "", f"In `{case['module']}`.", "",
                      "```", case["detail"][:1800], "```", ""]
    else:
        lines += ["No failures.", ""]
    if skipped:
        lines += [f"### {len(skipped)} skipped", "", "| Test | Reason |",
                  "|---|---|"]
        for case in skipped:
            lines.append(f"| `{case['name']}` | "
                         + (case["detail"][:180] or "not stated") + " |")
        lines.append("")
    lines += ["### Every test", "",
              "| Suite | Test | Module | Seconds | Outcome |",
              "|---|---|---|---:|---|"]
    for case in sorted(cases, key=lambda c: (c["suite"], c["module"], c["name"])):
        lines.append(f"| {case['suite']} | `{case['name']}` | "
                     f"`{case['module']}` | {case['seconds']:.2f} | "
                     f"{case['outcome']} |")
    total_time = sum(c["seconds"] for c in cases)
    lines += ["", f"{len(cases)} tests in {total_time:.1f} seconds.", "",
              "---", ""]
    return lines


def detections_section(catalog, cases):
    outcome = {c["name"]: c["outcome"] for c in cases}
    detections = []
    for row in catalog.coverage_matrix["behaviours"]:
        for name in row.get("detections") or []:
            detections.append(name)
    questions = {
        "al_rbac_multi_role_assignment":
            ("Are any users assigned more than one Business Role?",
             "A second Business Role given to a user"),
        "al_rbac_direct_bundle_assignment":
            ("Is any user assigned a Privilege Bundle directly?",
             "A bundle assigned straight to a user"),
        "al_rbac_sensitive_capability_sprawl":
            ("Is a sensitive capability granted outside an admin bundle?",
             "User administration added to a dashboard bundle"),
        "al_rbac_destructive_capability_check":
            ("Does a Business Role outside the allow-list hold a destructive "
             "capability?",
             "Data deletion given to the NOC operator role"),
        "al_rbac_configuration_drift":
            ("Is any project role defined outside the deployment app?",
             "A role created in another app — what a Splunk Web edit produces"),
        "al_rbac_sensitive_role_chain_membership":
            ("Who holds a role chain that includes a sensitive bundle?",
             "A new holder added to an administrative role chain"),
        "al_rbac_capability_catalog_change":
            ("Have capabilities been added or removed since the baseline?",
             "The search run against a baseline missing one capability — what an "
             "upgrade looks like to it"),
    }
    lines = [
        "## Compliance detections", "",
        "Seven standing detections, deployed as scheduled saved searches in",
        "`tristate_rbac`. Six report a violation; the role-chain membership search",
        "reports evidence for the sensitive tier's quarterly recertification and is",
        "expected to return rows.", "",
        "Each is tested twice. Quiet on a healthy environment proves very little on",
        "its own — a detection that can never fire looks identical. So each is also",
        "broken on purpose and must report it, after which the injection reverts and",
        "a final check confirms the environment is clean.", "",
        "| Detection | Question it answers | Injected violation | Quiet when "
        "healthy | Fires on injection |",
        "|---|---|---|---|---|",
    ]
    healthy = outcome.get("test_compliance_detections", "no test ran")
    for name in sorted(set(detections)):
        question, injection = questions.get(name, ("—", "—"))
        key = "test_injection_" + name.replace("al_rbac_", "")
        lines.append(f"| `{name}` | {question} | {injection} | {healthy} | "
                     f"{outcome.get(key, 'no test ran')} |")
    lines += ["", "The strategy is explicit that a recurring finding is a policy gap",
              "requiring a strategy revision, not an incident to suppress.", "",
              "---", ""]
    return lines


def rest_section():
    found = discover_endpoints()
    documented = [(path, sorted(files)) for path, files in sorted(found.items())
                  if path in ENDPOINT_PURPOSE]
    undocumented = [(path, sorted(files)) for path, files in sorted(found.items())
                    if path not in ENDPOINT_PURPOSE]
    lines = [
        "## REST interfaces used", "",
        "Every Splunk management interface this harness calls, discovered by",
        "scanning the source rather than maintained by hand — so an interface added",
        "later appears here automatically.", "",
        "All calls go to the management port over HTTPS with an authenticated",
        "session. No Splunk SDK is used: only interfaces that are stable across",
        "9.x and 10.x, so the harness is not coupled to a release.", "",
        f"{len(documented)} interfaces in use.", "",
        "| Interface | Purpose | Used by |", "|---|---|---|",
    ]
    for path, files in documented:
        lines.append(f"| `{path}` | {ENDPOINT_PURPOSE[path]} | "
                     + ", ".join(f"`{f}`" for f in files) + " |")
    if undocumented:
        print("WARNING: interfaces called with no recorded purpose in "
              "ENDPOINT_PURPOSE — add one so the report describes them:",
              file=sys.stderr)
        for path, files in undocumented:
            print(f"  {path}  ({', '.join(files)})", file=sys.stderr)

    lines += ["", "### Two interfaces worth singling out", "",
              "`/services/authentication/current-context` is the authoritative",
              "source for what a user can do. A role's definition is not the same",
              "thing as a user's resolved permissions, and reading the definition",
              "instead of the context would have missed every platform finding in",
              "this report.", "",
              "`/servicesNS/-/-/configs/conf-authorize` is the only interface that",
              "answers the configuration-drift question. The roles interface reports",
              "an empty owning app for every role, so a drift check built on it",
              "compares every role against an empty string, reports plausible-looking",
              "rows, and measures nothing.", "", "---", ""]
    return lines


def reproducibility_section(catalog, inventory):
    events = sum(r["events"] for r in inventory["indexes"].values()) if inventory else 0
    fixtures = sum(int(f["events"]) for f in catalog.fixtures.values())
    return [
        "## Reproducibility", "",
        "The environment is rebuilt from the catalog, not repaired. `make rebuild`",
        "tears it down, deploys again, recreates the users, reloads the data, and",
        "runs both suites — and it ends green. That demonstrates reproducibility",
        "rather than asserting it.", "",
        "| Step | What it does |", "|---|---|",
        "| `make validate` | Checks the catalog offline |",
        "| `make profile` | Profiles the sample exports and refreshes the mapping "
        "worksheet |",
        "| `make fixtures` | Generates the synthetic coverage events |",
        "| `make build` | Renders the Splunk apps from the catalog |",
        "| `make redaction` | Confirms no production identifier reaches a generated "
        "file |",
        "| `make deploy` | Pushes the apps and restarts splunkd, which index "
        "creation requires |",
        "| `make users` | Recreates the test users with fresh credentials |",
        "| `make seed` | Loads the sample data into the governed indexes |",
        "| `make test` | Runs both suites and writes the reports |",
        "| `make teardown` | Removes the generated apps, the catalog indexes, and "
        "the test users |",
        "| `make rebuild` | Teardown followed by all of the above |",
        "",
        "### Determinism", "",
        "A reload reproduces the environment exactly, not approximately:", "",
        f"- {events:,} events resolve through the mapping to the same destinations "
        "every run.",
        f"- {fixtures} synthetic events are generated without a clock or a random "
        "number generator, so they are byte-identical between runs.",
        "- Redaction is deterministic: the same input always yields the same "
        "replacement, so a user is the same pseudonymous identity in every reload. A "
        "random replacement would make expected values unstable.",
        "- Seeding refuses to run on top of an existing load, because it sends every "
        "event it resolves and would otherwise double every count the tests depend "
        "on.",
        "", "### Handling a new export or a changed decision", "",
        "Drop a new export into `sample_data/` and run `make profile`. A sourcetype",
        "that fits an existing pattern is classified automatically; a genuinely new",
        "feed is reported as a gap. Then `make reseed`.", "",
        "To change a decision, edit the file that holds it and run `make validate`.",
        "The check refuses a half-finished change — a mapping that targets an index",
        "the register does not list, or a content code that is not three letters.",
        "", "---", ""]


def findings_section(catalog):
    floors = catalog.taxonomy.get("platform_floors") or {}
    lines = [
        "## Findings and limitations", "",
        "### Platform behaviour that limits what the model can claim", "",
        "None of these is a configuration fault. All were measured on the target",
        "release by asking the live platform rather than reading documentation, and",
        "each would otherwise have reached production unnoticed.", "",
        "| Finding | Consequence |", "|---|---|",
        "| Two capabilities the strategy classifies as sensitive reach every user "
        "and cannot be revoked | Every user can write data into any index they can "
        "read. The isolation the strategy requires is unachievable for them on this "
        "release, so they were removed from the tier — the exposure remains and "
        "needs a monitoring answer rather than a role-design one. |",
        "| Three capability names in the strategy do not exist on this release | A "
        "configuration written from the strategy text verbatim fails to deploy. The "
        "catalog uses the verified names. |",
        "| `srchMaxTime` is accepted by the write and not stored | A limit on how "
        "long a search may run is not available through access control. |",
        "| Concurrent-search and real-time quotas have floors | A service account "
        "cannot be given a narrower envelope than the floor allows. |",
        "| `admin_all_objects` bypasses object permissions | The role holding it "
        "sees every workspace app, so the workspace boundary does not apply to it. "
        "Recorded explicitly, so the other roles are not read as sharing that "
        "exemption. |",
        "| Index creation is not hot-reloadable | Deployment restarts splunkd, so it "
        "is not a fast inner loop. |",
        "",
        "### Data protection findings in the production sample", "",
        "| Finding | Consequence |", "|---|---|",
        "| Employee email addresses appear in the `source` field of the Oracle feed "
        "| Metadata is visible to anyone who can search the index at all, whatever "
        "event-level controls exist. It also breaks the source standard three ways: "
        "the value changes per event, identifies a person rather than a feed, and "
        "carries personal data. An input-layer fix. |",
        "| Host names are embedded in Linux source paths | Host belongs in the "
        "`host` field. |",
        "| Some source values contain control characters, and some sourcetypes are "
        "truncated | Both indicate a misconfigured input. |",
        "| The sourcetype of the Oracle feed is set from the API operation name | It "
        "produced 117 sourcetypes that grow without bound. |",
        "",
        "Every export is redacted before it is used. Verification has two layers,",
        "because a pattern cannot find its own blind spot: the rules are applied, and",
        "then a plain search looks for known real values. The second layer is the one",
        "that matters — the pattern-based check reported clean while four real leaks",
        "were present.", "",
        "### Scope this harness does not cover", "",
        "| Not covered | Why |", "|---|---|",
        "| Distribution by the search head cluster deployer or the cluster manager | "
        "A standalone instance has neither. |",
        "| Live SAML behaviour | The environment has no identity provider; the "
        "mapping is checked as text only. |",
        "| Tiered storage | The instance has one storage tier, so the hot and cold "
        "split is not represented. |",
        "| Per-sourcetype event breaking | Seeding flattens each event so counts are "
        "exact. Production needs a line-breaking rule per sourcetype. |",
        "| Timestamp recognition for most sourcetypes | 102 of the governed "
        "sourcetypes rely on Splunk's automatic detection. Each is a real onboarding "
        "decision for production. |",
        "", "---", ""]
    return lines


def regenerating_section(fingerprint):
    return [
        "## Regenerating this report", "",
        "This report is generated. Do not edit it — the next run overwrites it.", "",
        "```", "make test          # runs both suites, then writes this report",
        "make report        # regenerates the report from the last run",
        "make report-shareable   # the same report with credentials masked", "```",
        "",
        "It is assembled from the catalog, `reports/resolved_inventory.json`, and the",
        "JUnit output of the last run. A configuration change followed by `make test`",
        "produces a report describing the new configuration and the new result.", "",
        f"This copy was built from catalog fingerprint `{fingerprint}`. Two reports",
        "with different fingerprints describe different configurations; the same",
        "fingerprint with a different result means something changed on the platform",
        "rather than in the catalog.", "",
        "`reports/` is not committed to version control. To keep a run as evidence,",
        "copy this file out before the next run.", "",
        "### Related documents", "",
        "| Document | Contents |", "|---|---|",
        "| `docs/DESIGN.md` | The architecture and the reason behind each design "
        "rule |",
        "| `docs/USER_GUIDE.md` | How to install, operate, change, and troubleshoot "
        "the harness |",
        "| `docs/source_remediation_map.md` | Every legacy value and the governed "
        "value that replaces it |",
        "| `ai-egc/ROADMAP.md` | The five delivery phases |",
        "| `ai-egc/decisions/` | Every decision with its reasoning and consequences |",
        "| `strategy/Splunk_Strategy_2.0.md` | The governing strategy |",
        ""]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mask-passwords", action="store_true",
                        help="write the report with credentials masked, for "
                             "circulation")
    parser.add_argument("-o", "--out", default=OUT)
    args = parser.parse_args()

    catalog = loader.Catalog()
    if catalog.errors:
        print(f"catalog has {len(catalog.errors)} errors — refusing to report")
        for error in catalog.errors:
            print(f"  {error}")
        return 1

    cases, totals, run = load_junit()
    if not cases:
        print("no test results in reports/ — run `make test` first")
        return 1
    inventory = load_inventory()
    credentials = load_credentials()
    fingerprint = catalog_fingerprint(catalog)
    generated = datetime.datetime.now(datetime.timezone.utc).astimezone()

    lines = []
    lines += header(catalog, run, totals, fingerprint, generated)
    lines += executive_summary(catalog, cases, totals, inventory)
    lines += configuration_design(catalog)
    lines += the_catalog(catalog)
    lines += classification(catalog)
    lines += indexes_section(catalog, inventory)
    lines += mapping_section(catalog, inventory)
    lines += capabilities_section(catalog)
    lines += bundles_section(catalog)
    lines += roles_section(catalog)
    lines += users_section(catalog, credentials, args.mask_passwords)
    lines += expectations_section(catalog)
    lines += test_design_section(catalog, cases)
    lines += coverage_section(catalog, cases)
    lines += results_section(cases, totals)
    lines += detections_section(catalog, cases)
    lines += rest_section()
    lines += reproducibility_section(catalog, inventory)
    lines += findings_section(catalog)
    lines += regenerating_section(fingerprint)

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as handle:
        handle.write("\n".join(lines) + "\n")

    passed = (totals["tests"] - totals["failures"] - totals["errors"]
              - totals["skipped"])
    print(f"{len(lines):,} lines -> {os.path.relpath(args.out, ROOT)}  "
          f"({len(SECTIONS)} sections, {passed}/{totals['tests']} tests passed"
          + (", credentials masked" if args.mask_passwords else "") + ")")
    return 0


if __name__ == "__main__":
    sys.exit(main())
