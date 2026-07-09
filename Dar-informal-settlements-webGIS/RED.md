# RED.md — Import Real GeoPolygon Data (GitHub → Render PostGIS → All APIs)

**Goal:** Put your real informal settlement polygon GeoJSON files in GitHub, load them into **Render PostgreSQL/PostGIS**, and serve them through **every API endpoint** used by the Vercel map and dashboard.

**Your live services:**

| Service | URL |
|---------|-----|
| Frontend (Vercel) | https://informal-settlement-mapping-and-gro.vercel.app |
| Backend (Render) | https://informal-settlement-mapping-and-growth-sm5w.onrender.com |
| PostgreSQL | Created on Render (you already have this) |

---

## TODO checklist (do in order)

- [ ] **1.** Prepare real GeoJSON polygon files (one file per year)
- [ ] **2.** Push files to GitHub in the correct folder
- [ ] **3.** Link `DATABASE_URL` from Render Postgres → Render web service
- [ ] **4.** Import polygons into PostGIS (local script → Render database)
- [ ] **5.** Compute yearly metrics for dashboard
- [ ] **6.** Redeploy Render API
- [ ] **7.** Verify all API endpoints return PostGIS data
- [ ] **8.** Confirm Vercel map + CSV reports work

---

## STEP 1 — Prepare your real GeoJSON polygons

### Required file names (exact)

Put files here in the repo:

```
Dar-informal-settlements-webGIS/backend/data/geojson/
├── settlements_2005.geojson
├── settlements_2010.geojson
├── settlements_2015.geojson
├── settlements_2020.geojson
└── settlements_2026.geojson
```

### Required format

| Rule | Detail |
|------|--------|
| Geometry type | `Polygon` or `MultiPolygon` |
| CRS | **EPSG:4326** (WGS84 lat/lon) |
| File type | `.geojson` FeatureCollection |

### Required properties per polygon feature

| Property | Type | Example |
|----------|------|---------|
| `id` | string | `DAR-2020-0001` |
| `name` | string | `Tandale` |
| `year` | integer | `2020` |
| `isi_score` | float 0–1 | `0.452` |
| `risk_level` | string | `low`, `medium`, or `high` |
| `area_ha` | float | `12.34` |
| `population_proxy` | integer | `42150` |
| `ndbi` | float | `0.21` |
| `ndvi` | float | `0.35` |
| `bsi` | float | `0.18` |
| `fragmentation_index` | float | `0.42` |

> Missing properties are auto-calculated on import, but **geometry + year** are required.

### If your file has a different name

Rename before push, for example:

```text
MySettlements_2020.geojson  →  settlements_2020.geojson
```

Or import one file manually (Step 4B):

```bash
python scripts/import_geojson_to_postgis.py --file "path/to/your_file.geojson" --year 2020
```

### Reproject in QGIS (if needed)

1. Open your shapefile/GeoJSON in QGIS
2. Export → Save Features As → GeoJSON
3. CRS: **EPSG:4326**
4. Save as `settlements_YYYY.geojson`

---

## STEP 2 — Push real data to GitHub

On your computer:

```bash
# Clone your repo (if not already)
git clone https://github.com/Aliah-02/Informal-settlement-mapping-and-growth-trend-visualization-platform.git
cd Informal-settlement-mapping-and-growth-trend-visualization-platform

# Copy your real GeoJSON files into:
#   Dar-informal-settlements-webGIS/backend/data/geojson/

git add Dar-informal-settlements-webGIS/backend/data/geojson/*.geojson
git commit -m "Add real informal settlement GeoJSON polygons for all years"
git push origin main
```

### Large files (> 50 MB per file)

Use **Git LFS**:

```bash
git lfs install
git lfs track "*.geojson"
git add .gitattributes
git add Dar-informal-settlements-webGIS/backend/data/geojson/*.geojson
git commit -m "Add real settlement GeoJSON via LFS"
git push origin main
```

---

## STEP 3 — Link Render PostgreSQL to your API

1. Open [Render Dashboard](https://dashboard.render.com/)
2. Open your **PostgreSQL** database (`darinformal-db` or similar)
3. Copy **External Database URL** (for import from your PC)  
   Also note **Internal Database URL** (for the API on Render)
4. Open web service **informal-settlement-mapping-and-growth-sm5w**
5. Go to **Environment** → add:

| Key | Value |
|-----|-------|
| `DATABASE_URL` | Click **Add from database** → select your Postgres → **Internal Database URL** |
| `USE_POSTGIS` | `true` |
| `AUTO_IMPORT_ON_STARTUP` | `true` |
| `FRONTEND_URL` | `https://informal-settlement-mapping-and-gro.vercel.app` |
| `DEBUG` | `false` |

6. **Delete** `CORS_ORIGINS` if it is empty
7. **Start Command** = leave blank
8. Save (do not redeploy yet — import data first in Step 4)

---

## STEP 4 — Import polygons into Render PostGIS

Run this **on your local computer** (not on Render). You need Python 3.12+.

### 4A — Setup (one time)

```bash
cd Dar-informal-settlements-webGIS/backend
python -m venv .venv

# Windows
.venv\Scripts\activate
# Mac/Linux
source .venv/bin/activate

pip install -r requirements.txt
```

### 4B — Import ALL years to Render Postgres

Replace the connection string with your **External Database URL** from Render:

```bash
# Windows PowerShell
$env:DATABASE_URL_SYNC="postgresql://USER:PASSWORD@HOST/darinformal?sslmode=require"

# Mac/Linux
export DATABASE_URL_SYNC="postgresql://USER:PASSWORD@HOST/darinformal?sslmode=require"
```

Then run:

```bash
# Apply schema + PostGIS extension
psql "$DATABASE_URL_SYNC" -f data/init.sql

# Import all GeoJSON polygons → PostGIS settlements table
python scripts/import_geojson_to_postgis.py --all

# Build dashboard metrics (KPIs, charts, CSV reports)
python scripts/compute_yearly_metrics.py
```

### 4C — Import ONE year only

```bash
python scripts/import_geojson_to_postgis.py --year 2020
python scripts/compute_yearly_metrics.py
```

### 4D — Verify in database

```bash
psql "$DATABASE_URL_SYNC" -c "SELECT year, COUNT(*) AS polygons, ROUND(SUM(area_ha)::numeric,1) AS total_ha FROM settlements GROUP BY year ORDER BY year;"
```

Expected output example:

```text
 year | polygons | total_ha
------+----------+----------
 2005 |       15 |    123.4
 2010 |       17 |    145.2
 ...
```

---

## STEP 5 — Redeploy Render API

1. Render Dashboard → **informal-settlement-mapping-and-growth-sm5w**
2. **Manual Deploy** → Deploy latest `main` branch
3. Wait ~2 minutes (free tier may take longer on cold start)

---

## STEP 6 — Verify ALL APIs use PostGIS data

Replace base URL if yours differs:

```text
BASE=https://informal-settlement-mapping-and-growth-sm5w.onrender.com/api
```

Run each check:

### 6.1 Health (must show `postgis`)

```bash
curl -s "$BASE/health" | python -m json.tool
```

**Expected:**

```json
{
  "status": "healthy",
  "data_source": "postgis",
  "database": {
    "configured": true,
    "connected": true,
    "settlement_count": 119
  },
  "data_years_available": [2005, 2010, 2015, 2020, 2026]
}
```

### 6.2 Risk layer GeoJSON (map polygons)

```bash
curl -s "$BASE/risk/2020" | python -c "import sys,json; d=json.load(sys.stdin); print('features:', len(d.get('features',[])))"
```

**Expected:** `features: 34` (or your real polygon count)

### 6.3 Growth trend (dashboard charts)

```bash
curl -s "$BASE/metrics/trend" | python -m json.tool
```

**Expected:** `metrics` array with one object per year

### 6.4 CSV report download

```bash
curl -O "$BASE/metrics/trend/csv"
```

**Expected:** file `darinformal_growth_trend_report.csv` downloads

### 6.5 Change detection

```bash
curl -s "$BASE/change/2010/2020" | python -m json.tool
```

**Expected:** `summary` with new/expanded/contracted counts

### 6.6 Settlements list

```bash
curl -s "$BASE/settlements?year=2020&limit=5" | python -m json.tool
```

### 6.7 Area of interest

```bash
curl -s "$BASE/aoi" | python -m json.tool
```

---

## STEP 7 — Connect Vercel frontend

In [Vercel Dashboard](https://vercel.com/) → your project → **Settings → Environment Variables**:

| Key | Value |
|-----|-------|
| `DARINFORMAL_API_URL` | `https://informal-settlement-mapping-and-growth-sm5w.onrender.com/api` |

**Redeploy** Vercel.

### Open and test

1. https://informal-settlement-mapping-and-gro.vercel.app
2. Map shows **your real polygons** colored by risk (green / orange / red)
3. Time slider switches years **2005 → 2026**
4. Dashboard KPIs and charts update per year
5. Click **⬇ CSV Report** → downloads growth trend CSV
6. Top-right badge shows: `API v1.0 · PostGIS · 5 yrs`

---

## API → data flow (how everything links)

```text
GitHub GeoJSON files
        │
        ▼  import_geojson_to_postgis.py
Render PostgreSQL / PostGIS
  ├── settlements          ← polygon geometries + ISI attributes
  └── yearly_metrics       ← dashboard KPIs (compute_yearly_metrics.py)
        │
        ▼  FastAPI (Render)
  GET /api/risk/{year}           → map polygons (Vercel Leaflet)
  GET /api/metrics/trend         → dashboard charts
  GET /api/metrics/trend/csv     → CSV download
  GET /api/change/{from}/{to}    → change detection overlay
  GET /api/settlements           → filtered settlement list
  GET /api/health                → status check
        │
        ▼
Vercel frontend (informal-settlement-mapping-and-gro.vercel.app)
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `data_source: geojson` in health | `DATABASE_URL` not linked on Render — redo Step 3 |
| `database.connected: false` | Use External URL with `?sslmode=require` for import; Internal URL on API |
| Import fails SSL error | Add `?sslmode=require` to `DATABASE_URL_SYNC` |
| `File not found` on import | File must be named `settlements_YYYY.geojson` in `backend/data/geojson/` |
| Empty map on Vercel | Set `DARINFORMAL_API_URL` with `/api` suffix; wait 30s for cold start |
| CORS error in browser | Set `FRONTEND_URL=https://informal-settlement-mapping-and-gro.vercel.app` on Render |
| Polygons wrong location | Reproject to EPSG:4326 in QGIS before import |
| `risk_level` error | Values must be exactly `low`, `medium`, or `high` |
| Re-import after update | Run `import_geojson_to_postgis.py --all` again (replaces per year) |

---

## Quick copy-paste (full import sequence)

```bash
cd Dar-informal-settlements-webGIS/backend
source .venv/bin/activate   # or .venv\Scripts\activate on Windows

export DATABASE_URL_SYNC="PASTE_YOUR_RENDER_EXTERNAL_DATABASE_URL_HERE"

psql "$DATABASE_URL_SYNC" -f data/init.sql
python scripts/import_geojson_to_postgis.py --all
python scripts/compute_yearly_metrics.py

curl -s https://informal-settlement-mapping-and-growth-sm5w.onrender.com/api/health
```

When health shows `"data_source": "postgis"` — **all APIs are linked to your real polygon data.**

---

## After import — update data later

When you have new GEE exports:

```bash
# 1. Replace GeoJSON in backend/data/geojson/
# 2. Push to GitHub
git add backend/data/geojson/
git commit -m "Update settlement polygons YYYY"
git push

# 3. Re-import to Render Postgres
export DATABASE_URL_SYNC="your_render_external_url"
python scripts/import_geojson_to_postgis.py --all
python scripts/compute_yearly_metrics.py
```

No Render redeploy needed unless you also changed API code.
