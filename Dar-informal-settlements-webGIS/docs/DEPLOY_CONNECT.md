# Connect Render + Vercel (your deployment)

## Your URLs

| Service | URL |
|---------|-----|
| **Frontend (Vercel)** | https://informal-settlement-mapping-and-gro.vercel.app |
| **Backend (Render)** | `https://YOUR-SERVICE-NAME.onrender.com` |

---

## Step 1 — Render must use branch `main`

The fixes are on **`main`**. In Render:

**Settings → Build & Deploy → Branch** → set to **`main`**

Then: **Manual Deploy → Clear build cache & deploy**

### Render environment (darinformal-api)

| Key | Value |
|-----|-------|
| `FRONTEND_URL` | `https://informal-settlement-mapping-and-gro.vercel.app` |
| `DEBUG` | `false` |
| `USE_POSTGIS` | `true` |
| `AUTO_IMPORT_ON_STARTUP` | `true` |

**Delete** `CORS_ORIGINS` if empty. **Start Command** must be **blank**.

Test: `https://YOUR-API.onrender.com/api/health`

---

## Step 2 — Vercel environment

**Settings → Environment Variables:**

| Key | Value |
|-----|-------|
| `DARINFORMAL_API_URL` | `https://YOUR-API.onrender.com/api` |

Replace `YOUR-API` with your actual Render service name. Must end with `/api`.

Redeploy Vercel after saving.

---

## Step 3 — Verify connection

1. Open https://informal-settlement-mapping-and-gro.vercel.app
2. Top-right badge should show: `API v1.0 · PostGIS · 5 yrs` (or GeoJSON if DB still seeding)
3. Map shows colored settlement polygons
4. Time slider changes years

If map is empty but API works: wait 60s (Render cold start) and refresh.

---

## Still failing?

| Symptom | Fix |
|---------|-----|
| `NoDecode` in logs | Wrong branch or cached build — use `main` + clear cache |
| Exited status 1 | Check Render logs after `Starting uvicorn...` |
| CORS error in browser | Set `FRONTEND_URL` exactly (no trailing slash) |
| API offline on Vercel | `DARINFORMAL_API_URL` must include `/api` suffix |
