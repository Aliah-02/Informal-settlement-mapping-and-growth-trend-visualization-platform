#!/usr/bin/env python3
"""Import all GEE data: GeoJSON → PostGIS + GeoTIFF catalog/publish.

One command after placing your files:

    python scripts/import_all_data.py

Place files first:
    backend/data/geojson/settlements_2005.geojson  (etc.)
    backend/data/raster/isi_2005.tif               (etc.)
"""

from __future__ import annotations

import argparse
import logging
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import get_settings

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)
SCRIPTS_DIR = Path(__file__).resolve().parent


def run_script(script: str, *args: str) -> int:
    cmd = [sys.executable, str(SCRIPTS_DIR / script), *args]
    logger.info("Running: %s", " ".join(cmd))
    return subprocess.call(cmd)


def main():
    parser = argparse.ArgumentParser(description="Import GeoJSON + rasters into DarInformal")
    parser.add_argument("--skip-geojson", action="store_true")
    parser.add_argument("--skip-raster", action="store_true")
    parser.add_argument("--publish-raster", action="store_true", help="Publish rasters to GeoServer")
    parser.add_argument("--year", type=int, help="Import single year only")
    args = parser.parse_args()

    settings = get_settings()
    logger.info("GeoJSON dir: %s", settings.geojson_dir)
    logger.info("Raster dir:  %s", settings.raster_dir)

    # Ensure directories exist
    settings.geojson_dir.mkdir(parents=True, exist_ok=True)
    settings.raster_dir.mkdir(parents=True, exist_ok=True)

    if not args.skip_geojson:
        logger.info("=== Step 1: GeoJSON → PostGIS ===")
        if args.year:
            rc = run_script("import_geojson_to_postgis.py", "--year", str(args.year))
        else:
            rc = run_script("import_geojson_to_postgis.py", "--all")
        if rc != 0:
            sys.exit(rc)
        run_script("compute_yearly_metrics.py")

    if not args.skip_raster:
        logger.info("=== Step 2: GeoTIFF scan ===")
        raster_args = ["--scan"]
        if args.year:
            raster_args += ["--year", str(args.year)]
        if args.publish_raster:
            raster_args = ["--publish"] + (["--year", str(args.year)] if args.year else [])
        run_script("publish_rasters_geoserver.py", *raster_args)

    logger.info("=== Import complete ===")
    logger.info("Restart API, then verify: curl http://localhost:8000/api/health")


if __name__ == "__main__":
    main()
