#!/usr/bin/env python3
"""Deploy the generated apps through the management API.

Why this exists: the strategy's deployment path is a filesystem sync into the
app directory, which `deploy/deploy.sh` does. On a host where the app directory
belongs to the splunk user and no elevation is available, that path is closed.
This one pushes exactly the same generated stanzas through the API and lets
splunkd do the writing, needing only admin credentials (ADR-011).

It is not the Splunk Web UI, and it is not a path the strategy prohibits: each
stanza is written into the named app's own local directory, never into
etc/system/local, and the catalog stays the source of truth.

Idempotent: an existing stanza is updated in place, a new one created, and a
stanza no longer generated is reported (`--prune` removes it).

    python -m deploy.deploy_rest [--prune] [--dry-run]
"""

import argparse
import glob
import os
import sys
import urllib.parse

from deploy.splunk_api import Splunk, SplunkError, load_settings
from generators import loader

ROOT = loader.ROOT
BUILD_DIR = os.path.join(ROOT, "build", "apps")

# Attributes the indexes endpoint rejects or manages itself.
SKIP_KEYS = {"disabled"}


def parse_conf(path):
    """Parse a Splunk .conf file into {stanza: {key: value}}.

    Hand-written rather than configparser: Splunk conf allows characters in keys
    and values that configparser mangles, and continuation lines that it does
    not understand.
    """
    stanzas, current = {}, None
    with open(path, encoding="utf-8") as handle:
        pending = ""
        for raw in handle:
            line = raw.rstrip("\n")
            if pending:
                line = pending + line.lstrip()
                pending = ""
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            if line.endswith("\\"):
                pending = line[:-1]
                continue
            if stripped.startswith("[") and stripped.endswith("]"):
                current = stripped[1:-1]
                stanzas.setdefault(current, {})
                continue
            if current is None or "=" not in stripped:
                continue
            key, _, value = stripped.partition("=")
            stanzas[current][key.strip()] = value.strip()
    return stanzas


def ensure_app(splunk, app, dry_run):
    """Create the app if it is absent, so its namespace exists."""
    if app in splunk.app_names():
        return False
    if dry_run:
        print(f"  would create app {app}")
        return True
    splunk.post("/services/apps/local", data={"name": app,
                                              "visible": "false"})
    print(f"  created app {app}")
    return True


def upsert(splunk, app, conf_name, stanza, values, existing, dry_run):
    """Create or update one stanza in one conf file inside the app namespace."""
    base = (f"/servicesNS/nobody/{urllib.parse.quote(app)}"
            f"/configs/conf-{urllib.parse.quote(conf_name)}")
    payload = {k: v for k, v in values.items() if k not in SKIP_KEYS}
    if dry_run:
        print(f"  would {'update' if stanza in existing else 'create'} "
              f"[{stanza}] in {conf_name}.conf ({len(payload)} attributes)")
        return
    if stanza in existing:
        splunk.post(f"{base}/{urllib.parse.quote(stanza, safe='')}",
                    data=payload)
    else:
        splunk.post(base, data={"name": stanza, **payload})


def existing_stanzas(splunk, app, conf_name):
    path = (f"/servicesNS/nobody/{urllib.parse.quote(app)}"
            f"/configs/conf-{urllib.parse.quote(conf_name)}")
    try:
        result = splunk.get(path, params={"count": 0})
    except SplunkError:
        return set()
    return {entry["name"] for entry in result.get("entry", [])}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true",
                        help="report what would change and send nothing")
    parser.add_argument("--prune", action="store_true",
                        help="remove deployed stanzas the catalog no longer "
                             "generates")
    args = parser.parse_args()

    if not os.path.isdir(BUILD_DIR):
        print("no build output — run `make build` first")
        return 1

    settings = load_settings()
    wanted_apps = settings["deployment"]["apps"]

    try:
        splunk = Splunk.from_env()
        info = splunk.server_info()
    except SplunkError as exc:
        print(f"cannot reach Splunk: {exc}")
        return 2
    print(f"target: Splunk {info['version']} ({info['server_name']})")

    changed = 0
    for app in wanted_apps:
        app_build = os.path.join(BUILD_DIR, app)
        if not os.path.isdir(app_build):
            print(f"{app}: not generated, skipping")
            continue
        print(f"{app}:")
        ensure_app(splunk, app, args.dry_run)

        for conf_path in sorted(glob.glob(os.path.join(app_build, "local",
                                                       "*.conf"))):
            conf_name = os.path.splitext(os.path.basename(conf_path))[0]
            stanzas = parse_conf(conf_path)
            existing = set() if args.dry_run else existing_stanzas(
                splunk, app, conf_name)
            for stanza, values in sorted(stanzas.items()):
                if not values:
                    continue        # an empty stanza carries no attributes yet
                upsert(splunk, app, conf_name, stanza, values, existing,
                       args.dry_run)
                changed += 1
            print(f"  {conf_name}.conf: {len(stanzas)} stanzas")

            orphans = sorted(existing - set(stanzas) - {"default"})
            if orphans:
                label = "removing" if args.prune else "orphaned (use --prune)"
                print(f"  {label}: {len(orphans)} stanzas no longer generated")
                for stanza in orphans:
                    print(f"    {stanza}")
                    if args.prune and not args.dry_run:
                        splunk.delete(
                            f"/servicesNS/nobody/{urllib.parse.quote(app)}"
                            f"/configs/conf-{urllib.parse.quote(conf_name)}"
                            f"/{urllib.parse.quote(stanza, safe='')}")

    if args.dry_run:
        print(f"\ndry run: {changed} stanzas would be written")
        return 0

    catalog = loader.Catalog()
    live = splunk.index_names()
    expected = set(catalog.index_by_name)
    absent = sorted(expected - live)
    print(f"\nindexes: {len(expected & live)} of {len(expected)} present")
    if absent:
        print("not yet present (indexing config may need a restart to take "
              "effect):")
        for name in absent[:12]:
            print(f"  {name}")
        if len(absent) > 12:
            print(f"  ... and {len(absent) - 12} more")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
