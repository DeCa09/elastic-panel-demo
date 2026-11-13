# Sources

Checked on 13 November 2026. Each fact has a verification level:

- **Page**: I read the published elastic.co page.
- **Docs source**: read in Elastic's public docs source on GitHub (`elastic/docs-content`, `elastic/kibana`), which is what elastic.co/docs is built from. The rendered page may lag slightly.
- **Repo**: read in the source code of a public repository.
- **Tested**: I ran it. See `TEST_LOG.md` for where (a local Elastic 9.5.6 stack, not Elastic Cloud).
- **Unverified**: I could not confirm it. Check before you rely on it.

## Elastic Cloud trial

| Fact | Level | Source |
|---|---|---|
| The trial lasts 14 days. "When you create an organization, you start with a free 14-day trial." | Page | https://www.elastic.co/docs/deploy-manage/deploy/elastic-cloud/create-an-organization |
| The trial includes one hosted deployment and three Serverless projects. | Page | same page |
| No credit card is needed to sign up. | Page | https://www.elastic.co/cloud/cloud-trial-overview |
| "Token usage for LLMs and other ML models is restricted during the trial period." The limit is not published. | Page | create-an-organization page |
| Hosted trial deployments are limited to 4 GB RAM per zone for data nodes. Serverless trials have limited scaling. | Docs source | `deploy-manage/deploy/_snippets/trial-limitations.md` |
| After expiry, deployments and projects are suspended; data is deleted 30 days later if you do not subscribe. | Page | create-an-organization page |
| Whether a trial can be extended. | Unverified | Not in the current docs. Ask Elastic support or your recruiter. |

## Hosted or Serverless

| Fact | Level | Source |
|---|---|---|
| The Managed OTLP endpoint is available on Serverless Observability and on Elastic Cloud Hosted (9.0+). It is not available for self-managed, ECE or ECK. | Page | https://www.elastic.co/docs/reference/managed-inputs/managed-otlp-endpoint |
| Auth header: `Authorization: ApiKey <key>`. Telemetry is stored in OpenTelemetry format. Limits: no Universal Profiling, no tail-based sampling at the endpoint. | Page | same page |
| Where to find the endpoint: **Add data > Applications > OpenTelemetry**, or the project's **Manage** page under **Application endpoints**. | Docs source | `solutions/observability/get-started/quickstart-elastic-cloud-otel-endpoint.md` |
| SLOs, APM, AI Assistant, Agent Builder and Elastic Managed LLMs need the **Observability Complete** tier on Serverless. Logs Essentials does not include them. | Docs source | https://www.elastic.co/docs/solutions/observability/observability-serverless-feature-tiers |
| Feature differences (Serverless has no APM tail-based sampling, no Universal Profiling, no agent central configuration; RUM is planned). | Docs source | https://www.elastic.co/docs/deploy-manage/deploy/elastic-cloud/differences-from-other-elasticsearch-offerings |
| Serverless regions in Europe include AWS Frankfurt, Ireland, London; Azure Frankfurt and others; GCP Frankfurt and others. No Swiss Serverless region. | Docs source | https://www.elastic.co/docs/deploy-manage/deploy/elastic-cloud/regions |
| Elastic Cloud Hosted has an AWS **Zurich** region: `aws-eu-central-2`, "EU (Zurich)". | Page | https://www.elastic.co/docs/reference/cloud/cloud-hosted/regions |
| Exact licence level needed on Hosted for SLOs, connectors and AI features. | Unverified | https://www.elastic.co/subscriptions/cloud (check the table) |

## AI: the AI Assistant is deprecated, the AI Agent is the default

| Fact | Level | Source |
|---|---|---|
| "The Elastic AI Assistant for Observability and Search is deprecated. The Elastic AI Agent is now the default chat experience. To switch back to the AI Assistant, go to GenAI settings." | Page | https://www.elastic.co/docs/solutions/observability/ai/observability-ai-assistant |
| "Elastic Agent Builder is the default chat experience in Observability." | Page | https://www.elastic.co/docs/solutions/observability/ai/agent-builder-observability |
| On an alert details page: "Click **Add to chat** in the page header. Elastic Agent Builder opens a new conversation with the alert attached and automatically sends *Investigate this alert*." | Page | https://www.elastic.co/docs/solutions/observability/incident-management/view-alerts |
| **Investigate map** on the full Service map page starts a chat with the map as context. | Page | agent-builder-observability page |
| These need "an Enterprise license on the Elastic Stack, or the Observability Complete feature tier on Elastic Observability Serverless". On the Stack they are GA from 9.6; on Serverless they are GA. | Page / Docs source | agent-builder-observability page |
| Agent Builder does not yet have the AI Assistant's knowledge base or the "AI Assistant" alert-rule action. | Docs source | https://www.elastic.co/docs/explore-analyze/ai-features/ai-chat-experiences/ai-agent-or-ai-assistant |
| Elastic Managed LLM is a preconfigured connector on Hosted and Serverless. No setup needed. Zero data retention. Billed per token. | Docs source | https://www.elastic.co/docs/reference/kibana/connectors-kibana/elastic-managed-llm |
| Elastic Inference Service regions include AWS `eu-central-2` (Zurich) and `eu-central-1`. EU projects are routed to the nearest EU region. | Docs source | https://www.elastic.co/docs/explore-analyze/elastic-inference/eis-region-and-hosting |
| A Kibana 9.5.6 header shows an **AI Agent** button, not "AI Assistant". | Tested | local stack screenshot |
| Quality of the AI Agent's answer on this demo's data. | Unverified | Needs an LLM. Test in your trial (SETUP.md step 7). |

## The demo application

| Fact | Level | Source |
|---|---|---|
| The Elastic fork starts with `./demo.sh docker`, asks for the OTLP endpoint and API key, and saves them in `.env.override`. It uses EDOT SDKs for some services and Elastic Agent as the collector. | Repo | https://github.com/elastic/opentelemetry-demo (`.github/README.md`, `demo.sh`), commit `2114f47` of 6 Nov 2026 |
| The collector exports with `otlphttp` to `ELASTIC_OTLP_ENDPOINT` and header `Authorization: ApiKey ...`. | Repo | `src/otel-collector/otelcol-elastic-config.yaml` |
| Feature flags live in `src/flagd/demo.flagd.json`. flagd reads that file and watches it for changes. | Repo + Tested | `compose.yaml`, flagd log shows `filepath event ... WRITE` |
| Current flags: `adFailure`, `adHighCpu`, `adManualGc`, `aiRunawayAgent`, `aiSlowResponse`, `cartFailure`, `cartMetricCardinalityOverflow`, `emailMemoryLeak`, `emitRawPii`, `failedReadinessProbe`, `imageSlowLoad`, `intlShippingSlowdown`, `kafkaConsumerDead`, `kafkaQueueProblems`, `loadGeneratorFloodHomepage`, `paymentFailure`, `paymentUnreachable`, `productCatalogFailure`, `productCatalogLockContention`, `recommendationCacheFailure`. | Repo | `src/flagd/demo.flagd.json` |
| `productCatalogLockContention`: every 10 s the product-catalog service takes an `ACCESS EXCLUSIVE` lock on `catalog.products` and holds it for 30 s. | Repo + Tested | `src/product-catalog/main.go` |
| The flag UI is at `http://localhost:8080/feature`, with a REST API at `/feature/api/read` and `/feature/api/write`. | Repo | `src/flagd-ui/README.md` |

## Kibana APIs used by the scripts

| Fact | Level | Source |
|---|---|---|
| `POST /api/actions/connector/{id}`, `POST /api/actions/connector/{id}/_execute`, `POST /api/alerting/rule/{id}`, `POST /api/observability/slos`. Header `kbn-xsrf: true`, auth `Authorization: ApiKey ...`. | Docs source + Tested | https://www.elastic.co/docs/api/doc/kibana and https://www.elastic.co/docs/api/doc/serverless |
| Dashboards API `PUT /api/dashboards/{id}`: "Generally available; added in 9.5.0". Supports inline ES|QL panels and SLO panels. | Repo + Tested | https://github.com/elastic/dashboards-api-spec (linked from the Kibana API docs) |
| Slack connector types: `.slack` (incoming webhook) and `.slack_api` (Web API). Teams connector `.teams` uses a webhook created with the Teams **Workflows** app. | Docs source | https://www.elastic.co/docs/reference/kibana/connectors-kibana/slack-action-type and `/teams-action-type` |
| Rule types `observability.rules.custom_threshold`, `slo.rules.burnRate`, `apm.transaction_duration` exist with the parameters used. | Tested | local Kibana 9.5.6 `GET /api/alerting/rule_types` |
| APM SLIs (`sli.apm.transactionDuration`, `sli.apm.transactionErrorRate`) work on OpenTelemetry-native data with index `metrics-*.otel-*`. | Tested | local stack |

## Data tiers, storage, pricing

| Fact | Level | Source |
|---|---|---|
| Hot, warm, cold and frozen tiers. The frozen tier uses partially mounted searchable snapshots. | Docs source | https://www.elastic.co/docs/manage-data/lifecycle/data-tiers |
| "Searchable snapshots is a feature that requires an Enterprise license." | Docs source | https://www.elastic.co/docs/deploy-manage/tools/snapshot-and-restore/searchable-snapshots |
| "In benchmarks, logsdb index mode reduced the storage footprint of log data by up to 60%." It is the default for new logs data streams in 9.0+ and on Serverless. | Docs source | https://www.elastic.co/docs/manage-data/data-store/data-streams/logs-data-stream |
| "In our benchmarks, metrics data stored in a TSDS used 70% less disk space than a regular data stream." | Docs source | https://www.elastic.co/docs/manage-data/data-store/data-streams/time-series-data-stream-tsds |
| Serverless Observability is billed per GB ingested and per GB retained per month. No data tiers to manage. | Page | https://www.elastic.co/pricing/serverless-observability |
| Exact prices per GB. | Unverified | Read them on the pricing page on the day. Do not quote prices from memory. |

## OpenTelemetry

| Fact | Level | Source |
|---|---|---|
| "Elastic Distributions of OpenTelemetry (EDOT) is an open-source ecosystem of OpenTelemetry distributions tailored to Elastic." From 9.5 the collector capability is built into Elastic Agent. | Docs source | https://www.elastic.co/docs/reference/opentelemetry |
| Elastic donated the Elastic Common Schema (ECS) to OpenTelemetry (2023). | Unverified wording | https://www.elastic.co/docs/reference/ecs/ecs-opentelemetry |
| Elastic donated its continuous profiling agent to OpenTelemetry. | Unverified wording | https://www.elastic.co/observability-labs/blog/elastic-profiling-agent-acceptance-opentelemetry |

## Customer stories (numbers quoted from the pages)

| Customer | What the page says | Level | Source |
|---|---|---|---|
| PepsiCo | "PepsiCo reduced MTTR by 30% with Elastic Observability". "Reduces monitoring tool count from 55 to less than 20". "99.9% uptime". "Lowers hardware costs up to 25% annually". | Page | https://www.elastic.co/customers/pepsico |
| Oney Bank (France; consumer finance for retailers) | "reduced incident detection time by 95%, from 20 minutes to just one minute, ensuring system continuity during peak business periods". "Oney Bank replaced five monitoring tools with Elastic Observability". "saving 30% of its costs annually". "improved service availability by 30%". | Page | https://www.elastic.co/customers/oney-bank |
| Italy's leading gas distribution company (not named on the page) | "achieves 99% uptime for its IT infrastructure". "reduced MTTR by 25%". "reduced the cost of its observability activities by 35%". | Page | https://www.elastic.co/customers/italian-gas-distribution |

## The fictional customer name

"Gipfelkorb AG" is invented. A name search in the Swiss commercial register (zefix.ch) on 13 November 2026 returned no company with that name. Search again before the interview if you want to be sure.
