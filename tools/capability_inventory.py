#!/usr/bin/env python3
"""Capture and diff the Splunk capability catalog.

The strategy defines an upgrade triage process: take a baseline before an
upgrade, take it again afterwards, and decide what to do with each capability
that appeared, disappeared, or was renamed. This tool is that process.

It is not hypothetical. Three capability names the strategy gives do not exist on
Splunk 10.4.1 — `edit_indexes`, `edit_indexes_allinternal`, and `clean_indexes` —
so a bundle built from the strategy text verbatim would fail to deploy. A
baseline taken before writing the bundles found that.

    python -m tools.capability_inventory                 # capture and diff
    python -m tools.capability_inventory --check-catalog # verify catalog names
"""

import argparse
import glob
import json
import os
import sys

from deploy.splunk_api import Splunk, SplunkError
from generators import loader

REPORTS = os.path.join(loader.ROOT, "reports")
BASELINE = os.path.join(REPORTS, "capability_baseline.json")


def capture(splunk):
    """The capability catalog the instance reports right now."""
    entry = splunk.get("/services/authorization/capabilities")["entry"][0]
    return sorted(entry["content"]["capabilities"])


def previous():
    """The most recent dated baseline, or None."""
    dated = sorted(glob.glob(os.path.join(REPORTS,
                                          "capability_baseline_*.json")))
    if not dated:
        return None, None
    with open(dated[-1], encoding="utf-8") as handle:
        return json.load(handle), os.path.basename(dated[-1])


def check_catalog(catalog, caps):
    """Every capability the catalog grants must exist on the target.

    A missing name is not a warning. Splunk rejects the stanza, so the bundle
    would not deploy at all.
    """
    problems = []
    for name, bundle in sorted(catalog.bundle_by_name.items()):
        for capability in bundle.get("capabilities", []):
            if capability not in caps:
                problems.append(f"bundle {name}: capability {capability!r} does "
                                f"not exist on this instance")
    for group in ("sensitive_capabilities", "destructive_capabilities"):
        entries = catalog.taxonomy.get(group) or []
        for capability in entries:
            if capability not in caps:
                problems.append(f"taxonomy {group}: {capability!r} does not "
                                f"exist on this instance")
    return problems


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check-catalog", action="store_true",
                        help="also verify every capability the catalog names")
    parser.add_argument("--save", metavar="LABEL",
                        help="save a dated baseline under this label, for a "
                             "later upgrade diff")
    args = parser.parse_args()

    try:
        splunk = Splunk.from_env()
        info = splunk.server_info()
        caps = capture(splunk)
    except SplunkError as exc:
        print(f"cannot reach Splunk: {exc}")
        return 2

    os.makedirs(REPORTS, exist_ok=True)
    with open(BASELINE, "w", encoding="utf-8") as handle:
        json.dump(caps, handle, indent=1)
    print(f"Splunk {info['version']}: {len(caps)} capabilities "
          f"-> {os.path.relpath(BASELINE, loader.ROOT)}")

    old, label = previous()
    if old is not None:
        added = sorted(set(caps) - set(old))
        removed = sorted(set(old) - set(caps))
        print(f"\ndiff against {label}: {len(added)} added, "
              f"{len(removed)} removed")
        for capability in added:
            print(f"  + {capability}   assign it to a pr_feat_* bundle, or "
                  f"decide that no role gets it")
        for capability in removed:
            print(f"  - {capability}   remove it from every bundle that grants "
                  f"it")
    else:
        print("\nno earlier dated baseline, so no diff. Use --save before an "
              "upgrade.")

    if args.save:
        dated = os.path.join(REPORTS, f"capability_baseline_{args.save}.json")
        with open(dated, "w", encoding="utf-8") as handle:
            json.dump(caps, handle, indent=1)
        print(f"saved {os.path.relpath(dated, loader.ROOT)}")

    if args.check_catalog:
        catalog = loader.Catalog()
        problems = check_catalog(catalog, caps)
        granted = {c for b in catalog.bundle_by_name.values()
                   for c in b.get("capabilities", [])}
        print(f"\ncatalog grants {len(granted)} distinct capabilities of "
              f"{len(caps)} available")
        if problems:
            print(f"{len(problems)} PROBLEMS:")
            for problem in problems:
                print(f"  {problem}")
            return 1
        print("every capability the catalog names exists on this instance")
    return 0


if __name__ == "__main__":
    sys.exit(main())
