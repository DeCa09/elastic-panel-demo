#!/usr/bin/env bash
# Return the demo to a clean, healthy state. Target: under 2 minutes.
#   1. every failure flag off
#   2. restart product-catalog so a held database lock is dropped at once
#   3. wait until shop latency is healthy again and the alert has recovered
# Usage: scripts/reset.sh
set -uo pipefail
. "$(dirname "$0")/lib.sh"
need KIBANA_URL ELASTICSEARCH_URL ELASTIC_API_KEY
start="$(date +%s)"
elapsed() { echo $(( $(date +%s) - start )); }
limit="${LATENCY_THRESHOLD_MS:-1000}"

say "Reset started $(date +%H:%M:%S)"
all_flags_off
ok "all failure flags are off"

if docker inspect product-catalog >/dev/null 2>&1; then
  docker restart product-catalog >/dev/null && ok "product-catalog restarted (database lock released)"
fi

say "Waiting for healthy latency (p95 of the last minute below $limit ms)"
while :; do
  p95="$(esql "FROM ${TRACES_INDEX:-traces-*.otel-*} | WHERE @timestamp > NOW() - 1 minute AND kind == \"Server\" AND service.name == \"${SHOP_SERVICE:-frontend}\" | STATS ROUND(PERCENTILE(duration, 95) / 1000000)")"
  if [ -n "$p95" ] && [ "${p95%.*}" -lt "$limit" ] 2>/dev/null; then
    ok "p95 is ${p95%.*} ms after $(elapsed)s"
    break
  fi
  if [ "$(elapsed)" -gt 240 ]; then bad "latency still '${p95}' ms after 4 minutes. Check docker ps and the shop."; exit 1; fi
  printf '  ...  p95 %s ms, %ss\n' "${p95:-?}" "$(elapsed)"
  sleep 5
done

say "Waiting for the alert to recover"
while :; do
  python3 "$ROOT/elastic/setup_elastic.py" run-soon
  sleep 4
  active="$(python3 "$ROOT/elastic/setup_elastic.py" active-alerts)"
  if [ "$active" = "0" ]; then ok "no active latency alert after $(elapsed)s"; break; fi
  if [ "$(elapsed)" -gt 300 ]; then bad "alert still active after 5 minutes"; exit 1; fi
  printf '  ...  active alerts: %s, %ss\n' "$active" "$(elapsed)"
  sleep 6
done

total="$(elapsed)"
echo
if [ "$total" -le 120 ]; then
  printf '\033[32mRESET DONE\033[0m in %ss. Ready for the next run.\n' "$total"
else
  printf '\033[33mRESET DONE\033[0m in %ss (target is 120s).\n' "$total"
fi
note "Slack shows a RECOVERED message. For a clean screen, set the Kibana time range to 'Last 15 minutes'."
