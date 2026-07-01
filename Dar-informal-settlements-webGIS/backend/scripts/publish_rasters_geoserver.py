#!/usr/bin/env python3
"""Validate and catalog ISI GeoTIFF rasters; optionally publish to GeoServer.

Expected filenames (any of these patterns per year):
  isi_2005.tif
  darinformal_2005.tif
  indices_2005.tif
  settlements_2005.tif   (if raster named like geojson — still detected by year)

Usage:
    python scripts/publish_rasters_geoserver.py --scan
    python scripts/publish_rasters_geoserver.py --publish
    python scripts/publish_rasters_geoserver.py --publish --year 2020
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import rasterio
import requests
from requests.auth import HTTPBasicAuth

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


def publish_to_geoserver(year: int, tif_path: Path) -> bool:
    """Publish a single GeoTIFF as GeoServer coverage layer isi_raster_{year}."""
    gs_url = os.getenv("GEOSERVER_URL", "http://localhost:8080/geoserver")
    user = os.getenv("GEOSERVER_USER", "admin")
    password = os.getenv("GEOSERVER_PASSWORD", "geoserver")
    workspace = os.getenv("GEOSERVER_WORKSPACE", "darinformal")
    auth = HTTPBasicAuth(user, password)

    # GeoServer needs file:// URL accessible FROM the GeoServer container/host
    geoserver_data_path = os.getenv("GEOSERVER_RASTER_PATH", str(tif_path.resolve()))
    file_url = Path(geoserver_data_path).as_uri()

    store_name = f"isi_raster_{year}"
    layer_name = f"isi_raster_{year}"

    store_xml = f"""<coverageStore>
  <name>{store_name}</name>
  <type>GeoTIFF</type>
  <enabled>true</enabled>
  <workspace><name>{workspace}</name></workspace>
  <url>{file_url}</url>
</coverageStore>"""

    r = requests.post(
        f"{gs_url}/rest/workspaces/{workspace}/coveragestores",
        data=store_xml,
        auth=auth,
        headers={"Content-Type": "text/xml"},
    )
    if r.status_code not in (200, 201, 409):
        logger.error("Coverage store %s failed: %s %s", store_name, r.status_code, r.text)
        return False

    coverage_xml = f"""<coverage>
  <name>{layer_name}</name>
  <nativeName>{layer_name}</nativeName>
  <title>ISI Raster {year}</title>
  <enabled>true</enabled>
  <srs>EPSG:4326</srs>
</coverage>"""

    r2 = requests.post(
        f"{gs_url}/rest/workspaces/{workspace}/coveragestores/{store_name}/coverages",
        data=coverage_xml,
        auth=auth,
        headers={"Content-Type": "text/xml"},
    )
    if r2.status_code in (200, 201, 409):
        logger.info("  ✓ Published raster layer %s:%s", workspace, layer_name)
        return True
    logger.error("Coverage %s failed: %s %s", layer_name, r2.status_code, r2.text)
    return False


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
    parser = argparse.ArgumentParser(description="Catalog and publish ISI GeoTIFF rasters")
    parser.add_argument("--scan", action="store_true", help="Scan and validate rasters only")
    parser.add_argument("--publish", action="store_true", help="Publish rasters to GeoServer")
    parser.add_argument("--year", type=int, help="Process a single year")
    args = parser.parse_args()

    settings = get_settings()
    years = [args.year] if args.year else settings.analysis_years

    logger.info("Raster directory: %s", settings.raster_dir)
    catalog = scan_rasters(years)

    if args.scan or not args.publish:
        if not catalog:
            logger.info("No rasters found. Place .tif files in %s", settings.raster_dir)
        return

    if not catalog:
        sys.exit(1)

    logger.info("Publishing %d raster(s) to GeoServer...", len(catalog))
    ok = sum(publish_to_geoserver(year, Path(meta["path"])) for year, meta in catalog.items())
    logger.info("Published %d / %d raster layers", ok, len(catalog))


if __name__ == "__main__":
    main()
