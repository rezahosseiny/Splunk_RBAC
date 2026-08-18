#!/usr/bin/env python3
"""Seed sample exports into the governed indexes.

Three properties this has to hold, all of which are tested rather than assumed:

**Keyed on the mapping, never per-feed.** The routing for every event comes from
catalog/mapping.yaml. There is no feed-specific branch here; a new export needs
new mapping rules, not new code (ADR-007).

**Redacted before ingestion.** catalog/redaction.yaml is applied to event content
first, and the seeder refuses to send a batch in which a redaction target
survived. Ingesting the raw export would copy real employee identifiers onto the
dev instance (ADR-009, ADR-010).

**Idempotent.** State is recorded with a fingerprint of the inputs. Re-running
with unchanged inputs is a no-op rather than a second copy of every event.

    python -m deploy.seed_data                      # seed everything
    python -m deploy.seed_data --dry-run            # write batches, send none
    python -m deploy.seed_data --force              # re-send despite state
"""

import argparse
import collections
import csv
import glob
import hashlib
import json
import os
import re
import sys

from deploy.splunk_api import Splunk, SplunkError, load_settings
from generators import loader
from tools import redact

ROOT = loader.ROOT
STATE_PATH = os.path.join(ROOT, "reports", "seed_state.json")
BATCH_DIR = os.path.join(ROOT, "build", "seed")
MAX_BATCH_BYTES = 4 * 1024 * 1024


def fingerprint(paths):
    """Hash the inputs whose change should force a re-seed."""
    digest = hashlib.sha256()
    for path in sorted(paths):
        digest.update(os.path.basename(path).encode())
        with open(path, "rb") as handle:
            while chunk := handle.read(1 << 20):
                digest.update(chunk)
    for name in ("mapping", "redaction", "indexes"):
        with open(os.path.join(ROOT, "catalog", f"{name}.yaml"), "rb") as fh:
            digest.update(fh.read())
    return digest.hexdigest()[:16]


def read_export(path):
    """Yield (legacy_index, legacy_sourcetype, legacy_source, raw, time) per event."""
    csv.field_size_limit(sys.maxsize)
    with open(path, newline="", encoding="utf-8", errors="replace") as handle:
        reader = csv.DictReader(handle)
        missing = {"index", "sourcetype", "source", "_raw"} - set(
            reader.fieldnames or [])
        if missing:
            raise SystemExit(f"{path}: missing columns {sorted(missing)}")
        for row in reader:
            index = (row.get("index") or "").strip()
            if index:
                yield (index, (row.get("sourcetype") or "").strip(),
                       (row.get("source") or "").strip(),
                       row.get("_raw") or "", (row.get("_time") or "").strip())


def read_fixture(path, catalog):
    """Yield events for one coverage fixture file, keyed by its index name."""
    name = os.path.splitext(os.path.basename(path))[0]
    fixture = catalog.fixtures.get(name)
    if not fixture:
        return
    with open(path, encoding="utf-8") as handle:
        for line in handle:
            line = line.rstrip("\n")
            if line:
                yield name, fixture["sourcetype"], fixture["source"], line


def collect(catalog, exports, fixtures, redactor):
    """Resolve, redact, and group every event by its governed destination."""
    batches = collections.defaultdict(list)
    gaps = collections.Counter()
    stats = {"read": 0, "routed": 0, "fixtures": 0}

    # Pass 1: learn the identity values the corpus contains, so bare hostnames
    # and names in prose are caught as well as their structured forms.
    for path in exports:
        for _ix, _st, _src, raw, _t in read_export(path):
            redactor.learn(raw)

    for path in exports:
        for legacy_index, legacy_st, legacy_src, raw, event_time in read_export(
                path):
            stats["read"] += 1
            resolved = catalog.resolve(legacy_index, legacy_st, legacy_src)
            if resolved is None:
                gaps[(legacy_index, legacy_st)] += 1
                continue
            key = (resolved["index"], resolved["sourcetype"],
                   resolved["source"])
            batches[key].append(
                with_timestamp(flatten(redactor.redact_event(raw)),
                               event_time))
            stats["routed"] += 1

    for path in fixtures:
        for index, sourcetype, source, line in read_fixture(path, catalog):
            batches[(index, sourcetype, source)].append(flatten(line))
            stats["fixtures"] += 1

    return batches, gaps, stats


UNDATED_RE = re.compile(r"^\s*\d")


def with_timestamp(event, event_time):
    """Ensure the event text starts with a timestamp Splunk can parse.

    Some exported events have an empty leading timestamp field and begin
    ", search_name=..." — the time is in the export's _time column but not in
    _raw. Splunk cannot date such a line, so it merges it into the preceding
    event: 20 events arrived as 1, and the counts the data-access tests depend on
    silently stopped matching.

    Prefixing the event's own _time fixes the cause rather than the symptom, and
    is faithful — it restores the timestamp the event actually had. Events that
    already start with one are untouched.
    """
    if not event_time or UNDATED_RE.match(event):
        return event
    return f"{event_time} {event}"


def flatten(event):
    """Collapse an event to a single line.

    props.conf sets SHOULD_LINEMERGE=false on every governed sourcetype, so
    Splunk indexes one event per line. Multi-line sources — Windows XML event
    logs, ActiveDirectory records — would therefore arrive as many events each,
    inflating counts and destroying the expected values the data-access tests
    compare against.

    Correcting that properly means a per-sourcetype LINE_BREAKER, which needs
    real onboarding knowledge of each feed and is recorded as a production gap.
    For a harness whose subject is RBAC rather than parsing fidelity, one event
    in equals one event indexed is the property that matters, and flattening
    guarantees it. Interior newlines become spaces; nothing is dropped.
    """
    if "\n" in event or "\r" in event:
        return " ".join(event.split())
    return event


def index_counts(splunk):
    """Event count per index, from a search rather than totalEventCount.

    totalEventCount on the indexes endpoint lags behind ingestion and is not a
    reliable basis for verification. tstats over all time is authoritative, and
    latest=+1d catches any event whose timestamp lands slightly ahead of now.
    """
    rows = splunk.search("| tstats count where index=* by index",
                         earliest="0", latest="+1d")
    return {row["index"]: int(row["count"]) for row in rows}


def chunk(events):
    """Split one destination's events into requests under the size cap."""
    current, size = [], 0
    for event in events:
        encoded = len(event) + 1
        if current and size + encoded > MAX_BATCH_BYTES:
            yield current
            current, size = [], 0
        current.append(event)
        size += encoded
    if current:
        yield current


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true",
                        help="resolve, redact, and write batches without "
                             "sending them")
    parser.add_argument("--force", action="store_true",
                        help="send even when the state file says the inputs "
                             "are unchanged")
    args = parser.parse_args()

    catalog = loader.Catalog()
    if catalog.errors:
        print(f"catalog has {len(catalog.errors)} errors — refusing to seed")
        for error in catalog.errors:
            print(f"  {error}")
        return 1

    settings = load_settings()
    host = settings["seeding"]["host"]
    exports = sorted(glob.glob(os.path.join(ROOT, "sample_data", "*.csv")))
    fixtures = sorted(glob.glob(os.path.join(ROOT, "sample_data", "fixtures",
                                             "*.log")))
    if not exports and not fixtures:
        print("nothing to seed: no sample_data/*.csv and no "
              "sample_data/fixtures/*.log (run `make fixtures`)")
        return 1

    print(f"inputs: {len(exports)} export(s), {len(fixtures)} fixture file(s)")
    stamp = fingerprint(exports + fixtures)

    state = {}
    if os.path.exists(STATE_PATH):
        with open(STATE_PATH, encoding="utf-8") as handle:
            state = json.load(handle)
    if state.get("fingerprint") == stamp and not args.force and not args.dry_run:
        print(f"already seeded with these inputs (fingerprint {stamp}); "
              f"nothing to do.")
        return 0
    if state and state.get("fingerprint") != stamp and not args.force \
            and not args.dry_run:
        # Seeding does not diff — it sends every event it resolves. On top of an
        # existing seed that silently doubles the counts every test depends on,
        # so changed inputs require a clean reload rather than an append.
        print(f"inputs have changed since the last seed "
              f"({state.get('fingerprint')} -> {stamp}).\n"
              f"Seeding is not incremental: re-sending now would ADD to the "
              f"{state.get('events', 0):,} events already indexed and double "
              f"the counts.\n"
              f"Run `make reseed` for a clean reload (teardown, deploy, seed), "
              f"or --force to append deliberately.")
        return 1

    redactor = redact.default()
    batches, gaps, stats = collect(catalog, exports, fixtures, redactor)

    if gaps:
        print(f"\nREFUSING TO SEED — {len(gaps)} unmapped (index, sourcetype) "
              f"pairs, {sum(gaps.values()):,} events:")
        for (index, sourcetype), count in gaps.most_common(15):
            print(f"  {count:7,d}  index={index} sourcetype={sourcetype}")
        print("Add rules to catalog/mapping.yaml, then re-run.")
        return 1

    # Refuse to send anything if a redaction target survived anywhere.
    leaks = collections.Counter()
    for events in batches.values():
        for leak in redactor.audit("\n".join(events),
                                   include_document_patterns=False):
            leaks[leak.split(":")[0]] += 1
    if leaks:
        print(f"\nREFUSING TO SEED — redaction targets survived: {dict(leaks)}")
        return 1

    print(f"resolved {stats['routed']:,} exported events + "
          f"{stats['fixtures']:,} fixture events into {len(batches)} "
          f"destinations; redaction clean")

    expected = collections.Counter()
    for (index, _st, _src), events in batches.items():
        expected[index] += len(events)

    if args.dry_run:
        os.makedirs(BATCH_DIR, exist_ok=True)
        for (index, sourcetype, source), events in sorted(batches.items()):
            safe = f"{index}__{sourcetype}__{source}".replace("/", "_")[:180]
            with open(os.path.join(BATCH_DIR, safe + ".log"), "w",
                      encoding="utf-8") as handle:
                handle.write("\n".join(events) + "\n")
        print(f"dry run: batches written to "
              f"{os.path.relpath(BATCH_DIR, ROOT)}; nothing sent")
        _report(expected, None)
        return 0

    try:
        splunk = Splunk.from_env()
        info = splunk.server_info()
    except SplunkError as exc:
        print(f"\ncannot reach Splunk: {exc}")
        return 2
    print(f"target: Splunk {info['version']} ({info['server_name']})")

    live = splunk.index_names()
    absent = sorted({ix for ix in expected} - live)
    if absent:
        print(f"\nREFUSING TO SEED — {len(absent)} target indexes do not "
              f"exist on the instance; deploy the index app first "
              f"(`make deploy`):")
        for name in absent[:12]:
            print(f"  {name}")
        return 1

    before = index_counts(splunk)
    sent = 0
    for (index, sourcetype, source), events in sorted(batches.items()):
        for part in chunk(events):
            splunk.stream_events(index, sourcetype, source, host,
                                 "\n".join(part) + "\n")
            sent += len(part)
    print(f"sent {sent:,} events")

    with open(STATE_PATH, "w", encoding="utf-8") as handle:
        json.dump({"fingerprint": stamp, "events": sent,
                   "expected_per_index": dict(expected)}, handle, indent=1,
                  sort_keys=True)
    _report(expected, (splunk, before))
    return 0


def _report(expected, verify):
    """Per-index expected counts, and landed counts when Splunk is reachable."""
    lines = ["# Seed verification", "",
             "Expected counts come from the mapping applied to the inputs.",
             "Landed counts are read back from the instance after ingestion;",
             "indexing is asynchronous, so a shortfall immediately after",
             "seeding may simply mean the queue has not drained.", "",
             "| index | expected | landed | delta |", "|---|---:|---:|---:|"]
    print(f"\n{'index':26s} {'expected':>9s}"
          + (f" {'landed':>8s} {'delta':>7s}" if verify else ""))
    for index in sorted(expected):
        if verify:
            splunk, before = verify
            landed = index_counts(splunk).get(index, 0) - before.get(index, 0)
            delta = landed - expected[index]
            print(f"{index:26s} {expected[index]:9,d} {landed:8,d} "
                  f"{delta:+7d}")
            lines.append(f"| `{index}` | {expected[index]:,} | {landed:,} | "
                         f"{delta:+,} |")
        else:
            print(f"{index:26s} {expected[index]:9,d}")
            lines.append(f"| `{index}` | {expected[index]:,} | — | — |")
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    with open(os.path.join(ROOT, "reports", "seed_verification.md"), "w",
              encoding="utf-8") as handle:
        handle.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    sys.exit(main())
