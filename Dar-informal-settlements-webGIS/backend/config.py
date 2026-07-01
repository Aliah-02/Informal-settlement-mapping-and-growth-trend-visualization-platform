"""Application configuration for DarInformal WebGIS platform."""

from functools import lru_cache
from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Environment-driven settings with sensible local defaults."""

    app_name: str = "DarInformal API"
    app_version: str = "1.0.0"
    debug: bool = False

    # Database
    database_url: str = (
        "postgresql+asyncpg://darinformal:darinformal@localhost:5432/darinformal"
    )
    database_url_sync: str = (
        "postgresql://darinformal:darinformal@localhost:5432/darinformal"
    )
    use_postgis: bool = True

    # GeoServer
    geoserver_url: str = "http://localhost:8080/geoserver"
    geoserver_public_url: str = "/geoserver"  # Nginx proxy path for frontend
    geoserver_workspace: str = "darinformal"
    geoserver_layer: str = "settlements"
    geoserver_user: str = "admin"
    geoserver_password: str = "geoserver"

    # CORS
    cors_origins: list[str] = ["http://localhost", "http://localhost:80", "http://localhost:3000"]

    # Data paths
    base_dir: Path = Path(__file__).resolve().parent
    data_dir: Path = base_dir / "data"
    geojson_dir: Path = data_dir / "geojson"

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

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    """Return cached settings instance."""
    return Settings()
