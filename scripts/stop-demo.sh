#!/usr/bin/env bash
# Stop the shop. Data already in Elastic stays there.
# Usage: scripts/stop-demo.sh          stop containers, keep volumes
#        scripts/stop-demo.sh --clean  also remove volumes
set -euo pipefail
. "$(dirname "$0")/lib.sh"
all_flags_off
if [ "${1:-}" = "--clean" ]; then
  compose_demo down --remove-orphans --volumes
else
  compose_demo down --remove-orphans
fi
ok "Shop stopped"
