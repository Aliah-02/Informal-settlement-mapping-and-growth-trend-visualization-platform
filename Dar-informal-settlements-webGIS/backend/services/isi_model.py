"""Informal Settlement Index (ISI) computation engine.

ISI = (0.3 * NDBI) + (0.25 * (1 - NDVI)) + (0.2 * BSI) + (0.25 * fragmentation_index)

Risk levels:
  - Low:    ISI < 0.2
  - Medium: 0.2 <= ISI <= 0.5
  - High:   ISI > 0.5
"""

from __future__ import annotations

from typing import Literal

from config import Settings, get_settings

RiskLevel = Literal["low", "medium", "high"]


def normalize_index(value: float, min_val: float = -1.0, max_val: float = 1.0) -> float:
    """Clamp and normalize a spectral index to [0, 1]."""
    clamped = max(min_val, min(max_val, value))
    if max_val == min_val:
        return 0.0
    return (clamped - min_val) / (max_val - min_val)


def compute_isi(
    ndbi: float,
    ndvi: float,
    bsi: float,
    fragmentation_index: float,
    settings: Settings | None = None,
) -> float:
    """Compute Informal Settlement Index using weighted formula."""
    cfg = settings or get_settings()

    ndbi_n = normalize_index(ndbi, -0.5, 0.8)
    ndvi_inv = 1.0 - normalize_index(ndvi, -0.2, 0.8)
    bsi_n = normalize_index(bsi, 0.0, 1.0)
    frag_n = max(0.0, min(1.0, fragmentation_index))

    isi = (
        cfg.isi_weight_ndbi * ndbi_n
        + cfg.isi_weight_ndvi_inv * ndvi_inv
        + cfg.isi_weight_bsi * bsi_n
        + cfg.isi_weight_fragmentation * frag_n
    )
    return round(max(0.0, min(1.0, isi)), 4)


def classify_risk(isi: float, settings: Settings | None = None) -> RiskLevel:
    """Classify ISI score into risk level."""
    cfg = settings or get_settings()
    if isi < cfg.isi_low_threshold:
        return "low"
    if isi <= cfg.isi_high_threshold:
        return "medium"
    return "high"


def risk_color(risk_level: RiskLevel) -> str:
    """Return hex color for risk level (for frontend legend)."""
    return {
        "low": "#22c55e",
        "medium": "#f59e0b",
        "high": "#ef4444",
    }[risk_level]


def estimate_population_proxy(area_ha: float, isi: float, density_factor: float = 8500.0) -> int:
    """Estimate population proxy from area and ISI intensity.

    Higher ISI correlates with denser informal housing patterns.
    density_factor represents persons per hectare at ISI=1.0.
    """
    density = density_factor * (0.4 + 0.6 * isi)
    return int(area_ha * density)


def compute_fragmentation_index(
    perimeter_m: float,
    area_m2: float,
    compactness_weight: float = 1.0,
) -> float:
    """Compute shape fragmentation index using perimeter-area ratio.

    Higher values indicate more fragmented / irregular settlement shapes
    typical of informal growth patterns.
    """
    if area_m2 <= 0:
        return 0.0
    # Normalized perimeter-to-area ratio (higher = more fragmented)
    ratio = perimeter_m / (2.0 * (area_m2 ** 0.5))
    # Typical range ~1.0-4.0 for polygons
    frag = (ratio - 1.0) / 3.0
    return round(max(0.0, min(1.0, frag * compactness_weight)), 4)
