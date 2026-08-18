#!/usr/bin/env python3
"""Generate synthetic events for the coverage fixtures.

The production export covers Classes 2, 3, and 5 and effectively only the `non`
compliance driver. Without Class 4 (OT) and Class 1 data the RBAC model's
sensitivity walls and compliance isolation have nothing to be tested against, so
ADR-008 D1 adds fixtures for the empty cells.

Event content is irrelevant to RBAC — only the index, sourcetype, and source
matter — so these are plausible-shaped synthetic events, not real telemetry. They
are deterministic: the same catalog produces byte-identical fixtures, so a
rebuild reproduces the environment exactly. A real OT export replaces a fixture
by adding a legacy_indexes entry targeting the same index, with no rework.

    python -m generators.make_fixtures [--out sample_data/fixtures]
"""

import argparse
import datetime
import hashlib
import os
import sys

from generators import loader

# Deterministic: no clock and no RNG, so the same catalog yields byte-identical
# fixtures and a rebuild reproduces the environment exactly.
#
# Fixture events are placed inside the same window the production export covers
# (2026-08-18 09:00-18:00 UTC). Spreading them forward from midnight pushed the
# tail past "now", where a latest=now search cannot see them and they look lost.
WINDOW_START = 1787043600       # 2026-08-18T09:00:00Z
WINDOW_END = 1787076000         # 2026-08-18T18:00:00Z


def prng(seed, index):
    """A stable integer stream from a seed and position."""
    digest = hashlib.blake2b(f"{seed}:{index}".encode(), digest_size=8).digest()
    return int.from_bytes(digest, "big")


def iso(epoch):
    """UTC timestamp from an epoch. Pure arithmetic — no clock is read."""
    moment = datetime.datetime.fromtimestamp(int(epoch),
                                             tz=datetime.timezone.utc)
    return moment.strftime("%Y-%m-%dT%H:%M:%SZ")


def spread(index, count):
    """Epoch for event `index` of `count`, evenly across the fixture window."""
    if count <= 1:
        return WINDOW_START
    step = (WINDOW_END - WINDOW_START) / (count - 1)
    return WINDOW_START + int(index * step)


def scada_event(name, i, when):
    r = prng(name, i)
    point = ["BKR_1201_STATUS", "XFMR_T3_TAP", "BUS_230KV_MW", "LINE_88_AMPS",
             "CAP_BANK_4_VAR"][r % 5]
    value = (r >> 8) % 100000 / 100.0
    quality = ["GOOD", "GOOD", "GOOD", "SUSPECT"][(r >> 16) % 4]
    sub = f"SUB{((r >> 20) % 12) + 1:02d}"
    return (f"{iso(when)} site={sub} point={point} "
            f"value={value} quality={quality} scan_group=2s")


def historian_event(name, i, when):
    r = prng(name, i)
    tag = ["UNIT1.GEN.MW", "UNIT1.STM.PRESS", "UNIT2.GEN.MW",
           "UNIT2.FW.FLOW", "PLANT.AUX.LOAD"][r % 5]
    value = (r >> 8) % 500000 / 1000.0
    return (f"{iso(when)} tag={tag} value={value} "
            f"units=eng confidence={90 + ((r >> 24) % 10)} interpolated=false")


def weather_event(name, i, when):
    r = prng(name, i)
    station = ["KDEN", "KCOS", "KGJT", "KPUB", "KALS"][r % 5]
    return (f"{iso(when)} station={station} "
            f"temp_f={20 + (r >> 8) % 80} wind_mph={(r >> 12) % 40} "
            f"dewpoint_f={10 + (r >> 16) % 50} "
            f"conditions={['clear', 'cloudy', 'rain', 'snow'][(r >> 20) % 4]}")


BUILDERS = {
    "ctl_cip_ics_scd_s": scada_event,
    "ctl_non_ics_hst_m": historian_event,
    "pub_non_app_wea_s": weather_event,
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", default=os.path.join("sample_data", "fixtures"))
    args = parser.parse_args()

    catalog = loader.Catalog()
    out_dir = os.path.join(loader.ROOT, args.out)
    os.makedirs(out_dir, exist_ok=True)

    missing = set(catalog.fixtures) - set(BUILDERS)
    if missing:
        print(f"no event builder for fixtures: {sorted(missing)}")
        return 1

    total = 0
    for name, fixture in sorted(catalog.fixtures.items()):
        builder = BUILDERS[name]
        count = int(fixture["events"])
        lines = [builder(name, i, spread(i, count))
                 for i in range(count)]
        path = os.path.join(out_dir, f"{name}.log")
        with open(path, "w", encoding="utf-8") as handle:
            handle.write("\n".join(lines) + "\n")
        total += count
        print(f"  {name:22s} {count:5d} events -> "
              f"sourcetype={fixture['sourcetype']} source={fixture['source']}")
    print(f"{total} synthetic fixture events in {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
