"""Service package for DarInformal backend."""

from .change_detection import detect_changes
from .isi_model import classify_risk, compute_isi, risk_color
from .loader import available_years, filter_settlements, load_year, to_feature_collection
from .metrics import compute_trend, compute_year_metrics

__all__ = [
    "available_years",
    "classify_risk",
    "compute_isi",
    "compute_trend",
    "compute_year_metrics",
    "detect_changes",
    "filter_settlements",
    "load_year",
    "risk_color",
    "to_feature_collection",
]
