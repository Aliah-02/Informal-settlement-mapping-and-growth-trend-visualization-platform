# Database Connection Guide — DarInformal Platform

This guide explains how to connect **PostgreSQL (PostGIS)** on Render to the DarInformal API for:

- Settlement polygon storage (map layers)
- User accounts (login / signup / admin)
- Visitor analytics (daily, monthly, yearly)
- Download logs (who downloaded reports)

---

## Architecture

```
Vercel (frontend)  →  Render API (FastAPI)  →  Render PostgreSQL (PostGIS)
```

| Component | URL / Service |
|-----------|----------------|
| Frontend | https://informal-settlement-mapping-and-gro.vercel.app |
| API | https://informal-settlement-mapping-and-growth-sm5w.onrender.com |
| Database | Render PostgreSQL (`darinformal-db` or your DB name) |

---

## Step 1 — Create PostgreSQL on Render

1. Open [Render Dashboard](https://dashboard.render.com)
2. Click **New** → **PostgreSQL**
3. Settings:
   - **Name:** `darinformal-db`
   - **Database:** `darinformal`
   - **User:** auto-generated
   - **Region:** same as your web service (e.g. Oregon)
   - **Plan:** Free (or paid for production)
4. Click **Create Database**

Wait until status shows **Available**.

---

## Step 2 — Link DATABASE_URL to the API service

1. Open your **web service:** `informal-settlement-mapping-and-growth-sm5w`
2. Go to **Environment**
3. Click **Add Environment Variable**
4. Key: `DATABASE_URL`
5. Value: click **Add from database** → select `darinformal-db` → choose **Internal Database URL**
6. Click **Save Changes**

Render will auto-redeploy the API.

### Other required environment variables

| Key | Example | Purpose |
|-----|---------|---------|
| `FRONTEND_URL` | `https://informal-settlement-mapping-and-gro.vercel.app` | CORS for Vercel |
| `JWT_SECRET` | `your-long-random-string-here` | Login token signing |
| `ADMIN_EMAIL` | `admin@lsm2group11.com` | Default admin account |
| `ADMIN_PASSWORD` | `ChangeMe@2026!` | Default admin password |
| `USE_POSTGIS` | `true` | Enable PostGIS mode |
| `AUTO_IMPORT_ON_STARTUP` | `true` | Import GeoJSON on first boot |

**Start Command** must be **blank** when using **Docker**. **Root Directory** must be **empty** (uses repo root `Dockerfile`).

### Render runtime settings (important)

| Setting | Correct value |
|---------|----------------|
| **Runtime** | **Docker** (recommended) |
| **Dockerfile Path** | `./Dockerfile` |
| **Docker Context** | `.` (repository root) |
| **Build Command** | *(leave empty for Docker)* |
| **Start Command** | *(leave empty for Docker)* |

If the service is set to **Python** instead of Docker, Render runs `pip install -r requirements.txt` at the repo root. This repo now includes root `requirements.txt`, `runtime.txt` (Python 3.12), and `start.sh` for that path — but **Docker is strongly recommended** because GeoPandas/Rasterio need system GDAL libraries.

**Wrong settings that cause build failure:**

```
ERROR: Could not open requirements file: requirements.txt
Using Python version 3.14.x
```

Fix: In Render → your web service → **Settings** → set **Runtime** to **Docker**, **Dockerfile Path** to `./Dockerfile`, clear custom Build/Start commands, then **Manual Deploy**.

---

## Step 3 — Verify connection

After redeploy (~2 minutes), open:

```
https://informal-settlement-mapping-and-growth-sm5w.onrender.com/api/health
```

Expected when connected:

```json
{
  "status": "healthy",
  "data_source": "postgis",
  "database": {
    "configured": true,
    "connected": true,
    "settlement_count": 119
  }
}
```

Check auth tables:

```
https://informal-settlement-mapping-and-growth-sm5w.onrender.com/api/auth/status
```

Expected:

```json
{
  "ready": true,
  "admin_users": 1
}
```

---

## Step 4 — Connect from your local machine (optional)

Use the **External Database URL** from Render Postgres → **Connections** tab.

```bash
# Example — replace with your External URL from Render
export DATABASE_URL="postgresql://user:password@dpg-xxxxx.oregon-postgres.render.com/darinformal"

cd Dar-informal-settlements-webGIS/backend

# Apply schema + import GeoJSON
python scripts/bootstrap_db.py
python scripts/import_geojson_to_postgis.py --all
python scripts/compute_yearly_metrics.py
```

### Using psql directly

```bash
psql "postgresql://USER:PASSWORD@HOST/DATABASE?sslmode=require"
```

```sql
-- Check tables
\dt

-- Verify users table
SELECT email, role, created_at FROM users;

-- Verify settlements
SELECT year, COUNT(*) FROM settlements GROUP BY year;
```

---

## Step 5 — Vercel frontend connection

In Vercel → Project → **Settings** → **Environment Variables**:

```
DARINFORMAL_API_URL=https://informal-settlement-mapping-and-growth-sm5w.onrender.com/api
```

Redeploy Vercel after saving.

---

## Tables created automatically

On API startup, `bootstrap_db.py` creates:

| Table | Purpose |
|-------|---------|
| `settlements` | Informal settlement polygons + ISI attributes |
| `yearly_metrics` | Pre-computed dashboard metrics |
| `change_detection` | Temporal change records |
| `users` | Login / signup accounts |
| `user_sessions` | Live user tracking |
| `page_visits` | Visitor statistics |
| `download_logs` | Who downloaded CSV reports |

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `Could not open requirements file: requirements.txt` | Switch Runtime to **Docker** with `./Dockerfile`, or redeploy after pulling latest `main` (root `requirements.txt` added) |
| Build uses Python 3.14 | Set Runtime to **Docker**, or ensure `runtime.txt` at repo root pins `python-3.12.12` |
| CORS / "Failed to fetch" on login | Redeploy Render after setting `FRONTEND_URL`; ensure `DATABASE_URL` is linked |
| `database.connected: false` | Add `DATABASE_URL` from Render Postgres internal URL |
| `auth/status` → `ready: false` | Redeploy API (clears build cache) so auth tables are created |
| Map works but login fails | Map uses GeoJSON fallback; login **requires** PostgreSQL |
| `settlement_count: 0` | Run `import_geojson_to_postgis.py --all` or wait for auto-import |
| SSL connection error | Render requires `sslmode=require` (handled automatically in code) |

---

## Default admin (change after first login)

| Field | Value |
|-------|-------|
| Email | `admin@lsm2group11.com` |
| Password | `Admin@2026!` |

Admin is created automatically on first successful database bootstrap.

---

## Security checklist

1. Change `ADMIN_PASSWORD` after first deploy
2. Set a strong random `JWT_SECRET` (32+ characters)
3. Never commit `DATABASE_URL` to GitHub
4. Use Render **Internal** Database URL on the web service (not External)

---

## Related docs

- [DEPLOY_CONNECT.md](docs/DEPLOY_CONNECT.md) — Render + Vercel setup
- [RED.md](RED.md) — Import real GeoJSON polygons into PostGIS
- [DATA_IMPORT.md](docs/DATA_IMPORT.md) — Data pipeline details
