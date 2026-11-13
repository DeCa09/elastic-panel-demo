# Test log

Date: 13 November 2026.

## Where the tests ran

No Elastic Cloud account, Slack workspace or LLM credentials existed. So the full flow was **not** run on the target environment. Instead I ran everything that does not need those credentials on a local stack:

| Part | Used in the test | Differs from your setup |
|---|---|---|
| Elastic | Elasticsearch, Kibana and Elastic Agent (as EDOT collector) **9.5.6** in Docker, local trial licence (`local-stack/docker-compose.yml`) | You will use Elastic Cloud Serverless with the Managed OTLP endpoint. |
| Shop | `github.com/elastic/opentelemetry-demo` at commit `2114f47` (6 Nov 2026), Compose files from the fork, **pre-built upstream images** `otel/demo:3.1.0-*` | You will build the fork's own images (EDOT SDK variants) with `start-demo.sh`. |
| Host | Linux x86-64 cloud container, 4 CPUs, 15 GB RAM | macOS on Apple Silicon with Docker Desktop. |
| Alert target | Kibana server-log connector (`ALERT_CHANNEL=serverlog`) | Slack incoming webhook. |
| AI | none (no LLM available) | Elastic AI Agent with Elastic Managed LLM. |

Three shop containers could not start in the test container because of its own limits (no IPv6, no `ulimit`): `image-provider`, `flagd-ui`, `telemetry-docs`. They are not part of the demo path. Product images did not load in the test shop for that reason. This should not happen on your Mac.

## Results

| # | Test | Result |
|---|---|---|
| 1 | Telemetry reaches Elasticsearch in OpenTelemetry-native data streams (`traces-generic.otel-default`, `logs-generic.otel-default`, `metrics-*.otel-default`) | Pass |
| 2 | `scripts/setup-elastic.sh all`: connector, 2 SLOs, dashboard, 2 rules created | Pass |
| 3 | Run `setup-elastic.sh all` a second and third time | Pass (objects updated or replaced, no duplicates) |
| 4 | `setup-elastic.sh test-connector` (server log) | Pass |
| 5 | Kibana accepts the `.slack` and `.teams` connector definitions and rules that use them | Pass (definition only; delivery not tested) |
| 6 | APM SLIs compute on OpenTelemetry data | Pass (latency SLO showed a real SLI value and went to "Violated" during the failure) |
| 7 | Dashboard renders: 5 tiles, 3 charts, 2 SLO panels, with real data | Pass (checked in a browser screenshot) |
| 8 | `break.sh` switches the flag; flagd picks up the file change | Pass (`filepath event ... WRITE` in the flagd log) |
| 9 | Failure is visible: `frontend` p95 from under 100 ms to 3 to 15 s; `product-catalog` requests up to 30 s; `sql.conn.query` spans up to 30 s; lock log line; `504` in `frontend-proxy` logs | Pass |
| 10 | Latency alert fires | Pass. Time from `break.sh` to active alert: **47, 49, 62, 96, 102 s** |
| 11 | Alert message goes out through the connector with reason and a link to the alert | Pass (server log) |
| 12 | Alert details page shows the threshold chart, investigation guide and related dashboard tabs | Pass (screenshot) |
| 13 | `fix.sh` → alert recovers, RECOVERED message sent | Pass. **65 and 68 s** |
| 14 | `reset.sh` | Pass. **70 and 71 s** from an active failure; 4 s when already healthy |
| 15 | `preflight.sh --quiet` | Pass when healthy. Correctly fails while latency is high |
| 16 | SLO burn rate rule fires during the failure | Pass |
| 17 | Runbook fallback ES\|QL query returns the chain frontend → product-catalog → `sql.conn.query` | Pass |
| 18 | `local-stack/docker-compose.yml` starts a working stack | Pass. `local-stack/up.sh` wraps it and was syntax-checked only |

## What the tests changed in the design

1. **APM latency rule → custom threshold rule.** With a 1-minute window the APM latency rule did not fire within 2 minutes, because it reads metrics that are rolled up once a minute and written at the end of that minute. The custom threshold rule on trace data fired on its first run.
2. **Flapping.** After several on/off cycles Kibana marked the alert as flapping and held back the recovery (253 s and 248 s). The rule now sets its own flapping threshold. Recovery then took 65 and 68 s.
3. **`fix.sh` restarts `product-catalog`.** That drops the lock and the queued queries at once, like rolling back a release.
4. **Revenue at risk follows slow or failed requests.** Completed checkouts barely dropped during this failure at low load, so a tile based only on checkouts did not react. The estimate now uses the share of slow or failed shop requests. The formula and its assumptions are shown on the dashboard.
5. **Long-lived flag streams.** `flagd` `EventStream` spans last 10 minutes and top any naive "slowest span" query. The runbook's query excludes them and the runbook warns about it.

## Not tested: do these first on your trial

| # | Untested | Risk | Where |
|---|---|---|---|
| U1 | Creating the Serverless project and finding the endpoints and keys | Low. UI steps come from Elastic's docs. | `SETUP.md` 2 and 3 |
| U2 | `start-demo.sh` on Apple Silicon, including the fork's image build | Medium. Long first build, memory. | `SETUP.md` 5 |
| U3 | Telemetry through the Managed OTLP endpoint. Field names on Cloud should match the local test (same OpenTelemetry-native format), but this is not confirmed. | Medium. If a dashboard panel is empty, a field name differs. | `SETUP.md` 5 and 6 |
| U4 | `setup-elastic.sh` against Serverless Kibana APIs (rule consumer, Dashboards API, SLO index pattern) | Medium. Fallback steps are in `SETUP.md` 6 and 10. | `SETUP.md` 6 |
| U5 | Slack delivery, and the alert link opening the alert page | Low. | `SETUP.md` 4 |
| U6 | AI Agent: available in the trial, **Add to chat** on a custom threshold alert, speed, answer quality, German summary | **High. This is the centre of the demo.** | `SETUP.md` 7 |
| U7 | `reset.sh` speed on Serverless. It uses an internal API to make the rule run at once. If Serverless blocks that, the reset still works but can take up to a minute longer. | Low. | `RUNBOOK.md` |
| U8 | Teams variant | Not needed unless you switch. | `SETUP.md` 4 |
| U9 | Click names in the runbook on Serverless navigation | Low. Correct them in your first walk-through. | `RUNBOOK.md` |
| U10 | The 12 minutes with you speaking | Rehearse with a timer at least three times. | `RUNBOOK.md` |
