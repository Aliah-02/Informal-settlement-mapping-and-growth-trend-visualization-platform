# DarInformal — VS Code / Local Development Setup

Step-by-step guide to run DarInformal in **Visual Studio Code** after cloning.

---

## Requirements

| Tool | Version | Download |
|------|---------|----------|
| **VS Code** | latest | https://code.visualstudio.com/ |
| **Python** | 3.12+ | https://www.python.org/downloads/ |
| **PostgreSQL + PostGIS** | 16 + 3.4 | https://postgis.net/install/ |
| **Git** | any | https://git-scm.com/ |

### VS Code extensions (auto-prompted on open)

- Python + Pylance + debugpy
- Live Server (optional — compound launch includes frontend server)
- PostgreSQL Client (optional)

---

## Step 1 — Clone & open in VS Code

```bash
git clone https://github.com/Aliah-02/Informal-settlement-mapping-and-growth-trend-visualization-platform.git
cd Informal-settlement-mapping-and-growth-trend-visualization-platform/Dar-informal-settlements-webGIS
code .
```

> Open **`Dar-informal-settlements-webGIS`** as the workspace root.

---

## Step 2 — Environment file

```bash
cp .env.example .env
```

```env
DEBUG=true
USE_POSTGIS=true
DATABASE_URL_SYNC=postgresql://darinformal:darinformal@localhost:5432/darinformal
CORS_ORIGINS=["http://localhost:5500","http://127.0.0.1:5500"]
```

---

## Step 3 — PostgreSQL + PostGIS

```sql
CREATE USER darinformal WITH PASSWORD 'darinformal';
CREATE DATABASE darinformal OWNER darinformal;
```

```bash
psql -U postgres -d darinformal -f backend/data/init.sql
psql -U darinformal -d darinformal -h localhost -c "SELECT PostGIS_Version();"
```

---

## Step 4 — Python virtual environment

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt
```

`Ctrl+Shift+P` → **Python: Select Interpreter** → `backend/.venv`

---

## Step 5 — Sample data & PostGIS import

```bash
python data/generate_sample_data.py
python scripts/import_geojson_to_postgis.py --all
python scripts/compute_yearly_metrics.py
```

---

## Step 6 — Run full stack (compound launch)

1. **Ctrl+Shift+D** → **DarInformal: Full Stack (Windows)** or **(Linux/macOS)**
2. Press **F5**

Starts:
- FastAPI → http://localhost:8000
- Frontend → http://localhost:5500

---

## Daily workflow

| Step | Action |
|------|--------|
| 1 | Start PostgreSQL service |
| 2 | **F5** → Full Stack compound launch |
| 3 | Edit code — backend auto-reloads; refresh browser for frontend |

---

## Launch configurations

| Configuration | Purpose |
|---------------|---------|
| **DarInformal: Full Stack** | API + frontend together (F5) |
| **FastAPI Backend** | Debug API with breakpoints |
| **Frontend (port 5500)** | Static frontend server only |
| **Import GeoJSON → PostGIS** | Load GEE exports into DB |
| **Compute Yearly Metrics** | Refresh dashboard cache |
| **Generate Sample Data** | Create synthetic GeoJSON |

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Wrong Python interpreter | Select `backend/.venv` |
| CORS errors | `DEBUG=true` + add port 5500 to `CORS_ORIGINS` |
| PostGIS connection refused | Start PostgreSQL service |
| Map empty, API works | Run import task; check `/api/health` |
