# Elastic panel demo kit

Everything for the Elastic Solutions Architect panel interview (week of 23 November 2026): a live Elastic Observability demo you can break and reset, a 12-minute runbook, a deck outline, an architecture diagram, and Q&A preparation.

**Story:** an online shop slows down → an alert reaches Slack through Elastic's native connector → the Elastic AI Agent finds the root cause across logs, metrics and traces → the business impact is visible in francs.

## Read in this order

| File | What it is |
|---|---|
| `README.md` | This page: status, decisions, open points. |
| `SETUP.md` | Step by step from zero to a working demo. |
| `RUNBOOK.md` | The 12-minute demo, minute by minute, with talk track, German terms and AI prompts. |
| `FALLBACK.md` | What to do when something fails live. How to record the backups. |
| `DECK.md` | 10-slide outline with speaker notes, timings and the value table. |
| `QA_PREP.md` | Likely questions per panel role, competitor answers, customer stories, land and expand. |
| `diagrams/architecture.svg` | Architecture diagram for slide 4 (`.mmd` is the same as Mermaid). |
| `SOURCES.md` | Every product fact with its source and how well it is verified. |
| `TEST_LOG.md` | What was run, where, and the results. |

## Three things that changed from the brief

1. **"AI Assistant" is now "AI Agent".** Elastic's docs say the AI Assistant for Observability is deprecated and the Elastic AI Agent (Agent Builder) is the default chat. The kit uses the AI Agent: on an alert page you click **Add to chat** and it sends "Investigate this alert". Use the new name in front of the panel.
2. **The alert is a custom threshold rule, not the APM latency rule.** I tested both. The APM rule reads one-minute rollups and fired after 2 to 3 minutes. The custom threshold rule on trace data fired after 47 to 102 seconds in five runs and recovers about 65 seconds after the fix. Both are native Elastic rules.
3. **The failure is a database lock (`productCatalogLockContention`).** It slows the shop, which matches the story, and leaves clear evidence in all three signals: a 30-second SQL span, a lock log line, and latency metrics.

## Decisions and recommendations

| Topic | Recommendation | Why |
|---|---|---|
| Trial start | **Monday 16 November 2026** | The trial lasts 14 days. Starting on the 16th covers the whole week of 23 to 27 November with 3 days of margin and leaves a week to rehearse. Rehearse on the local stack before that. |
| Hosted or Serverless | **Serverless, Observability project, "Observability Complete" tier**, EU region | Nothing to size. Always the current version, so the AI Agent with "Add to chat" on alerts is available (on Hosted that needs stack 9.6+). Managed OTLP endpoint, SLOs, connectors and the Elastic Managed LLM are included. The trial allows three projects, so you have a spare. |
| When Hosted is better | As the production answer in Q&A | Hosted has an AWS Zurich region. Serverless has no Swiss region today. |
| Slack or Teams | Slack | Fastest to set up. The Teams variant is documented in `SETUP.md` step 4. |
| Fictional customer | Gipfelkorb AG, Swiss online retailer | Invented. No company of that name in the Swiss commercial register on 13 November 2026. |

## Status: what is tested

Tested end to end on a **local Elastic 9.5.6 stack** with the demo's upstream images (details in `TEST_LOG.md`):

- Telemetry flow: shop → collector → Elasticsearch, in OpenTelemetry-native data streams.
- `setup-elastic.sh`: connector, 2 SLOs, dashboard, 2 rules. Safe to re-run.
- `break.sh` → alert active after 47 to 102 s (five runs) → alert text delivered through a connector.
- `fix.sh` → alert recovered after 65 and 68 s. `reset.sh` in 70 and 71 s. `preflight.sh`.
- The dashboard renders with real data. The evidence for the root cause is in the data.
- Kibana accepts the Slack and Teams connector definitions.

**Not tested** (no credentials existed):

- Elastic Cloud Serverless: project creation, the Managed OTLP endpoint, the scripts against Serverless APIs.
- Delivery to a real Slack or Teams channel.
- The AI Agent: availability in the trial, speed and answer quality.
- The fork's own image build on Apple Silicon (`start-demo.sh` on your Mac).
- The German session variant and the timing with you speaking.

Do these first when the trial starts. `SETUP.md` marks them with ⚠️.

## Quick start (after `SETUP.md` steps 1 to 4)

```bash
cp .env.example .env        # then fill it in
```

```bash
scripts/start-demo.sh
```

```bash
scripts/setup-elastic.sh
```

```bash
scripts/preflight.sh
```

```bash
scripts/break.sh
```

```bash
scripts/reset.sh
```

## Rules of this project

- Secrets live only in `.env`, which git ignores. No key or webhook URL belongs in any document.
- The trial is free. Nothing here costs money. Two things would: subscribing to Elastic Cloud, and connecting your own LLM provider. Neither is needed.
- This is a local git repository. Nothing has been pushed anywhere.
