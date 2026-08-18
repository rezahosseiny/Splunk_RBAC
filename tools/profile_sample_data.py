#!/usr/bin/env python3
"""Profile a Splunk CSV export into a mapping worksheet.

Facts only: this tool never proposes governance decisions. It reports what a
sample export actually contains and which strategy standards each value
violates, so the mapping decisions can be made from a compact worksheet
instead of raw CSV.

Re-runnable: point it at any export with columns index, source, sourcetype,
_time, _raw (extra columns ignored).

Redaction rules from catalog/redaction.yaml are applied to every value this
tool emits, and writing is refused if an email address survives. Hostnames are
left intact here: this worksheet is the diagnostic view and stays gitignored,
unlike docs/source_remediation_map.md.

    python -m tools.profile_sample_data sample_data/Splunk_Sample_data.csv \
        -o reports/mapping_worksheet.md
"""

import argparse
import collections
import csv
import os
import re
import sys

from tools import docmeta, redact

# Strategy: sourcetype/source are tag:tag:tag, max 5 tags, all lower case.
TAG_RE = re.compile(r"^[a-z0-9_\-\.]+(?::[a-z0-9_\-\.]+)*$")
MAX_TAGS = 5

# Values that change per instance/run are prohibited in source and sourcetype.
EPHEMERAL_PATTERNS = [
    ("bare_port", re.compile(r"^(?:udp|tcp):\d+$")),
    ("guid", re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-"
                        r"[0-9a-f]{4}-[0-9a-f]{12}", re.I)),
    ("timestamp", re.compile(r"\d{14}")),
    ("long_digit_run", re.compile(r"\d{9,}")),
    ("abs_path", re.compile(r"^/(?:opt|var|etc|home)/")),
    ("url", re.compile(r"^https?://")),
]


def violations(value, kind):
    """Return the list of standard violations for one source/sourcetype."""
    found = []
    if value != value.lower():
        found.append("not_lowercase")
    if not TAG_RE.match(value):
        found.append("not_tag_format")
    if value.count(":") + 1 > MAX_TAGS:
        found.append(f"over_{MAX_TAGS}_tags")
    if ":" not in value and kind == "sourcetype":
        found.append("single_tag")
    for name, pattern in EPHEMERAL_PATTERNS:
        if pattern.search(value):
            found.append(f"ephemeral:{name}")
    return found


def profile(path):
    """Read the export and return per-index profiles plus totals."""
    csv.field_size_limit(sys.maxsize)
    events = collections.Counter()
    sourcetypes = collections.defaultdict(collections.Counter)
    sources = collections.defaultdict(collections.Counter)
    times = []

    with open(path, newline="", encoding="utf-8", errors="replace") as handle:
        reader = csv.DictReader(handle)
        missing = {"index", "source", "sourcetype"} - set(reader.fieldnames or [])
        if missing:
            raise SystemExit(f"{path}: missing required columns: {sorted(missing)}")
        for row in reader:
            index = (row.get("index") or "").strip()
            if not index:
                continue
            events[index] += 1
            sourcetypes[index][(row.get("sourcetype") or "").strip()] += 1
            sources[index][(row.get("source") or "").strip()] += 1
            if row.get("_time"):
                times.append(row["_time"])

    indexes = []
    for index in sorted(events):
        st_rows = [
            {"value": v, "count": n, "violations": violations(v, "sourcetype")}
            for v, n in sorted(sourcetypes[index].items(), key=lambda kv: -kv[1])
        ]
        src_rows = [
            {"value": v, "count": n, "violations": violations(v, "source")}
            for v, n in sorted(sources[index].items(), key=lambda kv: -kv[1])
        ]
        indexes.append({
            "index": index,
            "events": events[index],
            "sourcetypes": st_rows,
            "sources": src_rows,
            "clean_sourcetypes": sum(1 for r in st_rows if not r["violations"]),
            "clean_sources": sum(1 for r in src_rows if not r["violations"]),
        })

    return {
        "path": path,
        "total_events": sum(events.values()),
        "time_min": min(times) if times else None,
        "time_max": max(times) if times else None,
        "indexes": indexes,
    }


def write_worksheet(data, out_path):
    """Emit the full worksheet: one section per legacy index.

    Values are redacted on the way out (catalog/redaction.yaml). Analysis above
    ran on the originals, so violation detection is unaffected.
    """
    r = redact.default()
    lines = docmeta.doc_header(
        "Sample Data Mapping Worksheet",
        "reports/mapping_worksheet.md",
        "What one production sample export contains, and which naming standards "
        "each value does not obey. Facts only, no decisions.")
    lines += [
        "Mapping decisions are in `catalog/mapping.yaml`. This document records",
        "only what the export contains.",
        "",
        f"- Source export: `{data['path']}`",
        f"- Events: {data['total_events']:,}",
        f"- Time range: {data['time_min']} .. {data['time_max']}",
        f"- Distinct legacy indexes: {len(data['indexes'])}",
        "",
        "## Summary",
        "",
        "| legacy index | events | sourcetypes | clean st | sources | clean src |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for entry in data["indexes"]:
        lines.append(
            f"| `{entry['index']}` | {entry['events']:,} "
            f"| {len(entry['sourcetypes'])} | {entry['clean_sourcetypes']} "
            f"| {len(entry['sources'])} | {entry['clean_sources']} |"
        )

    for entry in data["indexes"]:
        lines += ["", f"## `{entry['index']}` — {entry['events']:,} events", ""]
        lines.append("### sourcetypes")
        lines.append("")
        lines.append("| sourcetype | events | violations |")
        lines.append("|---|---:|---|")
        for row in entry["sourcetypes"]:
            flags = ", ".join(row["violations"]) or "—"
            lines.append(f"| `{r.redact(row['value'])}` | {row['count']:,} | {flags} |")
        lines.append("")
        lines.append("### sources")
        lines.append("")
        lines.append("| source | events | violations |")
        lines.append("|---|---:|---|")
        for row in entry["sources"][:25]:
            flags = ", ".join(row["violations"]) or "—"
            lines.append(f"| `{r.redact(row['value'])}` | {row['count']:,} | {flags} |")
        if len(entry["sources"]) > 25:
            lines.append(f"| _… {len(entry['sources']) - 25} more sources_ | | |")

    text = "\n".join(lines) + "\n"
    leaks = r.audit(text, include_document_patterns=False)
    if leaks:
        raise SystemExit(f"refusing to write {out_path}: " + "; ".join(leaks))

    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as handle:
        handle.write(text)


def print_summary(data):
    """Compact stdout summary — the review surface."""
    redactor = redact.default()
    print(f"{data['path']}: {data['total_events']:,} events, "
          f"{len(data['indexes'])} indexes, "
          f"{data['time_min']} .. {data['time_max']}")
    print(f"{'legacy index':22s} {'events':>7s} {'st':>4s} {'ok':>4s} "
          f"{'src':>5s} {'ok':>4s}  top sourcetypes")
    for entry in data["indexes"]:
        top = ", ".join(redactor.redact(row["value"])
                       for row in entry["sourcetypes"][:3])
        print(f"{entry['index']:22s} {entry['events']:7,d} "
              f"{len(entry['sourcetypes']):4d} {entry['clean_sourcetypes']:4d} "
              f"{len(entry['sources']):5d} {entry['clean_sources']:4d}  {top[:60]}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv_path", help="Splunk CSV export to profile")
    parser.add_argument("-o", "--out", default="reports/mapping_worksheet.md",
                        help="worksheet output path")
    args = parser.parse_args()

    data = profile(args.csv_path)
    write_worksheet(data, args.out)
    print_summary(data)
    print(f"\nWorksheet written to {args.out}")


if __name__ == "__main__":
    main()
