"""Shared fixtures.

The static suite needs nothing but the repository. The behavioural suite needs a
Splunk instance and the test-user credentials, and skips with a clear reason when
they are absent — so a checkout with no instance still runs everything it can.
"""

import json
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from generators import loader                                    # noqa: E402
from deploy.splunk_api import Splunk, SplunkError, load_settings  # noqa: E402

CREDENTIALS = os.path.join(loader.ROOT, "config", "test_user_credentials.json")


@pytest.fixture(scope="session")
def catalog():
    """The loaded catalog. Session-scoped: parsing it repeatedly proves nothing."""
    return loader.Catalog()


@pytest.fixture(scope="session")
def build_dir(catalog):
    """The generated app tree, built once if it is absent.

    The static suite reads the generated confs, so it must not depend on someone
    having run `make build` first.
    """
    path = os.path.join(loader.ROOT, "build", "apps")
    if not os.path.isdir(path):
        from generators import build
        build.main()
    return path


@pytest.fixture(scope="session")
def credentials():
    if not os.path.exists(CREDENTIALS):
        pytest.skip("no config/test_user_credentials.json — run `make users` "
                    "against a deployed instance first")
    with open(CREDENTIALS, encoding="utf-8") as handle:
        return json.load(handle)


@pytest.fixture(scope="session")
def admin():
    """An admin session, or a skip with the reason."""
    try:
        splunk = Splunk.from_env()
        splunk.server_info()
    except SplunkError as exc:
        pytest.skip(f"no Splunk connection: {exc}")
    return splunk


@pytest.fixture(scope="session")
def user_sessions(credentials, catalog):
    """One authenticated session per test user, keyed by role.

    Keyed by role rather than username because every assertion is about what a
    ROLE grants. The user is only the way to observe it.
    """
    url = load_settings()["splunk"]["management_url"]
    verify = load_settings()["splunk"].get("verify_tls", True)
    sessions = {}
    for user in catalog.user_list:
        username = user["username"]
        if username not in credentials:
            pytest.skip(f"{username} has no stored credential — re-run "
                        f"`make users`")
        sessions[user["role"]] = Splunk(url, username,
                                        credentials[username]["password"],
                                        verify=verify)
    return sessions


@pytest.fixture(scope="session")
def seeded_counts(admin):
    """Event count per index, from a search rather than a lagging metric."""
    rows = admin.search("| tstats count where index=* by index",
                        earliest="0", latest="+1d")
    return {row["index"]: int(row["count"]) for row in rows}


def context_of(session):
    """The effective role and capability set the instance reports for a user."""
    content = session.get(
        "/services/authentication/current-context")["entry"][0]["content"]
    return {
        "roles": sorted(content.get("roles") or []),
        "capabilities": set(content.get("capabilities") or []),
        "username": content.get("username"),
    }
