#!/usr/bin/env bash
# Remove everything this project created, returning the instance to a clean
# slate: generated apps, catalog-defined indexes and their data, and test users.
#
# Destructive by design and scoped by the catalog. It never touches Splunk
# internal indexes, built-in roles, or any app this project did not generate.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if [[ "${1:-}" != "--yes" ]]; then
  echo "This deletes the generated apps, every catalog-defined index and its"
  echo "data, and the test users, on the instance in config/settings.yaml."
  echo "Re-run with --yes to proceed."
  exit 1
fi

python3 -m deploy.teardown --yes
rm -f reports/seed_state.json
echo "teardown complete; run 'make all' to rebuild"
