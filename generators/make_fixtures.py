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
import hashlib
import os
import sys

from generators import loader

# Deterministic pseudo-randomness: no Math.random, no clock, so output is stable.
EPOCH_START = 1787000000        # 2026-08-18T00:00:00Z, fixed by choice


def prng(seed, index):
    """A stable integer stream from a seed and position."""
    digest = hashlib.blake2b(f"{seed}:{index}".encode(), digest_size=8).digest()
    return int.from_bytes(digest, "big")


def iso(epoch):
    """UTC timestamp without importing a clock."""
    days, rem = divmod(int(epoch), 86400)
    hh, rem = divmod(rem, 3600)
    mm, ss = divmod(rem, 60)
    # 1787000000 = 2026-08-18; only the time-of-day varies across a fixture.
    day = 18 + (days - 1787000000 // 86400)
    return f"2026-08-{day:02d}T{hh:02d}:{mm:02d}:{ss:02d}Z"


def scada_event(name, i):
    r = prng(name, i)
    point = ["BKR_1201_STATUS", "XFMR_T3_TAP", "BUS_230KV_MW", "LINE_88_AMPS",
             "CAP_BANK_4_VAR"][r % 5]
    value = (r >> 8) % 100000 / 100.0
    quality = ["GOOD", "GOOD", "GOOD", "SUSPECT"][(r >> 16) % 4]
    sub = f"SUB{((r >> 20) % 12) + 1:02d}"
    return (f"{iso(EPOCH_START + i * 7)} site={sub} point={point} "
            f"value={value} quality={quality} scan_group=2s")


def historian_event(name, i):
    r = prng(name, i)
    tag = ["UNIT1.GEN.MW", "UNIT1.STM.PRESS", "UNIT2.GEN.MW",
           "UNIT2.FW.FLOW", "PLANT.AUX.LOAD"][r % 5]
    value = (r >> 8) % 500000 / 1000.0
    return (f"{iso(EPOCH_START + i * 11)} tag={tag} value={value} "
            f"units=eng confidence={90 + ((r >> 24) % 10)} interpolated=false")


def weather_event(name, i):
    r = prng(name, i)
    station = ["KDEN", "KCOS", "KGJT", "KPUB", "KALS"][r % 5]
    return (f"{iso(EPOCH_START + i * 900)} station={station} "
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
        lines = [builder(name, i) for i in range(count)]
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
