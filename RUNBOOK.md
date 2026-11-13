# Demo runbook: 12 minutes

**Session:** Tuesday 24 November 2026, 13:00 to 14:00 CET. Preflight at 12:30 and 12:55. Pre-trigger the backup alert at 12:40 (`FALLBACK.md`).

**Story in one sentence:** the shop slows down, Elastic alerts the on-call engineer in Slack within about a minute, the AI Agent finds the root cause across traces, logs and metrics, and the business sees what it costs.

**The failure:** `productCatalogLockContention`. The product database gets an exclusive lock. Product pages hang for up to 30 seconds. It looks like a bad migration or a runaway batch job on Black Friday.

**Tested or not.** The break, alert, dashboard, traces, logs and reset steps were tested on a local Elastic 9.5.6 stack. The AI Agent steps and the Slack delivery were not (no LLM, no Slack in the test). Click names come from Kibana 9.5.6 and Elastic's docs. Serverless navigation can differ slightly. Walk through once and correct the names in this file.

## People and pains

| Panellist | Plays | Cares about | Short name below |
|---|---|---|---|
| RVP | CTO, executive sponsor | Outcomes, risk, cost | **CTO** |
| Senior Manager SA | Head of Platform / SRE lead | Daily operations, on-call | **SRE** |
| Director SA | Head of E-Commerce | Revenue, customer experience | **BIZ** |
| Principal SA | Lead Platform Engineer | Architecture, OpenTelemetry, scale | **ENG** |

| Pain | Short |
|---|---|
| P1 Tool sprawl: three tools, no shared context | **P1** |
| P2 Customers report incidents before monitoring does | **P2** |
| P3 Long resolution times, war rooms | **P3** |
| P4 Nobody sees the business impact during an incident | **P4** |

## Before the session

**The evening before**
- [ ] `scripts/reset.sh`, then `scripts/preflight.sh`. All green.
- [ ] Record the backup video (`FALLBACK.md`).
- [ ] Laptop on power. Notifications off (macOS Focus). Docker Desktop set to not update.

**30 minutes before**
- [ ] `scripts/start-demo.sh` if the shop is not running. Wait 5 minutes.
- [ ] `scripts/preflight.sh`. All green. Check the test message in Slack.
- [ ] Ask the AI Agent one warm-up question: `Which services are sending telemetry?`

**5 minutes before**
- [ ] `scripts/preflight.sh --quiet`. All green.
- [ ] Browser, one window, zoom 125%, these tabs in this order:
  1. **Dashboard** "Shop business impact (panel demo)", time range *Last 15 minutes*
  2. **Service map**: Applications > Service inventory > Service map
  3. **Slack** `#shop-alerts` (clear or scroll past old messages)
  4. The shop, http://localhost:8080
- [ ] Terminal, large font, in the project folder, with `scripts/break.sh` typed but **not** run.
- [ ] Second monitor or phone: this runbook and a timer.
- [ ] Backup video and screenshots open in another window.

## The 12 minutes

Start the timer when you leave the slide. German key terms are in the last column. Say them even if the session is in English when the panel is DACH; it shows fluency.

| Time | Show and click | Say | Pain / role | German key terms |
|---|---|---|---|---|
| **0:00** | **Terminal.** Press Enter on `scripts/break.sh`. | "I am now breaking the shop on purpose. One flag locks the product database. This is what a bad migration does on Black Friday. I will not tell the system what I did. Let's see how long Gipfelkorb takes to find it." | P2 / all | Störung (incident), Datenbanksperre (database lock) |
| **0:20** | **Tab 4, the shop.** Click one product. | "This is the shop. Right now it still answers. In a minute it will hang." Do not wait for it to hang. | BIZ | Kundenerlebnis (customer experience) |
| **0:40** | **Tab 1, dashboard.** Point at the five tiles, left to right. | "Mrs/Mr [BIZ], this is your view. Completed checkouts per minute, failed checkouts, slow requests, latency, and an estimate of revenue at risk. The estimate uses two assumptions, shown at the top: average order value and normal checkout rate. All of this comes from the same data your engineers use. No separate BI pipeline." | P4 / BIZ, CTO | Kaufabschlüsse (checkouts), Umsatzrisiko (revenue at risk), Annahme (assumption) |
| **1:30** | **Tab 2, service map.** Hover `frontend`, then `checkout`. | "Mr/Mrs [ENG], this is your landscape, drawn from OpenTelemetry traces. No agents per tool, no manual diagram. Every service, every dependency, with latency and errors. Today this lives in three tools. Here it is one store." | P1 / ENG | Abhängigkeiten (dependencies), verteiltes Tracing, Tool-Wildwuchs (tool sprawl) |
| **2:00** | **Tab 3, Slack.** The alert message is there (it arrives 1 to 2 minutes after the break; if it is not there yet, stay on the service map and keep talking until 3:00). Read the first two lines aloud. | "There it is. [N] seconds after the failure, the on-call engineer has this in Slack. Not a customer call. It says what is wrong, on which service, with the measured value, and it links straight to the evidence. This is Elastic's native Slack connector. No glue code. Teams, PagerDuty, ServiceNow, email and webhooks work the same way." | P2 / SRE | Alarmierung (alerting), Bereitschaftsdienst (on-call), Erkennungszeit (detection time) |
| **2:40** | **Click the link in the Slack message.** The alert details page opens in a new tab. Point at the status "Active", the chart with the threshold line, then the tabs **Investigation guide** and **Related dashboards**. | "One click from Slack to the alert. The chart shows latency against the threshold. The team's own runbook is attached to the rule, and so is the business dashboard. The engineer at 3 a.m. does not need to remember where to look." | P3 / SRE | Schwellenwert (threshold), Runbook, Ursachenanalyse (root cause analysis) |
| **3:30** | **Click "Add to chat"** in the page header. The AI Agent opens and sends *Investigate this alert* by itself. While it works, keep talking. | "Now the part that changes the night shift. I hand the alert to the Elastic AI Agent. It does not guess from a prompt. It queries your real traces, logs and metrics with your permissions. And it runs on Elastic's managed LLM with zero data retention, or on your own model if you prefer." | P3 / SRE, CTO | KI-Agent, Datenhoheit (data sovereignty) |
| **4:30** | **Read the answer.** Scroll to the conclusion. Point at the service name and the evidence. | "It says the frontend is slow because **product-catalog** is slow, and that product-catalog is waiting on the database. That is the correct service. I never told it." If the answer is weak, go to "If the AI answers poorly" below. | P3 / all | Ursache (root cause), betroffene Dienste (affected services) |
| **5:10** | **Type prompt 2** (below). | "A good engineer does not trust a summary. Let me ask for the evidence." Read the top row of the answer. | P3 / ENG | Nachweis (evidence) |
| **6:00** | **Terminal.** Run `scripts/fix.sh`. | "We know enough. I roll back the change." (`fix.sh` switches the flag off and restarts product-catalog.) Say the time out loud: "Six minutes from failure to fix. Today that takes Gipfelkorb [X] hours on average." (X is an assumption from the deck.) | P3 / CTO | Behebung (fix), Wiederherstellungszeit (time to resolve) |
| **6:20** | **Verify by hand. Tab 2, service map.** Click `product-catalog` > **Service Details**. Open the **Transactions** tab. Click `oteldemo.ProductCatalogService/GetProduct` (or `ListProducts`). Scroll to the trace sample. | "Mr/Mrs [ENG], here is the same finding without AI. One request. The frontend calls product-catalog. And here: one SQL query, 30 seconds. Normally 3 milliseconds." Point at the long `sql.conn.query` span. | P1, P3 / ENG | Trace, Spanne (span), Antwortzeit (response time) |
| **7:20** | **Same page, Logs tab** (or the "Logs" tab of the trace sample). Find the line `lock contention scenario active: holding ACCESS EXCLUSIVE lock on catalog.products`. | "And the log line from the same service, same second. Trace and log are linked by the trace ID because both arrive through OpenTelemetry into one store. In the current setup this is three tools and a chat thread." | P1 / ENG, SRE | Protokolle (logs), Korrelation |
| **8:10** | **AI Agent chat. Type prompt 3** (German summary). | "Mr/Mrs [CTO], you do not read traces. So I ask for your version." Read the German summary aloud. | P4 / CTO | Zusammenfassung (summary) |
| **9:00** | **Tab 1, dashboard.** Point at "Slow or failed shop requests" and "Revenue at risk". Then the chart "p95 latency by service": the spike and the drop after the fix. Then the two SLO panels. | "Mrs/Mr [BIZ], this is what the incident cost while it lasted, with the assumptions we agreed. And this is the error budget of the latency SLO. You can see this week's incidents in it. That is the conversation SLOs give you: not 'was there an alert' but 'how much reliability did we spend, and on what'." | P4 / BIZ, CTO | Fehlerbudget (error budget), Service-Level-Ziel (SLO) |
| **10:15** | **Tab 3, Slack.** The RECOVERED message is there (it arrives about 1 to 2 minutes after the fix, so it has been there for a while). | "And Slack tells the team it is over. Detected in about a minute, explained in three, fixed in six." | P2, P3 / SRE | Entwarnung (all clear) |
| **10:45** | **Slide or dashboard stays up.** Recap, one sentence per pain. | "Four pains, four answers. One: three tools became one store, fed by OpenTelemetry, so no lock-in on the way in. Two: the alert reached Slack before any customer called. Three: the AI Agent named the root cause and the engineer verified it in one screen. Four: the business saw the cost live." | P1 to P4 / all | Zusammenfassung |
| **11:30** | Go back to the slides (slide 7). | "Let me put numbers on that." | | Geschäftswert (business value) |
| **12:00** | **End of demo.** | | | |

### Hard time checks

- **3:00 and no Slack alert:** do not wait. Open tab **Alerts** (Observability > Alerts) and open the alert from there. If there is no alert either, go to `FALLBACK.md`, case B.
- **5:30 and the AI has no useful answer:** stop the AI part. Say the line in "If the AI answers poorly", run `scripts/fix.sh`, and continue at 6:20.
- **9:00 and you are still in traces:** skip prompt 3. Go to the dashboard.
- **11:30:** stop wherever you are. Say the recap. Finishing on time beats finishing the list.

## The AI prompts

Copy these into a note you can paste from. Typing live costs time.

**Prompt 1 (sent automatically by "Add to chat"):**
```
Investigate this alert
```

**Prompt 2 (evidence):**
```
Which downstream service causes the latency in frontend? Compare p95 span duration by service and span name for the last 15 minutes, and show log messages from the slowest service that mention locks, timeouts or errors.
```

**Prompt 3 (executive summary in German):**
```
Fasse für unseren CTO in drei Sätzen auf Deutsch zusammen: Was ist passiert, wie waren die Kunden betroffen, und was ist der nächste Schritt?
```

**Optional prompt 4 (only if you are ahead of time, for BIZ):**
```
How many checkouts completed in the last 10 minutes compared with the 10 minutes before? Use the "order placed" log messages of the checkout service.
```

### What a good answer contains

The data holds this evidence (verified in the test run):

- `frontend` p95 latency jumps from under 100 ms to several seconds. Requests end at 15 s (client timeout).
- `product-catalog` is the slowest service. Its `GetProduct` and `ListProducts` requests take up to 30 s.
- Inside them, the database span `sql.conn.query` takes up to 30 s.
- `product-catalog` logs: `lock contention scenario active: holding ACCESS EXCLUSIVE lock on catalog.products`.
- `frontend-proxy` logs show `504` responses with `response_timeout`. `load-generator` logs show `Timeout 15000ms exceeded`.

One trap in the data: the feature flag service keeps streaming connections open for 10 minutes (`flagd.evaluation.v2.Service/EventStream`). They look like very slow requests. If the agent blames `flagd`, say: "Those are long-lived streams, not slow requests. A good example of why the engineer stays in the loop." Then use the narrow prompt below.

A good answer names **product-catalog** and the **database lock** (or at least "slow database queries in product-catalog"). An acceptable answer names product-catalog as the slow dependency without the lock.

### If the AI answers poorly

Stay calm. Say this:

> "This is a useful moment. The agent gives a first hypothesis, and the engineer stays in charge. Let me narrow it down."

Then, in this order:

1. **Narrow prompt:**
   ```
   Look only at the service product-catalog in the last 15 minutes. Which span names are slowest, and what do its logs say about locks?
   ```
2. **Give it the query** (tested: the top rows show `frontend` waiting on `ProductCatalogService`, and `sql.conn.query` in `product-catalog`):
   ```
   Run this ES|QL and explain the result: FROM traces-*.otel-* | WHERE @timestamp > NOW() - 15 minutes AND name NOT LIKE "*EventStream*" AND kind IN ("Server", "Client") | STATS p95_ms = ROUND(PERCENTILE(duration, 95) / 1000000), spans = COUNT(*) BY service.name, name, kind | SORT p95_ms DESC | LIMIT 8
   ```
3. **Skip the AI.** Say: "Let me show you the same path by hand. It is three clicks." Go to the 6:20 step. The manual path proves the platform. The AI is the accelerator, not the foundation.

If the AI gives a **wrong** root cause, say so plainly: "That is not right, and here is how I know." Then show the trace. Honesty with a wrong AI answer scores better than defending it.

If the AI is **unavailable** (trial token limit, model error): `FALLBACK.md`, case C.

## After the demo

During Q&A, or right after the session:

```bash
scripts/reset.sh
```

It takes about 70 seconds (tested) and leaves the demo ready for another run. If you already ran `fix.sh`, it finishes faster.

## Numbers to fill in after your first rehearsal

| Number | Local test | Your Elastic Cloud rehearsal |
|---|---|---|
| Seconds from `break.sh` to Slack alert | 47, 49, 62, 96, 102 s | ____ |
| Seconds from `fix.sh` to RECOVERED in Slack | 65, 68 s | ____ |
| `reset.sh` duration | 70 to 71 s | ____ |
| Seconds for the AI Agent's first answer | not tested | ____ |
| "Completed checkouts" tile when healthy (for `BASELINE_ORDERS_PER_MIN`) | 2 to 3 at 5 shoppers | ____ |

## German glossary

| English | German |
|---|---|
| Observability | Observability (also: Beobachtbarkeit) |
| Incident | Störung, Vorfall |
| Alert, alerting | Alarm, Alarmierung |
| On-call | Bereitschaftsdienst, Pikett (Swiss) |
| Root cause analysis | Ursachenanalyse |
| Latency, response time | Latenz, Antwortzeit |
| Detection time (MTTD) | Erkennungszeit |
| Resolution time (MTTR) | Wiederherstellungszeit, Zeit bis zur Behebung |
| Error budget | Fehlerbudget |
| Service level objective | Service-Level-Ziel (SLO) |
| Tool sprawl | Tool-Wildwuchs |
| Vendor lock-in | Herstellerabhängigkeit, Lock-in |
| Data residency | Datenstandort, Datenhaltung in der Schweiz |
| Revenue at risk | Umsatzrisiko, gefährdeter Umsatz |
| Checkout | Kaufabschluss, Checkout |
| Shopping cart | Warenkorb |
| Database lock | Datenbanksperre |
| Logs, metrics, traces | Logs (Protokolle), Metriken, Traces |
| Business value | Geschäftswert, Nutzen |
| Proof of value / pilot | Pilot, Machbarkeitsnachweis |
