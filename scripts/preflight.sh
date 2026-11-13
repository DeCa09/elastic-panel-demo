#!/usr/bin/env bash
# Check that everything is ready for the demo. Run it 30 minutes before, and
# again 5 minutes before. Exit code 0 means go.
# Usage: scripts/preflight.sh            all checks, sends one test message to Slack/Teams
#        scripts/preflight.sh --quiet    same, but does not post the test message
set -uo pipefail
. "$(dirname "$0")/lib.sh"
need KIBANA_URL ELASTICSEARCH_URL ELASTIC_API_KEY
quiet="${1:-}"
fails=0
check() { if "$@"; then return 0; else fails=$((fails + 1)); return 1; fi; }

say "1. Local shop"
if docker info >/dev/null 2>&1; then ok "Docker is running"; else bad "Docker is not running"; fails=$((fails + 1)); fi
for c in frontend frontend-proxy checkout product-catalog load-generator flagd otel-collector; do
  state="$(docker inspect -f '{{.State.Status}}' "$c" 2>/dev/null || echo missing)"
  if [ "$state" = "running" ]; then ok "container $c is running"; else bad "container $c is $state"; fails=$((fails + 1)); fi
done
t="$(curl -s -o /dev/null -w '%{http_code} %{time_total}' --max-time 10 "$SHOP_URL" || true)"
case "$t" in
  200*) ok "shop answers at $SHOP_URL in ${t#200 }s" ;;
  *)    bad "shop does not answer at $SHOP_URL ($t)"; fails=$((fails + 1)) ;;
esac

say "2. Feature flags"
on="$(flags_on)"
if [ -z "$on" ]; then ok "all failure flags are off"; else bad "flags still on: $(echo "$on" | tr '\n' ' ') (run scripts/reset.sh)"; fails=$((fails + 1)); fi

say "3. Data is flowing into Elastic (last 2 minutes)"
for pair in "traces:${TRACES_INDEX:-traces-*.otel-*}" "logs:${LOGS_INDEX:-logs-*.otel-*}" "metrics:metrics-*.otel-*"; do
  kind="${pair%%:*}"; index="${pair#*:}"
  n="$(esql "FROM $index | WHERE @timestamp > NOW() - 2 minutes | STATS COUNT(*)")"
  if [ -n "$n" ] && [ "$n" -gt 0 ] 2>/dev/null; then ok "$kind: $n documents"; else bad "$kind: no recent documents in $index"; fails=$((fails + 1)); fi
done
n="$(esql "FROM ${LOGS_INDEX:-logs-*.otel-*} | WHERE @timestamp > NOW() - 5 minutes AND service.name == \"checkout\" AND body.text == \"order placed\" | STATS COUNT(*)")"
if [ -n "$n" ] && [ "$n" -gt 0 ] 2>/dev/null; then ok "checkouts in the last 5 minutes: $n"; else bad "no completed checkouts in the last 5 minutes"; fails=$((fails + 1)); fi
p95="$(esql "FROM ${TRACES_INDEX:-traces-*.otel-*} | WHERE @timestamp > NOW() - 1 minute AND kind == \"Server\" AND service.name == \"${SHOP_SERVICE:-frontend}\" | STATS ROUND(PERCENTILE(duration, 95) / 1000000)")"
limit="${LATENCY_THRESHOLD_MS:-1000}"
if [ -n "$p95" ] && [ "${p95%.*}" -lt "$limit" ] 2>/dev/null; then ok "shop p95 latency is ${p95%.*} ms (alert threshold $limit ms)"; else bad "shop p95 latency is '${p95}' ms, not below $limit ms. The shop is not healthy yet."; fails=$((fails + 1)); fi

say "4. Elastic objects"
check python3 "$ROOT/elastic/setup_elastic.py" status
active="$(python3 "$ROOT/elastic/setup_elastic.py" active-alerts)"
if [ "$active" = "0" ]; then ok "no active latency alert (clean start)"; else bad "latency alert state: $active (run scripts/reset.sh and wait)"; fails=$((fails + 1)); fi

say "5. Alert connector"
if [ "$quiet" = "--quiet" ]; then
  note "skipped the test message (--quiet)"
else
  check python3 "$ROOT/elastic/setup_elastic.py" test-connector && note "check that the test message arrived in your channel"
fi

say "6. Check by hand (not scriptable)"
note "AI Agent chat opens and answers 'Which services do you see?'"
note "Kibana, Slack and the terminal are open and logged in; screen sharing shows the right window"
note "Backup video and screenshots are open in a second window (FALLBACK.md)"

echo
if [ "$fails" -eq 0 ]; then
  printf '\033[32mPREFLIGHT PASSED\033[0m  You are ready.\n'
else
  printf '\033[31mPREFLIGHT FAILED\033[0m  %s check(s) failed. See FALLBACK.md if you are short on time.\n' "$fails"
  exit 1
fi
