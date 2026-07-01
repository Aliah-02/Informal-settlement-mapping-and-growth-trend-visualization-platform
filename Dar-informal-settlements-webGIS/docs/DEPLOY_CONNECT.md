# Connect Render (API) + Vercel (Frontend)

Simple 2-step cloud setup for the WebGIS.

```text
Browser  →  Vercel (map + dashboard)
                │
                │  HTTPS  /api/risk/2020  etc.
                ▼
            Render (FastAPI + PostGIS)
```

---

## Step 1 — Render (backend)

1. [Render Dashboard](https://dashboard.render.com/) → **New** → **Blueprint**
2. Connect your GitHub repo
3. **Root Directory:** `Dar-informal-settlements-webGIS`
4. After deploy, open **darinformal-api** → **Environment** and set:

| Key | Example value |
|-----|----------------|
| `FRONTEND_URL` | `https://your-project.vercel.app` |

5. **Delete** `CORS_ORIGINS` if it exists and is empty.
6. **Start Command** — leave **blank** (uses Docker `start.sh`).
7. **Manual Deploy** → **Clear build cache & deploy** (important after code updates).

8. Test:
   ```
   https://YOUR-API.onrender.com/api/health
   ```
   Expect: `"status": "healthy"`

Copy your API URL: `https://YOUR-API.onrender.com/api`

---

## Step 2 — Vercel (frontend)

1. [Vercel](https://vercel.com/new) → Import repo
2. **Root Directory:** `Dar-informal-settlements-webGIS/frontend`
3. **Environment variable:**

| Key | Value |
|-----|-------|
| `DARINFORMAL_API_URL` | `https://YOUR-API.onrender.com/api` |

4. Deploy

5. Open your Vercel URL — map polygons load from Render API.

---

## Step 3 — Link them (after both are live)

Back on Render, set:

```
FRONTEND_URL=https://your-actual-vercel-url.vercel.app
```

Redeploy Render API. Vercel preview URLs (`*.vercel.app`) are allowed automatically.

---

## If Render exits with status 1

| Log message | Fix |
|-------------|-----|
| `NoDecode` import error | **Clear build cache & deploy** — old Docker image cached |
| `cors_origins` parse error | Delete empty `CORS_ORIGINS` env var on Render |
| `No module named config` | Redeploy latest code (fixed in `start.sh`) |
| No open ports | Clear **Start Command** in Render settings |

---

## Local test (VS Code)

```bash
cd Dar-informal-settlements-webGIS
make setup && make import
make dev-api      # :8000
make dev-frontend # :5500
```

F5 → **DarInformal: Full Stack** in VS Code.
