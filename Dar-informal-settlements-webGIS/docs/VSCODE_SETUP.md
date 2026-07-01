# DarInformal — VS Code / Local Development Setup

Step-by-step guide to run DarInformal in **Visual Studio Code** after cloning.

---

## Requirements (install before opening VS Code)

| Tool | Version | Download |
|------|---------|----------|
| **VS Code** | latest | https://code.visualstudio.com/ |
| **Python** | 3.12+ | https://www.python.org/downloads/ |
| **PostgreSQL + PostGIS** | 16 + 3.4 | https://postgis.net/install/ |
| **Git** | any | https://git-scm.com/ |
| **Java JDK** | 17 | For GeoServer (optional for WMS) |
| **GeoServer** | 2.24+ | https://geoserver.org/download/ (optional) |

### VS Code extensions (auto-prompted on open)

- Python + Pylance + debugpy
- Live Server (frontend)
- PostgreSQL Client (optional)
- REST Client (optional)

---

## Step 1 — Clone & open in VS Code

```bash
git clone https://github.com/Aliah-02/Informal-settlement-mapping-and-growth-trend-visualization-platform.git
cd Informal-settlement-mapping-and-growth-trend-visualization-platform/Dar-informal-settlements-webGIS
code .
```

> **Open the `Dar-informal-settlements-webGIS` folder** as the workspace root (not the parent repo).

---

## Step 2 — Environment file

```bash
cp .env.example .env
```

Edit `.env` for local VS Code development:

```env
DEBUG=true
USE_POSTGIS=true

DATABASE_URL_SYNC=postgresql://darinformal:darinformal@localhost:5432/darinformal

# Full URL required when not using Nginx
GEOSERVER_PUBLIC_URL=http://localhost:8080/geoserver

CORS_ORIGINS=["http://localhost:5500","http://localhost:3000","http://127.0.0.1:5500"]
```

---

## Step 3 — PostgreSQL + PostGIS

### Windows (pgAdmin or psql)

```sql
CREATE USER darinformal WITH PASSWORD 'darinformal';
CREATE DATABASE darinformal OWNER darinformal;
```

Then in VS Code terminal:

```powershell
psql -U postgres -d darinformal -f backend\data\init.sql
```

### Linux / macOS

```bash
sudo -u postgres psql -c "CREATE USER darinformal WITH PASSWORD 'darinformal';"
sudo -u postgres psql -c "CREATE DATABASE darinformal OWNER darinformal;"
sudo -u postgres psql -d darinformal -f backend/data/init.sql
```

Verify:

```bash
psql -U darinformal -d darinformal -h localhost -c "SELECT PostGIS_Version();"
```

---

## Step 4 — Python virtual environment

In VS Code terminal (`Ctrl+`` `):

```bash
cd backend
python -m venv .venv

# Windows
.venv\Scripts\activate
pip install -r requirements.txt

# macOS / Linux
source .venv/bin/activate
pip install -r requirements.txt
```

Select interpreter in VS Code:
`Ctrl+Shift+P` → **Python: Select Interpreter** → `backend/.venv`

Or run task: `Ctrl+Shift+P` → **Tasks: Run Task** → `DarInformal: Create venv + install deps`

---

## Step 5 — Sample data & PostGIS import

```bash
# Generate GeoJSON (if missing)
python data/generate_sample_data.py

# Import into PostGIS
python scripts/import_geojson_to_postgis.py --all
python scripts/compute_yearly_metrics.py
```

Or use VS Code debugger:
- **Run and Debug** (`Ctrl+Shift+D`) → **Import GeoJSON → PostGIS**

Verify:

```bash
curl http://localhost:8000/api/health
```

---

## Step 6 — Run backend from VS Code

1. Open **Run and Debug** panel (`Ctrl+Shift+D`)
2. Select **FastAPI Backend**
3. Press **F5** (starts uvicorn with hot reload + breakpoints)

API available at:
- http://localhost:8000/docs
- http://localhost:8000/api/health

---

## Step 7 — Run frontend from VS Code

### Option A — Live Server extension (recommended)

1. Install **Live Server** extension
2. Right-click `frontend/index.html` → **Open with Live Server**
3. Opens at http://localhost:5500 (API URL auto-configured via `frontend/js/config.js`)

### Option B — Simple HTTP server

```bash
cd frontend
python -m http.server 3000
```

Open http://localhost:3000

---

## Step 8 — GeoServer (optional, for WMS hybrid mode)

1. Download & start GeoServer standalone → http://localhost:8080/geoserver
2. In VS Code terminal (project root):

```bash
pip install requests
set GEOSERVER_URL=http://localhost:8080/geoserver
set POSTGRES_HOST=localhost
python scripts/setup_geoserver.py
```

Or: **Tasks: Run Task** → `DarInformal: Setup GeoServer`

In the map legend, set **Map source** to **Hybrid (WMS + API)**.

---

## Daily development workflow

| Step | Action |
|------|--------|
| 1 | Start PostgreSQL service |
| 2 | `F5` → **FastAPI Backend** |
| 3 | Right-click `index.html` → **Open with Live Server** |
| 4 | (Optional) Start GeoServer |
| 5 | Edit code — backend auto-reloads, refresh browser for frontend |

---

## VS Code launch configurations

| Configuration | Purpose |
|---------------|---------|
| **FastAPI Backend** | Debug API with breakpoints |
| **Import GeoJSON → PostGIS** | Load GEE exports into DB |
| **Compute Yearly Metrics** | Refresh dashboard cache |
| **Generate Sample Data** | Create synthetic GeoJSON |

---

## Troubleshooting in VS Code

| Problem | Fix |
|---------|-----|
| Wrong Python interpreter | `Ctrl+Shift+P` → Python: Select Interpreter → `.venv` |
| CORS errors | Set `DEBUG=true` and add Live Server port to `CORS_ORIGINS` in `.env` |
| `postgis` connection refused | Start PostgreSQL Windows service / `sudo systemctl start postgresql` |
| Map empty, API works | Select **API GeoJSON** map mode, or run data import task |
| Breakpoints not hit | Ensure **FastAPI Backend** launch config is used (not plain terminal) |

---

## Minimum vs full stack in VS Code

| Component | Minimum dev | Full WebGIS |
|-----------|-------------|-------------|
| PostGIS | ✅ | ✅ |
| FastAPI (F5) | ✅ | ✅ |
| Live Server | ✅ | ✅ |
| GeoServer | ❌ | ✅ |

**Minimum**: Steps 1–7 only. Use **API GeoJSON** map mode.
