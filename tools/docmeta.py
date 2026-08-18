#!/usr/bin/env python3
"""The standard document header, shared by every generated document.

The repository standard requires six fields on every document. Generating them
from one place keeps the generated documents inside the standard, and keeps the
author attribution correct without anyone editing output by hand.
"""

import datetime
import os

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def doc_header(document, location, covers, status="Generated"):
    """The standard document header. Every document in this repository has one.

    Generated documents emit it from code, so a regeneration cannot drop it.
    Last Updated comes from the input the document is derived from, not from the
    clock: the document changes only when its input changes.
    """
    return [
        f"# {document}",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| **Document** | {document} |",
        f"| **Location in Repo** | `{location}` |",
        "| **Author** | Reza Hosseiny |",
        f"| **Status** | {status} |",
        f"| **Last Updated** | {stamp()} |",
        f"| **Covers** | {covers} |",
        "",
    ]


def stamp():
    """Date of the newest catalog or sample input, not the current time."""
    newest = 0
    for folder in ("catalog", "sample_data"):
        base = os.path.join(ROOT_DIR, folder)
        for name in sorted(os.listdir(base)) if os.path.isdir(base) else []:
            path = os.path.join(base, name)
            if os.path.isfile(path):
                newest = max(newest, os.path.getmtime(path))
    return datetime.datetime.fromtimestamp(
        newest or 0, tz=datetime.timezone.utc).strftime("%Y-%m-%d")
