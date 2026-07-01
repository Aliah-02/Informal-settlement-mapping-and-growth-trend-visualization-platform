.PHONY: help setup install import dev-api dev-frontend test-api

help:
	@echo "DarInformal — local development (no Docker)"
	@echo "  make setup         Create venv + install Python deps"
	@echo "  make import        Import GeoJSON → PostGIS + compute metrics"
	@echo "  make dev-api       Start FastAPI on :8000"
	@echo "  make dev-frontend  Serve frontend on :5500"
	@echo "  make test-api      Curl health endpoint"

setup install:
	cd backend && python3 -m venv .venv && .venv/bin/pip install -r requirements.txt

import:
	cd backend && .venv/bin/python scripts/import_all_data.py

dev-api:
	cd backend && .venv/bin/uvicorn main:app --reload --host 127.0.0.1 --port 8000

dev-frontend:
	cd frontend && python3 -m http.server 5500 --bind 127.0.0.1

test-api:
	curl -s http://localhost:8000/api/health | python3 -m json.tool
