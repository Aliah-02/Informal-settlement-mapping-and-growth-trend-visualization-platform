#!/usr/bin/env python3
"""Compute and store yearly_metrics in PostGIS from settlements table.

Usage:
    python scripts/compute_yearly_metrics.py
    python scripts/compute_yearly_metrics.py --year 2020
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import get_settings
from db.repository import get_available_years, upsert_yearly_metrics
from services.metrics import compute_year_metrics

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def compute_and_store(year: int) -> dict:
    """Compute metrics for a year and upsert into yearly_metrics table."""
    metrics = compute_year_metrics(year)
    upsert_yearly_metrics(metrics)
    logger.info(
        "Year %d: %d settlements, %.1f ha, avg ISI %.3f",
        year, metrics["total_settlements"], metrics["total_area_ha"], metrics["average_isi"],
    )
    return metrics


def main():
    parser = argparse.ArgumentParser(description="Compute yearly metrics in PostGIS")
    parser.add_argument("--year", type=int, help="Compute for a specific year only")
    args = parser.parse_args()

    settings = get_settings()
    years = [args.year] if args.year else get_available_years(settings)
    if not years:
        # Fall back to analysis years if PostGIS empty — metrics will use geojson via compute_year_metrics
        years = settings.analysis_years

    for year in years:
        try:
            compute_and_store(year)
        except Exception as exc:
            logger.error("Failed for year %d: %s", year, exc)


if __name__ == "__main__":
    main()
