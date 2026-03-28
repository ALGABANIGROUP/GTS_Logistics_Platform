from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Optional
from types import SimpleNamespace

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel, EmailStr
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession
from backend.database.config import get_db_async
from backend.config import settings
from backend.security.auth import get_password_hash
from backend.routes.auth_extended import (
    _build_reset_link,
    _create_password_reset_token,
    _get_user_from_reset_token,
)
from backend.models.user import User as UserModel
from backend.services.email_dispatcher import dispatch_email

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

    async def _dispatch_reset(recipient_email: str, reset_link: str) -> None:
        subject = "GTS Password Reset"
        body = f"""<!DOCTYPE html>
<html>
  <body style="margin:0;padding:24px;font-family:Arial,sans-serif;background-color:#0b1220;color:#e2e8f0;">
    <h2 style="margin:0 0 12px;color:#ffffff;">Reset your password</h2>
    <p style="margin:0 0 16px;">We received a request to reset your password.</p>
    <p style="margin:0 0 20px;">
      <a href="{reset_link}" style="background:#2563eb;color:#ffffff;text-decoration:none;padding:10px 16px;border-radius:6px;display:inline-block;">
        Reset Password
      </a>
    </p>
    <p style="margin:0 0 8px;color:#cbd5e1;">This link expires in 5 minutes and can only be used once.</p>
    <p style="margin:0;color:#cbd5e1;">If you did not request this, you can ignore this email.</p>
  </body>
</html>"""
        await dispatch_email(
            bot_name="operations_manager",
            to_email=recipient_email,
            subject=subject,
            body=body,
            html=True,
            plain_text=f"Reset your password using this link: {reset_link}",
            audit_context={"category": "password_reset"},
        )

    async def _send_admin_reset_notice(requested_email: str) -> None:
        await dispatch_email(
            bot_name="operations_manager",
            to_email=settings.ADMIN_EMAIL or settings.SMTP_FROM or "admin@gabanilogistics.com",
            subject="Password reset requested",
            body=f"A password reset was requested for user: {requested_email}",
            html=False,
            audit_context={"category": "password_reset_admin_notice", "requested_email": requested_email},
        )

    background.add_task(_dispatch_reset, email, link)
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
