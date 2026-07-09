"""Visitor tracking, heartbeat, and public stats."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Header, Request
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from db.database import get_session
from routers.auth import get_current_user_optional
from services.activity_service import record_page_visit, touch_session, visitor_stats

router = APIRouter(prefix="/api/activity", tags=["Activity"])


def _db_dep():
    SessionLocal = get_session()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.commit()
        db.close()


class VisitRequest(BaseModel):
    page_path: str = Field(..., min_length=1, max_length=512)


@router.post("/visit")
def log_visit(
    body: VisitRequest,
    request: Request,
    x_session_token: Annotated[str, Header(alias="X-Session-Token")],
    db: Session = Depends(_db_dep),
    user=Depends(get_current_user_optional),
):
    record_page_visit(
        db,
        session_token=x_session_token,
        page_path=body.page_path,
        user_id=user.id if user else None,
        ip_address=request.client.host if request.client else None,
    )
    return {"status": "recorded"}


@router.post("/heartbeat")
def heartbeat(
    request: Request,
    x_session_token: Annotated[str, Header(alias="X-Session-Token")],
    db: Session = Depends(_db_dep),
    user=Depends(get_current_user_optional),
):
    touch_session(
        db,
        x_session_token,
        user_id=user.id if user else None,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    return {"status": "ok"}


@router.get("/stats")
def public_stats(db: Session = Depends(_db_dep)):
    return visitor_stats(db)
