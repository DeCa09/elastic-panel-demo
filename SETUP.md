# Setup

From nothing to a working demo. Plan 2 to 3 hours the first time, most of it waiting for Docker.

**Tested or not?** The scripts were run end to end against a local Elastic 9.5.6 stack (see `TEST_LOG.md`). They were **not** run against Elastic Cloud, Slack or an LLM, because no credentials existed. Steps marked ⚠️ are untested and may need a small adjustment. Do them first, early in your trial.

## What you will have at the end

| Piece | Where it runs | Made by |
|---|---|---|
| Web shop with about 20 microservices, a load generator and feature flags | Docker Desktop on your Mac | `scripts/start-demo.sh` |
| Logs, metrics and traces in Elastic | Elastic Cloud Serverless, Observability project | the shop's collector, over OTLP |
| Slack connector, 2 alert rules, 2 SLOs, 1 business dashboard | Elastic | `scripts/setup-elastic.sh` |
| AI Agent chat with an LLM | Elastic | built in (step 7) |
| Break, fix, reset, preflight | your terminal | `scripts/*.sh` |

## 0. What you need on your Mac

- macOS on Apple Silicon with **Docker Desktop**. In Docker Desktop > Settings > Resources, give it at least **8 GB memory and 4 CPUs**. The shop is heavy. Close other containers.
- `git`, `curl` and `python3` (run `xcode-select --install` if `python3` is missing). No Python packages are needed.
- About 15 GB free disk.
- Port `8080` free.

## 1. When to start the trial

The trial lasts **14 days**. The interview is on **Tuesday 24 November 2026, 13:00 to 14:00 CET**.

**Recommended: create the Elastic Cloud account on Monday 16 November 2026.** The trial then runs until about Monday 30 November. The interview falls on day 9, with 6 days of margin, and you get 8 days to rehearse on the real environment.

- Starting this weekend also works (the trial would end around 27 to 29 November). Do not start later than Wednesday 18 November: you need the days to fix what is untested.
- Until the 16th, rehearse on the local stack (step 11). It is free and uses the same scripts.
- If the interview moves to 30 November or later, tell me. Options are a second trial with another email address, or asking Elastic for an extension (not documented, so ask your recruiter). Do not subscribe: that costs money.

## 2. Create the Elastic project ⚠️

Recommendation: **Elastic Cloud Serverless, Observability project, feature tier "Observability Complete"**. Reasons are in the README.

1. Go to https://cloud.elastic.co and sign up. No credit card is needed.
2. Choose **Serverless**, then **Observability**.
3. Pick the **Observability Complete** tier. *Logs Essentials* has no APM, no SLOs and no AI Agent.
4. Region: choose an EU region, for example AWS Frankfurt (`eu-central-1`). There is no Swiss Serverless region. You cannot change the region later.
5. Name it `gipfelkorb-demo` and create it. It is ready in a few minutes.

You get three Serverless projects in a trial. Keep one spare slot so you can build a clean second project if the first gets messy.

## 3. Collect endpoints and keys ⚠️

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Fill in these values. Never paste them into a document or a chat.

| Variable | Where to find it |
|---|---|
| `KIBANA_URL` | The URL in your browser when the project is open, up to `.elastic.cloud` (no path, no trailing slash). |
| `ELASTICSEARCH_URL` | Cloud Console > your project > **Manage** > **Application endpoints** > Elasticsearch. Or in Kibana: **Help menu (?) > Connection details**. |
| `ELASTIC_API_KEY` | In Kibana: **Help menu (?) > Connection details > API key**. Give it a name, create it, copy the **encoded** value. It expires after 90 days by default, which is fine. |
| `ELASTIC_OTLP_ENDPOINT` | In Kibana: **Add data > Applications > OpenTelemetry**. Copy the value shown for `OTEL_EXPORTER_OTLP_ENDPOINT`. It is not the Elasticsearch URL and not the Kibana URL. |
| `ELASTIC_OTLP_API_KEY` | Same page: create the API key it offers. Copy only the key itself, without `ApiKey ` in front. |

The key in `ELASTIC_API_KEY` creates the alert rules, and the rules then run with that key's rights. Create it as the project admin and do not restrict it.

## 4. Create the Slack webhook ⚠️

1. Create a free Slack workspace at https://slack.com/get-started (for example `gipfelkorb-demo`).
2. Create a channel `#shop-alerts`.
3. Go to https://api.slack.com/apps > **Create New App** > **From scratch**. Name it `Elastic Alerts`, pick your workspace.
4. In the app: **Incoming Webhooks** > switch on > **Add New Webhook to Workspace** > choose `#shop-alerts` > **Allow**.
5. Copy the webhook URL into `.env` as `SLACK_WEBHOOK_URL`. Keep `ALERT_CHANNEL=slack`.

**Teams variant.** Elastic's Teams connector needs a webhook made with the Teams **Workflows** app (the old Office 365 connectors are retired). In Teams: channel > **...** > **Workflows** > a "send webhook alerts to a channel" template > copy the URL. Put it in `TEAMS_WEBHOOK_URL` and set `ALERT_CHANNEL=teams`. Per Elastic's docs you cannot use the template "Post to a channel when a webhook request is received". This variant is untested.

**No Slack yet?** Set `ALERT_CHANNEL=serverlog`. Alerts then go to the Kibana server log. Good enough to test the rules.

## 5. Start the shop

```bash
scripts/start-demo.sh
```

What it does:
1. Clones `github.com/elastic/opentelemetry-demo` into `opentelemetry-demo/`.
2. Writes your OTLP endpoint and key into that repo's `.env.override` (the file the fork's own `demo.sh` uses).
3. Runs the same `docker compose up` as the fork's `./demo.sh docker`. The first run builds several images. On Apple Silicon allow 10 to 20 minutes. ⚠️ I tested with pre-built upstream images on Linux, not with this build on a Mac.
4. Waits until http://localhost:8080 answers.

Then check:
- Shop: http://localhost:8080
- Flag UI: http://localhost:8080/feature
- In Kibana: **Applications > Service inventory**. After 1 to 3 minutes you should see `frontend`, `checkout`, `product-catalog` and others.

If nothing arrives: `docker logs --tail 50 otel-collector`. A `401` or `403` means the OTLP key is wrong. A connection error means the endpoint is wrong.

After your first good rehearsal, pin the demo version so an upstream change cannot surprise you. Put the commit hash that `start-demo.sh` printed into `.env` as `DEMO_GIT_REF`.

## 6. Create the Elastic objects ⚠️ (tested locally, not on Serverless)

```bash
scripts/setup-elastic.sh
```

It creates, through the Kibana APIs:

| Object | Name | Notes |
|---|---|---|
| Connector | Panel demo: Slack #shop-alerts | Elastic's native Slack connector (incoming webhook). |
| SLO | Shop latency: 99% of requests under 1000 ms | APM latency indicator on `frontend`, rolling 7 days. |
| SLO | Checkout availability: 99.5% of orders succeed | APM availability indicator on `checkout`. |
| Dashboard | Shop business impact (panel demo) | ES\|QL panels, SLO panels, labelled assumptions. |
| Rule | Shop is slow: frontend p95 latency above 1000 ms | Custom threshold rule on trace data, checks every minute, posts to Slack when it fires and when it recovers. Linked to the dashboard and an investigation guide. |
| Rule | Shop latency SLO is burning its error budget | SLO burn rate rule. No Slack action, so the demo gets exactly one alert. |

Run it again at any time. It updates or replaces the same objects.

Other commands: `scripts/setup-elastic.sh status`, `test-connector`, `dashboard`, `rules`, `delete`.

**Why a custom threshold rule and not the APM latency rule?** I tested both. The APM latency rule reads metrics that are rolled up once a minute, so it fired 2 to 3 minutes after the failure and recovered slowly. The custom threshold rule reads the trace data directly and fired after 47 to 102 seconds in five runs. In production either is fine. In a 12-minute demo the difference matters.

**If a step fails on Serverless**, the likely causes are:
- *Rule creation, "consumer" error*: the script already retries with the other consumer value. If it still fails, create the rule by hand: **Alerts > Manage rules > Create rule > Custom threshold**, data view `traces-*.otel-*`, filter `service.name: "frontend" and kind: "Server"`, aggregation 95th percentile of `duration`, equation `A / 1000000`, above `1000`, last 1 minute, group by `service.name`, check every 1 minute. Add the Slack connector as action for "Alert" and "Recovered".
- *Dashboard, 404*: no Dashboards API. See "Dashboard by hand" below.
- *SLO shows "No data"*: wait 5 minutes. If still empty, edit the SLO in the UI and check the index pattern.

## 7. Check the AI Agent ⚠️

Elastic renamed this area. The **AI Assistant for Observability is deprecated. The Elastic AI Agent (built with Agent Builder) is now the default chat.** Say "AI Agent" in the interview. See `SOURCES.md`.

On Serverless Observability Complete the AI Agent comes with a preconfigured **Elastic Managed LLM**. There is nothing to install.

1. In Kibana, click **AI Agent** in the top bar. A chat opens.
2. Ask: `Which services are sending telemetry right now, and which has the highest latency?` You should get a list that includes `frontend` and `product-catalog`.
3. If there is no answer or an error about a model: open **GenAI Settings** (type it into the search bar at the top). Check that a default model is selected.
4. Run the real test: `scripts/break.sh`, wait for the Slack alert, open the alert, click **Add to chat**. The agent sends *Investigate this alert* by itself. Read the answer. Then run `scripts/reset.sh`.
5. Write down the exact answer quality in your rehearsal notes. If it is weak, try the follow-up prompts in `RUNBOOK.md`.

**Trial limit.** LLM token usage is restricted during the trial and the limit is not published. Do not burn it. Rehearse the AI part 3 or 4 times in total, not 30.

**Optional, your own LLM.** If the managed LLM is not available, you can add a connector for OpenAI, Azure OpenAI, Amazon Bedrock or Google Gemini with your own key. That costs money at the provider. Ask me before you do this.

**Optional, the old AI Assistant.** GenAI Settings has a switch back to the AI Assistant. It has "contextual insights" on log entries and APM errors. I do not recommend showing a deprecated feature to a panel of Elastic employees.

## 8. Preflight

```bash
scripts/preflight.sh
```

It checks Docker, the containers, the shop, the flags, fresh data in Elastic, latency, the rules, the SLOs, the dashboard, an LLM connector, and it posts one test message to Slack. `--quiet` skips the Slack message.

Green means go. Red tells you what to fix.

## 9. Rehearse

```bash
scripts/break.sh     # switch the failure on
# wait for Slack, walk through RUNBOOK.md
scripts/fix.sh       # roll back: flag off, restart product-catalog (used live in the demo)
scripts/reset.sh     # full reset, about 70 seconds
```

Measure two numbers in your first rehearsal and write them into `RUNBOOK.md`:
1. Seconds from `break.sh` to the Slack message. (Locally: 47 to 102 s.)
2. The "Completed checkouts" tile when healthy. Put that number in `.env` as `BASELINE_ORDERS_PER_MIN` and run `scripts/setup-elastic.sh dashboard`.

Keep rehearsals with the failure short. The SLOs look back 7 days, so every minute of failure stays visible in the error budget. That is realistic, and the runbook uses it, but ten long rehearsals will leave the latency SLO deep in the red.

## 10. Dashboard by hand (only if the script cannot create it)

**Dashboards > Create dashboard > Add panel > ES|QL.** Add one panel per query. The queries are in `elastic/setup_elastic.py`, function `dashboard_body`. The five tiles are metric charts, the rest are line or bar charts. Add the two SLOs with **Add panel > SLO Overview**. Save as "Shop business impact (panel demo)". Then open the latency rule, **Edit > Related dashboards**, and add it.

## 11. Plan B: local Elastic stack (tested)

Use this before the trial starts, or if Elastic Cloud is down on the day.

```bash
local-stack/up.sh
```

It starts Elasticsearch, Kibana and an EDOT collector in Docker, with a local trial licence, and writes six lines to `local-stack/demo.env`. Copy them into `.env`, then run `scripts/start-demo.sh` and `scripts/setup-elastic.sh`.

Limits: more load on your Mac (give Docker 12 GB), no Managed OTLP endpoint, and no Elastic Managed LLM, so the AI Agent cannot answer unless you add your own LLM connector.

Stop it with `local-stack/up.sh down`.

## 12. After the interview

```bash
scripts/stop-demo.sh --clean
scripts/setup-elastic.sh delete
```

Delete the Slack app and the trial project if you no longer need them. The trial ends by itself and costs nothing.

## Files

| File | Purpose |
|---|---|
| `.env.example` | Every setting, no values. |
| `scripts/lib.sh` | Shared helpers. Loads `.env`. |
| `scripts/start-demo.sh`, `stop-demo.sh` | Start and stop the shop. |
| `scripts/setup-elastic.sh`, `elastic/setup_elastic.py` | Create connector, SLOs, dashboard, rules. |
| `scripts/break.sh`, `fix.sh`, `reset.sh`, `preflight.sh` | Demo control. |
| `local-stack/` | Plan B environment. |
