# backend/routes/auth_extended.py

from __future__ import annotations

import os
import re
import hashlib
import hmac
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any, Optional, Dict, TYPE_CHECKING

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

# ---------------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------------

try:
    from backend.database.config import get_db_async
except Exception:
    from backend.database.config import get_db_async  # type: ignore

try:
    from backend.security.auth import (
        get_password_hash,
        verify_password,
        get_user_by_login,
        JWT_SECRET,
    )
except Exception:
    from backend.security.auth import (  # type: ignore
        get_password_hash,
        verify_password,
        get_user_by_login,
        JWT_SECRET,
    )

try:
    from backend.services.portal_requests_store import log_audit_action  # type: ignore
except Exception:
    log_audit_action = None  # type: ignore

# ORM model import with TYPE_CHECKING for Pylance
if TYPE_CHECKING:
    from backend.models.user import User as UserModel
else:
    try:
        from backend.models.user import User as UserModel  # type: ignore
    except Exception:
        try:
            from backend.database.models import User as UserModel  # type: ignore
        except Exception:
            class UserModel:  # type: ignore
                id: int
                email: str
                username: str
                hashed_password: str
                role: str
                is_active: bool


# ---------------------------------------------------------------------------
# Settings
# ---------------------------------------------------------------------------

PASSWORD_RESET_EXPIRE_MINUTES = int(os.getenv("PASSWORD_RESET_EXPIRE_MINUTES", "5"))
PASSWORD_RESET_SENDER = (
    os.getenv("PASSWORD_RESET_SENDER")
    or os.getenv("MAIL_FROM")
    or os.getenv("SMTP_FROM")
    or "no-reply@gabanilogistics.com"
)
PASSWORD_RESET_TOKEN_SECRET = os.getenv("PASSWORD_RESET_TOKEN_SECRET") or JWT_SECRET
FRONTEND_RESET_URL = (
    os.getenv("FRONTEND_RESET_URL")
    or os.getenv("FRONTEND_URL")
    or "https://gtsdispatcher.com/#token={token}"
)
PASSWORD_POLICY_REGEX = os.getenv(
    "PASSWORD_POLICY_REGEX",
    r"^(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()_+=\[\]{};':\",.<>/?\\|`~\-]).{8,}$",
)
PASSWORD_POLICY_HINT = (
    "Password must be at least 8 characters and include an uppercase letter, a number, and a symbol."
)


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class RegisterRequest(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8, max_length=128)
    full_name: Optional[str] = Field(None, max_length=200)
    role: Optional[str] = None


class RegisterResponse(BaseModel):
    id: int
    email: EmailStr
    username: str
    role: str
    is_active: bool


class RequestResetPayload(BaseModel):
    email: EmailStr


class ResetPasswordPayload(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8, max_length=128)


class SimpleMessage(BaseModel):
    ok: bool
    message: str


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

_reset_table_initialized = False


async def _ensure_reset_table(db: AsyncSession) -> None:
    global _reset_table_initialized
    if _reset_table_initialized:
        return

    await db.execute(
        text(
            """
            CREATE TABLE IF NOT EXISTS password_reset_tokens (
                id BIGSERIAL PRIMARY KEY,
                user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                token_hash TEXT NOT NULL UNIQUE,
                expires_at TIMESTAMPTZ NOT NULL,
                used_at TIMESTAMPTZ,
                created_at TIMESTAMPTZ DEFAULT NOW()
            );
            """
        )
    )
    await db.execute(
        text(
            """
            CREATE INDEX IF NOT EXISTS idx_password_reset_tokens_user
            ON password_reset_tokens(user_id);
            """
        )
    )
    await db.commit()
    _reset_table_initialized = True


def _hash_reset_token(token: str) -> str:
    key = PASSWORD_RESET_TOKEN_SECRET.encode("utf-8")
    msg = token.encode("utf-8")
    return hmac.new(key, msg, hashlib.sha256).hexdigest()


async def _create_password_reset_token(user: UserModel, db: AsyncSession) -> str:
    await _ensure_reset_table(db)

    token = secrets.token_urlsafe(16)
    token_hash = _hash_reset_token(token)
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=PASSWORD_RESET_EXPIRE_MINUTES)

    await db.execute(
        text(
            """
            UPDATE password_reset_tokens
            SET used_at = NOW()
            WHERE user_id = :user_id AND used_at IS NULL
            """
        ),
        {"user_id": int(getattr(user, "id"))},
    )
    await db.execute(
        text(
            """
            INSERT INTO password_reset_tokens (user_id, token_hash, expires_at)
            VALUES (:user_id, :token_hash, :expires_at)
            """
        ),
        {
            "user_id": int(getattr(user, "id")),
            "token_hash": token_hash,
            "expires_at": expires_at,
        },
    )
    await db.commit()
    return token


async def _get_user_from_reset_token(token: str, db: AsyncSession) -> UserModel:
    error = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Invalid or expired reset token",
    )
    await _ensure_reset_table(db)

    token_hash = _hash_reset_token(token)
    result = await db.execute(
        text(
            """
            SELECT user_id, expires_at, used_at
            FROM password_reset_tokens
            WHERE token_hash = :token_hash
            LIMIT 1
            """
        ),
        {"token_hash": token_hash},
    )
    row = result.mappings().first()
    if not row:
        raise error

    if row["used_at"] is not None:
        raise error

    if row["expires_at"] <= datetime.now(timezone.utc):
        raise error

    stmt = select(UserModel).where(UserModel.id == int(row["user_id"]))  # type: ignore[arg-type]
    user = (await db.execute(stmt)).scalar_one_or_none()
    if not user:
        raise error

    return user


def _build_reset_link(token: str) -> str:
    if "{token}" in FRONTEND_RESET_URL:
        return FRONTEND_RESET_URL.replace("{token}", token)
    if "?" in FRONTEND_RESET_URL:
        return f"{FRONTEND_RESET_URL}&token={token}"
    return f"{FRONTEND_RESET_URL}?token={token}"


def _send_reset_email(to_email: str, reset_link: str) -> None:
    try:
        from backend.utils.email_utils import send_email  # type: ignore
    except Exception:
        try:
            from utils.email_utils import send_email  # type: ignore
        except Exception:
            send_email = None  # type: ignore

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

    if send_email:
        send_email(
            subject=subject,
            body=body,
            to=[to_email],
            html=True,
            from_email=PASSWORD_RESET_SENDER,
        )
        return

    safe_link = reset_link.split("?", 1)[0].split("#", 1)[0]
    print("====================================")
    print("PASSWORD RESET EMAIL (fallback)")
    print(f"To:   {to_email}")
    print(f"Link: {safe_link}")
    print("====================================")


def _send_password_changed_email(to_email: str) -> None:
    try:
        from backend.utils.email_utils import send_email  # type: ignore
    except Exception:
        try:
            from utils.email_utils import send_email  # type: ignore
        except Exception:
            send_email = None  # type: ignore

    subject = "Your password was changed"
    body = """<!DOCTYPE html>
<html>
  <body style="margin:0;padding:24px;font-family:Arial,sans-serif;background-color:#0b1220;color:#e2e8f0;">
    <h2 style="margin:0 0 12px;color:#ffffff;">Password changed</h2>
    <p style="margin:0 0 12px;">Your GTS account password was just changed.</p>
    <p style="margin:0;color:#cbd5e1;">If you did not perform this change, please contact support immediately.</p>
  </body>
</html>"""

    if send_email:
        send_email(
            subject=subject,
            body=body,
            to=[to_email],
            html=True,
            from_email=PASSWORD_RESET_SENDER,
        )
        return

    print("====================================")
    print("PASSWORD CHANGED EMAIL (fallback)")
    print(f"To:   {to_email}")
    print("====================================")


def _send_admin_reset_requested_email(target_email: str) -> None:
    try:
        from backend.utils.email_utils import send_admin_notification  # type: ignore
    except Exception:
        try:
            from utils.email_utils import send_admin_notification  # type: ignore
        except Exception:
            send_admin_notification = None  # type: ignore

    if not send_admin_notification:
        return

    subject = "Password reset requested"
    body = f"Password reset requested for account: {target_email}"
    send_admin_notification(subject=subject, body=body, html=False, bot_name="service")


def _password_policy_error(password: str) -> Optional[str]:
    if not re.match(PASSWORD_POLICY_REGEX, password or ""):
        return PASSWORD_POLICY_HINT
    return None


# ---------------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------------

router = APIRouter(prefix="/api/v1/auth", tags=["Auth – Extended"])


# ---------------------------------------------------------------------------
# Register
# ---------------------------------------------------------------------------

@router.post(
    "/register-legacy",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register_user(
    payload: RegisterRequest,
    db: AsyncSession = Depends(get_db_async),
) -> RegisterResponse:

    email = payload.email.strip().lower()
    username = payload.username.strip().lower()

    existing_email = await get_user_by_login(db, email)
    existing_username = await get_user_by_login(db, username)

    if existing_email or existing_username:
        raise HTTPException(
            status_code=400,
            detail="User with this email or username already exists",
        )

    hashed = get_password_hash(payload.password)
    role = (payload.role or "customer").strip() or "customer"

    kwargs: Dict[str, Any] = {
        "email": email,
        "username": username,
        "hashed_password": hashed,
        "role": role,
        "is_active": True,
    }

    if hasattr(UserModel, "full_name") and payload.full_name:
        kwargs["full_name"] = payload.full_name

    user = UserModel(**kwargs)  # type: ignore[arg-type]
    db.add(user)
    await db.commit()
    await db.refresh(user)

    return RegisterResponse(
        id=int(getattr(user, "id")),
        email=getattr(user, "email"),
        username=getattr(user, "username"),
        role=getattr(user, "role"),
        is_active=bool(getattr(user, "is_active")),
    )


# ---------------------------------------------------------------------------
# Request password reset
# ---------------------------------------------------------------------------

@router.post(
    "/request-reset",
    response_model=SimpleMessage,
)
async def request_reset(
    payload: RequestResetPayload,
    background: BackgroundTasks,
    db: AsyncSession = Depends(get_db_async),
) -> SimpleMessage:
    user = await get_user_by_login(db, payload.email.lower())

    if not user:
        return SimpleMessage(ok=True, message="If account exists, reset link was sent.")

    role = str(getattr(user, "role", "")).lower()
    if role not in ("admin", "super_admin"):
        return SimpleMessage(ok=True, message="If account exists, reset link was sent.")

    token = await _create_password_reset_token(user, db)
    link = _build_reset_link(token)

    background.add_task(_send_reset_email, payload.email, link)
    background.add_task(_send_admin_reset_requested_email, payload.email)

    return SimpleMessage(ok=True, message="If account exists, reset link was sent.")


# ---------------------------------------------------------------------------
# Reset password
# ---------------------------------------------------------------------------

@router.post(
    "/reset-password",
    response_model=SimpleMessage,
)
async def reset_password(
    payload: ResetPasswordPayload,
    db: AsyncSession = Depends(get_db_async),
) -> SimpleMessage:
    policy_error = _password_policy_error(payload.new_password)
    if policy_error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=policy_error)

    user = await _get_user_from_reset_token(payload.token, db)

    current_hash = getattr(user, "hashed_password", None)
    if current_hash and verify_password(payload.new_password, current_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be different from the current password",
        )

    new_hash = get_password_hash(payload.new_password)
    setattr(user, "hashed_password", new_hash)

    db.add(user)

    token_hash = _hash_reset_token(payload.token)
    result = await db.execute(
        text(
            """
            UPDATE password_reset_tokens
            SET used_at = NOW()
            WHERE token_hash = :token_hash AND used_at IS NULL
            """
        ),
        {"token_hash": token_hash},
    )
    if result.rowcount == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token",
        )

    await db.commit()
    try:
        _send_password_changed_email(getattr(user, "email"))
    except Exception:
        pass
    if log_audit_action:
        try:
            await log_audit_action(
                request_id=None,
                action="password_reset",
                actor=str(getattr(user, "email", "unknown")),
                details={"user_id": getattr(user, "id", None)},
                session=db,
            )
        except Exception:
            pass

    return SimpleMessage(ok=True, message="Password has been reset successfully.")
