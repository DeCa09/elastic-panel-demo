# Q&A preparation

Ten minutes of questions. The panel scores composure, honesty and depth.

**How to answer.** Three steps, every time:
1. **Repeat the concern** in one short sentence. "You want to know what this costs at ten times the volume."
2. **Answer in 2 to 4 sentences.** Start with the answer, then the reason.
3. **Check.** "Does that answer it?" or "Shall I go deeper?"

**When you do not know:** "I do not know that for certain, and I would rather not guess. I will confirm it by tomorrow." Then write it down where they can see you do it. With a panel of Elastic employees, a confident wrong answer about their own product is the worst outcome.

**Facts and sources.** Product facts below are from Elastic's docs, checked on 13 November 2026 (`SOURCES.md`). Statements about competitors are general and public. Do not quote competitor prices or Elastic prices from memory.

---

## CTO / executive sponsor (RVP)

**What will this cost?**
On Serverless you pay for data ingested and data retained, per gigabyte, not per host or per user. So the cost follows your telemetry volume, which we control with sampling and retention. I will not give you a number today, because I have not seen your volumes. The half-day workshop is where we size it on your data, and the pilot gives us real numbers.

**Your value numbers are assumptions. Why should I believe them?**
You should not believe them yet. The "today" numbers are yours, the targets are ours, and the pilot has success criteria so we measure instead of argue. What I can show as evidence is public: PepsiCo reports 30% lower MTTR, and Oney Bank cut detection time from 20 minutes to one minute. Both are on elastic.co.

**What is the risk if this fails?**
Low, by design. Your teams keep their OpenTelemetry instrumentation and your current tools keep running in parallel during the pilot. If the pilot misses its criteria, you switch one collector setting back and have lost four to six weeks of a small team's time.

**Why not just fix our processes? We already own three tools.**
Process helps, and SLOs are part of our proposal for that reason. But the delay in your incidents comes from the gaps between the tools: three logins, three query languages, no shared trace ID. No process removes that. One store does.

**Where does our data go? We are a Swiss company.**
You choose the region. Elastic Cloud Hosted has an AWS Zurich region. Serverless today offers EU regions such as Frankfurt, but no Swiss region. If Swiss residency is a hard requirement, we plan with Hosted in Zurich or a self-managed deployment. I would confirm the exact requirement with your data protection officer first.

**And the AI? Does our data train a model?**
The Elastic Managed LLM is configured for zero data retention, per Elastic's documentation. Elastic's inference service has EU regions, including Zurich, and EU projects are routed to an EU region. The docs also say that model providers may process requests in other regions, so if that matters we would connect your own model instead. That is supported.

**How long until we see value?**
The pilot shows detection and root-cause speed on checkout within four to six weeks. Tool consolidation and its cost effect come in the expand phase, over the following two quarters.

---

## Head of Platform / SRE lead (Senior Manager SA)

**We already have alerts. They are noisy. Why would this be better?**
Two things change. Alerts are based on what the customer feels, latency and failed checkouts, and on SLO burn rates, instead of on CPU thresholds. And every alert carries its context: the chart, the runbook, the related dashboard, and one click to an AI investigation. Fewer alerts, each more useful.

**How do we migrate without a risky cut-over?**
We run in parallel. The OpenTelemetry Collector can export to your current backends and to Elastic at the same time. We start with checkout, compare for a few weeks, then move team by team. Dashboards and alert rules are rebuilt, not converted, so we do the important ones first.

**What happens to our Prometheus exporters and Grafana dashboards?**
Exporters keep working. The collector has a Prometheus receiver that scrapes them. Grafana dashboards do not move automatically. In the pilot we rebuild the handful that matter for checkout and see how much work that is before we commit to the rest.

**Who gets paged? We use Teams, not Slack.**
Elastic has a native Microsoft Teams connector, plus PagerDuty, Opsgenie, ServiceNow, email and generic webhooks. The demo used Slack because it was the quickest to set up. The rule and the message stay the same.

**How much do I have to trust the AI Agent?**
As much as a good junior colleague: it gives you a first hypothesis quickly and shows its evidence. It queries your data with your permissions, so you can check each step. In the demo I verified its answer in the trace view. That is how I would run it in production too.

**Your demo alert fired in a minute. Is that realistic in production?**
The rule checks every minute on trace data, so one to two minutes is realistic for a clear threshold breach. I should be open about one thing: I first used the APM latency rule, which reads one-minute rollups and took two to three minutes. For the demo I chose a custom threshold rule on raw traces. In production I would combine a fast threshold rule with SLO burn rate rules to keep noise down.

**How do we stop one team's debug logging from blowing up the bill?**
At the collector, before the data leaves your cluster: filter, sample and drop by attribute. In Elastic, set retention per data stream, and watch ingest per service on a dashboard. Cost per team becomes visible, which usually fixes the behaviour.

---

## Head of E-Commerce / business owner (Director SA)

**How do you calculate "revenue at risk"?**
In the demo it is a simple, visible formula: the share of shop requests that failed or took longer than one second, times your normal checkout rate, times your average order value. The two business numbers are assumptions shown on the dashboard. With your real conversion data we would replace the estimate with a measured one.

**Can I see this without learning your tool?**
Yes. The dashboard is a link. And the same alert that goes to engineers can go to a business channel in plain language. In the demo the AI Agent wrote a three-sentence summary in German for exactly that purpose.

**Does this slow down my shop?**
OpenTelemetry instrumentation adds a small overhead, and it is already in your services today. We would measure it on checkout in the pilot rather than quote a general number. Telemetry is sent asynchronously through a collector, so a problem on the Elastic side does not block a checkout.

**What about Black Friday specifically?**
Three things before the day: SLOs on checkout and payment with burn rate alerts, a load test with the alerts live, and the business dashboard on a screen in the room. On the day, the on-call engineer gets the alert in about a minute and a root cause hypothesis a few minutes later, instead of after the first customer complaints.

**Can it tell me which customers were affected?**
If the services put a customer or session identifier on their traces, yes, and you can count affected sessions or orders directly. Whether to send such identifiers is a privacy decision. We can also redact or hash them at the collector.

---

## Lead Platform Engineer (Principal SA)

**OpenTelemetry or Elastic agents? What do you actually recommend?**
OpenTelemetry. Applications use the OpenTelemetry SDKs or EDOT, Elastic's distributions of them, which stay compatible with upstream. The collector is the EDOT Collector, which from 9.5 is built into Elastic Agent. Data goes to the managed OTLP endpoint and is stored in OpenTelemetry format without translation.

**Is that real OTel-native storage, or do you translate to ECS?**
Through the managed OTLP endpoint it is stored natively: resource attributes and semantic conventions are preserved. I saw that in the demo data: fields like `resource.attributes.*`, `attributes.*`, span `kind` and `duration` in nanoseconds, in data streams such as `traces-generic.otel-default`. The older APM Server path does translate to ECS. Elastic's docs call that the legacy ingest path.

**How does it scale? We produce a lot of telemetry.**
On Serverless, ingest and search scale automatically and you pay by volume. On Hosted you size the deployment and use data tiers. Either way the first lever is at the edge: sampling and filtering in the collector. I would size it on measured volume from the pilot rather than on an estimate.

**What about tail-based sampling?**
The managed OTLP endpoint does not do tail-based sampling. Elastic's docs say so plainly. You do it at the edge with the collector's tail sampling processor, which also keeps the unsampled data inside your network. On Hosted with APM Server, tail-based sampling exists server-side.

**How do you keep storage cost down for logs and metrics?**
Logs use the logsdb index mode, which Elastic's benchmarks put at up to 60% less storage. Metrics use time series data streams, about 70% less in their benchmarks. On Hosted you add data tiers: hot, warm, cold and frozen on object storage with searchable snapshots. On Serverless there are no tiers to manage; you set retention per data stream.

**Retention: what do you propose?**
A starting point to validate in the workshop: traces 7 to 14 days, logs 30 days searchable, metrics 90 days or more with downsampling, and longer for audit-relevant logs. Retention is set per data stream, so checkout logs and debug logs do not need the same policy.

**Vendor lock-in. Be honest.**
Instrumentation and the collector are open, so the way in has no lock-in. The data keeps OpenTelemetry field names and can be exported through the APIs. What is specific to Elastic is what you build on top: dashboards, rules, SLO definitions and ES|QL queries. That is the same with every backend. It is why I keep the instrumentation layer strictly open.

**How is the telemetry secured?**
TLS in transit, encryption at rest, and API keys with narrow rights: the ingest key that the onboarding page creates is meant only for writing telemetry. Access in Kibana is by role and space. Sensitive attributes should be removed at the collector before they leave your cluster. The OpenTelemetry Collector has processors for redaction and filtering. On Serverless Complete and Hosted you can add private connectivity and IP filtering.

**What did not work in your demo setup?**
Three honest points. The APM latency rule was too slow for a 12-minute demo because it reads one-minute rollups, so I used a custom threshold rule. The feature flag service keeps long-lived streaming spans that look like slow requests and can mislead a naive query. And the AI Assistant I first planned to use is deprecated in favour of the AI Agent, which does not yet have the Assistant's knowledge base. I adapted to all three.

**AI Assistant or AI Agent? Which is it?**
The AI Agent, built with Agent Builder, is now the default chat in Observability. The AI Assistant for Observability is deprecated. The Agent can start from an alert with "Add to chat" or from the service map. It does not yet have the Assistant's knowledge base, so team-specific runbooks go into the rule's investigation guide for now.

**Why Kubernetes on a laptop was not in the demo.**
The demo ran with Docker Compose to keep the laptop stable. The same fork deploys to Kubernetes with Helm and the EDOT Collector as a DaemonSet plus gateway, which also adds pod logs, kubelet metrics and Kubernetes events. That is the setup I would use in your pilot.

---

## Why not Datadog, Grafana or Splunk?

Keep it fair. Start every answer with something true and positive about the other product. Never claim a competitor "cannot" do something unless you are certain.

**Why not Datadog?**
Datadog is a strong product and quick to start with. Two differences matter for Gipfelkorb. Deployment and residency: Datadog is SaaS only, while Elastic can run as Serverless, Hosted in a region you choose including Zurich, or self-managed. And the cost model: Elastic Serverless charges by data volume, where Datadog's public pricing is mostly per host and per product. With 60 services and a Black Friday peak, I would compare both on your real volumes rather than claim one is cheaper.

**Why not stay with Grafana and add Loki and Tempo?**
That is a reasonable path and it is open source, which fits your culture. It remains several backends, each with its own storage and query language, that your team runs and correlates. Our proposal is one store and one query language for all three signals, with the AI Agent working across them. If your team wants to operate that stack and has the capacity, it can work. You told us the gaps between tools are the problem.

**Why not Splunk?**
Splunk is very capable for logs, and many security teams know it. Its observability product and its log platform are separate products. Elastic gives you logs, metrics, traces, and later security analytics on one data store, with OpenTelemetry data stored natively. If you already had a large Splunk estate I would look at coexistence. You do not, so there is nothing to protect.

**Why not keep what we have and just add an AI tool on top?**
An AI layer over three tools still has to join data that shares no IDs and lives behind three APIs. The agent in the demo was fast because traces, logs and metrics were already linked in one place. The data foundation comes first. The AI is the accelerator.

---

## Social proof: real Elastic Observability customers

All numbers are quoted from the customer pages on elastic.co, read on 13 November 2026. Read the pages again before the interview. Use the numbers exactly as written.

| Customer | What Elastic's page says | Use it for | Link |
|---|---|---|---|
| **Oney Bank** (France; consumer finance for retailers such as Leroy Merlin and Boulanger) | Incident detection time reduced by 95%, "from 20 minutes to just one minute, ensuring system continuity during peak business periods". Replaced five monitoring tools. Saves 30% of its costs annually. Service availability improved by 30%. | The closest match: European, retail-facing, peak periods, tool consolidation, detection time. | https://www.elastic.co/customers/oney-bank |
| **PepsiCo** | "Reduced MTTR by 30% with Elastic Observability". Monitoring tools reduced "from 55 to less than 20". 99.9% uptime. Hardware costs lowered by up to 25% annually. | Resolution time and tool consolidation at very large scale. | https://www.elastic.co/customers/pepsico |
| **Italy's leading gas distribution company** (not named on the page) | 99% uptime for its IT infrastructure. MTTR reduced by 25%. Cost of observability activities reduced by 35%. | A second European data point for MTTR and cost. Say "an Italian gas distributor"; do not guess the name. | https://www.elastic.co/customers/italian-gas-distribution |

One line to say: "Oney Bank is the closest to you: European, serving retailers, and they went from 20 minutes to one minute to detect an incident, with peak periods as the stated reason."

---

## Land and expand

**Land (4 to 6 weeks): one journey.**
Checkout and its dependencies. Point the existing OpenTelemetry collector at Elastic, in parallel to the current tools. Two SLOs, alerts to the team's channel, one business dashboard. Success criteria agreed up front: detection under 2 minutes, root cause of a test incident under 15 minutes, a cost model based on measured volume. Sponsor: CTO. Champion: Head of Platform.

**Expand (two quarters): all services, then retire tools.**
Onboard the remaining teams one by one, each with its own SLOs. Add Kubernetes and infrastructure metrics. When a team is fully on Elastic, its logs and traces stop going to the old tools. The business case grows with each retired tool. The Head of E-Commerce gets Black Friday readiness: load test with live alerts, dashboard in the room.

**Extend (later): the same platform for security.**
The logs are already there. Security analytics can run on the same platform with the same skills. That is a separate decision with a separate sponsor, usually the CISO. Mention it once, as an option, and move on. This presentation is about observability.

**Why this order works for the customer:** small first commitment, proof on their own data, and each step pays for the next.

---

## Questions to ask the panel (if time is left)

- "As the Gipfelkorb team: what would have to be true after the pilot for you to say yes to the expand phase?"
- "Which of the four pains hurts most today?"
- And out of role, at the very end: "What separates the solutions architects who do well in the DACH team in their first year?"
