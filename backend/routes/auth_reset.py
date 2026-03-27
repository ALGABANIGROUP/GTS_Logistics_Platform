from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Optional
from types import SimpleNamespace

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel, EmailStr
from sqlalchemy import select, text
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
    result = await db.execute(
        text(
            """
            SELECT id, email, hashed_password
            FROM users
            WHERE lower(email) = lower(:email)
            LIMIT 1
            """
        ),
        {"email": email.strip().lower()},
    )
    row = result.mappings().first()
    if not row:
        return None
    return SimpleNamespace(
        id=int(row["id"]),
        email=row["email"],
        hashed_password=row.get("hashed_password"),
    )  # type: ignore[return-value]


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
    await db.execute(
        text(
            """
            UPDATE users
            SET hashed_password = :hashed_password
            WHERE id = :user_id
            """
        ),
        {
            "hashed_password": hashed,
            "user_id": int(getattr(user, "id")),
        },
    )
    await db.commit()
    return {"message": "Password has been reset successfully."}
