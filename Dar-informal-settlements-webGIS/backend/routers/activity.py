"""Visitor tracking, heartbeat, and public stats."""

from __future__ import annotations

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Header, Request
from pydantic import BaseModel, Field
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from db.database import get_session, is_database_configured
from routers.auth import get_current_user_optional
from services.activity_service import record_page_visit, touch_session, visitor_stats

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/activity", tags=["Activity"])

_EMPTY_STATS = {
    "daily_visitors": 0,
    "monthly_visitors": 0,
    "yearly_visitors": 0,
    "live_users": 0,
    "total_users_joined": 0,
    "total_downloads": 0,
    "download_rate_pct": 0.0,
}


def _db_dep():
    SessionLocal = get_session()
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


class VisitRequest(BaseModel):
    page_path: str = Field(..., min_length=1, max_length=512)


@router.post("/visit")
def log_visit(
    body: VisitRequest,
    request: Request,
    x_session_token: Annotated[str | None, Header(alias="X-Session-Token")] = None,
    db: Session = Depends(_db_dep),
    user=Depends(get_current_user_optional),
):
    if not is_database_configured() or not x_session_token:
        return {"status": "skipped"}
    try:
        record_page_visit(
            db,
            session_token=x_session_token,
            page_path=body.page_path,
            user_id=user.id if user else None,
            ip_address=request.client.host if request.client else None,
        )
        return {"status": "recorded"}
    except SQLAlchemyError as exc:
        logger.warning("Visit tracking skipped: %s", exc)
        return {"status": "skipped"}


@router.post("/heartbeat")
def heartbeat(
    request: Request,
    x_session_token: Annotated[str | None, Header(alias="X-Session-Token")] = None,
    db: Session = Depends(_db_dep),
    user=Depends(get_current_user_optional),
):
    if not is_database_configured() or not x_session_token:
        return {"status": "ok"}
    try:
        touch_session(
            db,
            x_session_token,
            user_id=user.id if user else None,
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
        )
    except SQLAlchemyError as exc:
        logger.warning("Heartbeat skipped: %s", exc)
    return {"status": "ok"}


@router.get("/stats")
def public_stats(db: Session = Depends(_db_dep)):
    if not is_database_configured():
        return _EMPTY_STATS
    try:
        return visitor_stats(db)
    except SQLAlchemyError as exc:
        logger.warning("Stats unavailable: %s", exc)
        return _EMPTY_STATS
