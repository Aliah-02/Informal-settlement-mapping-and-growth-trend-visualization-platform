#!/usr/bin/env python3
"""Validate and catalog ISI GeoTIFF rasters from backend/data/raster/.

Usage:
    python scripts/catalog_rasters.py
    python scripts/catalog_rasters.py --year 2020
"""

from __future__ import annotations

import argparse
import json
import logging
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import rasterio

from config import get_settings

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

YEAR_PATTERN = re.compile(r"(20\d{2})")
RASTER_NAMES = ["isi_{year}.tif", "darinformal_{year}.tif", "indices_{year}.tif", "raster_{year}.tif"]


def discover_rasters(raster_dir: Path, years: list[int]) -> dict[int, Path]:
    """Find raster file for each year in directory."""
    found: dict[int, Path] = {}
    if not raster_dir.exists():
        raster_dir.mkdir(parents=True, exist_ok=True)
        return found

    all_tifs = list(raster_dir.glob("*.tif")) + list(raster_dir.glob("*.tiff"))

    for year in years:
        for pattern in RASTER_NAMES:
            candidate = raster_dir / pattern.format(year=year)
            if candidate.exists():
                found[year] = candidate
                break
        if year not in found:
            for tif in all_tifs:
                match = YEAR_PATTERN.search(tif.stem)
                if match and int(match.group(1)) == year:
                    found[year] = tif
                    break
    return found


def validate_raster(path: Path) -> dict:
    """Return raster metadata for logging/manifest."""
    with rasterio.open(path) as src:
        return {
            "path": str(path),
            "crs": str(src.crs) if src.crs else None,
            "bands": src.count,
            "width": src.width,
            "height": src.height,
            "bounds": list(src.bounds),
            "dtype": str(src.dtypes[0]),
        }


def write_manifest(raster_dir: Path, catalog: dict[int, dict]) -> Path:
    manifest_path = raster_dir / "raster_manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(catalog, f, indent=2)
    return manifest_path


def scan_rasters(years: list[int] | None = None) -> dict[int, dict]:
    settings = get_settings()
    years = years or settings.analysis_years
    raster_dir = settings.raster_dir
    discovered = discover_rasters(raster_dir, years)

    catalog: dict[int, dict] = {}
    for year, path in sorted(discovered.items()):
        try:
            meta = validate_raster(path)
            meta["year"] = year
            catalog[year] = meta
            logger.info(
                "Year %d: %s (%d bands, %s, %dx%d)",
                year, path.name, meta["bands"], meta["crs"], meta["width"], meta["height"],
            )
        except Exception as exc:
            logger.error("Year %d: invalid raster %s — %s", year, path, exc)

    missing = [y for y in years if y not in catalog]
    if missing:
        logger.warning("Missing raster files for years: %s", missing)

    write_manifest(raster_dir, catalog)
    return catalog


def main():
    parser = argparse.ArgumentParser(description="Catalog ISI GeoTIFF rasters")
    parser.add_argument("--year", type=int, help="Process a single year")
    args = parser.parse_args()

    settings = get_settings()
    years = [args.year] if args.year else settings.analysis_years

    logger.info("Raster directory: %s", settings.raster_dir)
    catalog = scan_rasters(years)
    if not catalog:
        logger.info("No rasters found. Place .tif files in %s", settings.raster_dir)


if __name__ == "__main__":
    main()
