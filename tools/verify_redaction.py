#!/usr/bin/env python3
"""Verify that no production identifier reaches a generated file.

Two independent layers, because they fail differently:

1. **Rule audit.** Applies the patterns in catalog/redaction.yaml. Detects that
   redaction did not run, or ran and left a value outside the reserved range its
   rule replaces into.
2. **Forbidden-literal search.** Plain substring search for known-real values.
   This is the layer that matters: a rule's own pattern cannot detect its own
   blind spot. When this project's pattern-based audit first reported "clean",
   a literal search found four live leaks — Kerberos machine accounts carrying
   '$', host labels containing '_', GUIDs preceded by '_' where no word boundary
   exists, and JSON nested inside a JSON string. Keep this layer.

Scope: generated documents and governance records. The files that *define* the
rules — catalog/redaction.yaml and tools/redact.py — are excluded, because they
necessarily contain the patterns and the internal domain name they protect;
flagging them would train the reader to ignore this report.

    python -m tools.verify_redaction              # check generated files
    python -m tools.verify_redaction --csv sample_data/export.csv
"""

import argparse
import csv
import glob
import os
import sys

from tools import redact

# Files that define the rules, so they legitimately contain rule text.
EXCLUDED = {
    os.path.join("catalog", "redaction.yaml"),
    os.path.join("tools", "redact.py"),
    os.path.join("tools", "verify_redaction.py"),
}

TARGET_GLOBS = [
    "docs/*.md",
    "reports/*.md",
    "catalog/*.yaml",
    "ai-egc/**/*.md",
    "*.md",
]


def target_files():
    seen = []
    for pattern in TARGET_GLOBS:
        for path in sorted(glob.glob(pattern, recursive=True)):
            normalised = os.path.normpath(path)
            if normalised not in EXCLUDED and normalised not in seen:
                seen.append(normalised)
    return seen


def check_files(redactor):
    """Audit every generated document. Returns a list of (path, findings)."""
    findings = []
    for path in target_files():
        with open(path, encoding="utf-8", errors="replace") as handle:
            text = handle.read()
        leaks = redactor.audit(text, include_document_patterns=False)
        if leaks:
            findings.append((path, leaks))
    return findings


def check_export(redactor, csv_path):
    """Redact a whole export and confirm nothing survives, event by event."""
    csv.field_size_limit(sys.maxsize)
    with open(csv_path, newline="", encoding="utf-8", errors="replace") as fh:
        rows = [row.get("_raw") or "" for row in csv.DictReader(fh)]

    for raw in rows:                        # pass 1: learn the corpus
        redactor.learn(raw)

    findings = []
    for index, raw in enumerate(rows):      # pass 2: redact and audit
        redacted = redactor.redact_event(raw)
        leaks = redactor.audit(redacted, include_document_patterns=False)
        if leaks:
            findings.append((f"{csv_path} event {index}", leaks))
    return len(rows), findings


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv", action="append", default=[],
                        help="also verify a full export, event by event")
    args = parser.parse_args()

    redactor = redact.default()
    print(f"redaction: email mode={redactor.mode}, "
          f"{len([r for r in redactor.rules if redactor._on(r)])} rules enabled, "
          f"{len(redactor.forbidden_literals)} forbidden literals")

    findings = check_files(redactor)
    print(f"generated files: {len(target_files())} checked, "
          f"{len(findings)} with findings")

    for csv_path in args.csv:
        count, export_findings = check_export(redactor, csv_path)
        print(f"{csv_path}: {count:,} events checked, "
              f"{len(export_findings)} with findings")
        findings.extend(export_findings[:20])

    if findings:
        print("\nFINDINGS — treat each as a redaction defect, not as a reason "
              "to extend the literal list:")
        for where, leaks in findings:
            print(f"  {where}")
            for leak in leaks:
                print(f"      {leak}")
        return 1

    print("\nclean — no production identifier found in any checked file.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
