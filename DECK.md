# Deck outline: 10 slides, 30 minutes

Format per slide: headline, visual, speaker notes, German key terms, time.
Headlines are full sentences. A panellist who reads only the headlines should get the story.

**Every number about Gipfelkorb AG is an assumption.** Gipfelkorb AG is a made-up company. Each assumption is marked *(A)* and listed in the table at the end. Say "as you told us in discovery" when you use one. That is the role play.

## Time plan

| # | Slide | Minutes | Running total |
|---|---|---|---|
| 1 | Title and panel roles | 1:30 | 1:30 |
| 2 | Customer and pain | 3:00 | 4:30 |
| 3 | Desired outcomes | 1:30 | 6:00 |
| 4 | Architecture | 3:00 | 9:00 |
| 5 | Why Elastic | 2:00 | 11:00 |
| 6 | Live demo | 12:00 | 23:00 |
| 7 | Business value | 3:00 | 26:00 |
| 8 | Roadmap | 2:00 | 28:00 |
| 9 | Next steps | 1:00 | 29:00 |
| | Buffer (questions during the talk, slow screen share) | 1:00 | 30:00 |
| 10 | Appendix | Q&A only | |

Checkpoints: you must be **in the demo by 11:00** and **out of it by 23:00**. If you reach slide 6 late, shorten slides 8 and 9, not the demo.

The 10-minute intro before this is the panel's part plus your short introduction. Keep yours to 90 seconds: who you are, five years building production systems, customer-facing AI/ML work with large enterprises in Switzerland and Germany, and one line on why observability: "Every ML platform I ran was only as good as its monitoring."

---

## Slide 1. Title and roles (1:30)

**Headline:** From "the customer called us" to "we knew in a minute": observability for Gipfelkorb AG

**Visual:** Title on the left. On the right, four name cards: panellist name, the customer role they play, and what you will show them.

| Panellist | Role today | You will see |
|---|---|---|
| [RVP name] | CTO, executive sponsor | Risk, cost, a plan |
| [Senior Manager SA name] | Head of Platform / SRE lead | What on-call looks like afterwards |
| [Director SA name] | Head of E-Commerce | Revenue impact, live |
| [Principal SA name] | Lead Platform Engineer | Architecture, OpenTelemetry, scale |

**Speaker notes:** "Thank you for the time. To make this real, I would like to treat you as the Gipfelkorb team we met in discovery. [Name], you are the CTO. [Name], Head of Platform. [Name], Head of E-Commerce. [Name], Lead Platform Engineer. Is that all right? In the next 30 minutes: what we heard, what we propose, a live demo, the business case, and the next step. Please interrupt me."

Ask for the role agreement and wait for the nod. It sets up every later "Mr/Mrs CTO".

**German:** Vielen Dank für Ihre Zeit. Rollenverteilung. Unterbrechen Sie mich gerne.

---

## Slide 2. Customer and pain (3:00)

**Headline:** Today an incident at Gipfelkorb is found by customers and solved in a war room

**Visual:** The broken process as a horizontal flow with five steps and a clock under each. Under the flow, three large numbers.

```
Shop slows down → Customer complains → Support opens ticket → War room: 3 teams, 3 tools → Fix
      0 min            ~25 min (A)            ~35 min (A)          Grafana | log tool | Jaeger   ~3 h (A)
```

Under the flow:
- **6 of 10** incidents are reported by customers first *(A)*
- **~3 hours** average time to resolve *(A)*
- **~CHF 115,000** estimated revenue lost in one 47-minute slowdown on Black Friday 2025 *(A)*

Small box on the right, "Landscape": about 60 microservices on Kubernetes *(A)*, 8 product teams *(A)*, Prometheus and Grafana for metrics, a separate log tool, Jaeger for traces, Black Friday at about 12 times normal traffic *(A)*.

**Speaker notes:** "Let me play back what we heard. Tell me where I am wrong. Your shop runs on about 60 microservices on Kubernetes. You have good tools, but three of them: metrics in one, logs in another, traces in a third. When the shop slows down, the first person to notice is usually a customer. Then support, then a ticket, then a war room where three teams each look at their own tool and paste screenshots into a chat. On average it takes about three hours. [To BIZ] Last Black Friday, a 47-minute slowdown at peak cost you roughly CHF 115,000 by our estimate. [To SRE] And your on-call engineers spend the first half hour just finding out which service to look at. Did I get that right?"

Pause. Let them correct you. A correction is a gift: repeat it and use it later.

**German:** Störung, Tool-Wildwuchs, Kundenmeldung, Bereitschaftsdienst, Umsatzverlust, "Habe ich das richtig verstanden?"

---

## Slide 3. Desired outcomes (1:30)

**Headline:** Four outcomes, one for each pain

**Visual:** Two columns, four rows. Left column in red, right in green.

| Pain today | Outcome you asked for |
|---|---|
| ❌ Three tools, no shared context | ✅ One place for logs, metrics and traces |
| ❌ Customers report incidents first | ✅ We know before the customer does: detection in minutes |
| ❌ About 3 hours to resolve, in a war room | ✅ Root cause in minutes, by one engineer |
| ❌ Nobody sees the business cost during an incident | ✅ Revenue impact visible live, in CHF |

And one line underneath: "No lock-in on instrumentation: keep OpenTelemetry."

**Speaker notes:** "So success looks like this. One place instead of three. Knowing before the customer. Root cause in minutes, not hours. And for you, [BIZ] and [CTO], seeing what an incident costs while it happens. [To ENG] And you were clear on one condition: the teams have started with OpenTelemetry and you will not re-instrument for a vendor. We agree."

**German:** Zielbild, Erkennung in Minuten, Ursachenanalyse, kein Lock-in.

---

## Slide 4. Architecture (3:00)

**Headline:** OpenTelemetry in, one store, alerting and AI on top

**Visual:** `diagrams/architecture.svg`, full slide. It has the four numbered ❌ → ✅ callouts at the bottom.

**Speaker notes:** Walk left to right, then the callouts.
- "On the left, your services. They keep their OpenTelemetry SDKs. Where you want less work, Elastic's distributions of the OpenTelemetry SDKs, EDOT, are drop-in and fully upstream-compatible."
- "They send OTLP to a collector in your cluster. That is the EDOT Collector, which is the OpenTelemetry Collector with Elastic support."
- "The collector sends to Elastic's managed OTLP endpoint. [To ENG] The data is stored in OpenTelemetry format. No translation into a proprietary schema. Your attribute names stay your attribute names."
- "One store, Elasticsearch, holds all three signals, linked by trace ID."
- "On top: the Applications views with the service map, SLOs and alerting with native connectors to Slack or Teams, the AI Agent, and dashboards."
- Then the callouts, one sentence each: "Pain one, tool sprawl, is solved here. Pain two here..."

Features to name: Managed OTLP endpoint, EDOT, Applications (APM) and service map, SLOs, alerting rules and connectors, AI Agent (Agent Builder), dashboards with ES|QL.

**For ENG, if asked:** Kubernetes and host metrics come from the same collector. Prometheus endpoints can be scraped by the collector's Prometheus receiver, so existing exporters keep working.

**German:** Zielarchitektur, offener Standard, ein Datenspeicher, Signale verknüpft über die Trace-ID.

---

## Slide 5. Why Elastic (2:00)

**Headline:** Why Elastic for Gipfelkorb: open on the way in, one platform inside, your choice where it runs

**Visual:** Three columns, each with an icon, one claim and one proof.

| Open standards | One platform | Your terms |
|---|---|---|
| OpenTelemetry-native: data stored in OTel format through the managed OTLP endpoint | Logs, metrics and traces in one store, one query language (ES\|QL), one alerting engine | Serverless, Hosted or self-managed. Hosted has an AWS Zurich region |
| *Proof:* the demo uses the standard OpenTelemetry demo app, unchanged instrumentation | *Proof:* the AI Agent investigates across all three signals in one step | *Proof:* pay for data ingested and retained on Serverless, not per host or per user |

Footer: "The same platform also runs security analytics and search. One skill set, one data store, later."

**Speaker notes:** "Three reasons. First, open. You keep OpenTelemetry. If you ever leave Elastic, your instrumentation leaves with you. Second, one platform. Not three products with a shared login, but one data store. That is why the AI Agent you are about to see can follow a problem from a metric to a trace to a log line. Third, your terms. [To CTO] You can run this as a managed service, including in the AWS Zurich region for hosted deployments, or on your own infrastructure. And the price follows data volume, not the number of hosts or engineers."

Be fair about the current tools: "Prometheus, Grafana and Jaeger are good tools. The cost is not the tools. It is the gaps between them."

**German:** Offene Standards, eine Plattform, Datenstandort Schweiz, Betriebsmodell, verbrauchsbasierte Kosten.

---

## Slide 6. Live demo (12:00)

**Headline:** Black Friday, 10:14: the shop slows down

**Visual:** One sentence, large, and the four roles small at the bottom:

> "You will see a real slowdown, an alert in Slack in about a minute, the AI Agent finding the root cause, and the cost in francs. This addresses all four pains."

**Speaker notes:** Say the sentence. Then: "Everything is live. The shop runs on my laptop and sends its telemetry to Elastic Cloud right now." Switch to the terminal. Follow `RUNBOOK.md`.

**German:** Live-Demo, "Sie sehen gleich...".

---

## Slide 7. Business value (3:00)

**Headline:** The pilot targets: detection in minutes, resolution about a third faster, three tools become one

**Visual:** Before/after table. Right column narrower, with the source of each target.

| | Today *(A)* | Target with Elastic | Why we believe it |
|---|---|---|---|
| Time to detect | ~25 minutes, often by a customer | Under 2 minutes | Demo: about 1 minute. Oney Bank: from 20 minutes to 1 minute |
| Time to resolve | ~3 hours | ~2 hours (minus 30%) *(A)* | PepsiCo: MTTR minus 30%. Italian gas distributor: minus 25% |
| Tools for observability | 3 (metrics, logs, traces) | 1 | PepsiCo: from 55 monitoring tools to under 20. Oney Bank replaced 5 |
| Yearly tool and platform cost | ~CHF 420,000 *(A)* | Minus 20 to 30% *(A)*, to be validated with real volumes | Oney Bank: minus 30%. Italian gas distributor: minus 35% |
| Black Friday exposure | ~CHF 115,000 for one 47-minute slowdown *(A)* | Minutes instead of 47 | Detection and root cause as in the demo |

Bottom line, one sentence: "Estimated value in year one: about CHF 300,000 to 400,000 *(A)*, before the Black Friday effect. We will measure it in the pilot instead of asking you to believe it."

**Speaker notes:** "[To CTO] These are targets, not promises, and every 'today' number is what you told us or what we assumed. Detection: you saw about a minute. Oney Bank, a French consumer-finance company that serves retailers, went from 20 minutes to one minute and specifically mentions peak business periods. Resolution: PepsiCo reports 30% lower MTTR, an Italian gas distributor 25%. We plan with 30% for you and will measure it. Tools: three become one. Cost: other customers report 30 to 35% lower cost after consolidation. I am not going to promise you that number before I have seen your data volumes. That is what the pilot is for."

How the year-one estimate is built (keep on the appendix slide, show only if asked):
- Incidents: 24 customer-facing incidents per year *(A)*. Degraded minutes today: 24 × (25 + 180) = 4,920. Target: 24 × (2 + 126) = 3,072. Saved: about 1,850 minutes.
- Revenue: CHF 180 million online revenue per year *(A)* is about CHF 342 per minute. If 30% of revenue is lost while the shop is degraded *(A)*: about CHF 103 per minute. 1,850 × 103 ≈ **CHF 190,000**.
- Engineering time: a war room of 6 people *(A)* for 3 hours, 24 times a year, at CHF 120 per hour *(A)* is about CHF 52,000. One third saved: about **CHF 17,000**.
- Tooling: 25% of CHF 420,000 *(A)* is about **CHF 105,000**.
- Total: about **CHF 310,000**. Range CHF 300,000 to 400,000 depending on the cost saving.
- Black Friday: peak minute is about 12 × CHF 342 ≈ CHF 4,100 *(A)*. 47 minutes × 4,100 × 60% loss *(A)* ≈ CHF 115,000.

**German:** Geschäftswert, Erkennungszeit, Wiederherstellungszeit, Annahmen, "Wir messen es im Piloten".

---

## Slide 8. Roadmap (2:00)

**Headline:** Land on checkout before Black Friday, then expand service by service

**Visual:** Three phases on a timeline.

| Land: pilot (4 to 6 weeks) | Expand: all services (quarter 1 and 2) | Extend: platform (later) |
|---|---|---|
| One critical journey: checkout and its dependencies | All 60 services, Kubernetes and infrastructure metrics | Security analytics on the same data and platform |
| OTLP from the existing OpenTelemetry SDKs | SLOs per team, burn rate alerts, on-call routing | Synthetic monitoring of the shop from outside |
| 2 SLOs, alerts to Slack, business dashboard | Retire the separate log and tracing tools | AI Agent workflows for common incidents |
| **Success criteria:** detect in under 2 minutes, root cause of a test incident in under 15 minutes, agreed cost model | **Success criteria:** 3 tools to 1, MTTR minus 30% | **Success criteria:** agreed when we get there |

**Speaker notes:** "We do not ask for a big bang. Land: one journey, checkout, in four to six weeks, with success criteria we agree today. Because your teams already use OpenTelemetry, the pilot is mostly configuration: point the collector at a new endpoint. Existing tools keep running in parallel. Expand: once the pilot proves the numbers, we onboard the other services team by team and retire the log and tracing tools. Extend: the same platform and the same data can later serve your security team. That is a separate decision for a later day."

**German:** Pilot, Erfolgskriterien, schrittweise Einführung, Parallelbetrieb, Ablösung.

---

## Slide 9. Next steps (1:00)

**Headline:** Three decisions today get the pilot running in two weeks

**Visual:** Three numbered items, each with an owner and a date.

1. **Agree the pilot scope and success criteria.** Owner: Head of Platform and me. This week.
2. **Name two engineers and give access to a test cluster.** Owner: Lead Platform Engineer. Next week.
3. **Technical workshop, half a day:** data volumes, retention, residency, cost model. Owner: me, with the CTO's sponsor. Within two weeks.

**Speaker notes:** "[To CTO] To start, I need three things. Agreement on scope and success criteria. Two engineers and a test cluster. And half a day for a workshop on volumes, retention and residency, so that the cost model rests on your numbers and not on mine. Can we agree on these today? What would stop us?"

End on the question. Then stop talking.

**German:** Nächste Schritte, Verantwortliche, "Was würde uns aufhalten?"

---

## Slide 10. Appendix for Q&A (not presented)

One slide per topic, shown only when asked. Content is in `QA_PREP.md`.

| Appendix slide | Content |
|---|---|
| A1 Scaling and data volume | How volume is sized in the pilot. Sampling at the collector. Serverless scales by itself; Hosted scales by tier. |
| A2 Cost | Serverless: per GB ingested and retained. What drives volume. How logsdb and time series data streams reduce storage. |
| A3 Retention and data tiers | Hosted: hot, warm, cold, frozen with searchable snapshots. Serverless: retention per data stream, no tiers to manage. |
| A4 Security and residency | Regions (Hosted: AWS Zurich; Serverless: EU regions, no Swiss region today). API keys, roles, encryption. Where the LLM runs. PII redaction at the collector. |
| A5 Alternatives considered | Keep the three tools; Grafana stack; Datadog; Splunk. Fair comparison. |
| A6 Value model | The calculation behind slide 7, with every assumption. |
| A7 Customer references | PepsiCo, Oney Bank, Italian gas distributor, with links. |

---

## All assumptions in one place

Nothing in this table is measured or comes from a real company. Replace with your own story if you prefer other values, and keep the arithmetic consistent.

| Assumption | Value | Used on |
|---|---|---|
| Online revenue per year | CHF 180 million | 7 |
| Microservices | about 60 | 2, 8 |
| Product teams | 8 | 2 |
| Share of incidents reported by customers first | 6 of 10 | 2 |
| Average time to detect | 25 minutes | 2, 7 |
| Average time to resolve | 3 hours | 2, 7 |
| Customer-facing incidents per year | 24 | 7 |
| Revenue lost while the shop is degraded | 30% of normal | 7 |
| Black Friday peak traffic and revenue | 12 times normal | 2, 7 |
| Black Friday 2025 slowdown | 47 minutes, 60% of revenue lost during it | 2, 7 |
| War room | 6 people, CHF 120 per hour | 7 |
| Current yearly tool and platform cost | CHF 420,000 | 7 |
| Target MTTR reduction | 30% | 7, 8 |
| Target cost reduction | 20 to 30% | 7 |
| Dashboard: average order value | CHF 85 | demo |
| Dashboard: normal checkouts per minute | measured in rehearsal | demo |

Customer numbers on slide 7 (PepsiCo, Oney Bank, Italian gas distributor) are **not** assumptions. They are quoted from elastic.co. See `SOURCES.md`.

## Slides as a file

This is the outline. If you want the actual slides (PowerPoint, Google Slides or a web deck), tell me and I will build them from this file and the SVG.
