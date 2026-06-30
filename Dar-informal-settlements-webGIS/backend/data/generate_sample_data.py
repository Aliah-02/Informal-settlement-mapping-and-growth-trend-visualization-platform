#!/usr/bin/env python3
"""Generate synthetic informal settlement GeoJSON for Dar es Salaam.

This script creates representative sample data for years 2005, 2010, 2015,
2020, and 2026. Settlement polygons grow and fragment over time to simulate
realistic informal expansion patterns in Dar es Salaam's peri-urban zones.

Usage:
    python generate_sample_data.py
    python generate_sample_data.py --output-dir ./geojson
"""

from __future__ import annotations

import argparse
import json
import math
import random
from pathlib import Path

# Dar es Salaam known informal settlement cluster centers (approximate)
SETTLEMENT_SEEDS = [
    {"name": "Kigamboni", "lng": 39.32, "lat": -6.87, "base_size": 0.004},
    {"name": "Tandale", "lng": 39.24, "lat": -6.80, "base_size": 0.003},
    {"name": "Manzese", "lng": 39.21, "lat": -6.79, "base_size": 0.0035},
    {"name": "Mbagala", "lng": 39.28, "lat": -6.84, "base_size": 0.004},
    {"name": "Buguruni", "lng": 39.22, "lat": -6.83, "base_size": 0.003},
    {"name": "Kimara", "lng": 39.17, "lat": -6.76, "base_size": 0.003},
    {"name": "Gongo la Mboto", "lng": 39.26, "lat": -6.86, "base_size": 0.0035},
    {"name": "Mabibo", "lng": 39.19, "lat": -6.78, "base_size": 0.0025},
    {"name": "Tabata", "lng": 39.23, "lat": -6.82, "base_size": 0.003},
    {"name": "Makuburi", "lng": 39.25, "lat": -6.85, "base_size": 0.003},
    {"name": "Keko", "lng": 39.27, "lat": -6.83, "base_size": 0.0028},
    {"name": "Mburahati", "lng": 39.20, "lat": -6.81, "base_size": 0.0025},
    {"name": "Sinza", "lng": 39.18, "lat": -6.77, "base_size": 0.002},
    {"name": "Ubungo", "lng": 39.16, "lat": -6.78, "base_size": 0.0025},
    {"name": "Kijitonyama", "lng": 39.15, "lat": -6.77, "base_size": 0.002},
]

# Year-specific growth multipliers (informal expansion accelerates post-2010)
YEAR_GROWTH = {
    2005: 0.55,
    2010: 0.70,
    2015: 0.85,
    2020: 1.00,
    2026: 1.18,
}

# Additional settlements appear in later years
YEAR_NEW_SETTLEMENTS = {
    2005: 0,
    2010: 2,
    2015: 3,
    2020: 4,
    2026: 5,
}


def compute_isi(ndbi: float, ndvi: float, bsi: float, frag: float) -> float:
    """Compute ISI using the project formula."""
    ndbi_n = max(0, min(1, (ndbi + 0.5) / 1.3))
    ndvi_inv = 1.0 - max(0, min(1, (ndvi + 0.2) / 1.0))
    bsi_n = max(0, min(1, bsi))
    frag_n = max(0, min(1, frag))
    return round(0.3 * ndbi_n + 0.25 * ndvi_inv + 0.2 * bsi_n + 0.25 * frag_n, 4)


def classify_risk(isi: float) -> str:
    if isi < 0.2:
        return "low"
    if isi <= 0.5:
        return "medium"
    return "high"


def make_irregular_polygon(
    center_lng: float,
    center_lat: float,
    size_deg: float,
    n_vertices: int = 8,
    irregularity: float = 0.4,
) -> list[list[float]]:
    """Create an irregular polygon simulating informal settlement shape."""
    coords = []
    for i in range(n_vertices):
        angle = (2 * math.pi * i) / n_vertices
        r = size_deg * (1 + irregularity * (random.random() - 0.5))
        lng = center_lng + r * math.cos(angle)
        lat = center_lat + r * math.sin(angle) * 0.7  # flatten for lat
        coords.append([round(lng, 6), round(lat, 6)])
    coords.append(coords[0])  # close ring
    return coords


def compute_area_ha(coords: list[list[float]]) -> float:
    """Approximate polygon area in hectares using shoelace formula."""
    n = len(coords) - 1
    area = 0.0
    for i in range(n):
        j = (i + 1) % n
        area += coords[i][0] * coords[j][1]
        area -= coords[j][0] * coords[i][1]
    area = abs(area) / 2.0
    # Convert deg² to ha (rough at Dar es Salaam latitude ~6.8°S)
    meters_per_deg_lat = 111_320
    meters_per_deg_lng = 111_320 * math.cos(math.radians(-6.8))
    area_m2 = area * meters_per_deg_lat * meters_per_deg_lng
    return round(area_m2 / 10_000.0, 2)


def compute_perimeter_m(coords: list[list[float]]) -> float:
    """Approximate polygon perimeter in meters."""
    total = 0.0
    meters_per_deg_lat = 111_320
    meters_per_deg_lng = 111_320 * math.cos(math.radians(-6.8))
    for i in range(len(coords) - 1):
        dlat = (coords[i + 1][1] - coords[i][1]) * meters_per_deg_lat
        dlng = (coords[i + 1][0] - coords[i][0]) * meters_per_deg_lng
        total += math.sqrt(dlat**2 + dlng**2)
    return total


def fragmentation_index(perimeter_m: float, area_m2: float) -> float:
    if area_m2 <= 0:
        return 0.0
    ratio = perimeter_m / (2.0 * math.sqrt(area_m2))
    return round(max(0.0, min(1.0, (ratio - 1.0) / 3.0)), 4)


def generate_spectral_indices(year: int, settlement_idx: int, is_core: bool) -> dict:
    """Generate realistic spectral index values for informal settlements."""
    random.seed(year * 1000 + settlement_idx)

    # Informal settlements: high NDBI, low NDVI, moderate-high BSI
    base_ndbi = 0.15 + (year - 2005) * 0.008
    base_ndvi = 0.35 - (year - 2005) * 0.006
    base_bsi = 0.25 + (year - 2005) * 0.005

    if is_core:
        ndbi = base_ndbi + random.uniform(0.05, 0.25)
        ndvi = base_ndvi - random.uniform(0.05, 0.20)
        bsi = base_bsi + random.uniform(0.05, 0.20)
        frag_base = 0.45
    else:
        ndbi = base_ndbi + random.uniform(-0.05, 0.15)
        ndvi = base_ndvi + random.uniform(-0.10, 0.10)
        bsi = base_bsi + random.uniform(-0.05, 0.15)
        frag_base = 0.30

    return {
        "ndbi": round(ndbi, 4),
        "ndvi": round(ndvi, 4),
        "bsi": round(bsi, 4),
        "fragmentation_index": round(frag_base + random.uniform(-0.1, 0.2), 4),
    }


def generate_year_data(year: int) -> dict:
    """Generate FeatureCollection for a given year."""
    growth = YEAR_GROWTH[year]
    features = []
    settlement_id = 1

    for idx, seed in enumerate(SETTLEMENT_SEEDS):
        size = seed["base_size"] * growth
        n_sub = max(1, int(growth * 2))
        for sub in range(n_sub):
            offset_lng = random.uniform(-0.008, 0.008) * growth
            offset_lat = random.uniform(-0.006, 0.006) * growth
            sub_size = size * random.uniform(0.5, 1.2)

            coords = make_irregular_polygon(
                seed["lng"] + offset_lng,
                seed["lat"] + offset_lat,
                sub_size,
                n_vertices=random.randint(6, 12),
                irregularity=0.3 + growth * 0.2,
            )

            spectral = generate_spectral_indices(year, idx * 10 + sub, is_core=(sub == 0))
            area_ha = compute_area_ha(coords)
            perim = compute_perimeter_m(coords)
            area_m2 = area_ha * 10_000
            frag = fragmentation_index(perim, area_m2)
            spectral["fragmentation_index"] = frag

            isi = compute_isi(spectral["ndbi"], spectral["ndvi"], spectral["bsi"], frag)
            risk = classify_risk(isi)
            pop = int(area_ha * 8500 * (0.4 + 0.6 * isi))

            suffix = f" Zone {sub + 1}" if n_sub > 1 else ""
            features.append({
                "type": "Feature",
                "geometry": {"type": "Polygon", "coordinates": [coords]},
                "properties": {
                    "id": f"DAR-{year}-{settlement_id:04d}",
                    "name": f"{seed['name']}{suffix}",
                    "year": year,
                    "isi_score": isi,
                    "risk_level": risk,
                    "area_ha": area_ha,
                    "population_proxy": pop,
                    **spectral,
                },
            })
            settlement_id += 1

    # Add emergent settlements in later years
    new_count = YEAR_NEW_SETTLEMENTS[year]
    for i in range(new_count):
        lng = random.uniform(39.10, 39.38)
        lat = random.uniform(-6.92, -6.70)
        size = random.uniform(0.001, 0.0025) * growth
        coords = make_irregular_polygon(lng, lat, size, irregularity=0.5)
        spectral = generate_spectral_indices(year, 900 + i, is_core=False)
        area_ha = compute_area_ha(coords)
        perim = compute_perimeter_m(coords)
        frag = fragmentation_index(perim, area_ha * 10_000)
        spectral["fragmentation_index"] = frag
        isi = compute_isi(spectral["ndbi"], spectral["ndvi"], spectral["bsi"], frag)

        features.append({
            "type": "Feature",
            "geometry": {"type": "Polygon", "coordinates": [coords]},
            "properties": {
                "id": f"DAR-{year}-{settlement_id:04d}",
                "name": f"Emergent Settlement {i + 1}",
                "year": year,
                "isi_score": isi,
                "risk_level": classify_risk(isi),
                "area_ha": area_ha,
                "population_proxy": int(area_ha * 8500 * (0.4 + 0.6 * isi)),
                **spectral,
            },
        })
        settlement_id += 1

    return {"type": "FeatureCollection", "features": features}


def main():
    parser = argparse.ArgumentParser(description="Generate Dar es Salaam sample settlement data")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(__file__).parent / "geojson",
        help="Output directory for GeoJSON files",
    )
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    args = parser.parse_args()

    random.seed(args.seed)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    years = [2005, 2010, 2015, 2020, 2026]
    for year in years:
        data = generate_year_data(year)
        out_path = args.output_dir / f"settlements_{year}.geojson"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        print(f"Generated {out_path} — {len(data['features'])} settlements")

    print(f"\nDone. Files written to {args.output_dir}")


if __name__ == "__main__":
    main()
