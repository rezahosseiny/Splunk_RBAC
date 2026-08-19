#!/usr/bin/env python3
"""Turn the JUnit XML into a report a person can read.

The suite's own output is a pass count. This says which behaviours were proven,
which detections were shown to fire, and what the recorded platform limits are —
because the reason for running the suite is evidence, not a green tick.

    python -m tools.test_report
"""

import glob
import os
import sys
import xml.etree.ElementTree as ET

from generators import loader
from tools import docmeta

REPORTS = os.path.join(loader.ROOT, "reports")
OUT = os.path.join(REPORTS, "test_summary.md")


def read_junit():
    """Collect every case from every JUnit file in reports/."""
    cases = []
    for path in sorted(glob.glob(os.path.join(REPORTS, "junit-*.xml"))):
        suite = os.path.basename(path)[6:-4]
        for case in ET.parse(path).getroot().iter("testcase"):
            outcome = "passed"
            detail = ""
            for child in case:
                if child.tag in ("failure", "error"):
                    outcome = "failed"
                    detail = (child.get("message") or "").strip()
                elif child.tag == "skipped":
                    outcome = "skipped"
                    detail = (child.get("message") or "").strip()
            cases.append({
                "suite": suite,
                "name": case.get("name"),
                "file": (case.get("classname") or "").replace(".", "/"),
                "time": float(case.get("time") or 0),
                "outcome": outcome,
                "detail": detail,
            })
    return cases


def main():
    catalog = loader.Catalog()
    cases = read_junit()
    if not cases:
        print(f"no JUnit output in {os.path.relpath(REPORTS, loader.ROOT)} — "
              f"run `make test` first")
        return 1

    by_outcome = {o: [c for c in cases if c["outcome"] == o]
                  for o in ("passed", "failed", "skipped")}
    lines = docmeta.doc_header(
        "RBAC Test Summary",
        "reports/test_summary.md",
        "Result of the static and behavioural suites: what was proven, which "
        "detections were shown to fire, and the platform limits that bound the "
        "result.")
    lines += [
        f"**{len(by_outcome['passed'])} passed, "
        f"{len(by_outcome['failed'])} failed, "
        f"{len(by_outcome['skipped'])} skipped** "
        f"across {len({c['suite'] for c in cases})} suites.",
        "",
    ]

    if by_outcome["failed"]:
        lines += ["## Failures", ""]
        for case in by_outcome["failed"]:
            lines += [f"### {case['name']}", "",
                      f"`{case['file']}`", "", "```",
                      case["detail"][:1500], "```", ""]
    else:
        lines += ["No failures.", ""]

    if by_outcome["skipped"]:
        lines += ["## Skipped, and why", "",
                  "| test | reason |", "|---|---|"]
        for case in by_outcome["skipped"]:
            lines.append(f"| `{case['name']}` | "
                         f"{case['detail'][:160] or 'not stated'} |")
        lines.append("")

    lines += ["## Behaviours proven", "",
              "Each row is a behaviour the strategy asserts. `covered by` names "
              "the tests that make a wrong answer visible.", "",
              "| id | behaviour | result |", "|---|---|---|"]
    names = {c["name"]: c["outcome"] for c in cases}
    for row in catalog.coverage_matrix["behaviours"]:
        outcomes = {names.get(t) for t in row["tests"]}
        if "failed" in outcomes:
            result = "**FAILED**"
        elif outcomes == {None}:
            result = "no test ran"
        elif "skipped" in outcomes and "passed" not in outcomes:
            result = "skipped"
        else:
            result = "proven"
        lines.append(f"| {row['id']} | {row['behaviour']} | {result} |")
    lines.append("")

    lines += ["## Detections", "",
              "Each detection must be quiet on a healthy environment AND fire "
              "when its violation is injected. A detection that cannot fire is "
              "indistinguishable from one with nothing to find.", "",
              "| detection | quiet when healthy | fires on injection |",
              "|---|---|---|"]
    for name in sorted(d for d in _detection_names(catalog)):
        healthy = names.get("test_compliance_detections", "no test ran")
        injection = names.get(
            "test_injection_" + name.replace("al_rbac_", ""), "no test ran")
        lines.append(f"| `{name}` | {healthy} | {injection} |")
    lines.append("")

    floors = catalog.taxonomy.get("platform_floors") or {}
    lines += ["## Platform limits that bound this result", "",
              f"Measured on {floors.get('measured_on', 'unknown')} on "
              f"{floors.get('measured_date', 'unknown')}. These are not test "
              "failures; they are limits the platform imposes, recorded so the "
              "result is read correctly.", ""]
    for capability, detail in sorted((floors.get("capabilities") or {}).items()):
        note = " ".join((detail or {}).get("note", "").split())
        lines.append(f"- `{capability}` reaches every role regardless of "
                     f"configuration." + (f" {note}" if note else ""))
    for key, value in sorted((floors.get("quota_minimums") or {}).items()):
        lines.append(f"- `{key}` cannot be set below {value} for a positive "
                     f"value.")
    for key, note in sorted((floors.get("unsupported_attributes")
                             or {}).items()):
        lines.append(f"- `{key}` is not stored on this release. "
                     f"{' '.join(note.split())}")
    lines.append("")

    os.makedirs(REPORTS, exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as handle:
        handle.write("\n".join(lines) + "\n")
    print(f"{len(cases)} cases: {len(by_outcome['passed'])} passed, "
          f"{len(by_outcome['failed'])} failed, "
          f"{len(by_outcome['skipped'])} skipped "
          f"-> {os.path.relpath(OUT, loader.ROOT)}")
    return 1 if by_outcome["failed"] else 0


def _detection_names(catalog):
    for row in catalog.coverage_matrix["behaviours"]:
        for name in row.get("detections") or []:
            yield name


if __name__ == "__main__":
    sys.exit(main())
