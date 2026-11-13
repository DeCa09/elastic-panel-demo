#!/usr/bin/env bash
# Inject the failure: switch on the demo's feature flag.
# Default: productCatalogLockContention (the product database gets locked, the shop slows down).
# Usage: scripts/break.sh [FLAG] [VARIANT]
set -euo pipefail
. "$(dirname "$0")/lib.sh"
flag="${1:-$DEMO_FLAG}"
variant="${2:-$DEMO_FLAG_VARIANT}"
set_flag "$flag" "$variant"
ok "$(date +%H:%M:%S)  $flag = $variant"
note "Expect the alert in about 1 to 2 minutes. Undo with scripts/fix.sh"
