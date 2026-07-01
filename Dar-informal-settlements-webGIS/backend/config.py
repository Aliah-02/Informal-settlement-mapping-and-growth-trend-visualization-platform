"""Application configuration for DarInformal WebGIS platform."""

from functools import lru_cache
import json
import os
from pathlib import Path

from pydantic import Field, computed_field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def _normalize_database_url(url: str) -> str:
    """Render/Heroku provide postgres:// — SQLAlchemy needs postgresql://."""
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql://", 1)
    return url


def _parse_cors_origins(value) -> list[str]:
    """Accept JSON array, comma-separated URLs, single URL, or empty."""
    defaults = [
        "http://localhost",
        "http://localhost:80",
        "http://localhost:3000",
        "http://localhost:5500",
        "http://127.0.0.1:5500",
    ]
    if value is None:
        return list(defaults)
    if isinstance(value, list):
        return [str(o).strip() for o in value if str(o).strip()] or list(defaults)
    if isinstance(value, str):
        raw = value.strip()
        if not raw:
            return list(defaults)
        if raw.startswith("["):
            try:
                parsed = json.loads(raw)
                if isinstance(parsed, list):
                    return [str(o).strip() for o in parsed if str(o).strip()] or list(defaults)
            except json.JSONDecodeError:
                pass
        if "," in raw:
            return [o.strip() for o in raw.split(",") if o.strip()]
        return [raw]
    return list(defaults)


class Settings(BaseSettings):
    """Environment-driven settings with sensible local defaults."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

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

    # String env only — never bind CORS_ORIGINS to list[str] (breaks on empty string)
    cors_origins_str: str = Field(default="", validation_alias="CORS_ORIGINS")

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

    @computed_field  # type: ignore[prop-decorator]
    @property
    def cors_origins(self) -> list[str]:
        """Resolved CORS allow-list from env string + frontend URL."""
        origins = _parse_cors_origins(self.cors_origins_str or None)
        if self.frontend_url:
            url = self.frontend_url.rstrip("/")
            if url and url not in origins:
                origins.append(url)
        vercel_url = os.getenv("VERCEL_URL")
        if vercel_url:
            full = f"https://{vercel_url}" if not vercel_url.startswith("http") else vercel_url
            if full not in origins:
                origins.append(full)
        return origins

    @model_validator(mode="after")
    def apply_cloud_env(self) -> "Settings":
        """Map Render DATABASE_URL."""
        render_db = os.getenv("DATABASE_URL")
        if render_db:
            sync_url = _normalize_database_url(render_db)
            self.database_url_sync = sync_url
            self.database_url = sync_url.replace("postgresql://", "postgresql+asyncpg://", 1)
        return self


@lru_cache
def get_settings() -> Settings:
    """Return cached settings instance."""
    return Settings()
