"""Location-based analytics — districts and wards from settlement coordinates."""

from __future__ import annotations

import csv
import io
from datetime import datetime, timezone
from typing import Any

from config import Settings, get_settings
from services.data_source import available_years, load_year

# Dar es Salaam district bounding boxes (approximate, WGS84)
DISTRICT_BOUNDS: dict[str, dict[str, float]] = {
    "Kinondoni": {"west": 39.12, "east": 39.35, "south": -6.82, "north": -6.70},
    "Ubungo": {"west": 39.05, "east": 39.20, "south": -6.82, "north": -6.72},
    "Ilala": {"west": 39.20, "east": 39.42, "south": -6.88, "north": -6.78},
    "Temeke": {"west": 39.05, "east": 39.42, "south": -6.95, "north": -6.86},
}

DISTRICT_COLORS = {
    "Kinondoni": "#eab308",
    "Ubungo": "#8b5cf6",
    "Ilala": "#22c55e",
    "Temeke": "#3b82f6",
}


def assign_district(lng: float, lat: float) -> str:
    """Assign a settlement centroid to a Dar es Salaam district."""
    for name, b in DISTRICT_BOUNDS.items():
        if b["west"] <= lng <= b["east"] and b["south"] <= lat <= b["north"]:
            return name
    # Fallback by latitude band
    if lat > -6.78:
        return "Kinondoni"
    if lat > -6.86:
        return "Ilala"
    return "Temeke"


def _centroid(geom: dict) -> tuple[float, float]:
    coords = geom.get("coordinates", [])
    if geom.get("type") == "Polygon" and coords:
        ring = coords[0]
    elif geom.get("type") == "MultiPolygon" and coords:
        ring = coords[0][0]
    else:
        return 39.25, -6.82
    lng = sum(p[0] for p in ring) / len(ring)
    lat = sum(p[1] for p in ring) / len(ring)
    return lng, lat


def compute_location_analytics(
    year: int | None = None,
    settings: Settings | None = None,
) -> dict[str, Any]:
    """Aggregate settlement metrics by district and ward (settlement name)."""
    cfg = settings or get_settings()
    years = available_years(cfg)
    if not years:
        return {"year": year, "districts": [], "wards": [], "years_available": []}

    target_year = year or years[-1]
    if target_year not in years:
        target_year = years[-1]

    prev_year = years[years.index(target_year) - 1] if years.index(target_year) > 0 else None

    try:
        gdf = load_year(target_year, cfg)
        prev_gdf = load_year(prev_year, cfg) if prev_year else None
    except (FileNotFoundError, ValueError):
        return {
            "year": target_year,
            "previous_year": prev_year,
            "years_available": years,
            "districts": [],
            "wards": [],
        }

    if gdf is None or len(gdf) == 0:
        return {
            "year": target_year,
            "previous_year": prev_year,
            "years_available": years,
            "districts": [],
            "wards": [],
        }

    district_stats: dict[str, dict] = {
        d: {
            "district": d,
            "settlements": 0,
            "total_area_ha": 0.0,
            "avg_isi": 0.0,
            "high_risk_count": 0,
            "population_proxy": 0,
            "growth_pct": 0.0,
            "color": DISTRICT_COLORS.get(d, "#94a3b8"),
        }
        for d in DISTRICT_BOUNDS
    }
    ward_stats: dict[str, dict] = {}
    isi_sums: dict[str, float] = {d: 0.0 for d in DISTRICT_BOUNDS}

    for _, row in gdf.iterrows():
        geom = row.geometry.__geo_interface__ if hasattr(row.geometry, "__geo_interface__") else {}
        lng, lat = _centroid(geom)
        district = assign_district(lng, lat)
        name = str(row.get("name", "Settlement"))
        sym = "".join(w[0] for w in name.split()[:2]).upper()[:6] or name[:3].upper()

        d = district_stats[district]
        d["settlements"] += 1
        d["total_area_ha"] += float(row.get("area_ha", 0))
        isi_sums[district] += float(row.get("isi_score", 0))
        if row.get("risk_level") == "high":
            d["high_risk_count"] += 1
        d["population_proxy"] += int(row.get("population_proxy", 0))

        if name not in ward_stats:
            ward_stats[name] = {
                "symbol": sym,
                "name": name,
                "district": district,
                "settlements": 0,
                "total_area_ha": 0.0,
                "change_pct": 0.0,
            }
        w = ward_stats[name]
        w["settlements"] += 1
        w["total_area_ha"] += float(row.get("area_ha", 0))

    if prev_gdf is not None:
        prev_district_area: dict[str, float] = {d: 0.0 for d in DISTRICT_BOUNDS}
        prev_ward_area: dict[str, float] = {}
        for _, row in prev_gdf.iterrows():
            geom = row.geometry.__geo_interface__ if hasattr(row.geometry, "__geo_interface__") else {}
            lng, lat = _centroid(geom)
            district = assign_district(lng, lat)
            prev_district_area[district] += float(row.get("area_ha", 0))
            name = str(row.get("name", "Settlement"))
            prev_ward_area[name] = prev_ward_area.get(name, 0) + float(row.get("area_ha", 0))

        for d_name, d in district_stats.items():
            prev = prev_district_area.get(d_name, 0)
            if prev > 0:
                d["growth_pct"] = round(((d["total_area_ha"] - prev) / prev) * 100, 2)

        for name, w in ward_stats.items():
            prev = prev_ward_area.get(name, 0)
            if prev > 0:
                w["change_pct"] = round(((w["total_area_ha"] - prev) / prev) * 100, 2)

    for d_name, d in district_stats.items():
        if d["settlements"] > 0:
            d["avg_isi"] = round(isi_sums[d_name] / d["settlements"], 4)
        d["total_area_ha"] = round(d["total_area_ha"], 2)

    districts = sorted(district_stats.values(), key=lambda x: x["growth_pct"], reverse=True)
    wards = sorted(ward_stats.values(), key=lambda x: x["settlements"], reverse=True)

    return {
        "year": target_year,
        "previous_year": prev_year,
        "years_available": years,
        "districts": districts,
        "wards": wards,
    }


def export_location_csv(analytics: dict[str, Any], district: str | None = None) -> str:
    """CSV report for all locations or a single district."""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["DarInformal — Location Analytics Report"])
    writer.writerow(["Year", analytics.get("year", "")])
    writer.writerow(["District Filter", district or "All"])
    writer.writerow(["Generated (UTC)", datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")])
    writer.writerow([])

    writer.writerow(["DISTRICT SUMMARY"])
    writer.writerow([
        "district", "settlements", "total_area_ha", "avg_isi",
        "high_risk_count", "population_proxy", "growth_pct",
    ])
    for d in analytics.get("districts", []):
        if district and d["district"].lower() != district.lower():
            continue
        writer.writerow([
            d["district"], d["settlements"], d["total_area_ha"], d["avg_isi"],
            d["high_risk_count"], d["population_proxy"], d["growth_pct"],
        ])

    writer.writerow([])
    writer.writerow(["WARD / SETTLEMENT DETAIL"])
    writer.writerow(["symbol", "name", "district", "settlements", "total_area_ha", "change_pct"])
    for w in analytics.get("wards", []):
        if district and w["district"].lower() != district.lower():
            continue
        writer.writerow([
            w["symbol"], w["name"], w["district"],
            w["settlements"], round(w["total_area_ha"], 2), w["change_pct"],
        ])

    return output.getvalue()
