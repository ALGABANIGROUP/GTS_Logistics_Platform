# backend/routes/auth_extended.py

from __future__ import annotations

import os
import re
import hashlib
import hmac
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any, Optional, Dict, TYPE_CHECKING
from types import SimpleNamespace

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func

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
UNSAFE_TEXT_PATTERNS = ("%00", "\\x00", "../", "..\\")
ALLOWED_COUNTRY_CODES = {"CA", "US"}


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class RegisterRequest(BaseModel):
    email: EmailStr
    username: Optional[str] = Field(default=None, min_length=3, max_length=50)
    password: str = Field(..., min_length=8, max_length=128)
    full_name: Optional[str] = Field(None, max_length=200)
    role: Optional[str] = None
    company_name: Optional[str] = Field(default=None, max_length=255)
    country: Optional[str] = Field(default=None, max_length=100)
    phone_number: Optional[str] = Field(default=None, max_length=50)
    system_type: Optional[str] = Field(default=None, max_length=50)
    subscription_tier: Optional[str] = Field(default=None, max_length=50)

    model_config = ConfigDict(extra="ignore")


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


def _user_value(user: Any, field: str) -> Any:
    if isinstance(user, dict):
        return user.get(field)
    return getattr(user, field, None)


async def _load_reset_user_by_email(email: str, db: AsyncSession) -> Optional[Any]:
    result = await db.execute(
        text(
            """
            SELECT id, email, hashed_password, role, is_active
            FROM users
            WHERE lower(email) = lower(:email)
            LIMIT 1
            """
        ),
        {"email": str(email or "").strip().lower()},
    )
    row = result.mappings().first()
    if not row:
        return None
    return SimpleNamespace(
        id=int(row["id"]),
        email=row["email"],
        hashed_password=row["hashed_password"],
        role=row.get("role"),
        is_active=row.get("is_active"),
    )


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
        {"user_id": int(_user_value(user, "id"))},
    )
    await db.execute(
        text(
            """
            INSERT INTO password_reset_tokens (user_id, token_hash, expires_at)
            VALUES (:user_id, :token_hash, :expires_at)
            """
        ),
        {
            "user_id": int(_user_value(user, "id")),
            "token_hash": token_hash,
            "expires_at": expires_at,
        },
    )
    await db.commit()
    return token


async def _get_user_from_reset_token(token: str, db: AsyncSession) -> Any:
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

    user = await _load_reset_user_by_email_by_id(int(row["user_id"]), db)
    if not user:
        raise error

    return user


async def _load_reset_user_by_email_by_id(user_id: int, db: AsyncSession) -> Optional[Any]:
    result = await db.execute(
        text(
            """
            SELECT id, email, hashed_password, role, is_active
            FROM users
            WHERE id = :user_id
            LIMIT 1
            """
        ),
        {"user_id": int(user_id)},
    )
    row = result.mappings().first()
    if not row:
        return None
    return SimpleNamespace(
        id=int(row["id"]),
        email=row["email"],
        hashed_password=row["hashed_password"],
        role=row.get("role"),
        is_active=row.get("is_active"),
    )


def _build_reset_link(token: str) -> str:
    if "{token}" in FRONTEND_RESET_URL:
        return FRONTEND_RESET_URL.replace("{token}", token)
    if "?" in FRONTEND_RESET_URL:
        return f"{FRONTEND_RESET_URL}&token={token}"
    return f"{FRONTEND_RESET_URL}?token={token}"


def _send_reset_email(to_email: str, reset_link: str) -> None:
    try:
        from backend.services.email_dispatcher import dispatch_email_sync  # type: ignore
    except Exception:
        dispatch_email_sync = None  # type: ignore

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

    if dispatch_email_sync:
        dispatch_email_sync(
            bot_name="operations_manager",
            to_email=to_email,
            subject=subject,
            body=body,
            html=True,
            plain_text=f"Reset your password using this link: {reset_link}",
            audit_context={"category": "password_reset"},
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
        from backend.services.email_dispatcher import dispatch_email_sync  # type: ignore
    except Exception:
        dispatch_email_sync = None  # type: ignore

    subject = "Your password was changed"
    body = """<!DOCTYPE html>
<html>
  <body style="margin:0;padding:24px;font-family:Arial,sans-serif;background-color:#0b1220;color:#e2e8f0;">
    <h2 style="margin:0 0 12px;color:#ffffff;">Password changed</h2>
    <p style="margin:0 0 12px;">Your GTS account password was just changed.</p>
    <p style="margin:0;color:#cbd5e1;">If you did not perform this change, please contact support immediately.</p>
  </body>
</html>"""

    if dispatch_email_sync:
        dispatch_email_sync(
            bot_name="operations_manager",
            to_email=to_email,
            subject=subject,
            body=body,
            html=True,
            plain_text="Your GTS account password was changed.",
            audit_context={"category": "password_change_notice"},
        )
        return

    print("====================================")
    print("PASSWORD CHANGED EMAIL (fallback)")
    print(f"To:   {to_email}")
    print("====================================")


def _send_admin_reset_requested_email(target_email: str) -> None:
    try:
        from backend.services.email_dispatcher import dispatch_email_sync  # type: ignore
    except Exception:
        dispatch_email_sync = None  # type: ignore

    if not dispatch_email_sync:
        return

    subject = "Password reset requested"
    body = f"Password reset requested for account: {target_email}"
    dispatch_email_sync(
        bot_name="operations_manager",
        to_email=os.getenv("ADMIN_EMAIL") or PASSWORD_RESET_SENDER,
        subject=subject,
        body=body,
        html=False,
        audit_context={"category": "password_reset_admin_notice", "requested_email": target_email},
    )


def _password_policy_error(password: str) -> Optional[str]:
    if not re.match(PASSWORD_POLICY_REGEX, password or ""):
        return PASSWORD_POLICY_HINT
    return None


def _registration_error(field: str, message: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail={"field": field, "message": message},
    )


def _text_contains_unsafe_sequences(value: Optional[str]) -> bool:
    if not value:
        return False

    if any(ord(char) < 32 for char in value):
        return True

    lowered = value.lower()
    return any(pattern in lowered for pattern in UNSAFE_TEXT_PATTERNS)


def _registration_input_error(payload: RegisterRequest) -> Optional[HTTPException]:
    fields = {
        "email": payload.email,
        "username": payload.username,
        "full_name": payload.full_name,
        "company_name": payload.company_name,
        "country": payload.country,
        "phone_number": payload.phone_number,
        "system_type": payload.system_type,
        "subscription_tier": payload.subscription_tier,
    }

    for field, value in fields.items():
        if _text_contains_unsafe_sequences(value):
            return _registration_error(field, "Invalid characters are not allowed")

    return None


async def _create_registered_user(
    payload: RegisterRequest,
    db: AsyncSession,
) -> Any:
    email = payload.email.strip().lower()
    username = (payload.username or email.split("@")[0]).strip().lower()
    company_name = (payload.company_name or "").strip()
    country_code = (payload.country or "").strip().upper()

    if country_code not in ALLOWED_COUNTRY_CODES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Registration is currently available only for Canada and the United States.",
        )

    existing_email = await db.execute(select(UserModel).where(func.lower(UserModel.email) == email))
    if existing_email.scalar_one_or_none():
        raise _registration_error("email", "This email is already registered")

    existing_username = await db.execute(select(UserModel).where(func.lower(UserModel.username) == username))
    if existing_username.scalar_one_or_none():
        raise _registration_error("username", "Username is already taken")

    if company_name and hasattr(UserModel, "company"):
        existing_company = await db.execute(
            select(UserModel).where(func.lower(func.trim(UserModel.company)) == company_name.lower())
        )
        if existing_company.scalar_one_or_none():
            raise _registration_error("company_name", "This company name is already registered")

    hashed = get_password_hash(payload.password)
    user = UserModel(
        email=email,
        username=username,
        hashed_password=hashed,
        full_name=(payload.full_name or "").strip() or None,
        role=(payload.role or "user").strip() or "user",
        is_active=True,
    )

    if hasattr(user, "company"):
        setattr(user, "company", company_name or None)
    if hasattr(user, "country"):
        setattr(user, "country", country_code or None)
    if hasattr(user, "phone_number"):
        setattr(user, "phone_number", (payload.phone_number or "").strip() or None)
    if hasattr(user, "system_type"):
        setattr(user, "system_type", (payload.system_type or "").strip() or None)
    if hasattr(user, "subscription_tier"):
        setattr(user, "subscription_tier", (payload.subscription_tier or "").strip() or None)

    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


# ---------------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------------

router = APIRouter(prefix="/api/v1/auth", tags=["Auth – Extended"])


# ---------------------------------------------------------------------------
# Register
# ---------------------------------------------------------------------------

@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
)
async def register(
    payload: RegisterRequest,
    db: AsyncSession = Depends(get_db_async),
) -> Dict[str, Any]:
    input_error = _registration_input_error(payload)
    if input_error:
        raise input_error

    policy_error = _password_policy_error(payload.password)
    if policy_error:
        raise _registration_error("password", policy_error)

    try:
        user = await _create_registered_user(payload, db)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"field": "form", "message": "Registration failed"},
        ) from exc

    return {
        "ok": True,
        "message": "Registration successful",
        "user": {
            "id": int(getattr(user, "id")),
            "email": getattr(user, "email"),
            "username": getattr(user, "username"),
            "full_name": getattr(user, "full_name", None),
            "company_name": getattr(user, "company", None),
        },
    }


@router.get("/check-email")
async def check_email(email: EmailStr, db: AsyncSession = Depends(get_db_async)) -> Dict[str, bool]:
    normalized = str(email).strip().lower()
    result = await db.execute(select(UserModel.id).where(func.lower(UserModel.email) == normalized))
    return {"exists": result.scalar_one_or_none() is not None}


@router.get("/check-company")
async def check_company(company_name: str, db: AsyncSession = Depends(get_db_async)) -> Dict[str, bool]:
    normalized = (company_name or "").strip().lower()
    if not normalized or not hasattr(UserModel, "company"):
        return {"exists": False}

    result = await db.execute(
        select(UserModel.id).where(func.lower(func.trim(UserModel.company)) == normalized)
    )
    return {"exists": result.scalar_one_or_none() is not None}


@router.post(
    "/register-legacy",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register_user(
    payload: RegisterRequest,
    db: AsyncSession = Depends(get_db_async),
) -> RegisterResponse:
    input_error = _registration_input_error(payload)
    if input_error:
        raise input_error

    user = await _create_registered_user(payload, db)

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
    user = await _load_reset_user_by_email(payload.email.lower(), db)

    if not user:
        return SimpleMessage(ok=True, message="If account exists, reset link was sent.")

    role = str(_user_value(user, "role") or "").lower()
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

    current_hash = _user_value(user, "hashed_password")
    if current_hash and verify_password(payload.new_password, current_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be different from the current password",
        )

    new_hash = get_password_hash(payload.new_password)
    await db.execute(
        text(
            """
            UPDATE users
            SET hashed_password = :new_hash
            WHERE id = :user_id
            """
        ),
        {
            "new_hash": new_hash,
            "user_id": int(_user_value(user, "id")),
        },
    )

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
        _send_password_changed_email(str(_user_value(user, "email") or ""))
    except Exception:
        pass
    if log_audit_action:
        try:
            await log_audit_action(
                request_id=None,
                action="password_reset",
                actor=str(_user_value(user, "email") or "unknown"),
                details={"user_id": _user_value(user, "id")},
                session=db,
            )
        except Exception:
            pass

    return SimpleMessage(ok=True, message="Password has been reset successfully.")
