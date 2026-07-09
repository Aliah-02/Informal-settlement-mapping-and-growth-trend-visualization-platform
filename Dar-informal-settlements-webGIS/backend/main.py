"""DarInformal WebGIS — FastAPI Backend Application."""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import Depends, FastAPI, Header, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from sqlalchemy.orm import Session

from config import get_settings
from db.database import check_connection, get_session
from models.schemas import (
    ChangeDetectionResponse,
    RiskLayerResponse,
    TrendResponse,
)
from routers import activity, admin_dashboard, auth
from routers.auth import get_current_user_optional
from scripts.bootstrap_db import bootstrap_database
from services.activity_service import record_download
from services.change_detection import detect_changes
from services.data_source import (
    available_years,
    data_source_label,
    filter_settlements,
    load_year,
    use_postgis,
)
from services.loader import to_feature_collection
from services.metrics import compute_trend, compute_year_metrics
from services.reports import export_change_detection_csv, export_growth_trend_csv

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: verify PostGIS + data availability; shutdown: cleanup."""
    try:
        bootstrap_database()
    except Exception as exc:
        logger.warning("Database bootstrap skipped: %s", exc)
    db_status = check_connection(settings)
    years = available_years(settings)
    source = data_source_label(settings)
    logger.info(
        "DarInformal API starting — source=%s, years=%s, postgis=%s",
        source,
        years,
        db_status.get("connected", False),
    )
    if not years:
        logger.warning("No settlement data found (PostGIS or GeoJSON)")
    yield
    logger.info("DarInformal API shutting down")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "Informal Settlement Mapping and Growth Trend Visualization API "
        "for Dar es Salaam, Tanzania (2005–2026). "
        "PostGIS-backed GeoJSON delivery for WebGIS clients."
    ),
    lifespan=lifespan,
)

_cors_kw: dict = {
    "allow_origins": settings.cors_origins + (["*"] if settings.debug else []),
    "allow_credentials": True,
    "allow_methods": ["*"],
    "allow_headers": ["*"],
}
if settings.allow_vercel_previews():
    _cors_kw["allow_origin_regex"] = r"https://.*\.vercel\.app"

app.add_middleware(CORSMiddleware, **_cors_kw)

app.include_router(auth.router)
app.include_router(activity.router)
app.include_router(admin_dashboard.router)


def _db_dep():
    SessionLocal = get_session()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.commit()
        db.close()


@app.exception_handler(FileNotFoundError)
async def file_not_found_handler(request, exc: FileNotFoundError):
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@app.exception_handler(ValueError)
async def value_error_handler(request, exc: ValueError):
    return JSONResponse(status_code=400, content={"detail": str(exc)})


@app.get("/api/health", tags=["System"])
async def health_check():
    """Service health with PostGIS connectivity and data availability."""
    db_status = check_connection(settings)
    years = available_years(settings)
    return {
        "status": "healthy",
        "version": settings.app_version,
        "data_source": data_source_label(settings),
        "database": {
            "connected": db_status.get("connected", False),
            "postgis_version": db_status.get("postgis_version"),
            "settlement_count": db_status.get("settlement_count", 0),
        },
        "data_years_available": years,
    }


@app.get("/api/risk/{year}", response_model=RiskLayerResponse, tags=["Risk Layers"])
async def get_risk_layer(year: int):
    """Return GeoJSON risk layer for a given analysis year."""
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
            "data_source": data_source_label(settings),
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


@app.get("/api/metrics/trend/csv", tags=["Analytics", "Reports"])
async def download_growth_trend_csv(
    request: Request,
    db: Session = Depends(_db_dep),
    user=Depends(get_current_user_optional),
    x_session_token: str | None = Header(default=None, alias="X-Session-Token"),
):
    """Download growth trend analytics as CSV report."""
    trend = compute_trend(settings)
    if not trend.get("metrics"):
        raise HTTPException(status_code=404, detail="No trend data available for export")
    record_download(
        db,
        report_type="growth_trend",
        report_label="Growth Trend Report",
        session_token=x_session_token,
        user_id=user.id if user else None,
        user_email=user.email if user else None,
        ip_address=request.client.host if request.client else None,
    )
    csv_content = export_growth_trend_csv(trend)
    filename = "darinformal_growth_trend_report.csv"
    return Response(
        content=csv_content,
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@app.get("/api/change/{from_year}/{to_year}/csv", tags=["Change Detection", "Reports"])
async def download_change_detection_csv(
    from_year: int,
    to_year: int,
    request: Request,
    db: Session = Depends(_db_dep),
    user=Depends(get_current_user_optional),
    x_session_token: str | None = Header(default=None, alias="X-Session-Token"),
):
    """Download change detection results as CSV report."""
    if from_year >= to_year:
        raise HTTPException(status_code=400, detail="from_year must be less than to_year")
    try:
        result = detect_changes(from_year, to_year, settings)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    record_download(
        db,
        report_type="change_detection",
        report_label=f"Change Detection {from_year}-{to_year}",
        session_token=x_session_token,
        user_id=user.id if user else None,
        user_email=user.email if user else None,
        ip_address=request.client.host if request.client else None,
    )
    csv_content = export_change_detection_csv(result)
    filename = f"darinformal_change_{from_year}_{to_year}.csv"
    return Response(
        content=csv_content,
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@app.get(
    "/api/change/{from_year}/{to_year}",
    response_model=ChangeDetectionResponse,
    tags=["Change Detection"],
)
async def get_change_detection(from_year: int, to_year: int):
    """Detect informal settlement changes between two years."""
    if from_year >= to_year:
        raise HTTPException(status_code=400, detail="from_year must be less than to_year")
    if from_year not in settings.analysis_years or to_year not in settings.analysis_years:
        raise HTTPException(status_code=400, detail=f"Years must be in {settings.analysis_years}")
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
        raise HTTPException(status_code=400, detail=f"Year must be in {settings.analysis_years}")

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
        "data_source": data_source_label(settings),
        "features": features,
    }


@app.post("/api/admin/import", tags=["Admin"])
async def trigger_import():
    """Trigger GeoJSON → PostGIS import (development convenience endpoint)."""
    if not settings.debug:
        raise HTTPException(status_code=403, detail="Import endpoint disabled in production")
    import subprocess
    result = subprocess.run(
        ["python", "scripts/import_geojson_to_postgis.py", "--all"],
        capture_output=True,
        text=True,
        cwd=str(settings.base_dir),
    )
    if result.returncode != 0:
        raise HTTPException(status_code=500, detail=result.stderr)
    subprocess.run(
        ["python", "scripts/compute_yearly_metrics.py"],
        cwd=str(settings.base_dir),
    )
    return {"status": "imported", "output": result.stdout}


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
