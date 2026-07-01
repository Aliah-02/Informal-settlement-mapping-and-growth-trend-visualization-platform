"""Application configuration for DarInformal WebGIS platform."""

from functools import lru_cache
import json
import os
from pathlib import Path
from typing import Optional

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings


def _normalize_database_url(url: str) -> str:
    """Render/Heroku provide postgres:// — SQLAlchemy needs postgresql://."""
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql://", 1)
    return url


class Settings(BaseSettings):
    """Environment-driven settings with sensible local defaults."""

    app_name: str = "DarInformal API"
    app_version: str = "1.0.0"
    debug: bool = False

    # Database — Render sets DATABASE_URL automatically
    database_url: str = (
        "postgresql+asyncpg://darinformal:darinformal@localhost:5432/darinformal"
    )
    database_url_sync: str = (
        "postgresql://darinformal:darinformal@localhost:5432/darinformal"
    )
    use_postgis: bool = True
    auto_import_on_startup: bool = True

    # Production frontend (Vercel) — used for CORS
    frontend_url: str = ""

    # GeoServer (optional — not available on Render free tier)
    geoserver_url: str = "http://localhost:8080/geoserver"
    geoserver_public_url: str = "/geoserver"
    geoserver_workspace: str = "darinformal"
    geoserver_layer: str = "settlements"
    geoserver_user: str = "admin"
    geoserver_password: str = "geoserver"

    # CORS
    cors_origins: list[str] = [
        "http://localhost",
        "http://localhost:80",
        "http://localhost:3000",
        "http://localhost:5500",
        "http://127.0.0.1:5500",
    ]

    # Data paths
    base_dir: Path = Path(__file__).resolve().parent
    data_dir: Path = base_dir / "data"
    geojson_dir: Path = data_dir / "geojson"
    raster_dir: Path = data_dir / "raster"

    # Dar es Salaam AOI bounds (approximate metropolitan extent)
    aoi_west: float = 39.05
    aoi_south: float = -6.95
    aoi_east: float = 39.45
    aoi_north: float = -6.65

    # Supported analysis years
    analysis_years: list[int] = [2005, 2010, 2015, 2020, 2026]

    # ISI risk thresholds
    isi_low_threshold: float = 0.2
    isi_high_threshold: float = 0.5

    # ISI formula weights
    isi_weight_ndbi: float = 0.3
    isi_weight_ndvi_inv: float = 0.25
    isi_weight_bsi: float = 0.2
    isi_weight_fragmentation: float = 0.25

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return [o.strip() for o in v.split(",") if o.strip()]
        return v

    @model_validator(mode="after")
    def apply_cloud_env(self) -> "Settings":
        """Map Render DATABASE_URL and merge Vercel CORS origins."""
        render_db = os.getenv("DATABASE_URL")
        if render_db:
            sync_url = _normalize_database_url(render_db)
            self.database_url_sync = sync_url
            self.database_url = sync_url.replace("postgresql://", "postgresql+asyncpg://", 1)

        origins = list(self.cors_origins)
        if self.frontend_url:
            url = self.frontend_url.rstrip("/")
            if url not in origins:
                origins.append(url)
        vercel_url = os.getenv("VERCEL_URL")
        if vercel_url:
            full = f"https://{vercel_url}" if not vercel_url.startswith("http") else vercel_url
            if full not in origins:
                origins.append(full)
        self.cors_origins = origins
        return self

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    """Return cached settings instance."""
    return Settings()
