# backend/routes/user_preferences.py

from __future__ import annotations

from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.db_config import get_async_db
from backend.security.auth import get_current_user
from backend.models.user import User

router = APIRouter(prefix="/users", tags=["User Preferences"])


class UserPreferences(BaseModel):
    language: Optional[str] = "en"
    theme: Optional[str] = "dark"
    timezone: Optional[str] = "UTC"
    notifications: Optional[Dict[str, bool]] = {
        "email": True,
        "push": True,
        "sms": False,
        "marketing": False
    }
    dashboard_layout: Optional[str] = "default"


class UserPreferencesResponse(BaseModel):
    preferences: UserPreferences


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


@router.get("/me/preferences", response_model=UserPreferencesResponse)
async def get_user_preferences(
    db: AsyncSession = Depends(get_async_db),
    current_user: Any = Depends(get_current_user),
) -> UserPreferencesResponse:
    """Get current user's preferences."""
    email = _extract_email(current_user)
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email not found in token.",
        )

    user = await _get_user_by_email(db, email)

    # Default preferences
    default_prefs = UserPreferences()

    # Get user preferences from JSONB field (assuming settings column exists)
    # For now, return defaults since we need to add settings column to User model
    user_prefs = getattr(user, 'settings', {}) or {}

    # Merge with defaults
    merged_prefs = UserPreferences(
        language=user_prefs.get('language', default_prefs.language),
        theme=user_prefs.get('theme', default_prefs.theme),
        timezone=user_prefs.get('timezone', default_prefs.timezone),
        notifications=user_prefs.get('notifications', default_prefs.notifications),
        dashboard_layout=user_prefs.get('dashboard_layout', default_prefs.dashboard_layout),
    )

    return UserPreferencesResponse(preferences=merged_prefs)


@router.put("/me/preferences", response_model=UserPreferencesResponse)
async def update_user_preferences(
    preferences: UserPreferences,
    db: AsyncSession = Depends(get_async_db),
    current_user: Any = Depends(get_current_user),
) -> UserPreferencesResponse:
    """Update current user's preferences."""
    email = _extract_email(current_user)
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email not found in token.",
        )

    user = await _get_user_by_email(db, email)

    # Update user settings (assuming settings column exists as JSONB)
    # For now, we'll store in a way that can be extended later
    settings_data = {
        'language': preferences.language,
        'theme': preferences.theme,
        'timezone': preferences.timezone,
        'notifications': preferences.notifications,
        'dashboard_layout': preferences.dashboard_layout,
    }

    # If User model has settings column, update it
    if hasattr(user, 'settings'):
        await db.execute(
            update(User)
            .where(User.id == user.id)
            .values(settings=settings_data)
        )
        await db.commit()
        await db.refresh(user)

    return UserPreferencesResponse(preferences=preferences)


