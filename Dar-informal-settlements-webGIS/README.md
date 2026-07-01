# DarInformal

**Informal Settlement Mapping and Growth Trend Visualization Platform**  
*Dar es Salaam, Tanzania — 2005 to 2026*

Production WebGIS platform with **PostGIS** as the central spatial database, **FastAPI** for analytics and GeoJSON delivery, and **Leaflet** for interactive visualization.

---

## Architecture

```text
Google Earth Engine
    │  Export GeoJSON + GeoTIFF
    ▼
GeoJSON files  ──►  import script  ──►  PostGIS (settlements, yearly_metrics, change_detection)
                                              │
                         ┌────────────────────┴────────────────────┐
                         ▼                                         ▼
                    FastAPI API                              Analytics + CSV
                         │
                         ▼
                  Leaflet Frontend
              (API GeoJSON vector layers)
```

| Component | Role |
|-----------|------|
| **PostGIS** | Central spatial database — settlements, metrics, change detection |
| **FastAPI** | REST API — risk layers, trends, change detection, CSV reports |
| **Leaflet** | Interactive map, time slider, dashboard |
| **GEE scripts** | Satellite data pipeline (Sentinel-2 / Landsat) |

---

## Cloud Deployment (Render + Vercel — Free Tier)

| Tier | Platform | Component |
|------|----------|-----------|
| Backend | [Render](https://render.com) (free) | FastAPI + PostgreSQL/PostGIS |
| Frontend | [Vercel](https://vercel.com) (free) | Leaflet map + analytics dashboard |

```text
Vercel (frontend)  ──HTTPS──►  Render (FastAPI)
                                    │
                                    ▼
                             Render PostgreSQL + PostGIS
```

**Integration:** Set `DARINFORMAL_API_URL` on Vercel → your Render API URL. Set `FRONTEND_URL` and `CORS_ORIGINS` on Render → your Vercel URL.

Full step-by-step guide: **[docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)**

---

## CSV Growth Trend Reports

| Method | Endpoint / Action |
|--------|-------------------|
| Dashboard | Click **⬇ CSV Report** in the analytics panel |
| API | `GET /api/metrics/trend/csv` |
| Change detection | `GET /api/change/{from}/{to}/csv` |

```bash
curl -O http://localhost:8000/api/metrics/trend/csv
```

---

## Quick Start (Local)

### Prerequisites

- Python 3.12+
- PostgreSQL 16 + PostGIS 3.4
- GDAL (`libgdal-dev` on Linux)

### 1. Clone and configure

```bash
git clone https://github.com/Aliah-02/Informal-settlement-mapping-and-growth-trend-visualization-platform.git
cd Informal-settlement-mapping-and-growth-trend-visualization-platform/Dar-informal-settlements-webGIS
cp .env.example .env
```

### 2. PostgreSQL + PostGIS

```bash
createdb darinformal
psql -d darinformal -f backend/data/init.sql
```

### 3. Backend setup

```bash
make setup
cd backend/data && python3 generate_sample_data.py && cd ../..
make import
make dev-api      # http://localhost:8000
```

### 4. Frontend

```bash
make dev-frontend # http://localhost:5500
```

| Service | URL |
|---------|-----|
| **Web App** | http://localhost:5500 |
| **API Docs** | http://localhost:8000/docs |
| **API Health** | http://localhost:8000/api/health |

### VS Code (recommended)

Open `Dar-informal-settlements-webGIS` as workspace root → **F5** → **DarInformal: Full Stack**.  
See **[docs/VSCODE_SETUP.md](docs/VSCODE_SETUP.md)**.

---

## PostGIS Integration

### Schema

| Table | Purpose |
|-------|---------|
| `settlements` | Primary spatial layer — polygons with ISI attributes |
| `yearly_metrics` | Pre-computed dashboard KPIs per year |
| `change_detection` | Cached temporal change records |
| `import_log` | Import audit trail |
| `v_settlements_all` | All-years view for exports |

### Import GEE exports

```bash
cd backend
python scripts/import_geojson_to_postgis.py --all
python scripts/compute_yearly_metrics.py
# Or one command:
python scripts/import_all_data.py
```

See **[docs/DATA_IMPORT.md](docs/DATA_IMPORT.md)** for GeoJSON + GeoTIFF naming.

### Fallback mode

If PostGIS is empty, the API falls back to `backend/data/geojson/*.geojson`. Set `USE_POSTGIS=false` to force file mode.

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/health` | Health + PostGIS status |
| `GET` | `/api/risk/{year}` | GeoJSON risk layer |
| `GET` | `/api/metrics/trend` | Time-series analytics |
| `GET` | `/api/metrics/trend/csv` | Growth trend CSV report |
| `GET` | `/api/change/{from}/{to}` | Change detection |
| `GET` | `/api/change/{from}/{to}/csv` | Change detection CSV |
| `GET` | `/api/settlements` | Filtered settlement list |
| `GET` | `/api/aoi` | Dar es Salaam bounding box |
| `POST` | `/api/admin/import` | Re-import GeoJSON (debug only) |

---

## Repository Structure

```
Dar-informal-settlements-webGIS/
├── render.yaml                     # Render Blueprint (API + Postgres)
├── docs/DEPLOYMENT.md              # Render + Vercel guide
├── backend/
│   ├── main.py                     # FastAPI application
│   ├── Dockerfile                  # Render container image
│   ├── start.sh                    # Render entrypoint
│   ├── config.py
│   ├── db/                         # PostGIS layer
│   ├── services/                   # ISI, metrics, reports, change detection
│   ├── scripts/                    # import, bootstrap, catalog_rasters
│   └── data/                       # init.sql, geojson/, raster/
├── frontend/                       # Leaflet + Chart.js (Vercel)
├── gee/                            # Google Earth Engine scripts
├── Makefile                        # Local dev commands
└── .vscode/                        # Compound launch configs
```

---

## Data Pipeline: GEE → PostGIS

```text
1. Run GEE scripts (gee/05_yearly_export.js or landsat5-7-early-years/)
2. Download GeoJSON from Google Drive
3. Rename to settlements_YYYY.geojson → backend/data/geojson/
4. python scripts/import_all_data.py
5. Restart API (or redeploy on Render)
```

---

## Informal Settlement Index (ISI)

```
ISI = (0.3 × NDBI) + (0.25 × (1 − NDVI)) + (0.2 × BSI) + (0.25 × fragmentation)
```

| Risk | ISI Range | Color |
|------|-----------|-------|
| Low | < 0.2 | Green `#22c55e` |
| Medium | 0.2 – 0.5 | Orange `#f59e0b` |
| High | > 0.5 | Red `#ef4444` |

---

## Troubleshooting

### PostGIS connection refused

Ensure PostgreSQL is running and `DATABASE_URL_SYNC` in `.env` matches your credentials.

### Empty map / no data

```bash
psql -U darinformal -d darinformal -c "SELECT year, COUNT(*) FROM settlements GROUP BY year;"
make import
```

### API shows `data_source: geojson` instead of `postgis`

PostGIS table is empty — run `make import` and restart the API.

### CORS errors in browser

Serve frontend via `http://localhost:5500` (not `file://`). Add your port to `CORS_ORIGINS` in `.env`.

---

## Makefile Commands

```bash
make setup         # Create venv + install deps
make import        # Import GeoJSON → PostGIS + catalog rasters
make dev-api       # Start FastAPI on :8000
make dev-frontend  # Serve frontend on :5500
make test-api      # Curl health endpoint
```

---

## Future Roadmap

- ML upgrade path (U-Net on Dynamic World labels)
- WorldPop population disaggregation
- Sentinel-2 NRT monitoring pipeline
- PostGIS `ST_ClusterDBSCAN` for settlement grouping
- Multi-city AOI configuration (Nairobi, Lagos, Kampala)

---

## License

MIT License

## Acknowledgments

Developed for urban resilience planning in Dar es Salaam, Tanzania.  
Satellite data: ESA Copernicus (Sentinel-2), USGS (Landsat), Google (Dynamic World).
