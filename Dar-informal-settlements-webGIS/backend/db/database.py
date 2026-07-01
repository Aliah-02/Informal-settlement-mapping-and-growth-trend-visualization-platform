"""PostGIS database engine and session management."""

from __future__ import annotations

import logging
import os
from contextlib import contextmanager
from typing import Generator
from urllib.parse import urlparse

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from config import Settings, get_settings

logger = logging.getLogger(__name__)

_engine: Engine | None = None
_SessionLocal: sessionmaker | None = None


def is_database_configured() -> bool:
    """True when Render/local DATABASE_URL is set."""
    return bool(os.getenv("DATABASE_URL", "").strip())


def _connect_args_for_url(url: str) -> dict:
    """Render Postgres requires SSL."""
    host = urlparse(url).hostname or ""
    if "dpg-" in host or host.endswith(".render.com"):
        return {"sslmode": "require"}
    return {}


def get_engine(settings: Settings | None = None) -> Engine:
    """Return singleton SQLAlchemy engine (sync, psycopg2)."""
    global _engine, _SessionLocal
    if _engine is None:
        cfg = settings or get_settings()
        url = cfg.database_url_sync
        _engine = create_engine(
            url,
            pool_pre_ping=True,
            pool_size=5,
            max_overflow=10,
            echo=cfg.debug,
            connect_args=_connect_args_for_url(url),
        )
        _SessionLocal = sessionmaker(bind=_engine, autocommit=False, autoflush=False)
        host = urlparse(url).hostname or "unknown"
        logger.info("PostGIS engine → host=%s configured=%s", host, is_database_configured())
    return _engine


def get_session() -> sessionmaker:
    if _SessionLocal is None:
        get_engine()
    assert _SessionLocal is not None
    return _SessionLocal


@contextmanager
def session_scope(settings: Settings | None = None) -> Generator[Session, None, None]:
    SessionLocal = get_session()
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def check_connection(settings: Settings | None = None) -> dict:
    """Verify PostGIS connectivity and return status info."""
    if not is_database_configured():
        return {
            "configured": False,
            "connected": False,
            "error": "DATABASE_URL not set — link Render PostgreSQL to this web service",
        }

    cfg = settings or get_settings()
    try:
        engine = get_engine(cfg)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            version = conn.execute(text("SELECT PostGIS_Version()")).scalar()
            try:
                settlement_count = conn.execute(
                    text("SELECT COUNT(*) FROM settlements")
                ).scalar()
                years = conn.execute(
                    text("SELECT DISTINCT year FROM settlements ORDER BY year")
                ).fetchall()
                year_list = [row[0] for row in years]
            except Exception:
                settlement_count = 0
                year_list = []
        return {
            "configured": True,
            "connected": True,
            "postgis_version": version,
            "settlement_count": settlement_count,
            "years": year_list,
        }
    except Exception as exc:
        logger.warning("PostGIS connection failed: %s", exc)
        return {"configured": True, "connected": False, "error": str(exc)}
