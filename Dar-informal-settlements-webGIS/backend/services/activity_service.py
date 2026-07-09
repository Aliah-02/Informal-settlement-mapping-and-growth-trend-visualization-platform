"""Visitor presence, page visits, and download logging."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from db.models import DownloadLog, PageVisit, User, UserSession

LIVE_USER_WINDOW_MINUTES = 5


def touch_session(
    db: Session,
    session_token: str,
    *,
    user_id: int | None = None,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> UserSession:
    now = datetime.now(timezone.utc)
    row = db.scalar(select(UserSession).where(UserSession.session_token == session_token))
    if row is None:
        row = UserSession(
            session_token=session_token,
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            last_seen_at=now,
        )
        db.add(row)
    else:
        row.last_seen_at = now
        if user_id is not None:
            row.user_id = user_id
        if ip_address:
            row.ip_address = ip_address
        if user_agent:
            row.user_agent = user_agent
    db.flush()
    return row


def record_page_visit(
    db: Session,
    *,
    session_token: str,
    page_path: str,
    user_id: int | None = None,
    ip_address: str | None = None,
) -> None:
    now = datetime.now(timezone.utc)
    touch_session(db, session_token, user_id=user_id, ip_address=ip_address)
    db.add(
        PageVisit(
            session_token=session_token,
            page_path=page_path,
            user_id=user_id,
            ip_address=ip_address,
            visited_at=now,
        )
    )


def record_download(
    db: Session,
    *,
    report_type: str,
    report_label: str,
    session_token: str | None = None,
    user_id: int | None = None,
    user_email: str | None = None,
    ip_address: str | None = None,
) -> None:
    db.add(
        DownloadLog(
            user_id=user_id,
            user_email=user_email,
            session_token=session_token,
            report_type=report_type,
            report_label=report_label,
            ip_address=ip_address,
        )
    )


def visitor_stats(db: Session) -> dict[str, Any]:
    now = datetime.now(timezone.utc)
    day_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    month_start = day_start.replace(day=1)
    year_start = day_start.replace(month=1, day=1)
    live_cutoff = now - timedelta(minutes=LIVE_USER_WINDOW_MINUTES)

    daily = db.scalar(
        select(func.count(func.distinct(PageVisit.session_token))).where(
            PageVisit.visited_at >= day_start
        )
    ) or 0
    monthly = db.scalar(
        select(func.count(func.distinct(PageVisit.session_token))).where(
            PageVisit.visited_at >= month_start
        )
    ) or 0
    yearly = db.scalar(
        select(func.count(func.distinct(PageVisit.session_token))).where(
            PageVisit.visited_at >= year_start
        )
    ) or 0
    total_users = db.scalar(select(func.count(User.id))) or 0
    total_downloads = db.scalar(select(func.count(DownloadLog.id))) or 0
    live_users = db.scalar(
        select(func.count(UserSession.id)).where(UserSession.last_seen_at >= live_cutoff)
    ) or 0

    download_users = db.scalar(
        select(func.count(func.distinct(DownloadLog.user_id))).where(DownloadLog.user_id.isnot(None))
    ) or 0
    download_rate_pct = round((download_users / total_users * 100), 1) if total_users else 0.0

    return {
        "daily_visitors": daily,
        "monthly_visitors": monthly,
        "yearly_visitors": yearly,
        "live_users": live_users,
        "total_users_joined": total_users,
        "total_downloads": total_downloads,
        "download_rate_pct": download_rate_pct,
    }


def download_report(db: Session, limit: int = 200) -> list[dict[str, Any]]:
    rows = db.scalars(
        select(DownloadLog).order_by(DownloadLog.downloaded_at.desc()).limit(limit)
    ).all()
    return [
        {
            "id": r.id,
            "user_id": r.user_id,
            "user_email": r.user_email or "Guest",
            "report_type": r.report_type,
            "report_label": r.report_label,
            "ip_address": r.ip_address,
            "downloaded_at": r.downloaded_at.isoformat() if r.downloaded_at else None,
        }
        for r in rows
    ]
