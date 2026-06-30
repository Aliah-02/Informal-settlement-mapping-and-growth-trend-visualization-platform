"""Pydantic schemas for API request/response models."""

from typing import Any, Literal, Optional

from pydantic import BaseModel, Field


RiskLevel = Literal["low", "medium", "high"]


class SettlementFeature(BaseModel):
    """Single informal settlement feature."""

    id: str
    name: str
    year: int
    isi_score: float = Field(ge=0.0, le=1.0)
    risk_level: RiskLevel
    area_ha: float = Field(ge=0.0)
    population_proxy: int = Field(ge=0)
    ndbi: float = Field(ge=-1.0, le=1.0)
    ndvi: float = Field(ge=-1.0, le=1.0)
    bsi: float = Field(ge=0.0, le=1.0)
    fragmentation_index: float = Field(ge=0.0, le=1.0)
    geometry: dict[str, Any]


class RiskLayerResponse(BaseModel):
    """GeoJSON FeatureCollection for a given year."""

    type: str = "FeatureCollection"
    year: int
    features: list[dict[str, Any]]
    metadata: dict[str, Any]


class YearMetrics(BaseModel):
    """Aggregated metrics for a single year."""

    year: int
    total_settlements: int
    total_area_ha: float
    average_isi: float
    high_risk_area_ha: float
    medium_risk_area_ha: float
    low_risk_area_ha: float
    high_risk_count: int
    population_proxy_total: int
    growth_rate_pct: Optional[float] = None


class TrendResponse(BaseModel):
    """Time-series metrics across all years."""

    years: list[int]
    metrics: list[YearMetrics]
    summary: dict[str, Any]


class ChangeDetectionResponse(BaseModel):
    """Change detection between two years."""

    from_year: int
    to_year: int
    new_settlements: list[dict[str, Any]]
    expanded_settlements: list[dict[str, Any]]
    contracted_settlements: list[dict[str, Any]]
    stable_settlements: list[dict[str, Any]]
    area_change_ha: float
    isi_change_avg: float
    summary: dict[str, Any]


class SettlementsQueryParams(BaseModel):
    """Query parameters for settlement listing."""

    year: Optional[int] = None
    risk_level: Optional[RiskLevel] = None
    min_isi: Optional[float] = None
    max_isi: Optional[float] = None
    limit: int = Field(default=500, ge=1, le=5000)
    offset: int = Field(default=0, ge=0)


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    version: str
    database: str
    data_years_available: list[int]
