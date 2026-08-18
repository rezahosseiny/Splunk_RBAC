#!/usr/bin/env bash
# Sync the generated apps to the Splunk instance and refresh.
#
# Idempotent: rsync --delete makes the deployed app match build/apps exactly, so
# a stanza removed from the catalog is removed from the instance too. Apps that
# were generated previously but are no longer in build/apps are removed.
#
# Requires write access to the app directory, which is owned by the splunk user.
# Where that is unavailable, use deploy/deploy_rest.py instead (ADR-011).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BUILD="$ROOT/build/apps"
APP_DIR="$(python3 -c "import yaml;print(yaml.safe_load(open('$ROOT/config/settings.yaml'))['deployment']['app_dir'])")"
SPLUNK_HOME="$(python3 -c "import yaml;print(yaml.safe_load(open('$ROOT/config/settings.yaml'))['splunk']['splunk_home'])")"

[[ -d "$BUILD" ]] || { echo "no build output — run 'make build' first"; exit 1; }

if [[ ! -w "$APP_DIR" ]]; then
  cat >&2 <<MSG
cannot write to $APP_DIR (owned by the splunk user).

Either grant access:
    sudo setfacl -R -m u:$(whoami):rwx $APP_DIR      # or add $(whoami) to the splunk group
or deploy through the management API instead, which needs only credentials:
    make deploy-rest
MSG
  exit 1
fi

for app in "$BUILD"/*; do
  name="$(basename "$app")"
  echo "deploying $name"
  rsync -a --delete "$app/" "$APP_DIR/$name/"
done

echo "refreshing configuration"
if ! "$SPLUNK_HOME/bin/splunk" reload index 2>/dev/null; then
  echo "reload unavailable; a restart is required for index changes:"
  echo "    sudo systemctl restart splunk"
fi
echo "done"
