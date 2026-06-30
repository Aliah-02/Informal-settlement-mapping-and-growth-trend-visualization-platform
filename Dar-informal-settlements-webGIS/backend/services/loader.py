"""Data loading utilities for GeoJSON settlement layers."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Optional

import geopandas as gpd
from shapely.geometry import mapping, shape

from config import Settings, get_settings
from services.isi_model import classify_risk, compute_isi, estimate_population_proxy

logger = logging.getLogger(__name__)

# In-memory cache for loaded GeoDataFrames keyed by year
_gdf_cache: dict[int, gpd.GeoDataFrame] = {}


def _geojson_path(year: int, settings: Settings) -> Path:
    """Resolve GeoJSON file path for a given year."""
    return settings.geojson_dir / f"settlements_{year}.geojson"


def available_years(settings: Settings | None = None) -> list[int]:
    """Return list of years with available GeoJSON data."""
    cfg = settings or get_settings()
    years = []
    for year in cfg.analysis_years:
        if _geojson_path(year, cfg).exists():
            years.append(year)
    return sorted(years)


def clear_cache() -> None:
    """Clear in-memory GeoDataFrame cache."""
    _gdf_cache.clear()


def load_year(
    year: int,
    settings: Settings | None = None,
    use_cache: bool = True,
) -> gpd.GeoDataFrame:
    """Load settlement GeoDataFrame for a given year."""
    cfg = settings or get_settings()

    if use_cache and year in _gdf_cache:
        return _gdf_cache[year]

    path = _geojson_path(year, cfg)
    if not path.exists():
        raise FileNotFoundError(f"No settlement data found for year {year} at {path}")

    gdf = gpd.read_file(path)

    # Ensure CRS is WGS84
    if gdf.crs is None:
        gdf.set_crs(epsg=4326, inplace=True)
    elif gdf.crs.to_epsg() != 4326:
        gdf = gdf.to_crs(epsg=4326)

    # Recompute ISI if missing or incomplete
    gdf = _enrich_features(gdf, year, cfg)

    if use_cache:
        _gdf_cache[year] = gdf

    logger.info("Loaded %d settlements for year %d", len(gdf), year)
    return gdf


def _enrich_features(gdf: gpd.GeoDataFrame, year: int, settings: Settings) -> gpd.GeoDataFrame:
    """Ensure all required attributes exist on features."""
    required = ["ndbi", "ndvi", "bsi", "fragmentation_index"]
    for col in required:
        if col not in gdf.columns:
            gdf[col] = 0.3  # sensible default

    if "isi_score" not in gdf.columns:
        gdf["isi_score"] = gdf.apply(
            lambda row: compute_isi(
                row["ndbi"], row["ndvi"], row["bsi"], row["fragmentation_index"], settings
            ),
            axis=1,
        )

    if "risk_level" not in gdf.columns:
        gdf["risk_level"] = gdf["isi_score"].apply(lambda s: classify_risk(s, settings))

    if "area_ha" not in gdf.columns:
        # Project to UTM 37S for accurate area in Tanzania
        gdf_proj = gdf.to_crs(epsg=32737)
        gdf["area_ha"] = gdf_proj.geometry.area / 10_000.0

    if "population_proxy" not in gdf.columns:
        gdf["population_proxy"] = gdf.apply(
            lambda row: estimate_population_proxy(row["area_ha"], row["isi_score"]),
            axis=1,
        )

    if "year" not in gdf.columns:
        gdf["year"] = year

    if "name" not in gdf.columns:
        gdf["name"] = [f"Settlement {i + 1}" for i in range(len(gdf))]

    if "id" not in gdf.columns:
        gdf["id"] = [f"DAR-{year}-{i + 1:04d}" for i in range(len(gdf))]

    return gdf


def to_feature_collection(gdf: gpd.GeoDataFrame) -> dict[str, Any]:
    """Convert GeoDataFrame to GeoJSON FeatureCollection dict."""
    features = []
    for _, row in gdf.iterrows():
        geom = mapping(row.geometry)
        props = {
            k: (float(v) if hasattr(v, "item") else v)
            for k, v in row.items()
            if k != "geometry"
        }
        # Ensure JSON-serializable types
        for key, val in props.items():
            if hasattr(val, "item"):
                props[key] = val.item()
            elif isinstance(val, (int, float, str, bool)) or val is None:
                pass
            else:
                props[key] = str(val)
        features.append({"type": "Feature", "geometry": geom, "properties": props})
    return {"type": "FeatureCollection", "features": features}


def filter_settlements(
    year: Optional[int] = None,
    risk_level: Optional[str] = None,
    min_isi: Optional[float] = None,
    max_isi: Optional[float] = None,
    limit: int = 500,
    offset: int = 0,
    settings: Settings | None = None,
) -> tuple[list[dict[str, Any]], int]:
    """Query settlements with optional filters. Returns (features, total_count)."""
    cfg = settings or get_settings()
    target_year = year or (available_years(cfg)[-1] if available_years(cfg) else 2026)

    gdf = load_year(target_year, cfg)
    filtered = gdf.copy()

    if risk_level:
        filtered = filtered[filtered["risk_level"] == risk_level]
    if min_isi is not None:
        filtered = filtered[filtered["isi_score"] >= min_isi]
    if max_isi is not None:
        filtered = filtered[filtered["isi_score"] <= max_isi]

    total = len(filtered)
    page = filtered.iloc[offset : offset + limit]

    features = []
    for _, row in page.iterrows():
        features.append(
            {
                "id": row["id"],
                "name": row["name"],
                "year": int(row["year"]),
                "isi_score": float(row["isi_score"]),
                "risk_level": row["risk_level"],
                "area_ha": float(row["area_ha"]),
                "population_proxy": int(row["population_proxy"]),
                "ndbi": float(row["ndbi"]),
                "ndvi": float(row["ndvi"]),
                "bsi": float(row["bsi"]),
                "fragmentation_index": float(row["fragmentation_index"]),
                "geometry": mapping(row.geometry),
            }
        )
    return features, total
