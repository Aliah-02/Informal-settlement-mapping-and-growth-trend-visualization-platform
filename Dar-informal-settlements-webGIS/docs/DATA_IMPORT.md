# Importing Your GEE Data (GeoJSON + GeoTIFF)

Use this guide when you have **GeoJSON settlement files** and **GeoTIFF raster files** from Google Earth Engine.

---

## 1. File naming (required)

### GeoJSON → `backend/data/geojson/`

| Year | Filename |
|------|----------|
| 2005 | `settlements_2005.geojson` |
| 2010 | `settlements_2010.geojson` |
| 2015 | `settlements_2015.geojson` |
| 2020 | `settlements_2020.geojson` |
| 2026 | `settlements_2026.geojson` |

Import a single file with a custom path:

```bash
python scripts/import_geojson_to_postgis.py --file "D:/your/path/Tandale_2020.geojson" --year 2020
```

### GeoTIFF → `backend/data/raster/`

Accepted names per year: `isi_YYYY.tif`, `darinformal_YYYY.tif`, `indices_YYYY.tif`, or any `.tif` containing the year in the filename.

---

## 2. Required GeoJSON properties

| Property | Type | Example |
|----------|------|---------|
| `id` | string | `DAR-2020-0001` |
| `name` | string | `Tandale` |
| `year` | int | `2020` |
| `isi_score` | float | `0.452` |
| `risk_level` | string | `low` / `medium` / `high` |
| `area_ha` | float | `12.34` |
| `population_proxy` | int | `42150` |
| `ndbi`, `ndvi`, `bsi`, `fragmentation_index` | float | spectral values |

**CRS:** EPSG:4326 (WGS84)

---

## 3. Import commands

```bash
cd backend
source .venv/bin/activate          # Windows: .venv\Scripts\activate

# ONE COMMAND — GeoJSON → PostGIS + raster catalog
python scripts/import_all_data.py

# GeoJSON only
python scripts/import_all_data.py --skip-raster

# Single year
python scripts/import_all_data.py --year 2020
```

### Step by step

```bash
python scripts/import_geojson_to_postgis.py --all
python scripts/compute_yearly_metrics.py
python scripts/catalog_rasters.py
```

---

## 4. Verify import

```bash
psql -U darinformal -d darinformal -c \
  "SELECT year, COUNT(*) FROM settlements GROUP BY year ORDER BY year;"

curl http://localhost:8000/api/health
curl http://localhost:8000/api/risk/2020
curl http://localhost:8000/api/metrics/trend
```

Raster catalog: `backend/data/raster/raster_manifest.json`

---

## 5. Restart API

```bash
uvicorn main:app --reload --port 8000
```

Refresh the browser — time slider should show all imported years.

---

## 6. Production (Render Postgres)

```bash
DATABASE_URL_SYNC="postgresql://user:pass@host/darinformal" \
  python scripts/import_geojson_to_postgis.py --all
```

Get the external DB URL from Render → PostgreSQL → **Connections**.

---

## 7. Troubleshooting

| Problem | Solution |
|---------|----------|
| Year not in API | Filename must be `settlements_YYYY.geojson` |
| `risk_level` error | Values must be `low`, `medium`, or `high` |
| CRS error | Reproject in QGIS to EPSG:4326 |
| Empty map after import | Restart API; check `/api/health` |
| Raster not cataloged | Run `catalog_rasters.py`; check `raster_manifest.json` |

---

## 8. VS Code task

**Ctrl+Shift+P** → **Tasks: Run Task** → `DarInformal: Import data to PostGIS`
