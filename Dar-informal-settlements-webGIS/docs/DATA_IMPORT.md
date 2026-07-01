# Importing Your GEE Data (GeoJSON + GeoTIFF)

Use this guide when you already have **GeoJSON settlement files** and **GeoTIFF raster files** for all years from Google Earth Engine.

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

If your files have different names, **rename them** to match, or import individually:

```bash
python scripts/import_geojson_to_postgis.py --file "D:/your/path/Tandale_2020.geojson" --year 2020
```

### GeoTIFF → `backend/data/raster/`

Any of these names work per year:

| Accepted names |
|----------------|
| `isi_2005.tif` |
| `darinformal_2005.tif` |
| `indices_2005.tif` |
| `raster_2005.tif` |
| Any `.tif` containing the year in the filename (e.g. `DarInformal_ISI_2020.tif`) |

---

## 2. Required GeoJSON properties

Each polygon feature should include (or they will be auto-computed):

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

## 3. Folder layout after copying files

```
backend/data/
├── geojson/
│   ├── settlements_2005.geojson
│   ├── settlements_2010.geojson
│   ├── settlements_2015.geojson
│   ├── settlements_2020.geojson
│   └── settlements_2026.geojson
└── raster/
    ├── isi_2005.tif
    ├── isi_2010.tif
    ├── isi_2015.tif
    ├── isi_2020.tif
    └── isi_2026.tif
```

---

## 4. Import commands

Open terminal in `backend/` with venv active:

```bash
cd backend
source .venv/bin/activate          # Windows: .venv\Scripts\activate

# ONE COMMAND — import everything
python scripts/import_all_data.py

# With GeoServer raster publishing (GeoServer must be running)
python scripts/import_all_data.py --publish-raster
```

### Or step by step

```bash
# A) GeoJSON → PostGIS
python scripts/import_geojson_to_postgis.py --all
python scripts/compute_yearly_metrics.py

# B) Validate rasters
python scripts/publish_rasters_geoserver.py --scan

# C) Publish rasters to GeoServer (optional)
python scripts/publish_rasters_geoserver.py --publish
```

### Import a single year

```bash
python scripts/import_all_data.py --year 2020
```

---

## 5. Verify import

### PostGIS (settlements)

```bash
psql -U darinformal -d darinformal -c \
  "SELECT year, COUNT(*) FROM settlements GROUP BY year ORDER BY year;"
```

### API

```bash
curl http://localhost:8000/api/health
curl http://localhost:8000/api/risk/2020
curl http://localhost:8000/api/metrics/trend
```

### Raster manifest

After `--scan`, check:

```
backend/data/raster/raster_manifest.json
```

### GeoServer WMS (vector settlements)

```
http://localhost:8080/geoserver/darinformal/wms
  ?service=WMS&request=GetMap&layers=darinformal:settlements
  &CQL_FILTER=year=2020&styles=settlements_risk
  &bbox=39.05,-6.95,39.45,-6.65&width=800&height=600&srs=EPSG:4326&format=image/png
```

### GeoServer WMS (ISI raster per year)

```
http://localhost:8080/geoserver/darinformal/wms
  ?service=WMS&request=GetMap&layers=darinformal:isi_raster_2020
  &bbox=39.05,-6.95,39.45,-6.65&width=800&height=600&srs=EPSG:4326&format=image/png
```

---

## 6. Restart services

After import, restart the API:

```bash
# VS Code: Shift+F5 then F5
# Or terminal:
uvicorn main:app --reload --port 8000
```

Refresh the browser map — time slider should show all imported years.

---

## 7. GeoServer raster path (Docker vs local)

GeoServer must **read the .tif files from its own filesystem**.

### Local GeoServer (Windows)

Set env var to your actual path before publishing:

```powershell
$env:GEOSERVER_RASTER_PATH="C:\path\to\Dar-informal-settlements-webGIS\backend\data\raster\isi_2020.tif"
python scripts/publish_rasters_geoserver.py --publish --year 2020
```

### Docker Compose

Rasters are shared via volume mount (add to `docker-compose.yml` geoserver service):

```yaml
volumes:
  - ./backend/data/raster:/opt/raster:ro
```

Then set in `.env`:

```
GEOSERVER_RASTER_PATH=/opt/raster/isi_2020.tif
```

---

## 8. Troubleshooting

| Problem | Solution |
|---------|----------|
| Year not in API | Check filename is `settlements_YYYY.geojson` |
| `risk_level` error | Values must be `low`, `medium`, or `high` |
| CRS error | Reproject in QGIS to EPSG:4326 before import |
| Empty map after import | Restart API; check `/api/health` |
| Raster not in GeoServer | Run `--scan` first; check `raster_manifest.json` |
| GeoServer can't find .tif | Set `GEOSERVER_RASTER_PATH` to path visible inside GeoServer |

---

## 9. VS Code task

**Ctrl+Shift+P** → **Tasks: Run Task** → `DarInformal: Import data to PostGIS`

Or add to launch: run **Import GeoJSON → PostGIS** debug config before **Full Stack**.
