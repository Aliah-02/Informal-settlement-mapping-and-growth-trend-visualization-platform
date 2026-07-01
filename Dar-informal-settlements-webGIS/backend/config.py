"""Application configuration — works with pydantic-settings 2.6.1 on Render."""

from functools import lru_cache
import json
import os
from pathlib import Path

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def _normalize_database_url(url: str) -> str:
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql://", 1)
    return url


def _parse_cors_origins(raw: str | None) -> list[str]:
    """Parse CORS_ORIGINS env: empty, single URL, comma list, or JSON array."""
    defaults = [
        "http://localhost:5500",
        "http://127.0.0.1:5500",
        "http://localhost:8000",
    ]
    if not raw or not str(raw).strip():
        return defaults
    text = str(raw).strip()
    if text.startswith("["):
        try:
            parsed = json.loads(text)
            if isinstance(parsed, list):
                return [str(u).strip() for u in parsed if str(u).strip()] or defaults
        except json.JSONDecodeError:
            pass
    if "," in text:
        return [u.strip() for u in text.split(",") if u.strip()]
    return [text]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "DarInformal API"
    app_version: str = "1.0.0"
    debug: bool = False

    database_url: str = (
        "postgresql+asyncpg://darinformal:darinformal@localhost:5432/darinformal"
    )
    database_url_sync: str = (
        "postgresql://darinformal:darinformal@localhost:5432/darinformal"
    )
    use_postgis: bool = True
    auto_import_on_startup: bool = True

    # Set on Render to your Vercel URL, e.g. https://myapp.vercel.app
    frontend_url: str = ""

    # Optional extra CORS URLs (string only — never list type from env)
    cors_origins_str: str = Field(default="", validation_alias="CORS_ORIGINS")

    base_dir: Path = Path(__file__).resolve().parent
    data_dir: Path = base_dir / "data"
    geojson_dir: Path = data_dir / "geojson"
    raster_dir: Path = data_dir / "raster"

    aoi_west: float = 39.05
    aoi_south: float = -6.95
    aoi_east: float = 39.45
    aoi_north: float = -6.65

    analysis_years: list[int] = [2005, 2010, 2015, 2020, 2026]
    isi_low_threshold: float = 0.2
    isi_high_threshold: float = 0.5
    isi_weight_ndbi: float = 0.3
    isi_weight_ndvi_inv: float = 0.25
    isi_weight_bsi: float = 0.2
    isi_weight_fragmentation: float = 0.25

    @model_validator(mode="after")
    def apply_cloud_env(self) -> "Settings":
        db = os.getenv("DATABASE_URL")
        if db:
            sync = _normalize_database_url(db)
            self.database_url_sync = sync
            self.database_url = sync.replace("postgresql://", "postgresql+asyncpg://", 1)
        return self

    def cors_origins_list(self) -> list[str]:
        """Allowed browser origins for Vercel + local dev."""
        origins = _parse_cors_origins(self.cors_origins_str)
        if self.frontend_url:
            url = self.frontend_url.rstrip("/")
            if url and url not in origins:
                origins.append(url)
        return origins

    @property
    def cors_origins(self) -> list[str]:
        return self.cors_origins_list()

    def allow_vercel_previews(self) -> bool:
        """True when any configured origin is a Vercel deployment."""
        return self.frontend_url.endswith(".vercel.app") or any(
            ".vercel.app" in o for o in self.cors_origins_list()
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()
