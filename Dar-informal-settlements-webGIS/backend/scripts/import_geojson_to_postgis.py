#!/usr/bin/env python3
"""Import GEE-exported GeoJSON settlement files into PostGIS.

Usage:
    python scripts/import_geojson_to_postgis.py --all
    python scripts/import_geojson_to_postgis.py --year 2020
    python scripts/import_geojson_to_postgis.py --file data/geojson/settlements_2020.geojson
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

# Allow running from backend/ directory
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import geopandas as gpd
from shapely.geometry import MultiPolygon, Polygon
from sqlalchemy import text

from config import get_settings
from db.database import get_engine, session_scope
from services.isi_model import classify_risk, compute_isi, estimate_population_proxy

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def to_multipolygon(geom):
    """Convert Polygon to MultiPolygon for PostGIS schema compliance."""
    if geom is None:
        return None
    if geom.geom_type == "Polygon":
        return MultiPolygon([geom])
    if geom.geom_type == "MultiPolygon":
        return geom
    return geom


def enrich_gdf(gdf: gpd.GeoDataFrame, year: int) -> gpd.GeoDataFrame:
    """Ensure all required columns exist with valid values."""
    settings = get_settings()
    gdf = gdf.copy()

    for col in ["ndbi", "ndvi", "bsi", "fragmentation_index"]:
        if col not in gdf.columns:
            gdf[col] = 0.3

    if "isi_score" not in gdf.columns:
        gdf["isi_score"] = gdf.apply(
            lambda r: compute_isi(r["ndbi"], r["ndvi"], r["bsi"], r["fragmentation_index"], settings),
            axis=1,
        )
    if "risk_level" not in gdf.columns:
        gdf["risk_level"] = gdf["isi_score"].apply(lambda s: classify_risk(s, settings))

    if "area_ha" not in gdf.columns:
        gdf_proj = gdf.to_crs(epsg=32737)
        gdf["area_ha"] = gdf_proj.geometry.area / 10_000.0

    if "population_proxy" not in gdf.columns:
        gdf["population_proxy"] = gdf.apply(
            lambda r: estimate_population_proxy(r["area_ha"], r["isi_score"]), axis=1
        )

    gdf["year"] = year
    if "id" not in gdf.columns:
        gdf["id"] = [f"DAR-{year}-{i + 1:04d}" for i in range(len(gdf))]
    if "name" not in gdf.columns:
        gdf["name"] = [f"Settlement {i + 1}" for i in range(len(gdf))]

    gdf["geometry"] = gdf.geometry.apply(to_multipolygon)
    gdf["settlement_id"] = gdf["id"].astype(str)
    gdf["data_source"] = "geojson_import"
    return gdf


def import_year(year: int, filepath: Path | None = None) -> int:
    """Import a single year's GeoJSON into PostGIS. Returns feature count."""
    settings = get_settings()
    path = filepath or settings.geojson_dir / f"settlements_{year}.geojson"

    if not path.exists():
        logger.error("File not found: %s", path)
        return 0

    logger.info("Importing %s → PostGIS (year %d)", path.name, year)
    gdf = gpd.read_file(path)
    if gdf.crs is None:
        gdf.set_crs(epsg=4326, inplace=True)
    elif gdf.crs.to_epsg() != 4326:
        gdf = gdf.to_crs(epsg=4326)

    gdf = enrich_gdf(gdf, year)
    engine = get_engine(settings)

    # Replace existing data for this year
    with session_scope(settings) as session:
        session.execute(text("DELETE FROM settlements WHERE year = :year"), {"year": year})

    export_cols = [
        "settlement_id", "name", "year", "isi_score", "risk_level",
        "area_ha", "population_proxy", "ndbi", "ndvi", "bsi",
        "fragmentation_index", "data_source", "geometry",
    ]
    gdf[export_cols].to_postgis("settlements", engine, if_exists="append", index=False)

    count = len(gdf)
    with session_scope(settings) as session:
        session.execute(
            text("""
                INSERT INTO import_log (year, source_file, features_imported, status)
                VALUES (:year, :file, :count, 'success')
            """),
            {"year": year, "file": str(path), "count": count},
        )

    logger.info("  ✓ Imported %d features for year %d", count, year)
    return count


def import_all() -> int:
    """Import all available GeoJSON files for configured analysis years."""
    settings = get_settings()
    total = 0
    for year in settings.analysis_years:
        path = settings.geojson_dir / f"settlements_{year}.geojson"
        if path.exists():
            total += import_year(year, path)
        else:
            logger.warning("Skipping year %d — no file at %s", year, path)
    return total


def main():
    parser = argparse.ArgumentParser(description="Import GeoJSON settlements into PostGIS")
    parser.add_argument("--all", action="store_true", help="Import all available years")
    parser.add_argument("--year", type=int, help="Import a specific year")
    parser.add_argument("--file", type=Path, help="Import a specific GeoJSON file")
    args = parser.parse_args()

    if args.all:
        count = import_all()
        logger.info("Total features imported: %d", count)
    elif args.year:
        import_year(args.year, args.file)
    elif args.file:
        # Infer year from filename
        year = int(args.file.stem.split("_")[-1])
        import_year(year, args.file)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
