"""PostGIS repository — CRUD and spatial queries for settlements."""

from __future__ import annotations

import logging
from typing import Any, Optional

import geopandas as gpd
import pandas as pd
from shapely.geometry import mapping
from sqlalchemy import text

from config import Settings, get_settings
from db.database import get_engine, session_scope

logger = logging.getLogger(__name__)

SETTLEMENT_COLUMNS = """
    settlement_id AS id, name, year, isi_score, risk_level,
    area_ha, population_proxy, ndbi, ndvi, bsi, fragmentation_index, geom
"""


def is_populated(settings: Settings | None = None) -> bool:
    """Return True if settlements table has at least one row."""
    cfg = settings or get_settings()
    try:
        engine = get_engine(cfg)
        with engine.connect() as conn:
            count = conn.execute(text("SELECT COUNT(*) FROM settlements")).scalar()
        return bool(count and count > 0)
    except Exception as exc:
        logger.debug("PostGIS not populated: %s", exc)
        return False


def get_available_years(settings: Settings | None = None) -> list[int]:
    """Return distinct years present in PostGIS."""
    cfg = settings or get_settings()
    engine = get_engine(cfg)
    with engine.connect() as conn:
        rows = conn.execute(
            text("SELECT DISTINCT year FROM settlements ORDER BY year")
        ).fetchall()
    return [row[0] for row in rows]


def load_year_gdf(year: int, settings: Settings | None = None) -> gpd.GeoDataFrame:
    """Load settlements for a year from PostGIS as GeoDataFrame."""
    cfg = settings or get_settings()
    engine = get_engine(cfg)
    sql = f"SELECT {SETTLEMENT_COLUMNS} FROM settlements WHERE year = %(year)s"
    gdf = gpd.read_postgis(sql, engine, params={"year": year}, geom_col="geom", crs="EPSG:4326")
    if gdf.empty:
        raise FileNotFoundError(f"No settlements in PostGIS for year {year}")
    logger.info("Loaded %d settlements from PostGIS for year %d", len(gdf), year)
    return gdf


def filter_settlements_db(
    year: Optional[int] = None,
    risk_level: Optional[str] = None,
    min_isi: Optional[float] = None,
    max_isi: Optional[float] = None,
    limit: int = 500,
    offset: int = 0,
    settings: Settings | None = None,
) -> tuple[list[dict[str, Any]], int]:
    """Query settlements from PostGIS with filters and pagination."""
    cfg = settings or get_settings()
    engine = get_engine(cfg)

    conditions = ["1=1"]
    params: dict[str, Any] = {"limit": limit, "offset": offset}

    if year is not None:
        conditions.append("year = :year")
        params["year"] = year
    if risk_level:
        conditions.append("risk_level = :risk_level")
        params["risk_level"] = risk_level
    if min_isi is not None:
        conditions.append("isi_score >= :min_isi")
        params["min_isi"] = min_isi
    if max_isi is not None:
        conditions.append("isi_score <= :max_isi")
        params["max_isi"] = max_isi

    where = " AND ".join(conditions)
    count_sql = f"SELECT COUNT(*) FROM settlements WHERE {where}"
    data_sql = f"""
        SELECT {SETTLEMENT_COLUMNS}
        FROM settlements WHERE {where}
        ORDER BY settlement_id
        LIMIT :limit OFFSET :offset
    """

    with engine.connect() as conn:
        total = conn.execute(text(count_sql), params).scalar() or 0
    gdf = gpd.read_postgis(data_sql, engine, params=params, geom_col="geom", crs="EPSG:4326")

    features = []
    for _, row in gdf.iterrows():
        features.append(_row_to_feature(row))
    return features, int(total)


def _row_to_feature(row: pd.Series) -> dict[str, Any]:
    return {
        "id": row["id"],
        "name": row["name"],
        "year": int(row["year"]),
        "isi_score": float(row["isi_score"]),
        "risk_level": row["risk_level"],
        "area_ha": float(row["area_ha"]),
        "population_proxy": int(row["population_proxy"]),
        "ndbi": float(row["ndbi"] or 0),
        "ndvi": float(row["ndvi"] or 0),
        "bsi": float(row["bsi"] or 0),
        "fragmentation_index": float(row["fragmentation_index"] or 0),
        "geometry": mapping(row.geom),
    }


def get_yearly_metrics_from_db(year: int, settings: Settings | None = None) -> Optional[dict]:
    """Fetch pre-computed yearly metrics from PostGIS."""
    cfg = settings or get_settings()
    engine = get_engine(cfg)
    with engine.connect() as conn:
        row = conn.execute(
            text("SELECT * FROM yearly_metrics WHERE year = :year"), {"year": year}
        ).mappings().first()
    return dict(row) if row else None


def get_all_yearly_metrics(settings: Settings | None = None) -> list[dict]:
    """Fetch all pre-computed yearly metrics ordered by year."""
    cfg = settings or get_settings()
    engine = get_engine(cfg)
    with engine.connect() as conn:
        rows = conn.execute(
            text("SELECT * FROM yearly_metrics ORDER BY year")
        ).mappings().all()
    return [dict(r) for r in rows]


def upsert_yearly_metrics(metrics: dict, settings: Settings | None = None) -> None:
    """Insert or update yearly metrics row."""
    cfg = settings or get_settings()
    with session_scope(cfg) as session:
        session.execute(
            text("""
                INSERT INTO yearly_metrics (
                    year, total_settlements, total_area_ha, average_isi,
                    high_risk_area_ha, medium_risk_area_ha, low_risk_area_ha,
                    high_risk_count, medium_risk_count, low_risk_count,
                    population_proxy_total, computed_at
                ) VALUES (
                    :year, :total_settlements, :total_area_ha, :average_isi,
                    :high_risk_area_ha, :medium_risk_area_ha, :low_risk_area_ha,
                    :high_risk_count, :medium_risk_count, :low_risk_count,
                    :population_proxy_total, NOW()
                )
                ON CONFLICT (year) DO UPDATE SET
                    total_settlements = EXCLUDED.total_settlements,
                    total_area_ha = EXCLUDED.total_area_ha,
                    average_isi = EXCLUDED.average_isi,
                    high_risk_area_ha = EXCLUDED.high_risk_area_ha,
                    medium_risk_area_ha = EXCLUDED.medium_risk_area_ha,
                    low_risk_area_ha = EXCLUDED.low_risk_area_ha,
                    high_risk_count = EXCLUDED.high_risk_count,
                    medium_risk_count = EXCLUDED.medium_risk_count,
                    low_risk_count = EXCLUDED.low_risk_count,
                    population_proxy_total = EXCLUDED.population_proxy_total,
                    computed_at = NOW()
            """),
            metrics,
        )


def clear_change_detection(from_year: int, to_year: int, settings: Settings | None = None) -> None:
    """Remove cached change detection records for a year pair."""
    cfg = settings or get_settings()
    with session_scope(cfg) as session:
        session.execute(
            text("DELETE FROM change_detection WHERE from_year = :fy AND to_year = :ty"),
            {"fy": from_year, "ty": to_year},
        )


def save_change_detection_records(
    from_year: int,
    to_year: int,
    records: list[dict],
    settings: Settings | None = None,
) -> int:
    """Persist change detection results to PostGIS."""
    cfg = settings or get_settings()
    clear_change_detection(from_year, to_year, cfg)
    inserted = 0
    with session_scope(cfg) as session:
        for rec in records:
            session.execute(
                text("""
                    INSERT INTO change_detection (
                        from_year, to_year, settlement_id, to_settlement_id, name,
                        change_type, isi_score, to_isi_score, area_ha, to_area_ha,
                        area_change_ha, area_change_pct, isi_change, overlap_ratio,
                        population_proxy, geom
                    ) VALUES (
                        :from_year, :to_year, :settlement_id, :to_settlement_id, :name,
                        :change_type, :isi_score, :to_isi_score, :area_ha, :to_area_ha,
                        :area_change_ha, :area_change_pct, :isi_change, :overlap_ratio,
                        :population_proxy, ST_SetSRID(ST_GeomFromGeoJSON(:geom_json), 4326)
                    )
                    ON CONFLICT (from_year, to_year, settlement_id, change_type) DO NOTHING
                """),
                rec,
            )
            inserted += 1
    return inserted
