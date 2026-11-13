#!/usr/bin/env bash
# Remove the failure, as an engineer would roll back a bad release:
# switch the feature flag off and restart product-catalog so the database
# lock and the queued queries are dropped at once.
# Usage: scripts/fix.sh [FLAG]
set -euo pipefail
. "$(dirname "$0")/lib.sh"
flag="${1:-$DEMO_FLAG}"
set_flag "$flag" off
ok "$(date +%H:%M:%S)  $flag = off"
if docker inspect product-catalog >/dev/null 2>&1; then
  docker restart product-catalog >/dev/null && ok "product-catalog restarted (rollback)"
fi
note "Slack gets the RECOVERED message in about 1 to 2 minutes."
