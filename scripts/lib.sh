#!/usr/bin/env bash
# Shared helpers. Source this file; do not run it.
# Works with the bash 3.2 that ships with macOS.

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [ ! -f "$ROOT/.env" ]; then
  echo "Missing $ROOT/.env. Copy .env.example to .env and fill it in." >&2
  exit 1
fi
set -a
# shellcheck disable=SC1091
. "$ROOT/.env"
set +a

DEMO_DIR="${DEMO_DIR:-$ROOT/opentelemetry-demo}"
case "$DEMO_DIR" in /*) ;; *) DEMO_DIR="$ROOT/$DEMO_DIR" ;; esac
FLAG_FILE="$DEMO_DIR/src/flagd/demo.flagd.json"
DEMO_FLAG="${DEMO_FLAG:-productCatalogLockContention}"
DEMO_FLAG_VARIANT="${DEMO_FLAG_VARIANT:-on}"
KIBANA_URL="${KIBANA_URL%/}"
ELASTICSEARCH_URL="${ELASTICSEARCH_URL%/}"
SHOP_URL="${SHOP_URL:-http://localhost:8080}"

ok()   { printf '  \033[32mOK\033[0m    %s\n' "$*"; }
bad()  { printf '  \033[31mFAIL\033[0m  %s\n' "$*"; }
note() { printf '  \033[33mNOTE\033[0m  %s\n' "$*"; }
say()  { printf '\n%s\n' "$*"; }

need() {
  # need VAR [VAR...] : stop if a variable is empty. Never prints values.
  local v missing=0
  for v in "$@"; do
    if [ -z "${!v:-}" ]; then echo "Missing $v in .env" >&2; missing=1; fi
  done
  [ "$missing" -eq 0 ] || exit 1
}

kb() {
  # kb METHOD PATH [JSON_BODY] : call the Kibana API. Prints the response body.
  local method="$1" path="$2" body="${3:-}"
  if [ -n "$body" ]; then
    curl -sS -X "$method" "$KIBANA_URL$path" \
      -H "Authorization: ApiKey $ELASTIC_API_KEY" \
      -H "kbn-xsrf: true" -H "Content-Type: application/json" -d "$body"
  else
    curl -sS -X "$method" "$KIBANA_URL$path" \
      -H "Authorization: ApiKey $ELASTIC_API_KEY" -H "kbn-xsrf: true"
  fi
}

esql() {
  # esql 'QUERY' : run ES|QL, print the first value of the first row.
  # Prints nothing when the query fails or returns no rows.
  local body
  body="$(python3 -c 'import json,sys; print(json.dumps({"query": sys.argv[1]}))' "$1")"
  curl -sS -X POST "$ELASTICSEARCH_URL/_query" \
    -H "Authorization: ApiKey $ELASTIC_API_KEY" \
    -H "Content-Type: application/json" -d "$body" |
    python3 -c 'import json,sys
try:
    d = json.load(sys.stdin); v = d["values"][0][0]
    print("" if v is None else v)
except Exception:
    pass'
}

compose_demo() {
  # Same Compose layers as the fork's ./demo.sh docker.
  (cd "$DEMO_DIR" && docker compose --env-file .env --env-file .env.override \
    -f compose.yaml -f compose.full.yaml -f compose.extras.yaml \
    -f docker-compose.elastic.yml ${DEMO_COMPOSE_EXTRA:-} "$@")
}

set_flag() {
  # set_flag FLAG VARIANT : set a flagd flag's defaultVariant.
  # flagd watches this file and applies the change within a few seconds.
  # The file is rewritten in place so the container's bind mount keeps working.
  python3 - "$FLAG_FILE" "$1" "$2" <<'PY'
import json, sys
path, flag, variant = sys.argv[1:4]
with open(path, "r+") as f:
    data = json.load(f)
    flags = data["flags"]
    if flag not in flags:
        sys.exit("Unknown flag %s. Known flags: %s" % (flag, ", ".join(sorted(flags))))
    if variant not in flags[flag]["variants"]:
        sys.exit("Unknown variant %s for %s. Variants: %s"
                 % (variant, flag, ", ".join(flags[flag]["variants"])))
    flags[flag]["defaultVariant"] = variant
    f.seek(0)
    f.write(json.dumps(data, indent=2) + "\n")
    f.truncate()
PY
}

all_flags_off() {
  # Put every flag back to its resting variant ("off").
  python3 - "$FLAG_FILE" <<'PY'
import json, sys
path = sys.argv[1]
with open(path, "r+") as f:
    data = json.load(f)
    for flag in data["flags"].values():
        if "off" in flag["variants"]:
            flag["defaultVariant"] = "off"
    f.seek(0)
    f.write(json.dumps(data, indent=2) + "\n")
    f.truncate()
PY
}

flags_on() {
  # Print the flags that are not "off", one per line.
  python3 - "$FLAG_FILE" <<'PY'
import json, sys
for name, flag in json.load(open(sys.argv[1]))["flags"].items():
    if flag["defaultVariant"] != "off":
        print("%s=%s" % (name, flag["defaultVariant"]))
PY
}
