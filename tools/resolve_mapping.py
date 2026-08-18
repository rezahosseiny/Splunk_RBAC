#!/usr/bin/env python3
"""Apply catalog/mapping.yaml to a Splunk CSV export.

Three jobs:

1. Prove the mapping covers the export. Any (legacy index, sourcetype) pair
   with no matching rule is reported as a gap — that is how a new production
   export surfaces feeds nobody has classified yet.
2. Derive the governed index catalog (which governed indexes exist, what lands
   in each, how many events) and validate every governed name against the
   taxonomy and the strategy's naming rules.
3. Emit the durable remediation document. Redaction rules from
   catalog/redaction.yaml are applied first, then legacy values are collapsed
   into patterns — which is what remediation acts on, and which keeps per-run
   identifiers out of the document. Writing is refused if any redaction target
   survives.

    python -m tools.resolve_mapping sample_data/Splunk_Sample_data.csv
"""

import argparse
import collections
import csv
import fnmatch
import json
import os
import re
import sys

import yaml

from tools import redact

CATALOG = os.path.join(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))), "catalog")

INDEX_NAME_RE = re.compile(
    r"^(?P<cls>[a-z]{3})_(?P<compliance>[a-z]{3})_(?P<domain>[a-z]{3})_"
    r"(?P<content>[a-z]{3})(?:_(?P<detail>[a-z0-9_]+?))?_(?P<retention>[sml])$"
)
TAG_RE = re.compile(r"^[a-z0-9_\-\.]+(?::[a-z0-9_\-\.]+)*$")
MAX_TAGS = 5


def collapse(value):
    """Reduce a value to its stable pattern, redaction rules first."""
    return redact.default().collapse(value)


def check_sanitized(text):
    """Return a list of redaction targets that survived in document text."""
    return redact.default().audit(text)


def load(name):
    with open(os.path.join(CATALOG, name), encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def slug(value):
    """Lowercase and reduce to characters the tag format permits."""
    value = re.sub(r"[^a-z0-9_.\-]+", "_", value.lower())
    return re.sub(r"[_\-]{2,}", "_", value).strip("_.-")


def render(template, sourcetype, source):
    """Expand the mapping templates."""
    return (template
            .replace("{tail_lower}", sourcetype.rsplit(":", 1)[-1].lower())
            .replace("{st_lower}", sourcetype.lower())
            .replace("{src_tail_lower}", source.rsplit(":", 1)[-1].lower())
            .replace("{src_lower}", source.lower())
            .replace("{src_tail_slug}", slug(source.rsplit(":", 1)[-1]))
            .replace("{src_slug}", slug(source)))


def match_rule(mapping, legacy_index, sourcetype):
    """Return the first rule whose glob matches, or None."""
    entry = mapping["legacy_indexes"].get(legacy_index)
    if not entry:
        return None
    for rule in entry.get("rules", []):
        if fnmatch.fnmatchcase(sourcetype, rule["match"]):
            return rule
    return None


def resolve(csv_path, mapping):
    """Walk the export, applying the mapping. Returns results and gaps."""
    csv.field_size_limit(sys.maxsize)
    governed = collections.defaultdict(lambda: {
        "events": 0,
        "sourcetypes": collections.Counter(),
        "sources": collections.Counter(),
        "from_legacy": collections.Counter(),
    })
    gaps = collections.Counter()
    remediation = collections.defaultdict(set)
    quarantined = collections.Counter()

    with open(csv_path, newline="", encoding="utf-8", errors="replace") as fh:
        for row in csv.DictReader(fh):
            legacy_index = (row.get("index") or "").strip()
            if not legacy_index:
                continue
            legacy_st = (row.get("sourcetype") or "").strip()
            legacy_src = (row.get("source") or "").strip()

            rule = match_rule(mapping, legacy_index, legacy_st)
            if rule is None:
                gaps[(legacy_index, legacy_st)] += 1
                continue

            index = rule["index"]
            sourcetype = render(rule["sourcetype"], legacy_st, legacy_src)
            source = render(rule["source"], legacy_st, legacy_src)

            bucket = governed[index]
            bucket["events"] += 1
            bucket["sourcetypes"][sourcetype] += 1
            bucket["sources"][source] += 1
            bucket["from_legacy"][legacy_index] += 1

            remediation[(legacy_index, collapse(legacy_st),
                         collapse(legacy_src))].add((index, sourcetype, source))
            if rule.get("quarantine_reason"):
                quarantined[(legacy_index, legacy_st,
                             rule["quarantine_reason"])] += 1

    return governed, gaps, remediation, quarantined


def validate_names(governed, mapping, taxonomy):
    """Check every governed index name, sourcetype, and source.

    A registered naming exception excuses the index NAME only. Sourcetypes and
    sources are always checked, because nothing about a vendor-mandated index
    name excuses a malformed source value written into it.
    """
    problems = []
    exempt = {name for name, entry in mapping["legacy_indexes"].items()
              if entry.get("naming_exception")}

    for index, bucket in sorted(governed.items()):
        if index not in exempt:
            match = INDEX_NAME_RE.match(index)
            if not match:
                problems.append(
                    f"index {index}: does not match the naming schema")
            else:
                for field, table in (("cls", "classes"),
                                     ("compliance", "compliance"),
                                     ("domain", "domains"),
                                     ("content", "content")):
                    code = match.group(field)
                    if code not in taxonomy[table]:
                        problems.append(
                            f"index {index}: {field} code '{code}' not "
                            f"registered in taxonomy.{table}")
                if match.group("retention") not in taxonomy["retention"]:
                    problems.append(f"index {index}: unknown retention suffix")

        for sourcetype in bucket["sourcetypes"]:
            if sourcetype == "stash":
                continue  # vendor-mandated for summary indexing
            if not TAG_RE.match(sourcetype):
                problems.append(
                    f"sourcetype {sourcetype}: not lowercase tag:tag:tag")
            if sourcetype.count(":") + 1 > MAX_TAGS:
                problems.append(
                    f"sourcetype {sourcetype}: exceeds {MAX_TAGS} tags")
        for source in bucket["sources"]:
            if not TAG_RE.match(source):
                problems.append(f"source {source}: not lowercase tag:tag:tag")
            if source.count(":") + 1 > MAX_TAGS:
                problems.append(f"source {source}: exceeds {MAX_TAGS} tags")
    return problems


def write_remediation(remediation, quarantined, csv_path, out_path):
    """The durable, accumulating legacy-to-governed remediation record."""
    lines = [
        "# Source, sourcetype, and index remediation map",
        "",
        "Legacy values as they exist in production, mapped to the governed",
        "values the strategy requires. This is the work list for bringing the",
        "real estate into conformance — each row is an input-layer change.",
        "",
        "Ephemeral fragments are collapsed into patterns (`{guid}`,",
        "`{timestamp}`, `{digits}`, `{hash}`): the pattern is what gets fixed,",
        "and collapsing keeps per-run identifiers out of this document.",
        "",
        f"Generated from `{csv_path}` by `tools/resolve_mapping.py`.",
        f"Rows: {len(remediation)}.",
        "",
        "| legacy index | legacy sourcetype | legacy source | "
        "governed index | governed sourcetype | governed source |",
        "|---|---|---|---|---|---|",
    ]
    for (legacy_index, legacy_st, legacy_src) in sorted(remediation):
        for (index, sourcetype, source) in sorted(
                remediation[(legacy_index, legacy_st, legacy_src)]):
            lines.append(
                f"| `{legacy_index}` | `{legacy_st}` | `{legacy_src}` "
                f"| `{index}` | `{sourcetype}` | `{source}` |")

    if quarantined:
        lines += [
            "",
            "## Quarantined — upstream defects to fix",
            "",
            "These values could not be classified and are routed to the",
            "quarantine index. Each is a genuine defect in the input",
            "configuration, not a naming choice.",
            "",
            "| legacy index | legacy sourcetype | events | reason |",
            "|---|---|---:|---|",
        ]
        for (legacy_index, legacy_st, reason), count in sorted(
                quarantined.items()):
            lines.append(
                f"| `{legacy_index}` | `{legacy_st}` | {count} | {reason} |")

    text = "\n".join(lines) + "\n"
    leaks = check_sanitized(text)
    if leaks:
        raise SystemExit(
            "refusing to write " + out_path + ": identifiers survived "
            "collapsing, so the document is not safe to commit:\n  "
            + "\n  ".join(leaks))

    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as handle:
        handle.write(text)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv_path")
    parser.add_argument("-o", "--out", default="docs/source_remediation_map.md")
    args = parser.parse_args()

    mapping = load("mapping.yaml")
    taxonomy = load("taxonomy.yaml")
    governed, gaps, remediation, quarantined = resolve(args.csv_path, mapping)
    problems = validate_names(governed, mapping, taxonomy)

    total = sum(b["events"] for b in governed.values())
    dropped = sum(gaps.values())
    print(f"{args.csv_path}: {total:,} events mapped into "
          f"{len(governed)} governed indexes, {dropped:,} unmapped\n")

    print(f"{'governed index':26s} {'events':>7s} {'st':>3s} {'src':>4s}  "
          f"from legacy")
    for index in sorted(governed):
        bucket = governed[index]
        legacy = ",".join(sorted(bucket["from_legacy"]))
        print(f"{index:26s} {bucket['events']:7,d} "
              f"{len(bucket['sourcetypes']):3d} {len(bucket['sources']):4d}  "
              f"{legacy[:44]}")

    if gaps:
        print(f"\nMAPPING GAPS ({len(gaps)} pairs, {dropped:,} events):")
        for (legacy_index, legacy_st), count in gaps.most_common(30):
            print(f"  {count:6,d}  index={legacy_index} sourcetype={legacy_st}")
    else:
        print("\nMapping gaps: none — every value in the export is classified.")

    if problems:
        print(f"\nNAMING PROBLEMS ({len(problems)}):")
        for problem in problems[:30]:
            print(f"  {problem}")
    else:
        print("Naming validation: clean.")

    inventory = {
        "source_export": args.csv_path,
        "indexes": {
            index: {
                "events": bucket["events"],
                "sourcetypes": sorted(bucket["sourcetypes"]),
                "sources": sorted(bucket["sources"]),
                "from_legacy": sorted(bucket["from_legacy"]),
            }
            for index, bucket in sorted(governed.items())
        },
    }
    os.makedirs(os.path.join(os.path.dirname(CATALOG), "reports"),
                exist_ok=True)
    inv_path = os.path.join(os.path.dirname(CATALOG), "reports",
                            "resolved_inventory.json")
    with open(inv_path, "w", encoding="utf-8") as handle:
        json.dump(inventory, handle, indent=1, sort_keys=True)
    print(f"Resolved inventory written to "
          f"{os.path.relpath(inv_path, os.path.dirname(CATALOG))}")

    write_remediation(remediation, quarantined, args.csv_path, args.out)
    print(f"\nRemediation map written to {args.out} "
          f"({len(remediation)} patterns)")
    return 1 if (gaps or problems) else 0


if __name__ == "__main__":
    sys.exit(main())
