#!/usr/bin/env bash
# Render start command when Runtime = Python (repo root).
# Prefer Docker: leave Start Command blank and use ./Dockerfile instead.
set -euo pipefail
cd "$(dirname "$0")/Dar-informal-settlements-webGIS/backend"
export PYTHONPATH="${PYTHONPATH:-}:$(pwd)"
exec bash start.sh
