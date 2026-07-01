# Connect Render + Vercel

## Your live URLs

| Service | URL |
|---------|-----|
| **Frontend (Vercel)** | https://informal-settlement-mapping-and-gro.vercel.app |
| **Backend (Render)** | https://informal-settlement-mapping-and-growth-sm5w.onrender.com |

---

## Fix: `Dockerfile: no such file or directory`

Render could not find the Dockerfile because **Root Directory** and **Dockerfile path** did not match.

### Option A — Root Directory empty (recommended)

In Render → your web service → **Settings**:

| Setting | Value |
|---------|-------|
| **Root Directory** | *(leave empty)* |
| **Dockerfile Path** | `Dockerfile` |
| **Docker Context** | `.` |

The repo now has `Dockerfile` at the **repository root** that builds the backend.

### Option B — Root Directory = subfolder

| Setting | Value |
|---------|-------|
| **Root Directory** | `Dar-informal-settlements-webGIS` |
| **Dockerfile Path** | `backend/Dockerfile` |
| **Docker Context** | `backend` |

---

## Render environment variables

| Key | Value |
|-----|-------|
| `FRONTEND_URL` | `https://informal-settlement-mapping-and-gro.vercel.app` |
| `DEBUG` | `false` |
| `USE_POSTGIS` | `true` |
| `AUTO_IMPORT_ON_STARTUP` | `true` |
| `PYTHONPATH` | `/app` |

Delete empty `CORS_ORIGINS`. **Start Command** = blank.

Then: **Manual Deploy → Clear build cache & deploy**

### Test API

```
https://informal-settlement-mapping-and-growth-sm5w.onrender.com/api/health
```

---

## Vercel environment variable

**Settings → Environment Variables:**

| Key | Value |
|-----|-------|
| `DARINFORMAL_API_URL` | `https://informal-settlement-mapping-and-growth-sm5w.onrender.com/api` |

Redeploy Vercel after saving.

---

## Verify

1. API health returns `"status": "healthy"` and 5 data years
2. Vercel map shows settlement polygons
3. No CORS errors in browser console (F12)
