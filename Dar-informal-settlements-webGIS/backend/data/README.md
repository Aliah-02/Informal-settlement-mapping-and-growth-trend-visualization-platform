# Sample Data Generation Guide

This directory contains synthetic informal settlement GeoJSON for Dar es Salaam,
covering analysis years **2005, 2010, 2015, 2020, and 2026**.

## Quick Start (Local Sample Data)

```bash
cd backend/data
python3 generate_sample_data.py
```

Output files are written to `backend/data/geojson/`:

| File | Description |
|------|-------------|
| `settlements_2005.geojson` | Baseline informal settlements (~55% of 2020 extent) |
| `settlements_2010.geojson` | Early growth phase |
| `settlements_2015.geojson` | Accelerated peri-urban expansion |
| `settlements_2020.geojson` | Current-state reference layer |
| `settlements_2026.geojson` | Projected / latest analysis (+18% growth) |

## Data Schema

Each feature includes:

```json
{
  "id": "DAR-2020-0001",
  "name": "Tandale",
  "year": 2020,
  "isi_score": 0.4521,
  "risk_level": "medium",
  "area_ha": 12.34,
  "population_proxy": 42150,
  "ndbi": 0.2845,
  "ndvi": 0.1823,
  "bsi": 0.3512,
  "fragmentation_index": 0.4123
}
```

## Production Data via Google Earth Engine

For production-quality data, use the GEE scripts in `/gee/`:

1. **`01_aoi_definition.js`** — Define Dar es Salaam AOI boundary
2. **`02_dynamic_world_labels.js`** — Extract weak labels from Dynamic World
3. **`03_spectral_indices.js`** — Compute NDVI, NDBI, BSI per year
4. **`04_isi_computation.js`** — Apply ISI formula and classify risk
5. **`05_yearly_export.js`** — Export GeoJSON + GeoTIFF to Google Drive / GCS

### Export Workflow

```text
GEE Code Editor → Run script → Export to Drive
  → Download GeoJSON → Place in backend/data/geojson/
  → Restart API (data auto-loaded on request)
```

### Supported Sensors

| Period | Primary Sensor | Fallback |
|--------|---------------|----------|
| 2005–2011 | Landsat 5/7 | Landsat 7 |
| 2012–2020 | Sentinel-2 + Landsat 8 | Landsat 8 |
| 2021–2026 | Sentinel-2 + Landsat 9 | Landsat 8/9 |

## Updating the ISI Model

Edit weights in `backend/config.py` or `backend/services/isi_model.py`:

```python
isi_weight_ndbi: float = 0.3
isi_weight_ndvi_inv: float = 0.25
isi_weight_bsi: float = 0.2
isi_weight_fragmentation: float = 0.25
```

After changing weights, regenerate data or re-run the API (ISI is recomputed
on load if missing from GeoJSON properties).

## Coordinate Reference System

All GeoJSON files use **EPSG:4326 (WGS84)**. Area calculations in the backend
are projected to **EPSG:32737 (UTM Zone 37S)** for accuracy.
