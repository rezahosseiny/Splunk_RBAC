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
import re
import sys
import time
import urllib.parse

from deploy.splunk_api import Splunk, SplunkError, load_settings
from generators import loader

ROOT = loader.ROOT
BUILD_DIR = os.path.join(ROOT, "build", "apps")

# The generic configs/conf-<file> endpoint creates a new stanza DISABLED unless
# told otherwise — an artifact of that API, not a catalog decision. Left
# unhandled, every index is created but silently accepts nothing: Splunk logs
# INDEXER_MISSING_INDEX and drops the events. So every stanza this writes is
# explicitly enabled.
FORCE_VALUES = {"disabled": "0"}


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


# Conf files where a stanza must match the catalog EXACTLY, so the stanza is
# replaced rather than updated. Updating only sets the keys present in the file:
# a capability removed from a bundle would stay granted on the instance for ever,
# and no report would show it. For RBAC that is not a cosmetic gap.
REPLACE_STANZAS = {"authorize"}


def upsert(splunk, app, conf_name, stanza, values, existing, dry_run):
    """Create or update one stanza in one conf file inside the app namespace."""
    base = (f"/servicesNS/nobody/{urllib.parse.quote(app)}"
            f"/configs/conf-{urllib.parse.quote(conf_name)}")
    payload = dict(values)
    payload.update(FORCE_VALUES)
    quoted = urllib.parse.quote(stanza, safe="")
    if dry_run:
        print(f"  would {'replace' if stanza in existing else 'create'} "
              f"[{stanza}] in {conf_name}.conf ({len(payload)} attributes)")
        return
    if stanza in existing and conf_name in REPLACE_STANZAS:
        # Delete then create, so an attribute dropped from the catalog is dropped
        # from the instance too.
        try:
            splunk.delete(f"{base}/{quoted}")
        except SplunkError:
            pass
        splunk.post(base, data={"name": stanza, **payload})
    elif stanza in existing:
        splunk.post(f"{base}/{quoted}", data=payload)
    else:
        splunk.post(base, data={"name": stanza, **payload})


def existing_stanzas(splunk, app, conf_name):
    """Stanzas this app itself owns in one conf file.

    The app namespace inherits every stanza visible to it — Splunk ships
    hundreds of props.conf sourcetypes — so an unfiltered listing looks like
    hundreds of orphans. Filtering on the owning app is what makes the orphan
    report mean "the catalog used to generate this and no longer does", which is
    the only reading under which --prune is safe.
    """
    path = (f"/servicesNS/nobody/{urllib.parse.quote(app)}"
            f"/configs/conf-{urllib.parse.quote(conf_name)}")
    try:
        result = splunk.get(path, params={"count": 0})
    except SplunkError:
        return set()
    owned = set()
    for entry in result.get("entry", []):
        acl = entry.get("acl") or {}
        if acl.get("app") == app:
            owned.add(entry["name"])
    return owned


def restart_and_wait(splunk, timeout=300):
    """Restart splunkd through the admin API and wait for it to answer again.

    Uses the management endpoint rather than systemctl, so no elevation is
    needed — the same reason the API deployment path exists (ADR-011).
    """
    try:
        splunk.post("/services/server/control/restart")
    except SplunkError as exc:
        # A restart drops the connection mid-response; that is success, not
        # failure, so only a refusal before the restart began is an error.
        if "401" in str(exc) or "403" in str(exc):
            print(f"  restart refused: {exc}")
            return False
    # Two phases, and the first is the one that is easy to get wrong: the old
    # process keeps answering for several seconds after the restart is accepted,
    # so polling for "up" straight away succeeds against the process that is
    # about to die and reports a restart that has not happened yet. Wait for the
    # port to go down first, then for it to come back.
    waited = 0
    went_down = False
    while waited < 90:
        time.sleep(3)
        waited += 3
        try:
            splunk.server_info()
        except SplunkError:
            went_down = True
            print(f"  splunkd stopped after {waited}s")
            break
    if not went_down:
        print("  splunkd never stopped — the restart was not honoured")
        return False

    while waited < timeout:
        time.sleep(5)
        waited += 5
        try:
            splunk.server_info()
        except SplunkError:
            continue
        print(f"  splunkd back after {waited}s")
        return True
    return False


def parse_meta(path):
    """Parse metadata/local.meta into {stanza: {key: value}}."""
    return parse_conf(path)


def push_views(splunk, app, app_build, dry_run):
    """Create or update each dashboard and nav file through the UI endpoint."""
    pushed = []
    for kind in ("views", "nav"):
        folder = os.path.join(app_build, "default", "data", "ui", kind)
        for path in sorted(glob.glob(os.path.join(folder, "*.xml"))):
            name = os.path.splitext(os.path.basename(path))[0]
            with open(path, encoding="utf-8") as handle:
                data = handle.read()
            base = (f"/servicesNS/nobody/{urllib.parse.quote(app)}"
                    f"/data/ui/{kind}")
            if dry_run:
                pushed.append(f"{kind}/{name}")
                continue
            try:
                splunk.post(f"{base}/{urllib.parse.quote(name)}",
                            data={"eai:data": data})
            except SplunkError:
                splunk.post(base, data={"name": name, "eai:data": data})
            pushed.append(f"{kind}/{name}")
    return pushed


def push_lookups(splunk, app, app_build, dry_run):
    """Upload each lookup table file, if any.

    The lookup-table-files endpoint requires the file to be staged under
    $SPLUNK_HOME/var/run/splunk/lookup_tmp first, which needs filesystem access
    this path does not have (ADR-011). No app currently ships a lookup — the
    capability baseline is embedded in its detection's SPL instead — so this
    reports the limitation rather than failing.
    """
    pushed = []
    for path in sorted(glob.glob(os.path.join(app_build, "lookups", "*"))):
        name = os.path.basename(path)
        if dry_run:
            pushed.append(name)
            continue
        with open(path, "rb") as handle:
            content = handle.read()
        url = (f"{splunk.base_url}/servicesNS/nobody/"
               f"{urllib.parse.quote(app)}/data/lookup-table-files")
        # The target name goes in the query string, not the multipart body:
        # this endpoint reads it before it parses the upload.
        response = splunk.session.post(
            url, params={"output_mode": "json", "name": name},
            files={"eai:data": (name, content, "text/csv")})
        if not response.ok:
            print(f"  NOT DEPLOYED: lookups/{name} — this endpoint needs the "
                  f"file staged on the Splunk filesystem, which the API path "
                  f"cannot do (ADR-011)")
            continue
        pushed.append(name)
    return pushed


def apply_metadata(splunk, app, app_build, dry_run):
    """Apply metadata/local.meta as object ACLs.

    A filesystem sync just copies the file. Through the API the same intent has
    to be expressed as an ACL on each object, because there is no endpoint that
    writes local.meta. The `[]` stanza becomes the app's own ACL; a `[views]`
    stanza becomes the ACL on each view in the app.

    This is the half of a workspace that grants the access. Without it the role
    exists and the app exists, and no user can open it.
    """
    path = os.path.join(app_build, "metadata", "local.meta")
    if not os.path.exists(path):
        return []
    applied = []
    for stanza, values in sorted(parse_meta(path).items()):
        access = values.get("access")
        if not access:
            continue
        reads, writes = [], []
        for part in access.split(","):
            match = re.match(r"\s*(read|write)\s*:\s*\[(.*?)\]", part)
            if not match:
                continue
            roles = [r.strip() for r in match.group(2).split(",") if r.strip()]
            (reads if match.group(1) == "read" else writes).extend(roles)
        payload = {"sharing": "global" if values.get("export") == "system"
                   else "app", "owner": "nobody"}
        if reads:
            payload["perms.read"] = ",".join(reads)
        if writes:
            payload["perms.write"] = ",".join(writes)

        if stanza == "":
            target = f"/servicesNS/nobody/{urllib.parse.quote(app)}/apps/local/{urllib.parse.quote(app)}/acl"
        elif stanza == "views":
            for view in sorted(glob.glob(os.path.join(
                    app_build, "default", "data", "ui", "views", "*.xml"))):
                name = os.path.splitext(os.path.basename(view))[0]
                target = (f"/servicesNS/nobody/{urllib.parse.quote(app)}"
                          f"/data/ui/views/{urllib.parse.quote(name)}/acl")
                if not dry_run:
                    splunk.post(target, data=payload)
                applied.append(f"views/{name}")
            continue
        else:
            applied.append(f"{stanza} (SKIPPED: no endpoint)")
            continue
        if not dry_run:
            splunk.post(target, data=payload)
        applied.append("app")
    return applied


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true",
                        help="report what would change and send nothing")
    parser.add_argument("--prune", action="store_true",
                        help="remove deployed stanzas the catalog no longer "
                             "generates")
    parser.add_argument("--restart", action="store_true",
                        help="restart splunkd afterwards and wait for it to "
                             "come back. Index creation is not hot-reloadable: "
                             "splunkd logs \"reload is not safe since a path "
                             "has been changed\" and the new index accepts "
                             "nothing until a restart.")
    parser.add_argument("--no-wait", action="store_true",
                        help="with --restart, return without waiting")
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
                # An empty stanza is NOT nothing. A pr_workspace_* role is
                # deliberately empty — it grants no index, capability, or quota
                # and exists as a named handle for app metadata to reference.
                # Skipping it leaves the role undefined, so a user holding it
                # reaches nothing: exactly the half-implemented workspace the
                # strategy warns about.
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

        views = push_views(splunk, app, app_build, args.dry_run)
        if views:
            print(f"  views and nav: {len(views)} pushed")
        lookups = push_lookups(splunk, app, app_build, args.dry_run)
        if lookups:
            print(f"  lookups: {', '.join(lookups)}")
        acls = apply_metadata(splunk, app, app_build, args.dry_run)
        if acls:
            print(f"  metadata as ACLs: {', '.join(acls)}")

        # Anything this path cannot deploy must be named, not passed over. A
        # silent skip is how a workspace ends up half-implemented.
        handled = {"local", "metadata", "lookups"}
        for entry in sorted(os.listdir(app_build)):
            if entry in handled or entry == "default":
                continue
            print(f"  NOT DEPLOYED: {entry}/ — no endpoint for it in this path")

    if args.dry_run:
        print(f"\ndry run: {changed} stanzas would be written")
        return 0

    if args.restart:
        print("\nrestarting splunkd — index configuration is not "
              "hot-reloadable")
        if not restart_and_wait(splunk):
            print("splunkd did not come back within the timeout; check "
                  "`systemctl status splunk`")
            return 1

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
