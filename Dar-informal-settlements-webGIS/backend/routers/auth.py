"""User authentication and registration routes."""

from __future__ import annotations

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from config import Settings, get_settings
from db.database import get_session, is_database_configured
from db.models import User
from models.schemas import (
    AuthResponse,
    LoginRequest,
    SignupRequest,
    UserPublic,
)
from services.activity_service import touch_session
from services.auth_service import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/auth", tags=["Auth"])


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


def _safe_touch_session(db, request: Request, user_id: int) -> None:
    session_token = request.headers.get("X-Session-Token")
    if not session_token:
        return
    try:
        touch_session(
            db,
            session_token,
            user_id=user_id,
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
        )
    except Exception as exc:
        logger.warning("Session tracking skipped: %s", exc)


def get_current_user_optional(
    authorization: Annotated[str | None, Header()] = None,
    db: Session = Depends(_db_dep),
    settings: Settings = Depends(get_settings),
) -> User | None:
    if not authorization or not authorization.startswith("Bearer "):
        return None
    token = authorization[7:]
    payload = decode_access_token(token, settings)
    if not payload or not payload.get("sub"):
        return None
    user = db.scalar(select(User).where(User.email == payload["sub"]))
    if not user or not user.is_active:
        return None
    return user


def get_current_user(
    user: Annotated[User | None, Depends(get_current_user_optional)],
) -> User:
    if user is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user


def require_admin(user: Annotated[User, Depends(get_current_user)]) -> User:
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return user


@router.get("/status")
def auth_status(db: Session = Depends(_db_dep)):
    """Check whether auth tables and admin user are ready."""
    if not is_database_configured():
        return {"ready": False, "detail": "DATABASE_URL not configured on API server"}
    try:
        from sqlalchemy import func

        count = db.scalar(select(func.count()).select_from(User).where(User.role == "admin"))
        return {"ready": True, "admin_users": int(count or 0)}
    except SQLAlchemyError as exc:
        return {"ready": False, "detail": "Auth tables not ready — redeploy API"}


@router.post("/signup", response_model=AuthResponse)
def signup(body: SignupRequest, request: Request, db: Session = Depends(_db_dep)):
    if not is_database_configured():
        raise HTTPException(
            status_code=503,
            detail="Login requires PostgreSQL. Link DATABASE_URL on Render and redeploy.",
        )
    try:
        if body.password != body.confirm_password:
            raise HTTPException(status_code=400, detail="Passwords do not match")
        existing = db.scalar(select(User).where(User.email == body.email.lower()))
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")

        user = User(
            email=body.email.lower().strip(),
            password_hash=hash_password(body.password),
            first_name=body.first_name.strip(),
            last_name=body.last_name.strip(),
            mobile=body.mobile.strip() if body.mobile else None,
            company_name=body.company_name.strip() if body.company_name else None,
            role="user",
        )
        db.add(user)
        db.flush()

        token = create_access_token(user.email, user.role)
        _safe_touch_session(db, request, user.id)

        return AuthResponse(
            access_token=token,
            token_type="bearer",
            user=UserPublic.model_validate(user),
        )
    except HTTPException:
        raise
    except SQLAlchemyError as exc:
        logger.exception("Signup database error")
        raise HTTPException(
            status_code=503,
            detail="Auth database not ready. Redeploy the API after linking DATABASE_URL.",
        ) from exc


@router.post("/login", response_model=AuthResponse)
def login(body: LoginRequest, request: Request, db: Session = Depends(_db_dep)):
    if not is_database_configured():
        raise HTTPException(
            status_code=503,
            detail="Login requires PostgreSQL. Link DATABASE_URL on Render and redeploy.",
        )
    try:
        user = db.scalar(select(User).where(User.email == body.email.lower().strip()))
        if not user or not verify_password(body.password, user.password_hash):
            raise HTTPException(status_code=401, detail="Invalid email or password")
        if not user.is_active:
            raise HTTPException(status_code=403, detail="Account disabled")

        from datetime import datetime, timezone

        user.last_login_at = datetime.now(timezone.utc)
        token = create_access_token(user.email, user.role)
        _safe_touch_session(db, request, user.id)

        return AuthResponse(
            access_token=token,
            token_type="bearer",
            user=UserPublic.model_validate(user),
        )
    except HTTPException:
        raise
    except SQLAlchemyError as exc:
        logger.exception("Login database error")
        raise HTTPException(
            status_code=503,
            detail="Auth database not ready. Redeploy the API after linking DATABASE_URL.",
        ) from exc


@router.get("/me", response_model=UserPublic)
def me(user: Annotated[User, Depends(get_current_user)]):
    return UserPublic.model_validate(user)


@router.post("/logout")
def logout():
    return {"status": "ok", "message": "Logged out — remove token on client"}
