"""DarInformal WebGIS — FastAPI Backend Application."""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from config import get_settings
from models.schemas import (
    ChangeDetectionResponse,
    HealthResponse,
    RiskLayerResponse,
    TrendResponse,
)
from services.change_detection import detect_changes
from services.loader import available_years, filter_settlements, load_year, to_feature_collection
from services.metrics import compute_trend, compute_year_metrics

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: verify data availability; shutdown: cleanup."""
    years = available_years(settings)
    logger.info("DarInformal API starting — data available for years: %s", years)
    if not years:
        logger.warning("No GeoJSON data found in %s", settings.geojson_dir)
    yield
    logger.info("DarInformal API shutting down")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "Informal Settlement Mapping and Growth Trend Visualization API "
        "for Dar es Salaam, Tanzania (2005–2026)."
    ),
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins + ["*"] if settings.debug else settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(FileNotFoundError)
async def file_not_found_handler(request, exc: FileNotFoundError):
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@app.exception_handler(ValueError)
async def value_error_handler(request, exc: ValueError):
    return JSONResponse(status_code=400, content={"detail": str(exc)})


@app.get("/api/health", response_model=HealthResponse, tags=["System"])
async def health_check():
    """Service health and data availability check."""
    years = available_years(settings)
    return HealthResponse(
        status="healthy",
        version=settings.app_version,
        database="postgis-ready",
        data_years_available=years,
    )


@app.get("/api/risk/{year}", response_model=RiskLayerResponse, tags=["Risk Layers"])
async def get_risk_layer(year: int):
    """Return GeoJSON risk layer for a given analysis year.

    Features include ISI scores, risk classification, and population proxy.
    """
    if year not in settings.analysis_years:
        raise HTTPException(
            status_code=400,
            detail=f"Year {year} not in supported range: {settings.analysis_years}",
        )
    try:
        gdf = load_year(year, settings)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    fc = to_feature_collection(gdf)
    metrics = compute_year_metrics(year, settings)

    return RiskLayerResponse(
        year=year,
        features=fc["features"],
        metadata={
            "total_features": len(fc["features"]),
            "average_isi": metrics["average_isi"],
            "total_area_ha": metrics["total_area_ha"],
            "risk_breakdown": {
                "high": metrics["high_risk_count"],
                "medium": metrics["medium_risk_count"],
                "low": metrics["low_risk_count"],
            },
            "risk_colors": {
                "low": "#22c55e",
                "medium": "#f59e0b",
                "high": "#ef4444",
            },
        },
    )


@app.get("/api/metrics/trend", response_model=TrendResponse, tags=["Analytics"])
async def get_metrics_trend():
    """Return time-series growth metrics across all available years."""
    result = compute_trend(settings)
    return TrendResponse(**result)


@app.get(
    "/api/change/{from_year}/{to_year}",
    response_model=ChangeDetectionResponse,
    tags=["Change Detection"],
)
async def get_change_detection(from_year: int, to_year: int):
    """Detect informal settlement changes between two years.

    Returns new, expanded, contracted, and stable settlement classifications.
    """
    if from_year >= to_year:
        raise HTTPException(
            status_code=400,
            detail="from_year must be less than to_year",
        )
    if from_year not in settings.analysis_years or to_year not in settings.analysis_years:
        raise HTTPException(
            status_code=400,
            detail=f"Years must be in {settings.analysis_years}",
        )
    try:
        result = detect_changes(from_year, to_year, settings)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return ChangeDetectionResponse(**result)


@app.get("/api/settlements", tags=["Settlements"])
async def list_settlements(
    year: Optional[int] = Query(None, description="Filter by analysis year"),
    risk_level: Optional[str] = Query(None, description="Filter: low, medium, high"),
    min_isi: Optional[float] = Query(None, ge=0.0, le=1.0),
    max_isi: Optional[float] = Query(None, ge=0.0, le=1.0),
    limit: int = Query(500, ge=1, le=5000),
    offset: int = Query(0, ge=0),
):
    """List informal settlements with optional filters and pagination."""
    if risk_level and risk_level not in ("low", "medium", "high"):
        raise HTTPException(status_code=400, detail="risk_level must be low, medium, or high")

    if year and year not in settings.analysis_years:
        raise HTTPException(
            status_code=400,
            detail=f"Year must be in {settings.analysis_years}",
        )

    try:
        features, total = filter_settlements(
            year=year,
            risk_level=risk_level,
            min_isi=min_isi,
            max_isi=max_isi,
            limit=limit,
            offset=offset,
            settings=settings,
        )
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "features": features,
    }


@app.get("/api/aoi", tags=["System"])
async def get_aoi_bounds():
    """Return Dar es Salaam Area of Interest bounding box."""
    return {
        "name": "Dar es Salaam Metropolitan Area",
        "country": "Tanzania",
        "bounds": {
            "west": settings.aoi_west,
            "south": settings.aoi_south,
            "east": settings.aoi_east,
            "north": settings.aoi_north,
        },
        "center": {
            "lat": (settings.aoi_south + settings.aoi_north) / 2,
            "lng": (settings.aoi_west + settings.aoi_east) / 2,
        },
        "analysis_years": settings.analysis_years,
    }
