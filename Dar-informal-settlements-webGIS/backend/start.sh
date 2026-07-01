#!/usr/bin/env bash
set -e
echo "=== DarInformal API starting on port ${PORT:-8000} ==="
python scripts/bootstrap_db.py || echo "Bootstrap skipped"
exec uvicorn main:app --host 0.0.0.0 --port "${PORT:-8000}"
