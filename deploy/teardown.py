#!/usr/bin/env python3
"""Return the instance to a clean slate.

Scoped by the catalog: it removes the apps this project generates, the indexes
the catalog defines, and the users the catalog declares. It never touches Splunk
internal indexes, built-in roles, or anything the catalog does not name — so a
teardown cannot reach beyond this project's own footprint.

Reproducibility depends on this working: `make rebuild` is teardown plus the
whole chain, and if that ends green from a clean instance then reproducibility is
demonstrated rather than asserted (ADR-007).

    python -m deploy.teardown --yes [--keep-apps]
"""

import argparse
import sys
import urllib.parse

from deploy.splunk_api import (Splunk, SplunkError, load_env,
                               load_settings)
from generators import loader

PROTECTED_PREFIXES = ("_",)          # _internal, _audit, _introspection, ...
PROTECTED_ROLES = {"admin", "power", "user", "can_delete"}


def purge_data(splunk, names):
    """Mark the events in an undeletable index unsearchable.

    `| delete` needs the can_delete capability, which no role holds by default
    and which the strategy classifies as destructive. It is granted for the
    duration of the purge and revoked immediately, so the elevated capability
    never outlives the operation that needs it.
    """
    username = load_env().get("SPLUNK_USERNAME", "admin")
    path = f"/services/authentication/users/{urllib.parse.quote(username)}"
    original = list(splunk.get(path)["entry"][0]["content"].get("roles") or [])
    if "can_delete" in original:
        granted = False
    else:
        splunk.post(path, data=[("roles", r)
                                for r in original + ["can_delete"]])
        granted = True
    try:
        for name in names:
            rows = splunk.search(f"search index={name} | delete",
                                 earliest="0", latest="+1d")
            deleted = next((r.get("deleted") for r in rows
                            if r.get("index") == name), "0")
            print(f"    purged {deleted} events from {name}")
    finally:
        if granted:
            splunk.post(path, data=[("roles", r) for r in original])
            print(f"    can_delete revoked from {username}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--yes", action="store_true",
                        help="required: confirms the destructive action")
    parser.add_argument("--keep-apps", action="store_true",
                        help="remove indexes and users but leave apps in place")
    args = parser.parse_args()
    if not args.yes:
        print("refusing to run without --yes")
        return 1

    catalog = loader.Catalog()
    settings = load_settings()

    try:
        splunk = Splunk.from_env()
        info = splunk.server_info()
    except SplunkError as exc:
        print(f"cannot reach Splunk: {exc}")
        return 2
    print(f"target: Splunk {info['version']} ({info['server_name']})")

    # Indexes: only those the catalog defines. Never a Splunk internal index,
    # and never one Splunk itself provides.
    #
    # Deletion must be called in the owning app's namespace — Splunk rejects a
    # cross-app delete with "sourceApp doesn't equal callerApp" — and it must
    # happen before the app is removed, because removing the app takes the index
    # definitions with it and leaves the bucket data orphaned on disk.
    owners = {}
    for row in splunk.search(
            "| rest /services/data/indexes | table title eai:acl.app"):
        owners[row.get("title")] = row.get("eai:acl.app")
    live = splunk.index_names()
    targets = [name for name in sorted(catalog.index_by_name)
               if name in live
               and not name.startswith(PROTECTED_PREFIXES)
               and name not in catalog.provided
               and owners.get(name) not in (None, "system")]
    skipped = sorted(set(catalog.index_by_name) & live - set(targets))
    removed = 0
    for name in targets:
        app = owners[name]
        try:
            splunk.delete(f"/servicesNS/nobody/{urllib.parse.quote(app)}"
                          f"/data/indexes/{urllib.parse.quote(name)}")
            removed += 1
        except SplunkError as exc:
            print(f"  index {name}: {exc}")
    print(f"indexes: removed {removed} of {len(targets)} removable "
          f"catalog-defined indexes")
    if skipped:
        print(f"  not removable ({len(skipped)}): Splunk-provided or "
              f"system-owned — {', '.join(skipped)}")
        # Their definitions must survive, but their DATA must not: teardown
        # cannot delete the index, so without this every reload adds another
        # copy of the seeded events and the counts drift upward silently.
        purge_data(splunk, skipped)

    # Users: only those the catalog declares. Never a role.
    users = getattr(catalog, "users", None)
    declared = [u["username"] for u in (users or {}).get("users", [])]
    if declared:
        existing = {e["name"] for e in
                    splunk.get("/services/authentication/users",
                               params={"count": 0})["entry"]}
        gone = 0
        for username in declared:
            if username in existing:
                try:
                    splunk.delete(f"/services/authentication/users/"
                                  f"{urllib.parse.quote(username)}")
                    gone += 1
                except SplunkError as exc:
                    print(f"  user {username}: {exc}")
        print(f"users: removed {gone} of {len(declared)} declared test users")
    else:
        print("users: none declared yet (catalog/users.yaml arrives in Phase 3)")

    if not args.keep_apps:
        installed = splunk.app_names()
        apps = [a for a in settings["deployment"]["apps"] if a in installed]
        for app in apps:
            try:
                splunk.delete(f"/services/apps/local/"
                              f"{urllib.parse.quote(app)}")
            except SplunkError as exc:
                print(f"  app {app}: {exc}")
        print(f"apps: removed {len(apps)} of "
              f"{len(settings['deployment']['apps'])} generated apps")

    print("\nProtected and untouched: Splunk internal indexes, built-in roles "
          f"({', '.join(sorted(PROTECTED_ROLES))}), and every app the catalog "
          "does not generate.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
