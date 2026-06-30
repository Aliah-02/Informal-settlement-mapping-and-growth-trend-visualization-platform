"""Analytics metrics computation for trend dashboard."""

from __future__ import annotations

import logging
from typing import Any, Optional

from config import Settings, get_settings
from services.loader import available_years, load_year

logger = logging.getLogger(__name__)


def compute_year_metrics(year: int, settings: Settings | None = None) -> dict[str, Any]:
    """Compute aggregated metrics for a single year."""
    cfg = settings or get_settings()
    gdf = load_year(year, cfg)

    high = gdf[gdf["risk_level"] == "high"]
    medium = gdf[gdf["risk_level"] == "medium"]
    low = gdf[gdf["risk_level"] == "low"]

    return {
        "year": year,
        "total_settlements": len(gdf),
        "total_area_ha": round(gdf["area_ha"].sum(), 2),
        "average_isi": round(gdf["isi_score"].mean(), 4),
        "high_risk_area_ha": round(high["area_ha"].sum(), 2),
        "medium_risk_area_ha": round(medium["area_ha"].sum(), 2),
        "low_risk_area_ha": round(low["area_ha"].sum(), 2),
        "high_risk_count": len(high),
        "medium_risk_count": len(medium),
        "low_risk_count": len(low),
        "population_proxy_total": int(gdf["population_proxy"].sum()),
        "growth_rate_pct": None,
    }


def compute_growth_rate(
    current: dict[str, Any],
    previous: dict[str, Any],
) -> float:
    """Calculate area growth rate between two year metrics."""
    prev_area = previous["total_area_ha"]
    if prev_area <= 0:
        return 0.0
    return round(
        ((current["total_area_ha"] - prev_area) / prev_area) * 100,
        2,
    )


def compute_trend(settings: Settings | None = None) -> dict[str, Any]:
    """Compute time-series metrics across all available years."""
    cfg = settings or get_settings()
    years = available_years(cfg)

    if not years:
        return {
            "years": [],
            "metrics": [],
            "summary": {"message": "No data available"},
        }

    metrics_list: list[dict[str, Any]] = []
    prev_metrics: Optional[dict[str, Any]] = None

    for year in years:
        m = compute_year_metrics(year, cfg)
        if prev_metrics is not None:
            m["growth_rate_pct"] = compute_growth_rate(m, prev_metrics)
        metrics_list.append(m)
        prev_metrics = m

    first = metrics_list[0]
    last = metrics_list[-1]
    total_growth = compute_growth_rate(last, first) if len(metrics_list) > 1 else 0.0

    high_risk_trend = [
        {"year": m["year"], "area_ha": m["high_risk_area_ha"]} for m in metrics_list
    ]

    return {
        "years": years,
        "metrics": metrics_list,
        "summary": {
            "period_start": years[0],
            "period_end": years[-1],
            "total_area_growth_pct": total_growth,
            "settlements_growth": last["total_settlements"] - first["total_settlements"],
            "isi_change": round(last["average_isi"] - first["average_isi"], 4),
            "population_proxy_growth": last["population_proxy_total"] - first["population_proxy_total"],
            "high_risk_area_trend": high_risk_trend,
            "latest_high_risk_pct": round(
                (last["high_risk_area_ha"] / last["total_area_ha"] * 100)
                if last["total_area_ha"] > 0
                else 0,
                1,
            ),
        },
    }
