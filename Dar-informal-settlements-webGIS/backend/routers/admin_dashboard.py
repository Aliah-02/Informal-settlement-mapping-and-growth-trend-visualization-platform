"""Admin-only analytics dashboard."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from db.database import get_session
from db.models import User
from models.schemas import UserPublic
from routers.auth import require_admin
from services.activity_service import download_report, visitor_stats

router = APIRouter(prefix="/api/admin", tags=["Admin Dashboard"])


def _db_dep():
    SessionLocal = get_session()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.commit()
        db.close()


@router.get("/dashboard")
def admin_dashboard(
    _: Annotated[object, Depends(require_admin)],
    db: Session = Depends(_db_dep),
):
    stats = visitor_stats(db)
    users = db.scalars(select(User).order_by(User.created_at.desc()).limit(50)).all()
    return {
        **stats,
        "recent_users": [UserPublic.model_validate(u) for u in users],
    }


@router.get("/downloads")
def admin_downloads(
    _: Annotated[object, Depends(require_admin)],
    db: Session = Depends(_db_dep),
    limit: int = Query(200, ge=1, le=1000),
):
    return {"downloads": download_report(db, limit=limit)}
