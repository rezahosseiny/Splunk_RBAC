#!/usr/bin/env python3
"""Create the test users, one for each Business Role.

Each user is deleted and recreated, so the result does not depend on what was
there before. Each gets exactly one role, which is the invariant the whole model
rests on and the thing a behavioural test reads back.

Passwords are generated here and written to config/test_user_credentials.json,
which is gitignored and written with owner-only permissions. Nothing else knows
them, and no password is printed or logged.

    python -m deploy.create_users              # recreate every test user
    python -m deploy.create_users --verify     # check, create nothing
"""

import argparse
import json
import os
import secrets
import stat
import string
import sys
import urllib.parse

from deploy.splunk_api import Splunk, SplunkError
from generators import loader

CREDENTIALS = os.path.join(loader.ROOT, "config", "test_user_credentials.json")
# Splunk's default password policy wants length and mixed classes. Excluding
# quotes and backslashes keeps a password safe to carry through a shell or a form
# without escaping, which is where credential handling usually goes wrong.
ALPHABET = string.ascii_letters + string.digits + "!@#%^*()-_=+[]{}:,.?"


def new_password(length=24):
    """A password that satisfies the default policy on every attempt."""
    while True:
        candidate = "".join(secrets.choice(ALPHABET) for _ in range(length))
        if (any(c.islower() for c in candidate)
                and any(c.isupper() for c in candidate)
                and any(c.isdigit() for c in candidate)
                and any(not c.isalnum() for c in candidate)):
            return candidate


def existing_users(splunk):
    return {entry["name"]: entry["content"].get("roles") or []
            for entry in splunk.get("/services/authentication/users",
                                    params={"count": 0})["entry"]}


def verify(splunk, catalog):
    """Report each declared user's actual role list."""
    live = existing_users(splunk)
    problems = []
    print(f"{'user':24s} {'expected role':24s} actual")
    for user in catalog.user_list:
        username, role = user["username"], user["role"]
        actual = live.get(username)
        if actual is None:
            state = "ABSENT"
            problems.append(f"{username}: does not exist")
        elif actual == [role]:
            state = "ok"
        else:
            state = f"WRONG: {actual}"
            problems.append(f"{username}: holds {actual}, expected [{role}]")
        print(f"{username:24s} {role:24s} {state}")
    return problems


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify", action="store_true",
                        help="report the current state and change nothing")
    args = parser.parse_args()

    catalog = loader.Catalog()
    if catalog.errors:
        print(f"catalog has {len(catalog.errors)} errors — refusing to create "
              f"users")
        for error in catalog.errors:
            print(f"  {error}")
        return 1

    try:
        splunk = Splunk.from_env()
        info = splunk.server_info()
    except SplunkError as exc:
        print(f"cannot reach Splunk: {exc}")
        return 2
    print(f"target: Splunk {info['version']} ({info['server_name']})")

    if args.verify:
        problems = verify(splunk, catalog)
        print()
        if problems:
            print(f"{len(problems)} PROBLEMS:")
            for problem in problems:
                print(f"  {problem}")
            return 1
        print(f"all {len(catalog.user_list)} test users hold exactly their one "
              f"role")
        return 0

    # Every role must exist before a user can be given it. A missing role means
    # the RBAC app is not deployed, and creating the users first would leave
    # accounts with no permissions and no explanation.
    live_roles = {entry["name"] for entry in
                  splunk.get("/services/authorization/roles",
                             params={"count": 0})["entry"]}
    absent = sorted({u["role"] for u in catalog.user_list} - live_roles)
    if absent:
        print(f"\nREFUSING — {len(absent)} roles do not exist on the instance. "
              f"Deploy tristate_rbac first (`make deploy`):")
        for role in absent:
            print(f"  {role}")
        return 1

    live = existing_users(splunk)
    credentials = {}
    created = recreated = 0
    for user in catalog.user_list:
        username = user["username"]
        if username in live:
            splunk.delete(f"/services/authentication/users/"
                          f"{urllib.parse.quote(username)}")
            recreated += 1
        else:
            created += 1
        password = new_password()
        splunk.post("/services/authentication/users", data={
            "name": username,
            "password": password,
            "roles": user["role"],
            "realname": user.get("realname", username),
            "email": user.get("email", ""),
            "force-change-pass": "0",
        })
        credentials[username] = {"password": password, "role": user["role"]}

    with open(CREDENTIALS, "w", encoding="utf-8") as handle:
        json.dump(credentials, handle, indent=1, sort_keys=True)
    os.chmod(CREDENTIALS, stat.S_IRUSR | stat.S_IWUSR)
    print(f"{created} created, {recreated} recreated; credentials written to "
          f"{os.path.relpath(CREDENTIALS, loader.ROOT)} (owner-only, gitignored)")

    problems = verify(splunk, catalog)
    print()
    if problems:
        print(f"{len(problems)} PROBLEMS after creation:")
        for problem in problems:
            print(f"  {problem}")
        return 1
    print(f"all {len(catalog.user_list)} test users hold exactly their one role")
    return 0


if __name__ == "__main__":
    sys.exit(main())
