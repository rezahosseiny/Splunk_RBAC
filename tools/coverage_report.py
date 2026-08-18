#!/usr/bin/env python3
"""Render the coverage matrix as a document.

The matrix answers one question for each behaviour the strategy asserts: if this
were broken, what would a person see? A row that cannot answer that is not
covered, whatever tests point at it.

    python -m tools.coverage_report
"""

import os
import sys

from generators import loader
from tools import docmeta

OUT = os.path.join(loader.ROOT, "reports", "coverage_matrix.md")


def main():
    catalog = loader.Catalog()
    rows = catalog.coverage_matrix["behaviours"]

    groups = {}
    for row in rows:
        groups.setdefault(row["id"].split("-")[0], []).append(row)

    lines = docmeta.doc_header(
        "RBAC Coverage Matrix",
        "reports/coverage_matrix.md",
        "Every behaviour the RBAC model asserts, what makes each one "
        "observable, and which tests cover it.")
    lines += [
        f"{len(rows)} behaviours, {len(catalog.role_list)} roles, "
        f"{len(catalog.bundle_by_name)} bundles.",
        "",
        "A behaviour is covered only when a wrong answer would be visible. Each",
        "row therefore records why the behaviour is observable, and not merely",
        "which test mentions it.",
        "",
    ]

    titles = {"COMP": "Composition semantics",
              "BOUND": "Boundary enforcement",
              "IDP": "Identity provider mapping",
              "DET": "Detection efficacy",
              "CAT": "Catalog integrity"}

    for prefix, group in groups.items():
        lines += [f"## {titles.get(prefix, prefix)}", ""]
        for row in group:
            lines += [f"### {row['id']} — {row['behaviour']}", ""]
            lines.append(f"**Strategy basis.** {row['strategy_basis']}")
            lines.append("")
            lines.append(f"**Observable because.** "
                         f"{' '.join(row['observable_because'].split())}")
            lines.append("")
            roles = ", ".join(f"`{r}`" for r in row.get("roles", []))
            lines.append(f"**Roles.** {roles or 'not role specific'}")
            lines.append("")
            tests = ", ".join(f"`{t}`" for t in row.get("tests", []))
            lines.append(f"**Tests.** {tests}")
            if row.get("detections"):
                lines.append("")
                lines.append("**Detections.** "
                             + ", ".join(f"`{d}`" for d in row["detections"]))
            if row.get("limitation"):
                lines.append("")
                lines.append(f"**Limitation.** "
                             f"{' '.join(row['limitation'].split())}")
            lines.append("")

    lines += ["## Effective permissions computed from the catalog", "",
              "| role | purpose | indexes | capabilities | jobs | disk | apps |",
              "|---|---|---:|---:|---:|---:|---|"]
    for role in catalog.role_list:
        name = role["name"]
        quotas = catalog.computed_quotas(name)
        apps = ", ".join(catalog.computed_workspace_apps(name)) or "—"
        lines.append(
            f"| `{name}` | {role.get('purpose', '—')} "
            f"| {len(catalog.computed_indexes(name))} "
            f"| {len(catalog.computed_capabilities(name))} "
            f"| {quotas.get('srchJobsQuota', '—')} "
            f"| {quotas.get('srchDiskQuota', '—')} | {apps} |")

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as handle:
        handle.write("\n".join(lines) + "\n")
    print(f"{len(rows)} behaviours -> {os.path.relpath(OUT, loader.ROOT)}")
    uncovered = [r["id"] for r in rows if not r.get("tests")]
    if uncovered:
        print(f"UNCOVERED: {uncovered}")
        return 1
    print("every behaviour names at least one test")
    return 0


if __name__ == "__main__":
    sys.exit(main())
