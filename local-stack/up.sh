#!/usr/bin/env bash
# Plan B: run Elasticsearch, Kibana and an EDOT collector on your laptop.
# Use it to rehearse before your trial starts, or if Elastic Cloud is unreachable.
# It has no Managed OTLP endpoint and no Elastic Managed LLM (no AI Agent answers
# unless you add your own LLM connector). The 30-day trial licence is local and free.
# Usage: local-stack/up.sh        start and write the values for .env to local-stack/demo.env
#        local-stack/up.sh down   stop and delete the local data
set -euo pipefail
cd "$(dirname "$0")"

if [ "${1:-}" = "down" ]; then
  docker compose down --volumes
  exit 0
fi

if [ ! -f .env ]; then
  umask 077
  {
    echo "ES_LOCAL_VERSION=9.5.6"
    echo "ES_LOCAL_PASSWORD=$(openssl rand -hex 12)"
    echo "KIBANA_LOCAL_PASSWORD=$(openssl rand -hex 12)"
    echo "KIBANA_ENCRYPTION_KEY=$(openssl rand -hex 16)"
  } > .env
fi
set -a; . ./.env; set +a

docker compose up -d
echo "Waiting for Kibana (1 to 3 minutes)..."
until curl -s -I http://localhost:5601 | grep -q "302 Found"; do sleep 5; done

key="$(curl -s -u "elastic:$ES_LOCAL_PASSWORD" -X POST http://localhost:9200/_security/api_key \
  -H 'Content-Type: application/json' -d '{"name":"panel-demo-local"}' |
  python3 -c 'import json,sys; print(json.load(sys.stdin)["encoded"])')"

umask 077
cat > demo.env <<ENV
KIBANA_URL=http://localhost:5601
ELASTICSEARCH_URL=http://localhost:9200
ELASTIC_API_KEY=$key
ELASTIC_OTLP_ENDPOINT=http://edot-collector:4318
ELASTIC_OTLP_API_KEY=unused
DEMO_COMPOSE_EXTRA=-f docker-compose.elastic-self-hosted.yml
ENV

cat <<MSG

Local stack is up. Kibana: http://localhost:5601
User: elastic. Password: see ES_LOCAL_PASSWORD in local-stack/.env

The connection values for the project are in local-stack/demo.env.
Copy those six lines into the project .env (replace the Elastic Cloud values).
Then run scripts/start-demo.sh and scripts/setup-elastic.sh as usual.
MSG
