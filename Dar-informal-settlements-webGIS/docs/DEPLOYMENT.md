# DarInformal — Cloud Deployment (Render + Vercel)

Deploy the full WebGIS stack on **free tiers**:
- **Backend (FastAPI + PostGIS)** → [Render](https://render.com)
- **Frontend (Leaflet + Dashboard)** → [Vercel](https://vercel.com)

> GeoServer WMS is **not** included on free cloud tiers. The app uses **API GeoJSON** mode automatically in production.

---

## Architecture (Production)

```text
Vercel (frontend)  ──HTTPS──►  Render (FastAPI API)
                                      │
                                      ▼
                               Render PostgreSQL + PostGIS
```

| Tier | Service | URL example |
|------|---------|-------------|
| Vercel | Static frontend | `https://darinformal.vercel.app` |
| Render | FastAPI backend | `https://darinformal-api.onrender.com` |
| Render | PostgreSQL | Internal `DATABASE_URL` |

---

## Part 1 — Deploy Backend on Render

### Option A: Blueprint (recommended)

1. Push repo to GitHub
2. Go to [Render Dashboard](https://dashboard.render.com/) → **New** → **Blueprint**
3. Connect repository
4. Set **Root Directory**: `Dar-informal-settlements-webGIS`
5. Render reads `render.yaml` and creates:
   - PostgreSQL database `darinformal-db`
   - Web service `darinformal-api` (Docker)

### Option B: Manual Web Service

1. **New** → **Web Service** → connect repo
2. **Root Directory**: `Dar-informal-settlements-webGIS/backend`
3. **Runtime**: Docker
4. **Plan**: Free
5. Add **PostgreSQL** database (free) and link `DATABASE_URL`

### Render environment variables

| Variable | Value |
|----------|-------|
| `DATABASE_URL` | Auto from Render Postgres |
| `USE_POSTGIS` | `true` |
| `AUTO_IMPORT_ON_STARTUP` | `true` |
| `FRONTEND_URL` | `https://your-app.vercel.app` |
| `CORS_ORIGINS` | `["https://your-app.vercel.app"]` |

### First deploy bootstrap

On startup, the API automatically:
1. Enables PostGIS extension
2. Applies `init.sql` schema
3. Imports bundled `data/geojson/*.geojson` if DB is empty

### Verify backend

```bash
curl https://darinformal-api.onrender.com/api/health
curl -O https://darinformal-api.onrender.com/api/metrics/trend/csv
```

> **Note:** Render free tier spins down after 15 min inactivity. First request may take ~30s.

---

## Part 2 — Deploy Frontend on Vercel

### Steps

1. Go to [Vercel Dashboard](https://vercel.com/new)
2. Import GitHub repository
3. Configure project:

| Setting | Value |
|---------|-------|
| **Root Directory** | `Dar-informal-settlements-webGIS/frontend` |
| **Framework Preset** | Other |
| **Build Command** | `npm run build` |
| **Output Directory** | `.` |

4. Add **Environment Variable**:

| Name | Value |
|------|-------|
| `DARINFORMAL_API_URL` | `https://darinformal-api.onrender.com/api` |

5. Click **Deploy**

### Build process

`npm run build` runs `scripts/build-env.mjs` which writes `js/env.js`:

```javascript
window.DARINFORMAL_API_URL = 'https://darinformal-api.onrender.com/api';
window.DARINFORMAL_DEFAULT_RENDER_MODE = 'geojson';
```

### Verify frontend

1. Open your Vercel URL
2. Map should load with settlement polygons
3. Time slider switches years
4. Click **⬇ CSV Report** in dashboard → downloads growth trend CSV

---

## Part 3 — Connect Frontend ↔ Backend

After both are deployed:

### 1. Update Render CORS

In Render dashboard → `darinformal-api` → **Environment**:

```
FRONTEND_URL=https://darinformal-xxxx.vercel.app
CORS_ORIGINS=["https://darinformal-xxxx.vercel.app"]
```

Redeploy API service.

### 2. Confirm Vercel API URL

In Vercel → **Settings** → **Environment Variables**:

```
DARINFORMAL_API_URL=https://darinformal-api.onrender.com/api
```

Redeploy frontend.

### 3. Integration checklist

| Check | Expected |
|-------|----------|
| `GET /api/health` | `"data_source": "postgis"` |
| Map loads on Vercel | Settlement polygons visible |
| Time slider | Years 2005–2026 switch |
| Dashboard charts | Bar/line charts populated |
| CSV download | `darinformal_growth_trend_report.csv` |
| Change detection CSV | Available after applying change mode |

---

## CSV Report Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /api/metrics/trend/csv` | Full growth trend report |
| `GET /api/change/{from}/{to}/csv` | Change detection report |

Frontend download button calls the trend CSV endpoint directly.

---

## Importing Your Own GEE Data (Production)

### GeoJSON

1. SSH is not available on Render free — use **one-time import** before deploy OR admin endpoint:

```bash
# Local: import to Render Postgres using external connection string
DATABASE_URL_SYNC="postgresql://user:pass@host/darinformal" \
  python scripts/import_geojson_to_postgis.py --all
```

Get external DB URL from Render → PostgreSQL → **Connections** → **External Database URL**

### Raster (GeoTIFF)

GeoServer is not on Render free tier. Options:
- Use **API GeoJSON** mode (default on Vercel)
- Host GeoServer separately (Railway, VPS) and set `GEOSERVER_PUBLIC_URL`

---

## Environment files reference

### Render (`darinformal-api`)

```env
DATABASE_URL=<auto>
USE_POSTGIS=true
AUTO_IMPORT_ON_STARTUP=true
FRONTEND_URL=https://darinformal.vercel.app
CORS_ORIGINS=["https://darinformal.vercel.app"]
```

### Vercel (`darinformal-frontend`)

```env
DARINFORMAL_API_URL=https://darinformal-api.onrender.com/api
```

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| CORS error on Vercel | Add Vercel URL to Render `CORS_ORIGINS` + `FRONTEND_URL` |
| API cold start slow | Normal on Render free — wait 30s |
| Empty map | Check `/api/health` — re-import GeoJSON to Render Postgres |
| CSV download fails | Ensure API URL correct in Vercel env |
| PostGIS extension error | Render Postgres supports `CREATE EXTENSION postgis` — check logs |
| WMS not working | Expected on free tier — use **API GeoJSON** map mode |

---

## Local vs Cloud

| Feature | Local (VS Code) | Render + Vercel |
|---------|-----------------|-----------------|
| PostGIS | ✅ | ✅ Render Postgres |
| GeoServer WMS | ✅ optional | ❌ not on free tier |
| CSV reports | ✅ | ✅ |
| Hybrid map mode | ✅ | API GeoJSON only |
| Docker | ✅ | Render uses Dockerfile |

---

## Quick deploy commands

```bash
# Clone
git clone https://github.com/Aliah-02/Informal-settlement-mapping-and-growth-trend-visualization-platform.git

# Test CSV locally
curl -O http://localhost:8000/api/metrics/trend/csv

# Render: push to GitHub → connect Blueprint
# Vercel: import frontend/ → set DARINFORMAL_API_URL → deploy
```
