#!/usr/bin/env bash
# Start the Elastic fork of the OpenTelemetry demo (the web shop) with Docker
# and send its logs, metrics and traces to Elastic Cloud over OTLP.
# The first run clones the repo and builds some images. Allow 10 to 20 minutes.
set -euo pipefail
. "$(dirname "$0")/lib.sh"
need ELASTIC_OTLP_ENDPOINT ELASTIC_OTLP_API_KEY

command -v docker >/dev/null || { echo "Docker is not installed or not on PATH" >&2; exit 1; }
docker info >/dev/null 2>&1 || { echo "Docker is not running. Start Docker Desktop first." >&2; exit 1; }

if [ ! -d "$DEMO_DIR/.git" ]; then
  say "Cloning github.com/elastic/opentelemetry-demo into $DEMO_DIR"
  git clone https://github.com/elastic/opentelemetry-demo.git "$DEMO_DIR"
  (cd "$DEMO_DIR" && git checkout --quiet "${DEMO_GIT_REF:-main}")
fi
say "Demo version: $(cd "$DEMO_DIR" && git log -1 --format='%h %ad' --date=short)"

# Write our settings into the fork's .env.override (the file its demo.sh uses).
# Values are passed through the environment, so secrets never show up in `ps`.
OVERRIDE="$DEMO_DIR/.env.override" LOCUST="${DEMO_LOCUST_USERS:-10}" python3 - <<'PY'
import os, re
path = os.environ["OVERRIDE"]
values = {
    "ELASTIC_OTLP_ENDPOINT": os.environ["ELASTIC_OTLP_ENDPOINT"],
    "ELASTIC_OTLP_API_KEY": os.environ["ELASTIC_OTLP_API_KEY"],
    "LOCUST_USERS": os.environ["LOCUST"],
}
lines = open(path).read().splitlines()
for key, value in values.items():
    new = '%s="%s"' % (key, value)
    for i, line in enumerate(lines):
        if re.match(r"^%s=" % re.escape(key), line):
            lines[i] = new
            break
    else:
        lines.append(new)
open(path, "w").write("\n".join(lines) + "\n")
PY
chmod 600 "$DEMO_DIR/.env.override"

all_flags_off
say "Starting the shop (docker compose up). This can take a while on the first run."
compose_demo up --build --remove-orphans --detach

say "Waiting for the shop at $SHOP_URL"
i=0
until curl -fsS -o /dev/null "$SHOP_URL"; do
  i=$((i + 1))
  if [ "$i" -gt 90 ]; then
    bad "Shop did not answer after 3 minutes. Check: docker ps -a ; docker logs otel-collector"
    exit 1
  fi
  sleep 2
done
ok "Shop is up: $SHOP_URL"
note "Feature flag UI: $SHOP_URL/feature   Load generator: $SHOP_URL/loadgen/"
note "First telemetry shows in Elastic after 1 to 3 minutes. Then run scripts/preflight.sh"
