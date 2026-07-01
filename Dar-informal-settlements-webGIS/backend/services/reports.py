"""CSV report generation for growth trend analytics."""

from __future__ import annotations

import csv
import io
from datetime import datetime, timezone
from typing import Any


def export_growth_trend_csv(trend: dict[str, Any], city: str = "Dar es Salaam") -> str:
    """Build CSV string for yearly growth metrics + summary block."""
    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow(["DarInformal — Informal Settlement Growth Trend Report"])
    writer.writerow(["City", city])
    writer.writerow(["Country", "Tanzania"])
    writer.writerow(["Generated (UTC)", datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")])
    writer.writerow([])

    summary = trend.get("summary", {})
    if summary and "message" not in summary:
        writer.writerow(["SUMMARY"])
        writer.writerow(["Period Start", summary.get("period_start", "")])
        writer.writerow(["Period End", summary.get("period_end", "")])
        writer.writerow(["Total Area Growth (%)", summary.get("total_area_growth_pct", "")])
        writer.writerow(["Settlements Growth (count)", summary.get("settlements_growth", "")])
        writer.writerow(["ISI Change", summary.get("isi_change", "")])
        writer.writerow(["Population Proxy Growth", summary.get("population_proxy_growth", "")])
        writer.writerow(["Latest High-Risk Area (%)", summary.get("latest_high_risk_pct", "")])
        writer.writerow([])

    writer.writerow(["YEARLY METRICS"])
    writer.writerow([
        "year",
        "total_settlements",
        "total_area_ha",
        "average_isi",
        "high_risk_area_ha",
        "medium_risk_area_ha",
        "low_risk_area_ha",
        "high_risk_count",
        "medium_risk_count",
        "low_risk_count",
        "population_proxy_total",
        "growth_rate_pct",
    ])

    for m in trend.get("metrics", []):
        writer.writerow([
            m.get("year", ""),
            m.get("total_settlements", ""),
            m.get("total_area_ha", ""),
            m.get("average_isi", ""),
            m.get("high_risk_area_ha", ""),
            m.get("medium_risk_area_ha", ""),
            m.get("low_risk_area_ha", ""),
            m.get("high_risk_count", ""),
            m.get("medium_risk_count", ""),
            m.get("low_risk_count", ""),
            m.get("population_proxy_total", ""),
            m.get("growth_rate_pct", ""),
        ])

    if summary.get("high_risk_area_trend"):
        writer.writerow([])
        writer.writerow(["HIGH RISK AREA TREND"])
        writer.writerow(["year", "high_risk_area_ha"])
        for row in summary["high_risk_area_trend"]:
            writer.writerow([row.get("year", ""), row.get("area_ha", "")])

    return output.getvalue()


def export_change_detection_csv(change: dict[str, Any]) -> str:
    """Build CSV for change detection between two years."""
    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow(["DarInformal — Settlement Change Detection Report"])
    writer.writerow(["From Year", change.get("from_year", "")])
    writer.writerow(["To Year", change.get("to_year", "")])
    writer.writerow(["Generated (UTC)", datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")])
    writer.writerow([])

    s = change.get("summary", {})
    writer.writerow(["SUMMARY"])
    writer.writerow(["New Settlements", s.get("new_count", "")])
    writer.writerow(["Expanded", s.get("expanded_count", "")])
    writer.writerow(["Contracted", s.get("contracted_count", "")])
    writer.writerow(["Stable", s.get("stable_count", "")])
    writer.writerow(["Area Change (%)", s.get("area_change_pct", "")])
    writer.writerow(["Area Change (ha)", change.get("area_change_ha", "")])
    writer.writerow([])

    writer.writerow(["NEW SETTLEMENTS"])
    writer.writerow(["id", "name", "isi_score", "risk_level", "area_ha", "population_proxy"])
    for item in change.get("new_settlements", []):
        writer.writerow([
            item.get("id", ""), item.get("name", ""), item.get("isi_score", ""),
            item.get("risk_level", ""), item.get("area_ha", ""), item.get("population_proxy", ""),
        ])

    return output.getvalue()
