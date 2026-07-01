#!/usr/bin/env bash
set -euo pipefail

PORT="${PORT:-8000}"
echo "=== DarInformal API starting on port ${PORT} ==="

python scripts/bootstrap_db.py || echo "Bootstrap skipped (non-fatal)"

# Production: no --reload (reload breaks Render health checks / port binding)
exec uvicorn main:app \
  --host 0.0.0.0 \
  --port "${PORT}" \
  --proxy-headers \
  --forwarded-allow-ips="*"
