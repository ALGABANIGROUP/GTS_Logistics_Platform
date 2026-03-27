from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel, EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.database.config import get_db_async
from backend.security.auth import get_password_hash
from backend.routes.auth_extended import (
    _build_reset_link,
    _create_password_reset_token,
    _get_user_from_reset_token,
    _send_reset_email,
)
from backend.models.user import User as UserModel
from backend.utils.email_utils import send_admin_notification

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


class ForgotPasswordPayload(BaseModel):
    email: EmailStr


async def _load_user(email: str, db: AsyncSession) -> UserModel | None:
    stmt = select(UserModel).where(UserModel.email == email.strip().lower())
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


@router.post("/forgot-password")
async def forgot_password(
    payload: ForgotPasswordPayload,
    background: BackgroundTasks,
    db: AsyncSession = Depends(get_db_async),
) -> dict[str, str]:
    email = payload.email.strip().lower()
    user = await _load_user(email, db)
    if not user:
        return {"message": "If this email exists, a reset link has been sent."}

    token = await _create_password_reset_token(user, db)
    link = _build_reset_link(token)

    def _send_admin_reset_notice(requested_email: str) -> None:
        subject = "Password reset requested"
        body = f"A password reset was requested for user: {requested_email}"
        send_admin_notification(subject=subject, body=body, html=False, bot_name="service")

    background.add_task(_send_reset_email, email, link)
    background.add_task(_send_admin_reset_notice, email)
    return {"message": "If this email exists, a reset link has been sent."}


@router.post("/reset-password-legacy", include_in_schema=False)
async def reset_password(
    token: str,
    new_password: str,
    db: AsyncSession = Depends(get_db_async),
) -> dict[str, str]:
    if not token or not new_password:
        raise HTTPException(status_code=400, detail="Token and new password are required")

    user = await _get_user_from_reset_token(token, db)
    hashed = get_password_hash(new_password)
    setattr(user, "hashed_password", hashed)
    db.add(user)
    await db.commit()
    return {"message": "Password has been reset successfully."}
