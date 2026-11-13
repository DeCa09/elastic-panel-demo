#!/usr/bin/env python3
"""Create the Elastic objects for the panel demo through the Kibana APIs.

Creates, in this order:
  1. an alerting connector (Slack webhook, Microsoft Teams webhook, or server log)
  2. two SLOs (shop latency, checkout availability)
  3. a business dashboard (Dashboards API, needs Kibana 9.5+ or Serverless)
  4. two alert rules (latency custom threshold with the connector, SLO burn rate)

Safe to run again: every object has a fixed ID and is replaced or updated.
Uses only the Python standard library. Reads settings from the environment
(scripts/setup-elastic.sh loads .env first). Never prints secrets.

Usage:
  python3 elastic/setup_elastic.py [all|connector|slos|rules|dashboard|test-connector|status|delete]
"""

import json
import os
import sys
import urllib.error
import urllib.request
import uuid

KIBANA_URL = os.environ.get("KIBANA_URL", "").rstrip("/")
API_KEY = os.environ.get("ELASTIC_API_KEY", "")
SPACE = os.environ.get("KIBANA_SPACE", "").strip()
CHANNEL = os.environ.get("ALERT_CHANNEL", "slack").strip().lower()
SLACK_WEBHOOK_URL = os.environ.get("SLACK_WEBHOOK_URL", "")
TEAMS_WEBHOOK_URL = os.environ.get("TEAMS_WEBHOOK_URL", "")

SHOP_SERVICE = os.environ.get("SHOP_SERVICE", "frontend")
CHECKOUT_SERVICE = os.environ.get("CHECKOUT_SERVICE", "checkout")
LATENCY_THRESHOLD_MS = int(os.environ.get("LATENCY_THRESHOLD_MS", "1000"))
SLO_APM_INDEX = os.environ.get("SLO_APM_INDEX", "metrics-apm*,apm-*,metrics-*.otel-*")
TRACES_INDEX = os.environ.get("TRACES_INDEX", "traces-*.otel-*")
LOGS_INDEX = os.environ.get("LOGS_INDEX", "logs-*.otel-*")

# Business assumptions for the dashboard. They are labelled as assumptions on
# the dashboard itself. Change them in .env.
AOV_CHF = float(os.environ.get("ASSUMED_AVG_ORDER_VALUE_CHF", "85"))
BASELINE_ORDERS_PER_MIN = float(os.environ.get("BASELINE_ORDERS_PER_MIN", "3"))

NAMESPACE = uuid.UUID("6f1d3c0a-7b1e-4c55-9d0e-0b5a5f0e2b11")


def fixed_id(name):
    """Stable UUID per object name, so reruns update instead of duplicating."""
    return str(uuid.uuid5(NAMESPACE, name))


CONNECTOR_ID = fixed_id("connector")
RULE_LATENCY_ID = fixed_id("rule-latency")
RULE_BURN_ID = fixed_id("rule-burn-rate")
SLO_LATENCY_ID = fixed_id("slo-latency").replace("-", "")
SLO_CHECKOUT_ID = fixed_id("slo-checkout").replace("-", "")
DASHBOARD_ID = fixed_id("dashboard")
TAG = "panel-demo"


class ApiError(Exception):
    def __init__(self, status, body):
        super().__init__("HTTP %s: %s" % (status, body[:600]))
        self.status = status
        self.body = body


def call(method, path, body=None, ok_missing=False):
    prefix = "/s/%s" % SPACE if SPACE else ""
    req = urllib.request.Request(
        KIBANA_URL + prefix + path,
        method=method,
        data=json.dumps(body).encode() if body is not None else None,
        headers={
            "Authorization": "ApiKey " + API_KEY,
            "kbn-xsrf": "true",
            "Content-Type": "application/json",
            # Accepted by Hosted and required by some Serverless endpoints.
            "elastic-api-version": "2023-10-31",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            raw = resp.read().decode()
            return json.loads(raw) if raw.strip() else {}
    except urllib.error.HTTPError as err:
        if ok_missing and err.code == 404:
            return None
        raise ApiError(err.code, err.read().decode(errors="replace"))


def info(msg):
    print("  " + msg)


# ---------------------------------------------------------------- connector

def connector_spec():
    if CHANNEL == "slack":
        if not SLACK_WEBHOOK_URL:
            sys.exit("ALERT_CHANNEL=slack but SLACK_WEBHOOK_URL is empty in .env")
        return {
            "name": "Panel demo: Slack #shop-alerts",
            "connector_type_id": ".slack",
            "secrets": {"webhookUrl": SLACK_WEBHOOK_URL},
        }
    if CHANNEL == "teams":
        if not TEAMS_WEBHOOK_URL:
            sys.exit("ALERT_CHANNEL=teams but TEAMS_WEBHOOK_URL is empty in .env")
        return {
            "name": "Panel demo: Microsoft Teams",
            "connector_type_id": ".teams",
            "secrets": {"webhookUrl": TEAMS_WEBHOOK_URL},
        }
    if CHANNEL == "serverlog":
        # Dry-run target: writes the alert text to the Kibana server log.
        return {"name": "Panel demo: server log (dry run)", "connector_type_id": ".server-log"}
    sys.exit("ALERT_CHANNEL must be slack, teams or serverlog")


def action_params(message):
    if CHANNEL == "serverlog":
        return {"message": message, "level": "warn"}
    return {"message": message}


def create_connector():
    print("Connector (%s)" % CHANNEL)
    # Rules reference the connector, so remove them first.
    for rule_id in (RULE_LATENCY_ID, RULE_BURN_ID):
        call("DELETE", "/api/alerting/rule/" + rule_id, ok_missing=True)
    call("DELETE", "/api/actions/connector/" + CONNECTOR_ID, ok_missing=True)
    out = call("POST", "/api/actions/connector/" + CONNECTOR_ID, connector_spec())
    info("created connector %s (%s)" % (out["name"], out["connector_type_id"]))


def test_connector():
    print("Connector test")
    text = "Preflight test from the Elastic panel demo. If you can read this, the connector works."
    out = call("POST", "/api/actions/connector/%s/_execute" % CONNECTOR_ID,
               {"params": action_params(text)})
    if out.get("status") != "ok":
        sys.exit("connector test failed: %s %s"
                 % (out.get("message", ""), out.get("service_message", "")))
    info("connector answered ok")


# --------------------------------------------------------------------- SLOs

def slo_bodies():
    latency = {
        "id": SLO_LATENCY_ID,
        "name": "Shop latency: 99%% of requests under %d ms" % LATENCY_THRESHOLD_MS,
        "description": "Share of %s requests served in under %d ms."
                       % (SHOP_SERVICE, LATENCY_THRESHOLD_MS),
        "indicator": {
            "type": "sli.apm.transactionDuration",
            "params": {
                "service": SHOP_SERVICE,
                "environment": "*",
                "transactionType": "request",
                "transactionName": "*",
                "threshold": LATENCY_THRESHOLD_MS,
                "index": SLO_APM_INDEX,
            },
        },
        "timeWindow": {"duration": "7d", "type": "rolling"},
        "budgetingMethod": "occurrences",
        "objective": {"target": 0.99},
        "tags": [TAG],
    }
    checkout = {
        "id": SLO_CHECKOUT_ID,
        "name": "Checkout availability: 99.5% of orders succeed",
        "description": "Share of %s requests that do not fail." % CHECKOUT_SERVICE,
        "indicator": {
            "type": "sli.apm.transactionErrorRate",
            "params": {
                "service": CHECKOUT_SERVICE,
                "environment": "*",
                "transactionType": "request",
                "transactionName": "*",
                "index": SLO_APM_INDEX,
            },
        },
        "timeWindow": {"duration": "7d", "type": "rolling"},
        "budgetingMethod": "occurrences",
        "objective": {"target": 0.995},
        "tags": [TAG],
    }
    return [latency, checkout]


def create_slos():
    print("SLOs")
    for body in slo_bodies():
        existing = call("GET", "/api/observability/slos/" + body["id"], ok_missing=True)
        if existing:
            # Update in place so the SLO keeps its history.
            update = dict(body)
            update.pop("id")
            call("PUT", "/api/observability/slos/" + body["id"], update)
            info("updated SLO: " + body["name"])
        else:
            call("POST", "/api/observability/slos", body)
            info("created SLO: " + body["name"])


# -------------------------------------------------------------------- rules

FIRING_TEXT = (
    "ALERT: {{rule.name}}\n"
    "{{context.reason}}\n"
    "Open the alert in Elastic: {{context.alertDetailsUrl}}"
)
RECOVERED_TEXT = (
    "RECOVERED: {{rule.name}}\n"
    "Shop latency is back under the threshold.\n"
    "Details: {{context.alertDetailsUrl}}"
)


INVESTIGATION_GUIDE = (
    "## Shop is slow\n"
    "1. Open **Applications > Service inventory > Service map**. Find the service with the highest latency.\n"
    "2. Open a slow trace of that service. Look for the longest span.\n"
    "3. Check the logs of that service for the same time.\n"
    "4. Open the related dashboard to see the business impact.\n"
    "5. Or ask the AI Agent: *Investigate this alert*."
)


def create_rules():
    print("Alert rules")
    for rule_id in (RULE_LATENCY_ID, RULE_BURN_ID):
        call("DELETE", "/api/alerting/rule/" + rule_id, ok_missing=True)

    on_change = {"summary": False, "notify_when": "onActionGroupChange", "throttle": None}
    # Custom threshold rule on raw trace data. It sees a slow request within
    # seconds. The APM latency rule reads 1-minute rollups and fires 2 to 3
    # minutes later, which is too slow for a 12-minute demo.
    latency_rule = {
        "name": "Shop is slow: %s p95 latency above %d ms" % (SHOP_SERVICE, LATENCY_THRESHOLD_MS),
        "rule_type_id": "observability.rules.custom_threshold",
        "consumer": "logs",
        "schedule": {"interval": "1m"},
        "tags": [TAG],
        # Rehearsals switch the failure on and off many times. Kibana would mark
        # the alert as "flapping" and then hold back the recovery for several
        # minutes. A threshold of 20 changes in 20 runs keeps that from happening.
        "flapping": {"look_back_window": 20, "status_change_threshold": 20},
        "params": {
            "criteria": [{
                "comparator": ">",
                "threshold": [LATENCY_THRESHOLD_MS],
                "timeSize": 1,
                "timeUnit": "m",
                "metrics": [{"name": "A", "aggType": "p95", "field": "duration"}],
                "equation": "A / 1000000",  # span duration is stored in nanoseconds
                "label": "p95 latency (ms)",
            }],
            "alertOnNoData": False,
            "alertOnGroupDisappear": False,
            "searchConfiguration": {
                "index": {"id": "panel-demo-traces", "title": TRACES_INDEX,
                          "timeFieldName": "@timestamp"},
                "query": {"query": 'service.name: "%s" and kind: "Server"' % SHOP_SERVICE,
                          "language": "kuery"},
            },
            "groupBy": ["service.name"],
        },
        # Shown on the alert details page: tabs "Investigation guide" and "Related dashboards".
        "artifacts": {
            "dashboards": [{"id": DASHBOARD_ID}],
            "investigation_guide": {"blob": INVESTIGATION_GUIDE},
        },
        "actions": [
            {"id": CONNECTOR_ID, "group": "custom_threshold.fired",
             "params": action_params(FIRING_TEXT), "frequency": on_change},
            {"id": CONNECTOR_ID, "group": "recovered",
             "params": action_params(RECOVERED_TEXT), "frequency": on_change},
        ],
    }
    try:
        out = call("POST", "/api/alerting/rule/" + RULE_LATENCY_ID, latency_rule)
    except ApiError as err:
        if err.status not in (400, 403):
            raise
        latency_rule["consumer"] = "observability"
        out = call("POST", "/api/alerting/rule/" + RULE_LATENCY_ID, latency_rule)
    info("created rule: " + out["name"])

    # Burn rate rule: how production alerting on the SLO would look.
    # It has no connector action, so the demo gets exactly one Slack alert.
    burn_rule = {
        "name": "Shop latency SLO is burning its error budget",
        "rule_type_id": "slo.rules.burnRate",
        "consumer": "slo",
        "schedule": {"interval": "1m"},
        "tags": [TAG],
        "params": {
            "sloId": SLO_LATENCY_ID,
            "windows": [
                {"id": fixed_id("w-critical"), "burnRateThreshold": 14.4,
                 "maxBurnRateThreshold": 168,
                 "longWindow": {"value": 1, "unit": "h"},
                 "shortWindow": {"value": 5, "unit": "m"},
                 "actionGroup": "slo.burnRate.alert"},
                {"id": fixed_id("w-high"), "burnRateThreshold": 6,
                 "maxBurnRateThreshold": 28,
                 "longWindow": {"value": 6, "unit": "h"},
                 "shortWindow": {"value": 30, "unit": "m"},
                 "actionGroup": "slo.burnRate.high"},
            ],
        },
        "actions": [],
    }
    out = call("POST", "/api/alerting/rule/" + RULE_BURN_ID, burn_rule)
    info("created rule: " + out["name"])


# ---------------------------------------------------------------- dashboard

def vis(x, y, w, h, config):
    return {"grid": {"x": x, "y": y, "w": w, "h": h}, "type": "vis", "config": config}


def metric(title, query, column, label, subtitle=None):
    primary = {"type": "primary", "column": column, "label": label}
    if subtitle:
        primary["subtitle"] = subtitle
    return {
        "type": "metric",
        "title": title,
        "data_source": {"type": "esql", "query": query},
        "metrics": [primary],
    }


def timeseries(title, query, y_column, kind="line", breakdown=None):
    layer = {
        "type": kind,
        "data_source": {"type": "esql", "query": query},
        "x": {"column": "t"},
        "y": [{"column": y_column}],
    }
    if breakdown:
        layer["breakdown_by"] = {"column": breakdown}
    return {"type": "xy", "title": title, "layers": [layer],
            "axis": {"x": {"title": {"visible": False}}}}


def dashboard_body():
    bucket = "t = BUCKET(@timestamp, 60, ?_tstart, ?_tend)"
    orders = 'FROM %s | WHERE service.name == "%s" AND body.text == "order placed"' % (
        LOGS_INDEX, CHECKOUT_SERVICE)
    minutes = "minutes = GREATEST(DATE_DIFF(\"second\", ?_tstart, ?_tend) / 60.0, 1.0)"
    server_spans = 'FROM %s | WHERE kind == "Server"' % TRACES_INDEX

    q_orders_per_min = (
        "%s | STATS orders = COUNT(*) | EVAL %s"
        " | EVAL orders_per_min = ROUND(orders / minutes, 1) | KEEP orders_per_min"
        % (orders, minutes))
    recent_shop = (
        '%s AND service.name == "%s" AND @timestamp > NOW() - 5 minutes'
        ' | STATS total = COUNT(*), bad = COUNT(*) WHERE status.code == "Error" OR duration > %d'
        " | EVAL bad_share = TO_DOUBLE(bad) / GREATEST(total, 1)"
        % (server_spans, SHOP_SERVICE, LATENCY_THRESHOLD_MS * 1000000))
    q_bad_share = recent_shop + " | EVAL bad_pct = ROUND(bad_share * 100, 1) | KEEP bad_pct"
    q_revenue_at_risk = (
        recent_shop + " | EVAL chf_at_risk_per_min = ROUND(bad_share * %s * %s) | KEEP chf_at_risk_per_min"
        % (BASELINE_ORDERS_PER_MIN, AOV_CHF))
    q_failed_checkouts = (
        '%s AND service.name == "frontend-proxy" AND name LIKE "POST *api/checkout*"'
        ' | STATS failed_checkouts = COUNT(*) WHERE status.code == "Error"' % server_spans)
    q_shop_p95 = (
        '%s AND service.name == "%s" AND @timestamp > NOW() - 5 minutes'
        " | STATS p95_ms = ROUND(PERCENTILE(duration, 95) / 1000000)" % (server_spans, SHOP_SERVICE))
    q_orders_ts = "%s | STATS orders = COUNT(*) BY %s" % (orders, bucket)
    q_latency_ts = (
        '%s AND service.name IN ("frontend", "checkout", "product-catalog", "cart", "payment")'
        " | STATS p95_ms = ROUND(PERCENTILE(duration, 95) / 1000000) BY %s, service.name"
        % (server_spans, bucket))
    q_errors_ts = (
        '%s AND status.code == "Error" | STATS failed_requests = COUNT(*) BY %s, service.name'
        % (server_spans, bucket))

    notes = (
        "## Online shop: business impact\n"
        "What an incident costs, from the same telemetry the engineers use.\n\n"
        "**Assumptions (not measured):** average order value CHF %g; normal rate %g completed "
        "checkouts per minute. **Revenue at risk per minute** = share of shop requests that failed "
        "or took longer than %d ms (last 5 minutes) x normal rate x average order value."
        % (AOV_CHF, BASELINE_ORDERS_PER_MIN, LATENCY_THRESHOLD_MS))

    panels = [
        {"grid": {"x": 0, "y": 0, "w": 48, "h": 7}, "type": "markdown",
         "config": {"content": notes, "settings": {"open_links_in_new_tab": True},
                    "hide_title": True}},
        vis(0, 7, 10, 6, metric("Completed checkouts", q_orders_per_min, "orders_per_min",
                                "orders per minute")),
        vis(10, 7, 9, 6, metric("Failed checkouts", q_failed_checkouts, "failed_checkouts",
                                "in the selected time range")),
        vis(19, 7, 9, 6, metric("Slow or failed shop requests", q_bad_share, "bad_pct",
                                "% of requests, last 5 min")),
        vis(28, 7, 10, 6, metric("Shop latency", q_shop_p95, "p95_ms", "p95 in ms, last 5 min")),
        vis(38, 7, 10, 6, metric("Revenue at risk (estimate)", q_revenue_at_risk,
                                 "chf_at_risk_per_min", "CHF per minute", "based on assumptions")),
        vis(0, 13, 24, 10, timeseries("Completed checkouts over time", q_orders_ts, "orders", "bar")),
        vis(24, 13, 24, 10, timeseries("p95 latency by service (ms)", q_latency_ts, "p95_ms",
                                       "line", "service.name")),
        {"grid": {"x": 0, "y": 23, "w": 12, "h": 9}, "type": "slo_overview",
         "config": {"slo_id": SLO_LATENCY_ID, "overview_mode": "single"}},
        {"grid": {"x": 12, "y": 23, "w": 12, "h": 9}, "type": "slo_overview",
         "config": {"slo_id": SLO_CHECKOUT_ID, "overview_mode": "single"}},
        vis(24, 23, 24, 9, timeseries("Failed requests by service", q_errors_ts, "failed_requests",
                                      "bar_stacked", "service.name")),
    ]
    return {
        "title": "Shop business impact (panel demo)",
        "description": "Checkouts, failed checkouts, latency and estimated revenue at risk.",
        "time_range": {"from": "now-15m", "to": "now"},
        "refresh_interval": {"pause": False, "value": 10000},
        "panels": panels,
    }


def create_dashboard():
    print("Dashboard")
    body = dashboard_body()
    try:
        call("PUT", "/api/dashboards/" + DASHBOARD_ID, body)
    except ApiError as err:
        if err.status in (400, 404) and "refresh_interval" in err.body:
            body.pop("refresh_interval")
            call("PUT", "/api/dashboards/" + DASHBOARD_ID, body)
        elif err.status == 404:
            sys.exit("This Kibana has no Dashboards API (needs 9.5+ or Serverless). "
                     "Build the dashboard by hand: see SETUP.md, 'Dashboard by hand'.")
        else:
            raise
    info("dashboard ready: %s/app/dashboards#/view/%s"
         % (KIBANA_URL + ("/s/" + SPACE if SPACE else ""), DASHBOARD_ID))


# ------------------------------------------------------------ status/delete

def status():
    """Print one line per object. Exit code 1 if anything is missing or unhealthy."""
    problems = 0

    def line(good, text):
        nonlocal problems
        if not good:
            problems += 1
        print("  %s  %s" % ("OK   " if good else "FAIL ", text))

    conn = call("GET", "/api/actions/connector/" + CONNECTOR_ID, ok_missing=True)
    line(bool(conn), "connector: %s" % (conn["name"] if conn else "missing"))

    for rule_id, label in ((RULE_LATENCY_ID, "latency rule"), (RULE_BURN_ID, "burn rate rule")):
        rule = call("GET", "/api/alerting/rule/" + rule_id, ok_missing=True)
        if not rule:
            line(False, "%s: missing" % label)
            continue
        last = (rule.get("last_run") or {})
        outcome = last.get("outcome") or "not run yet"
        active = (last.get("alerts_count") or {}).get("active")
        good = rule.get("enabled") and outcome in ("succeeded", "not run yet")
        line(good, "%s: enabled=%s last_run=%s active_alerts=%s"
             % (label, rule.get("enabled"), outcome, active))

    for slo_id, label in ((SLO_LATENCY_ID, "latency SLO"), (SLO_CHECKOUT_ID, "checkout SLO")):
        slo = call("GET", "/api/observability/slos/" + slo_id, ok_missing=True)
        if not slo:
            line(False, "%s: missing" % label)
            continue
        summary = slo.get("summary") or {}
        line(True, "%s: status=%s sli=%s" % (label, summary.get("status"), summary.get("sliValue")))

    dash = None
    try:
        dash = call("GET", "/api/dashboards/" + DASHBOARD_ID, ok_missing=True)
    except ApiError:
        pass
    line(bool(dash), "dashboard: %s" % ("present" if dash else "missing"))

    llm_types = (".inference", ".gen-ai", ".bedrock", ".gemini")
    llms = [c["name"] for c in call("GET", "/api/actions/connectors")
            if c.get("connector_type_id") in llm_types]
    # Informational only: a preconfigured managed LLM may not appear in this list.
    print("  %s  LLM connector for the AI chat: %s"
          % ("OK   " if llms else "NOTE ",
             ", ".join(llms[:4]) if llms else "none listed. Test the AI Agent by hand (SETUP.md step 7)"))
    return problems


def active_alerts():
    rule = call("GET", "/api/alerting/rule/" + RULE_LATENCY_ID, ok_missing=True)
    if not rule:
        print("missing")
        return
    print(((rule.get("last_run") or {}).get("alerts_count") or {}).get("active") or 0)


def run_soon():
    """Ask Kibana to run the latency rule now. Internal API, best effort."""
    try:
        call("POST", "/internal/alerting/rule/%s/_run_soon" % RULE_LATENCY_ID)
    except ApiError:
        pass


def delete_all():
    print("Deleting demo objects")
    for rule_id in (RULE_LATENCY_ID, RULE_BURN_ID):
        call("DELETE", "/api/alerting/rule/" + rule_id, ok_missing=True)
    call("DELETE", "/api/actions/connector/" + CONNECTOR_ID, ok_missing=True)
    for slo_id in (SLO_LATENCY_ID, SLO_CHECKOUT_ID):
        call("DELETE", "/api/observability/slos/" + slo_id, ok_missing=True)
    try:
        call("DELETE", "/api/dashboards/" + DASHBOARD_ID, ok_missing=True)
    except ApiError:
        pass
    info("done")


def main():
    if not KIBANA_URL or not API_KEY:
        sys.exit("KIBANA_URL and ELASTIC_API_KEY must be set (see .env.example)")
    cmd = sys.argv[1] if len(sys.argv) > 1 else "all"
    try:
        if cmd == "all":
            create_connector()
            create_slos()
            create_dashboard()
            create_rules()
            print("\nAll objects created. Run scripts/preflight.sh next.")
        elif cmd == "connector":
            create_connector()
            print("Rules were removed with the old connector. Run 'rules' next.")
        elif cmd == "slos":
            create_slos()
        elif cmd == "rules":
            create_rules()
        elif cmd == "dashboard":
            create_dashboard()
        elif cmd == "test-connector":
            test_connector()
        elif cmd == "status":
            sys.exit(1 if status() else 0)
        elif cmd == "active-alerts":
            active_alerts()
        elif cmd == "run-soon":
            run_soon()
        elif cmd == "delete":
            delete_all()
        else:
            sys.exit(__doc__)
    except ApiError as err:
        sys.exit("Kibana API error during '%s': %s" % (cmd, err))
    except urllib.error.URLError as err:
        sys.exit("Cannot reach Kibana at %s: %s" % (KIBANA_URL, err.reason))


if __name__ == "__main__":
    main()
