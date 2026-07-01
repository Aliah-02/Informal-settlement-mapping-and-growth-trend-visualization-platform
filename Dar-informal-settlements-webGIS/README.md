# DarInformal

**Informal Settlement Mapping and Growth Trend Visualization Platform**  
*Dar es Salaam, Tanzania — 2005 to 2026*

Production WebGIS platform with **PostGIS** as the central spatial database, **GeoServer** for WMS/WFS map tiles, **FastAPI** for analytics, and **Leaflet** for interactive visualization.

---

## Architecture

```text
Google Earth Engine
    │  Export GeoJSON + GeoTIFF
    ▼
GeoJSON files  ──►  import script  ──►  PostGIS (settlements, yearly_metrics, change_detection)
                                              │
                         ┌────────────────────┼────────────────────┐
                         ▼                    ▼                    ▼
                    FastAPI API          GeoServer WMS/WFS     Analytics cache
                         │                    │
                         └────────┬───────────┘
                                  ▼
                          Leaflet Frontend
                    (Hybrid: WMS tiles + API GeoJSON popups)
```

| Component | Role |
|-----------|------|
| **PostGIS** | Central spatial database — settlements, metrics, change detection |
| **FastAPI** | REST API — risk layers, trends, change detection, settlements |
| **GeoServer** | WMS/WFS map tiles styled by ISI risk level |
| **Leaflet** | Interactive map, time slider, dashboard |
| **GEE scripts** | Satellite data pipeline (Sentinel-2 / Landsat) |

---

## Quick Start (Docker — Recommended)

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) 24+ and Docker Compose v2
- 4 GB RAM, 10 GB disk

### 1. Clone the repository

```bash
git clone https://github.com/Aliah-02/Informal-settlement-mapping-and-growth-trend-visualization-platform.git
cd Informal-settlement-mapping-and-growth-trend-visualization-platform/Dar-informal-settlements-webGIS
```

### 2. Configure environment

```bash
cp .env.example .env
# Optional: edit .env to change passwords
```

### 3. Start the full stack

```bash
make up
# or: docker compose up -d
```

**First launch** (~2 minutes) automatically:
1. Creates PostGIS schema
2. Imports sample GeoJSON → PostGIS
3. Computes yearly metrics
4. Starts FastAPI
5. Configures GeoServer workspace + PostGIS layer
6. Serves frontend via Nginx

### 4. Open the platform

| Service | URL |
|---------|-----|
| **Web App** | http://localhost |
| **API Docs** | http://localhost:8000/docs |
| **API Health** | http://localhost:8000/api/health |
| **GeoServer Admin** | http://localhost:8080/geoserver/web/ (`admin` / `geoserver`) |
| **GeoServer WMS** | http://localhost/geoserver/darinformal/wms |

### 5. Verify PostGIS data

```bash
make shell-db
# inside psql:
SELECT year, COUNT(*), ROUND(SUM(area_ha)::numeric, 1) AS total_ha
FROM settlements GROUP BY year ORDER BY year;
\q
```

---

## Local Development (Without Docker)

### Prerequisites

- Python 3.12+
- PostgreSQL 16 + PostGIS 3.4
- GDAL (`libgdal-dev`)
- Node not required (vanilla JS frontend)

### 1. Clone and configure

```bash
git clone https://github.com/Aliah-02/Informal-settlement-mapping-and-growth-trend-visualization-platform.git
cd Informal-settlement-mapping-and-growth-trend-visualization-platform/Dar-informal-settlements-webGIS
cp .env.example .env
```

### 2. Start PostGIS

**Option A — Docker for DB only:**
```bash
docker compose up -d postgis
```

**Option B — Local PostgreSQL:**
```bash
createdb darinformal
psql -d darinformal -f backend/data/init.sql
```

### 3. Backend setup

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Generate sample data (if not present)
python data/generate_sample_data.py

# Import GeoJSON → PostGIS
python scripts/import_geojson_to_postgis.py --all
python scripts/compute_yearly_metrics.py

# Start API
uvicorn main:app --reload --port 8000
```

### 4. GeoServer (optional, for WMS)

```bash
docker compose up -d geoserver
# Wait ~60s, then:
pip install requests
GEOSERVER_URL=http://localhost:8080/geoserver POSTGRES_HOST=localhost \
  python ../scripts/setup_geoserver.py
```

### 5. Frontend

```bash
cd frontend
python3 -m http.server 3000
```

Open http://localhost:3000 — set API URL in browser console:
```javascript
window.DARINFORMAL_API_URL = 'http://localhost:8000/api';
window.DARINFORMAL_GEOSERVER_URL = 'http://localhost:8080/geoserver/darinformal/wms';
```

Or use Nginx/docker for unified routing.

---

## PostGIS Integration Guide

### Schema

| Table | Purpose |
|-------|---------|
| `settlements` | Primary spatial layer — polygons with ISI attributes |
| `yearly_metrics` | Pre-computed dashboard KPIs per year |
| `change_detection` | Cached temporal change records |
| `import_log` | Import audit trail |
| `v_settlements_wms` | GeoServer publishing view |

### Import GEE exports into PostGIS

After downloading GeoJSON from Google Earth Engine:

```bash
# Place files in backend/data/geojson/
#   settlements_2005.geojson
#   settlements_2010.geojson
#   ...

# Import all years
cd backend
python scripts/import_geojson_to_postgis.py --all

# Import single year
python scripts/import_geojson_to_postgis.py --year 2020

# Import specific file
python scripts/import_geojson_to_postgis.py --file data/geojson/settlements_2020.geojson

# Recompute dashboard metrics
python scripts/compute_yearly_metrics.py
```

**Docker re-import:**
```bash
make import
# or: docker compose run --rm data-import
```

### Spatial indexes

Created automatically in `init.sql`:
- `GIST(geom)` — spatial queries
- `(year, risk_level)` — filtered queries
- `isi_score` — range filters

### Verify connection from API

```bash
curl http://localhost:8000/api/health | python3 -m json.tool
```

Expected response:
```json
{
  "status": "healthy",
  "data_source": "postgis",
  "database": {
    "connected": true,
    "postgis_version": "3.4 ...",
    "settlement_count": 119
  },
  "data_years_available": [2005, 2010, 2015, 2020, 2026]
}
```

### Fallback mode

If PostGIS is empty, the API automatically falls back to reading GeoJSON files from `backend/data/geojson/`. Set `USE_POSTGIS=false` in `.env` to force file-based mode.

---

## GeoServer Integration

GeoServer reads directly from PostGIS `settlements` table and serves styled WMS tiles.

### Frontend map modes

Use the **Map source** dropdown in the legend:

| Mode | Rendering | Interaction |
|------|-----------|-------------|
| **Hybrid** (default) | GeoServer WMS tiles | API GeoJSON for popups |
| **GeoServer WMS** | WMS only | Limited popups |
| **API GeoJSON** | Vector polygons from FastAPI | Full popups/hover |

### WMS layer parameters

```
Layer:  darinformal:settlements
Style:  settlements_risk
Filter: CQL_FILTER=year=2020
```

See `geoserver/README.md` for WMS URL examples and manual setup.

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/health` | Health + PostGIS status |
| `GET` | `/api/geoserver` | WMS/WFS URLs for frontend |
| `GET` | `/api/risk/{year}` | GeoJSON risk layer + WMS metadata |
| `GET` | `/api/metrics/trend` | Time-series analytics |
| `GET` | `/api/change/{from}/{to}` | Change detection |
| `GET` | `/api/settlements` | Filtered settlement list |
| `GET` | `/api/aoi` | Dar es Salaam bounding box |
| `POST` | `/api/admin/import` | Re-import GeoJSON (debug mode only) |

---

## Repository Structure

```
Dar-informal-settlements-webGIS/
├── backend/
│   ├── main.py                     # FastAPI application
│   ├── config.py                   # Settings (PostGIS, GeoServer)
│   ├── db/
│   │   ├── database.py             # SQLAlchemy engine + health check
│   │   ├── models.py               # ORM models (GeoAlchemy2)
│   │   └── repository.py           # PostGIS CRUD + spatial queries
│   ├── services/
│   │   ├── data_source.py          # PostGIS primary, GeoJSON fallback
│   │   ├── loader.py               # GeoJSON file loader
│   │   ├── isi_model.py            # ISI computation
│   │   ├── change_detection.py     # Temporal analysis
│   │   └── metrics.py              # Dashboard aggregations
│   ├── scripts/
│   │   ├── import_geojson_to_postgis.py
│   │   └── compute_yearly_metrics.py
│   └── data/
│       ├── init.sql                # PostGIS schema
│       └── geojson/                # GEE export destination
├── frontend/
│   ├── index.html
│   ├── css/style.css
│   └── js/                         # map.js (WMS+API hybrid), api.js, ...
├── geoserver/
│   ├── styles/settlements_risk.sld
│   └── README.md
├── gee/                            # Google Earth Engine scripts
│   └── landsat5-7-early-years/     # L5+L7 pipeline for 2005/2010
├── scripts/
│   ├── setup_geoserver.py          # Auto-configure GeoServer
│   └── import_all.sh
├── nginx/nginx.conf                # Proxies /api/ and /geoserver/
├── docker-compose.yml              # Full stack
├── Makefile                        # Convenience commands
├── .env.example
└── README.md
```

---

## Data Pipeline: GEE → PostGIS

```text
1. Run GEE scripts (gee/05_yearly_export.js or landsat5-7-early-years/)
2. Download GeoJSON from Google Drive
3. Rename to settlements_YYYY.geojson
4. Place in backend/data/geojson/
5. Run: python scripts/import_geojson_to_postgis.py --all
6. Run: python scripts/compute_yearly_metrics.py
7. Restart API (or docker compose restart api)
8. GeoServer picks up new data automatically (same PostGIS table)
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

Weights configured in `backend/config.py`.

---

## Troubleshooting

### PostGIS connection refused

```bash
docker compose ps                    # check postgis is healthy
docker compose logs postgis          # view DB logs
```

Ensure `DATABASE_URL_SYNC` in `.env` matches your PostGIS credentials.

### Empty map / no data

```bash
# Check data in PostGIS
docker compose exec postgis psql -U darinformal -d darinformal \
  -c "SELECT year, COUNT(*) FROM settlements GROUP BY year;"

# Re-import
make import
```

### GeoServer layer not visible

```bash
docker compose logs geoserver
docker compose logs geoserver-setup  # check setup script output

# Manual re-setup
docker compose run --rm geoserver-setup
```

Verify WMS directly:
```
http://localhost/geoserver/darinformal/wms?service=WMS&version=1.1.1&request=GetCapabilities
```

### API shows `data_source: geojson` instead of `postgis`

PostGIS table is empty. Run import:
```bash
make import
docker compose restart api
```

### Port conflicts

Change ports in `.env`:
```
HTTP_PORT=8081
API_PORT=8001
GEOSERVER_PORT=8082
POSTGRES_PORT=5433
```

### Reset everything (clean slate)

```bash
docker compose down -v   # WARNING: deletes PostGIS + GeoServer data volumes
make up
```

### CORS errors in browser

Ensure frontend is served via Nginx (`http://localhost`) not `file://`. The Nginx proxy handles `/api/` and `/geoserver/` routing.

---

## Makefile Commands

```bash
make help       # List commands
make setup      # Copy .env + build images
make up         # Start full stack
make down       # Stop services
make logs       # Tail logs
make import     # Re-import GeoJSON → PostGIS
make test-api   # Curl health endpoint
make shell-db   # psql shell
```

---

## Future Roadmap

- ML upgrade path (U-Net on Dynamic World labels)
- WorldPop population disaggregation
- Sentinel-2 NRT monitoring pipeline
- PostGIS `ST_ClusterDBSCAN` for settlement grouping
- GeoServer raster layers for ISI GeoTIFF mosaics
- Multi-city AOI configuration (Nairobi, Lagos, Kampala)

---

## License

MIT License

## Acknowledgments

Developed for urban resilience planning in Dar es Salaam, Tanzania.  
Satellite data: ESA Copernicus (Sentinel-2), USGS (Landsat), Google (Dynamic World).
