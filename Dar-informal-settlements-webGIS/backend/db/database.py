"""PostGIS database engine and session management."""

from __future__ import annotations

import logging
from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from config import Settings, get_settings

logger = logging.getLogger(__name__)

_engine: Engine | None = None
_SessionLocal: sessionmaker | None = None


def get_engine(settings: Settings | None = None) -> Engine:
    """Return singleton SQLAlchemy engine (sync, psycopg2)."""
    global _engine, _SessionLocal
    if _engine is None:
        cfg = settings or get_settings()
        _engine = create_engine(
            cfg.database_url_sync,
            pool_pre_ping=True,
            pool_size=5,
            max_overflow=10,
            echo=cfg.debug,
        )
        _SessionLocal = sessionmaker(bind=_engine, autocommit=False, autoflush=False)
        logger.info("PostGIS engine created: %s", cfg.database_url_sync.split("@")[-1])
    return _engine


def get_session() -> sessionmaker:
    """Return session factory (call get_engine first)."""
    if _SessionLocal is None:
        get_engine()
    assert _SessionLocal is not None
    return _SessionLocal


@contextmanager
def session_scope(settings: Settings | None = None) -> Generator[Session, None, None]:
    """Provide a transactional scope around a series of operations."""
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
    cfg = settings or get_settings()
    try:
        engine = get_engine(cfg)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            version = conn.execute(text("SELECT PostGIS_Version()")).scalar()
            settlement_count = conn.execute(
                text("SELECT COUNT(*) FROM settlements")
            ).scalar()
            years = conn.execute(
                text("SELECT DISTINCT year FROM settlements ORDER BY year")
            ).fetchall()
        return {
            "connected": True,
            "postgis_version": version,
            "settlement_count": settlement_count,
            "years": [row[0] for row in years],
        }
    except Exception as exc:
        logger.warning("PostGIS connection failed: %s", exc)
        return {"connected": False, "error": str(exc)}
