#!/usr/bin/env python3
"""Thin Splunk REST wrapper.

Plain `requests` against the management API — no splunk-sdk, so nothing here is
coupled to a Splunk release (ADR-002). Only endpoints stable across 9.x and 10.x
are used.

Credentials come from config/.env, which is gitignored. Nothing in this module
prints or logs a credential.

    from deploy.splunk_api import Splunk
    splunk = Splunk.from_env()
    splunk.get("/services/server/info")
"""

import os
import sys

import requests
import urllib3
import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SETTINGS = os.path.join(ROOT, "config", "settings.yaml")
ENV_FILE = os.path.join(ROOT, "config", ".env")


class SplunkError(RuntimeError):
    """A REST call failed. The message carries Splunk's own explanation."""


def load_env(path=ENV_FILE):
    """Read config/.env into a dict. Absent file is not an error."""
    values = {}
    if not os.path.exists(path):
        return values
    with open(path, encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def load_settings(path=SETTINGS):
    with open(path, encoding="utf-8") as handle:
        return yaml.safe_load(handle)


class Splunk:
    """A logged-in session against one Splunk instance."""

    def __init__(self, base_url, username, password, verify=True):
        self.base_url = base_url.rstrip("/")
        self.verify = verify
        self.session = requests.Session()
        self.session.verify = verify
        self.session.auth = (username, password)
        if not verify:
            urllib3.disable_warnings(
                urllib3.exceptions.InsecureRequestWarning)

    @classmethod
    def from_env(cls):
        """Build a session from config/settings.yaml plus config/.env.

        Raises with an actionable message when credentials are absent, so every
        caller fails the same clear way rather than each inventing its own.
        """
        settings = load_settings()
        env = load_env()
        instance = settings["splunk"]
        username = env.get("SPLUNK_USERNAME")
        password = env.get("SPLUNK_PASSWORD")
        if not username or not password:
            raise SplunkError(
                "no Splunk credentials: copy config/.env.example to "
                "config/.env and set SPLUNK_USERNAME and SPLUNK_PASSWORD. "
                "config/.env is gitignored.")
        return cls(instance["management_url"], username, password,
                   verify=instance.get("verify_tls", True))

    # ---- primitives -----------------------------------------------------

    def _request(self, method, path, **kwargs):
        url = self.base_url + path
        params = kwargs.pop("params", {}) or {}
        params.setdefault("output_mode", "json")
        try:
            response = self.session.request(method, url, params=params,
                                            **kwargs)
        except requests.exceptions.RequestException as exc:
            raise SplunkError(f"{method} {path}: {exc}") from exc
        if response.status_code == 401:
            raise SplunkError(
                f"{method} {path}: 401 unauthorized — check SPLUNK_USERNAME "
                f"and SPLUNK_PASSWORD in config/.env")
        if not response.ok:
            raise SplunkError(f"{method} {path}: {response.status_code} "
                              f"{response.text[:400]}")
        return response

    def get(self, path, **kwargs):
        response = self._request("GET", path, **kwargs)
        return self._json(response)

    def post(self, path, data=None, **kwargs):
        response = self._request("POST", path, data=data, **kwargs)
        return self._json(response)

    def delete(self, path, **kwargs):
        return self._json(self._request("DELETE", path, **kwargs))

    @staticmethod
    def _json(response):
        if not response.content:
            return {}
        try:
            return response.json()
        except ValueError:
            return {"_raw": response.text}

    # ---- helpers used by the deploy and seed scripts --------------------

    def server_info(self):
        entry = self.get("/services/server/info")["entry"][0]["content"]
        return {"version": entry.get("version"),
                "build": entry.get("build"),
                "server_name": entry.get("serverName"),
                "mode": entry.get("mode")}

    def app_names(self):
        return {e["name"] for e in self.get("/services/apps/local",
                                           params={"count": 0})["entry"]}

    def index_names(self):
        return {e["name"] for e in
                self.get("/services/data/indexes",
                         params={"count": 0, "datatype": "all"})["entry"]}

    def stream_events(self, index, sourcetype, source, host, body):
        """Send newline-delimited events to one index/sourcetype/source.

        receivers/stream takes a whole batch in one request, which keeps seeding
        to a few hundred calls rather than one per event.
        """
        params = {"index": index, "sourcetype": sourcetype,
                  "source": source, "host": host}
        url = self.base_url + "/services/receivers/stream"
        try:
            response = self.session.post(
                url, params=params,
                data=body.encode("utf-8", errors="replace"))
        except requests.exceptions.RequestException as exc:
            raise SplunkError(f"stream to {index}: {exc}") from exc
        if not response.ok:
            raise SplunkError(f"stream to {index}: {response.status_code} "
                              f"{response.text[:300]}")

    def search(self, query, earliest="0", latest="now"):
        """Run a blocking search and return its rows."""
        job = self.post("/services/search/jobs",
                        data={"search": query, "exec_mode": "oneshot",
                              "earliest_time": earliest,
                              "latest_time": latest, "output_mode": "json"})
        return job.get("results", [])


def main():
    """Connectivity check — the first thing to run once credentials exist."""
    try:
        splunk = Splunk.from_env()
        info = splunk.server_info()
    except SplunkError as exc:
        print(f"FAILED: {exc}")
        return 1
    print(f"connected: Splunk {info['version']} build {info['build']} "
          f"({info['server_name']}, {info['mode']})")
    print(f"apps: {len(splunk.app_names())}, indexes: "
          f"{len(splunk.index_names())}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
