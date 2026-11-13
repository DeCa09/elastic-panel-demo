#!/usr/bin/env bash
# Create the connector, SLOs, alert rules and dashboard in Elastic.
# Usage: scripts/setup-elastic.sh [all|connector|slos|rules|dashboard|test-connector|status|delete]
set -euo pipefail
. "$(dirname "$0")/lib.sh"
need KIBANA_URL ELASTIC_API_KEY
exec python3 "$ROOT/elastic/setup_elastic.py" "${1:-all}"
