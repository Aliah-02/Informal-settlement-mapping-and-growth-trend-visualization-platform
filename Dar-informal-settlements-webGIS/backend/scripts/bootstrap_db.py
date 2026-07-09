"""Bootstrap PostGIS on cloud hosts (Render) and seed data if empty."""

from __future__ import annotations

import logging
import sys
from pathlib import Path

# Ensure /app (backend root) is on PYTHONPATH when run as scripts/bootstrap_db.py
_BACKEND_ROOT = Path(__file__).resolve().parent.parent
if str(_BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(_BACKEND_ROOT))

from sqlalchemy import text

from config import get_settings
from db.database import get_engine, is_database_configured, session_scope
from db.repository import is_populated
from services.auth_service import hash_password

logger = logging.getLogger(__name__)


def _run_sql_file(engine, sql_path: Path) -> None:
    if not sql_path.exists():
        return
    sql = sql_path.read_text(encoding="utf-8")
    statements = [s.strip() for s in sql.split(";") if s.strip() and not s.strip().startswith("--")]
    with engine.connect() as conn:
        for stmt in statements:
            try:
                conn.execute(text(stmt))
            except Exception as exc:
                logger.debug("SQL skip: %s", exc)
        conn.commit()


def bootstrap_database() -> None:
    """Enable PostGIS, apply schema, import GeoJSON if DB is empty."""
    settings = get_settings()
    if not settings.use_postgis:
        logger.info("PostGIS disabled — skipping bootstrap")
        return

    if not is_database_configured():
        logger.warning("DATABASE_URL not set — using GeoJSON files (link Render Postgres to enable PostGIS)")
        return

    try:
        engine = get_engine(settings)
        with engine.connect() as conn:
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis"))
            conn.commit()
        logger.info("PostGIS extension ready")
    except Exception as exc:
        logger.warning("PostGIS bootstrap failed (will use GeoJSON fallback): %s", exc)
        return

    init_sql = settings.data_dir / "init.sql"
    try:
        _run_sql_file(engine, init_sql)
        logger.info("Schema bootstrap applied")
    except Exception as exc:
        logger.warning("Schema bootstrap partial: %s", exc)

    if is_populated(settings):
        logger.info("PostGIS already has settlement data")
        return

    if not settings.auto_import_on_startup:
        logger.info("PostGIS empty — auto_import_on_startup=false, using GeoJSON fallback")
        return

    logger.info("PostGIS empty — importing bundled GeoJSON...")
    try:
        from scripts.import_geojson_to_postgis import import_all
        from scripts.compute_yearly_metrics import compute_and_store
        from db.repository import get_available_years

        count = import_all()
        if count > 0:
            for year in get_available_years(settings) or settings.analysis_years:
                compute_and_store(year)
            logger.info("Imported %d settlement features into PostGIS", count)
    except Exception as exc:
        logger.error("Auto-import failed: %s", exc)

    _seed_admin_user(settings)


def _seed_admin_user(settings) -> None:
    """Create default admin account if none exists."""
    try:
        with session_scope(settings) as db:
            existing = db.scalar(text("SELECT COUNT(*) FROM users WHERE role = 'admin'"))
            if existing and int(existing) > 0:
                return
            email = settings.admin_email.lower().strip()
            pwd_hash = hash_password(settings.admin_password)
            db.execute(
                text(
                    """
                    INSERT INTO users (email, password_hash, first_name, last_name, role, is_active)
                    VALUES (:email, :pwd, 'System', 'Administrator', 'admin', TRUE)
                    ON CONFLICT (email) DO NOTHING
                    """
                ),
                {"email": email, "pwd": pwd_hash},
            )
            logger.info("Default admin user seeded: %s", email)
    except Exception as exc:
        logger.warning("Admin seed skipped: %s", exc)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    bootstrap_database()
