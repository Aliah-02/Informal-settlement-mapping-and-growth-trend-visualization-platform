#!/usr/bin/env bash
# Render production entrypoint
set -uo pipefail

cd /app
export PYTHONPATH=/app

PORT="${PORT:-10000}"
echo "=== DarInformal API starting on port ${PORT} ==="
echo "FRONTEND_URL=${FRONTEND_URL:-not set}"

python -c "from scripts.bootstrap_db import bootstrap_database; bootstrap_database()" \
  || echo "Bootstrap warning (continuing — GeoJSON fallback available)"

echo "Starting uvicorn..."
exec uvicorn main:app --host 0.0.0.0 --port "${PORT}"
