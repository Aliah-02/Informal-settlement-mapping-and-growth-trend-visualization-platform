# DarInformal

**Informal Settlement Mapping and Growth Trend Visualization Platform**  
*Dar es Salaam, Tanzania — 2005 to 2026*

DarInformal is a production-ready WebGIS platform that detects, maps, and classifies informal settlements using satellite imagery intelligence. It tracks expansion and risk evolution across two decades and provides actionable intelligence through the **Informal Settlement Index (ISI)**.

Built for city planners, researchers, and urban development agencies working in East African metropolitan contexts.

---

## Features

- **Interactive Map** — Leaflet.js map centered on Dar es Salaam with risk-colored settlement polygons
- **Time Slider** — Animate settlement growth across 2005, 2010, 2015, 2020, and 2026
- **ISI Risk Intelligence** — Weighted composite index from NDBI, NDVI, BSI, and fragmentation
- **Change Detection** — Identify new, expanded, contracted, and stable settlements between years
- **Analytics Dashboard** — KPI cards, area growth charts, ISI trends, and risk breakdowns (Chart.js)
- **GEE Integration** — Google Earth Engine scripts for Sentinel-2 + Landsat production data pipeline
- **Docker Deployment** — One-command stack: PostGIS + FastAPI + Nginx

---

## Architecture

```text
Google Earth Engine (Sentinel-2 / Landsat 5/7/8/9)
        │
        ▼
  GEE Export Scripts (GeoJSON + GeoTIFF)
        │
        ▼
  FastAPI Backend (GeoPandas + Rasterio + Shapely)
        │
        ▼
  PostgreSQL + PostGIS (schema ready)
        │
        ▼
  Leaflet.js Frontend (Vanilla JS + Chart.js)
```

### Informal Settlement Index (ISI)

```
ISI = (0.3 × NDBI) + (0.25 × (1 − NDVI)) + (0.2 × BSI) + (0.25 × fragmentation_index)
```

| Risk Level | ISI Range | Color |
|------------|-----------|-------|
| Low | < 0.2 | Green `#22c55e` |
| Medium | 0.2 – 0.5 | Orange `#f59e0b` |
| High | > 0.5 | Red `#ef4444` |

---

## Repository Structure

```
Dar-informal-settlements-webGIS/
├── backend/
│   ├── main.py                  # FastAPI application
│   ├── config.py                # Settings and ISI weights
│   ├── services/
│   │   ├── loader.py            # GeoJSON data loading
│   │   ├── isi_model.py         # ISI computation engine
│   │   ├── change_detection.py  # Temporal change analysis
│   │   └── metrics.py           # Analytics aggregation
│   ├── data/
│   │   ├── geojson/             # Yearly settlement GeoJSON files
│   │   ├── generate_sample_data.py
│   │   └── init.sql             # PostGIS schema
│   └── models/                  # Pydantic schemas
├── frontend/
│   ├── index.html
│   ├── css/style.css
│   └── js/                      # map.js, slider.js, api.js, dashboard.js
├── gee/                         # Google Earth Engine scripts
│   └── landsat5-7-early-years/  # Dedicated L5+L7 pipeline for 2005 & 2010
├── nginx/nginx.conf
├── docker-compose.yml
└── .env.example
```

---

## Quick Start (Docker)

### Prerequisites

- Docker and Docker Compose
- 4 GB RAM minimum

### 1. Clone and configure

```bash
git clone <repository-url>
cd Dar-informal-settlements-webGIS
cp .env.example .env
# Edit .env — change POSTGRES_PASSWORD for production
```

### 2. Generate sample data (if not present)

```bash
cd backend/data
python3 generate_sample_data.py
cd ../..
```

### 3. Launch the stack

```bash
docker compose up --build -d
```

### 4. Access the platform

| Service | URL |
|---------|-----|
| Web App | http://localhost |
| API Docs | http://localhost:8000/docs |
| Health Check | http://localhost:8000/api/health |

---

## Local Development (without Docker)

### Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Generate sample data
cd data && python3 generate_sample_data.py && cd ..

# Run API
uvicorn main:app --reload --port 8000
```

### Frontend

Serve the `frontend/` directory with any static server. The API must be reachable at `/api/` (or set `window.DARINFORMAL_API_URL`).

```bash
# Using Python
cd frontend
python3 -m http.server 3000
# Set API URL in browser console: window.DARINFORMAL_API_URL = 'http://localhost:8000/api'
```

Or use the Nginx config in Docker which proxies `/api/` automatically.

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/health` | Service health and available data years |
| `GET` | `/api/risk/{year}` | GeoJSON risk layer for a given year |
| `GET` | `/api/metrics/trend` | Time-series growth metrics (2005–2026) |
| `GET` | `/api/change/{from_year}/{to_year}` | Change detection between two years |
| `GET` | `/api/settlements` | List settlements with filters (`year`, `risk_level`, `min_isi`, `max_isi`) |
| `GET` | `/api/aoi` | Dar es Salaam AOI bounding box |

### Example

```bash
curl http://localhost:8000/api/risk/2020
curl http://localhost:8000/api/metrics/trend
curl "http://localhost:8000/api/settlements?year=2020&risk_level=high&limit=10"
curl http://localhost:8000/api/change/2015/2020
```

---

## Generating Production Data via Google Earth Engine

### Prerequisites

1. [Google Earth Engine account](https://earthengine.google.com/)
2. GEE Code Editor access: https://code.earthengine.google.com/

### Workflow

Run scripts in order in the GEE Code Editor:

| Script | Purpose |
|--------|---------|
| `gee/01_aoi_definition.js` | Define Dar es Salaam AOI boundary |
| `gee/02_dynamic_world_labels.js` | Extract weak labels from Dynamic World |
| `gee/03_spectral_indices.js` | Compute NDVI, NDBI, BSI per year |
| `gee/04_isi_computation.js` | Apply ISI formula and risk classification |
| `gee/05_yearly_export.js` | Export GeoJSON + GeoTIFF to Google Drive |

### After Export

1. Download GeoJSON files from Google Drive (`DarInformal_GEE_Exports` folder)
2. Rename to `settlements_YYYY.geojson`
3. Place in `backend/data/geojson/`
4. Restart the API — data is loaded automatically on request

### Supported Sensors

| Period | Primary | Fallback |
|--------|---------|----------|
| 2005–2011 | Landsat 5/7 | Landsat 7 |
| 2012–2016 | Landsat 8 | Landsat 7 |
| 2017–2020 | Sentinel-2 + Landsat 8 | Landsat 8 |
| 2021–2026 | Sentinel-2 + Landsat 9 | Landsat 8/9 |

---

## Updating the ISI Model

Edit weights in `backend/config.py`:

```python
isi_weight_ndbi: float = 0.3
isi_weight_ndvi_inv: float = 0.25
isi_weight_bsi: float = 0.2
isi_weight_fragmentation: float = 0.25
isi_low_threshold: float = 0.2
isi_high_threshold: float = 0.5
```

The ISI is recomputed on data load if scores are missing from GeoJSON. For production, re-run `gee/04_isi_computation.js` and `gee/05_yearly_export.js` after changing weights.

---

## Production Deployment

### Security checklist

- Change `POSTGRES_PASSWORD` in `.env`
- Set `DEBUG=false`
- Restrict `CORS_ORIGINS` to your domain
- Use HTTPS (add TLS termination in Nginx or use a reverse proxy like Caddy/Traefik)
- Do not expose port 5432 publicly

### Scaling

- Mount `backend/data/geojson/` as a read-only volume
- Use PostGIS direct ingestion (`backend/data/init.sql`) for large datasets
- Add Redis caching for `/api/metrics/trend` in high-traffic deployments

---

## Future Roadmap

- **ML Upgrade Path** — Train U-Net / DeepLabV3+ on Dynamic World labels + high-res drone imagery for parcel-level detection
- **Population Disaggregation** — Integrate WorldPop / Facebook HRSL for validated population estimates per settlement
- **Real-time Monitoring** — Sentinel-2 NRT pipeline with weekly ISI updates
- **Multi-city Expansion** — Parameterized AOI config for Nairobi, Lagos, Kampala
- **PostGIS Direct Ingest** — Bulk load GEE exports into PostGIS with `ogr2ogr` for sub-second spatial queries
- **Mobile Field App** — Offline-capable settlement validation tool for community enumerators
- **Risk Alert System** — Webhook notifications when high-risk ISI expansion exceeds thresholds

---

## License

MIT License — See LICENSE file.

## Acknowledgments

Developed for urban resilience planning in Dar es Salaam, Tanzania. Satellite data courtesy of ESA Copernicus (Sentinel-2), USGS (Landsat), and Google (Dynamic World).
