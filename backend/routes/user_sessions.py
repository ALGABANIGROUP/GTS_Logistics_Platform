# backend/routes/user_sessions.py

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, List, Optional, Dict

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.db_config import get_async_db
from backend.security.auth import get_current_user
from backend.models.user import User
from backend.models.refresh_token import RefreshToken

router = APIRouter(prefix="/auth", tags=["User Sessions"])


class SessionInfo(BaseModel):
    id: int
    device_info: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    created_at: datetime
    expires_at: datetime
    is_current_session: bool = False
    location: Optional[str] = None


class SessionsResponse(BaseModel):
    sessions: List[SessionInfo]


def _extract_email(current_user: Any) -> Optional[str]:
    if isinstance(current_user, dict):
        return current_user.get("email")
    return getattr(current_user, "email", None)


async def _get_user_by_email(db: AsyncSession, email: str) -> User:
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user


def _extract_device_info(user_agent: Optional[str]) -> str:
    """Extract basic device info from user agent string."""
    if not user_agent:
        return "Unknown Device"

    # Simple device detection
    if "Mobile" in user_agent or "Android" in user_agent or "iPhone" in user_agent:
        return "Mobile Device"
    elif "Tablet" in user_agent or "iPad" in user_agent:
        return "Tablet"
    else:
        return "Desktop Computer"


def _extract_location_from_ip(ip_address: Optional[str]) -> Optional[str]:
    """Extract location info from IP (simplified - would need geoip service)."""
    if not ip_address or ip_address in ["127.0.0.1", "::1", "localhost"]:
        return "Local Network"
    # In a real implementation, you'd use a geoip service
    return f"IP: {ip_address}"


@router.get("/sessions", response_model=SessionsResponse)
async def get_user_sessions(
    db: AsyncSession = Depends(get_async_db),
    current_user: Any = Depends(get_current_user),
) -> SessionsResponse:
    """Get all active sessions for the current user."""
    email = _extract_email(current_user)
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email not found in token.",
        )

    user = await _get_user_by_email(db, email)

    # Get all active (non-revoked, non-expired) refresh tokens
    now = datetime.now(timezone.utc)
    result = await db.execute(
        select(RefreshToken)
        .where(
            RefreshToken.user_id == user.id,
            RefreshToken.revoked_at.is_(None),
            RefreshToken.expires_at > now
        )
        .order_by(RefreshToken.created_at.desc())
    )

    tokens = result.scalars().all()

    sessions = []
    for token in tokens:
        # For preview purposes, we'll create seed device/location info
        # In a real implementation, you'd store this in the token or a separate session table
        device_info = _extract_device_info(None)  # Would need to be stored
        location = _extract_location_from_ip(None)  # Would need to be stored

        session = SessionInfo(
            id=token.id,
            device_info=device_info,
            ip_address=None,  # Would need to be stored
            user_agent=None,  # Would need to be stored
            created_at=token.created_at,
            expires_at=token.expires_at,
            is_current_session=False,  # Would need logic to detect current session
            location=location
        )
        sessions.append(session)

    # Mark the most recent session as current (simplified logic)
    if sessions:
        sessions[0].is_current_session = True

    return SessionsResponse(sessions=sessions)


@router.delete("/sessions/{session_id}")
async def revoke_session(
    session_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: Any = Depends(get_current_user),
) -> Dict[str, str]:
    """Revoke a specific session (refresh token)."""
    email = _extract_email(current_user)
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email not found in token.",
        )

    user = await _get_user_by_email(db, email)

    # Find the token and ensure it belongs to the user
    result = await db.execute(
        select(RefreshToken)
        .where(
            RefreshToken.id == session_id,
            RefreshToken.user_id == user.id,
            RefreshToken.revoked_at.is_(None)
        )
    )

    token = result.scalar_one_or_none()
    if not token:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found or already revoked",
        )

    # Revoke the token
    await db.execute(
        update(RefreshToken)
        .where(RefreshToken.id == session_id)
        .values(revoked_at=datetime.now(timezone.utc))
    )

    await db.commit()

    return {"message": "Session revoked successfully"}


