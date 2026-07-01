# Informal Settlement Mapping and Growth Trend Visualization Platform

**DarInformal** — WebGIS platform for Dar es Salaam, Tanzania (2005–2026).

See [`Dar-informal-settlements-webGIS/README.md`](Dar-informal-settlements-webGIS/README.md) for full setup and deployment instructions.

## Quick Start

```bash
cd Dar-informal-settlements-webGIS
cp .env.example .env
cd backend/data && python3 generate_sample_data.py && cd ../..
make setup
# Start PostgreSQL/PostGIS locally, then:
make import
make dev-api      # terminal 1 — http://localhost:8000
make dev-frontend # terminal 2 — http://localhost:5500
```

Or use VS Code compound launch **DarInformal: Full Stack** — see `docs/VSCODE_SETUP.md`.

## Cloud deployment

- **Backend:** Render (FastAPI + PostGIS) — `render.yaml`
- **Frontend:** Vercel — `frontend/vercel.json`

See [`docs/DEPLOYMENT.md`](Dar-informal-settlements-webGIS/docs/DEPLOYMENT.md).
