#!/usr/bin/env bash
# Render production entrypoint — no --reload, bind to $PORT
set -euo pipefail

cd /app
export PYTHONPATH=/app

PORT="${PORT:-10000}"
echo "=== DarInformal API | port ${PORT} | PYTHONPATH=${PYTHONPATH} ==="

# Bootstrap PostGIS (import sample data on first run)
python -c "from scripts.bootstrap_db import bootstrap_database; bootstrap_database()" \
  || echo "Bootstrap skipped (non-fatal)"

exec uvicorn main:app \
  --host 0.0.0.0 \
  --port "${PORT}" \
  --proxy-headers \
  --forwarded-allow-ips="*"
