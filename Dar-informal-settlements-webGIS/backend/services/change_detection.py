"""Change detection between two analysis years."""

from __future__ import annotations

import logging
from typing import Any

import geopandas as gpd
from shapely.geometry import mapping
from shapely.ops import unary_union

from config import Settings, get_settings
from services.data_source import load_year

logger = logging.getLogger(__name__)

# Minimum overlap ratio to consider settlements as the same entity
OVERLAP_THRESHOLD = 0.3
# Area change ratio threshold for expansion/contraction
AREA_CHANGE_THRESHOLD = 0.15


def detect_changes(
    from_year: int,
    to_year: int,
    settings: Settings | None = None,
) -> dict[str, Any]:
    """Detect settlement changes between two years.

    Classifies settlements as new, expanded, contracted, or stable based on
    spatial overlap and area change analysis.
    """
    cfg = settings or get_settings()
    gdf_from = load_year(from_year, cfg)
    gdf_to = load_year(to_year, cfg)

    # Project to UTM for accurate spatial operations
    gdf_from_utm = gdf_from.to_crs(epsg=32737)
    gdf_to_utm = gdf_to.to_crs(epsg=32737)

    matched_to: set[int] = set()
    new_settlements: list[dict] = []
    expanded: list[dict] = []
    contracted: list[dict] = []
    stable: list[dict] = []

    for idx_from, row_from in gdf_from_utm.iterrows():
        geom_from = row_from.geometry
        area_from = geom_from.area

        best_match_idx = None
        best_overlap = 0.0

        for idx_to, row_to in gdf_to_utm.iterrows():
            if idx_to in matched_to:
                continue
            intersection = geom_from.intersection(row_to.geometry)
            if intersection.is_empty:
                continue
            overlap = intersection.area / min(area_from, row_to.geometry.area)
            if overlap > best_overlap:
                best_overlap = overlap
                best_match_idx = idx_to

        props_from = _feature_summary(gdf_from.loc[idx_from], from_year)

        if best_match_idx is None or best_overlap < OVERLAP_THRESHOLD:
            # No match — settlement disappeared (not tracked as new in from_year)
            continue

        matched_to.add(best_match_idx)
        row_to_orig = gdf_to.loc[best_match_idx]
        props_to = _feature_summary(row_to_orig, to_year)

        area_to = gdf_to_utm.loc[best_match_idx].geometry.area
        area_change_ratio = (area_to - area_from) / area_from if area_from > 0 else 0

        change_record = {
            "from": props_from,
            "to": props_to,
            "area_change_ha": round((area_to - area_from) / 10_000.0, 2),
            "area_change_pct": round(area_change_ratio * 100, 1),
            "isi_change": round(props_to["isi_score"] - props_from["isi_score"], 4),
            "overlap_ratio": round(best_overlap, 3),
        }

        if area_change_ratio > AREA_CHANGE_THRESHOLD:
            expanded.append(change_record)
        elif area_change_ratio < -AREA_CHANGE_THRESHOLD:
            contracted.append(change_record)
        else:
            stable.append(change_record)

    # Identify new settlements in to_year not matched from from_year
    for idx_to, row_to in gdf_to_utm.iterrows():
        if idx_to in matched_to:
            continue
        props = _feature_summary(gdf_to.loc[idx_to], to_year)
        new_settlements.append(props)

    area_from_total = gdf_from["area_ha"].sum()
    area_to_total = gdf_to["area_ha"].sum()
    isi_from_avg = gdf_from["isi_score"].mean()
    isi_to_avg = gdf_to["isi_score"].mean()

    return {
        "from_year": from_year,
        "to_year": to_year,
        "new_settlements": new_settlements,
        "expanded_settlements": expanded,
        "contracted_settlements": contracted,
        "stable_settlements": stable,
        "area_change_ha": round(area_to_total - area_from_total, 2),
        "isi_change_avg": round(isi_to_avg - isi_from_avg, 4),
        "summary": {
            "new_count": len(new_settlements),
            "expanded_count": len(expanded),
            "contracted_count": len(contracted),
            "stable_count": len(stable),
            "total_from": len(gdf_from),
            "total_to": len(gdf_to),
            "area_from_ha": round(area_from_total, 2),
            "area_to_ha": round(area_to_total, 2),
            "area_change_pct": round(
                ((area_to_total - area_from_total) / area_from_total * 100)
                if area_from_total > 0
                else 0,
                1,
            ),
            "isi_from_avg": round(isi_from_avg, 4),
            "isi_to_avg": round(isi_to_avg, 4),
        },
    }


def _feature_summary(row: gpd.GeoSeries, year: int) -> dict[str, Any]:
    """Extract summary properties from a settlement row."""
    return {
        "id": row["id"],
        "name": row["name"],
        "year": year,
        "isi_score": float(row["isi_score"]),
        "risk_level": row["risk_level"],
        "area_ha": float(row["area_ha"]),
        "population_proxy": int(row["population_proxy"]),
        "geometry": mapping(row.geometry),
    }
