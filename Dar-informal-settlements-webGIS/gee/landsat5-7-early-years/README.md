# Landsat 5 + Landsat 7 — Early Years (2005 & 2010)

Dedicated Google Earth Engine scripts for collecting and exporting Dar es Salaam informal settlement data for **2005** and **2010**, using **Landsat 5 (LT05)** and **Landsat 7 (LE07)** only.

> Landsat 8 does not exist for these years. Do **not** use the main `gee/05_yearly_export.js` logic with `LC08` for 2005/2010.

---

## Why a separate folder?

| Issue | Solution in this folder |
|-------|-------------------------|
| Empty `SR_B.*` bands | L5 + L7 collections only |
| SLC-off stripes (L7, post-2003) | Multi-scene median + cloud mask |
| Sparse dry-season coverage | Extended window May–October, cloud ≤ 40% |

---

## Scripts (run in order)

| # | Script | Purpose |
|---|--------|---------|
| 1 | `01_collect_l5_l7_scenes.js` | Inspect scene counts, preview composites |
| 2 | `02_composite_spectral_indices.js` | Dry-season median composite → NDVI, NDBI, BSI GeoTIFF |
| 3 | `03_isi_raster_export.js` | Compute ISI + risk raster, export GeoTIFF |
| 4 | `04_export_settlements_geojson.js` | Vectorize settlements, export GeoJSON for API |

**Shortcut:** Run only `04_export_settlements_geojson.js` for the full pipeline (collection → indices → ISI → GeoJSON + raster).

---

## GEE Code Editor setup

1. Open https://code.earthengine.google.com/
2. Create a new script folder: `DarInformal/landsat5-7-early-years/`
3. Paste each `.js` file as a separate script
4. Run script 1 first to verify scene counts in the **Console**
5. Submit exports from the **Tasks** tab

---

## Expected scene counts (approximate)

Dar es Salaam AOI, May–October, cloud ≤ 40%:

| Year | Landsat 7 | Landsat 5 | Merged |
|------|-----------|-----------|--------|
| 2005 | ~15–25 | ~10–20 | ~25–40 |
| 2010 | ~15–25 | ~5–15  | ~20–35 |

If counts are **0**, widen the date range in the script or increase `MAX_CLOUD_COVER`.

---

## After export

1. Download from Google Drive folder: `DarInformal_L5L7_EarlyYears`
2. Rename GeoJSON files:
   - `settlements_2005.geojson`
   - `settlements_2010.geojson`
3. Copy to `backend/data/geojson/`
4. Restart API or reload — years 2005 and 2010 will appear in `/api/health`

---

## Sensor harmonization

Landsat 5 TM and Landsat 7 ETM+ Surface Reflectance (Collection 2 Level 2) share band naming:

| Band | Use |
|------|-----|
| SR_B2 | Blue |
| SR_B4 | Red |
| SR_B5 | NIR |
| SR_B6 | SWIR1 |

Indices match the DarInformal backend ISI formula.

---

## Notes on Landsat 7 SLC-off

Since May 2003, Landsat 7 has scan-line gaps. This pipeline mitigates gaps by:

- Merging **many scenes** from L7 + L5
- Using **median** compositing
- Applying **QA_PIXEL** cloud/shadow masks

For production-quality gap-filled products, consider USGS `LANDSAT/LT05/C02/T1_L2` priority in gap areas or external gap-fill tools.
