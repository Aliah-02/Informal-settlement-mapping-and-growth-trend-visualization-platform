# Informal Settlement Mapping and Growth Trend Visualization Platform

**DarInformal** — WebGIS platform for Dar es Salaam, Tanzania (2005–2026).

See [`Dar-informal-settlements-webGIS/README.md`](Dar-informal-settlements-webGIS/README.md) for full setup and deployment instructions.

## Quick Start

```bash
cd Dar-informal-settlements-webGIS
cp .env.example .env
cd backend/data && python3 generate_sample_data.py && cd ../..
docker compose up --build -d
# Open http://localhost
```
