"""Unified data source — PostGIS primary, GeoJSON fallback."""

from __future__ import annotations

import logging
from typing import Any, Optional

import geopandas as gpd

from config import Settings, get_settings
from db import repository as db_repo
from services import loader as geojson_loader

logger = logging.getLogger(__name__)


def use_postgis(settings: Settings | None = None) -> bool:
    """Return True when PostGIS has settlement data."""
    cfg = settings or get_settings()
    if not cfg.use_postgis:
        return False
    return db_repo.is_populated(cfg)


def available_years(settings: Settings | None = None) -> list[int]:
    """Years available from PostGIS or GeoJSON files."""
    cfg = settings or get_settings()
    if use_postgis(cfg):
        years = db_repo.get_available_years(cfg)
        if years:
            return years
    return geojson_loader.available_years(cfg)


def load_year(
    year: int,
    settings: Settings | None = None,
    use_cache: bool = True,
) -> gpd.GeoDataFrame:
    """Load settlement GeoDataFrame from PostGIS or GeoJSON."""
    cfg = settings or get_settings()
    if use_postgis(cfg):
        try:
            return db_repo.load_year_gdf(year, cfg)
        except FileNotFoundError:
            logger.warning("Year %d not in PostGIS, trying GeoJSON", year)
    return geojson_loader.load_year(year, cfg, use_cache)


def filter_settlements(
    year: Optional[int] = None,
    risk_level: Optional[str] = None,
    min_isi: Optional[float] = None,
    max_isi: Optional[float] = None,
    limit: int = 500,
    offset: int = 0,
    settings: Settings | None = None,
) -> tuple[list[dict[str, Any]], int]:
    """Filter settlements via PostGIS or in-memory GeoJSON."""
    cfg = settings or get_settings()
    if use_postgis(cfg):
        target_year = year
        if target_year is None:
            years = available_years(cfg)
            target_year = years[-1] if years else None
        if target_year is not None:
            return db_repo.filter_settlements_db(
                year=target_year,
                risk_level=risk_level,
                min_isi=min_isi,
                max_isi=max_isi,
                limit=limit,
                offset=offset,
                settings=cfg,
            )
    return geojson_loader.filter_settlements(
        year=year,
        risk_level=risk_level,
        min_isi=min_isi,
        max_isi=max_isi,
        limit=limit,
        offset=offset,
        settings=cfg,
    )


def data_source_label(settings: Settings | None = None) -> str:
    """Human-readable label for active data backend."""
    return "postgis" if use_postgis(settings) else "geojson"
