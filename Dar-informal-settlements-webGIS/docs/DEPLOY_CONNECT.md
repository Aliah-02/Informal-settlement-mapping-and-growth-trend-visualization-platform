# Connect Render + Vercel

## Your URLs

| Service | URL |
|---------|-----|
| **Frontend (Vercel)** | https://informal-settlement-mapping-and-gro.vercel.app |
| **Backend (Render)** | https://informal-settlement-mapping-and-growth-sm5w.onrender.com |

---

## Current status (what your health JSON means)

```json
{
  "status": "healthy",
  "data_source": "geojson",
  "database": { "connected": false },
  "data_years_available": [2005, 2010, 2015, 2020, 2026]
}
```

| Field | Meaning |
|-------|---------|
| `status: healthy` | API is running — good |
| `data_source: geojson` | Serving map data from bundled files (works on Vercel) |
| `database.connected: false` | PostgreSQL not linked yet |
| `data_years_available: 5 yrs` | Map and dashboard will work |

**Your Vercel map should already show settlement polygons** using GeoJSON fallback.

### Render environment variables

| Key | Value |
|-----|-------|
| `FRONTEND_URL` | `https://informal-settlement-mapping-and-gro.vercel.app` |
| `DEBUG` | `false` |
| `USE_POSTGIS` | `true` |
| `AUTO_IMPORT_ON_STARTUP` | `true` |
| `JWT_SECRET` | long random string (required for login) |
| `ADMIN_EMAIL` | admin login email |
| `ADMIN_PASSWORD` | admin login password (change after first deploy) |
| `DATABASE_URL` | Render Postgres internal URL (for users & downloads) |

**Delete** `CORS_ORIGINS` if empty. **Start Command** must be **blank**.

Test: `https://informal-settlement-mapping-and-growth-sm5w.onrender.com/api/health`

---

## Auth & admin dashboard

- **Sign up / Login:** `/auth.html`
- **Admin dashboard:** `/admin.html` (admin role only)
- Default admin is created on first boot from `ADMIN_EMAIL` / `ADMIN_PASSWORD`
- Visitor stats and download logs require `DATABASE_URL` linked on Render

---

## Enable PostGIS (optional upgrade)

### Step 1 — Create PostgreSQL on Render

1. Render Dashboard → **New** → **PostgreSQL**
2. Name: `darinformal-db`, Plan: Free, Region: same as API
3. Create database

### Step 2 — Link DATABASE_URL to your web service

1. Open **informal-settlement-mapping-and-growth-sm5w** (web service)
2. **Environment** → **Add Environment Variable**
3. Key: `DATABASE_URL`
4. Value: click **Add from database** → select `darinformal-db` → **Internal Database URL**
5. Save → **Manual Deploy**

### Step 3 — Verify

After redeploy (~2 min), check:

```
https://informal-settlement-mapping-and-growth-sm5w.onrender.com/api/health
```

Expected after PostGIS links:

```json
{
  "data_source": "postgis",
  "database": {
    "configured": true,
    "connected": true,
    "settlement_count": 119
  }
}
```

On first boot the API auto-imports GeoJSON into PostGIS.

---

## Vercel connection

**Environment variable:**

```
DARINFORMAL_API_URL=https://informal-settlement-mapping-and-growth-sm5w.onrender.com/api
```

**Render environment:**

```
FRONTEND_URL=https://informal-settlement-mapping-and-gro.vercel.app
```

---

## Render Docker settings

| Setting | Value |
|---------|-------|
| Root Directory | *(empty)* |
| Dockerfile Path | `Dockerfile` |
| Start Command | *(empty)* |
