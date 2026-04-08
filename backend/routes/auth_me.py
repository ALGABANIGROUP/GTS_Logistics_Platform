from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from datetime import datetime, timezone, timedelta

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from backend.database.config import get_db_async
from backend.auth import get_password_hash, verify_password
from backend.security.access_context import build_auth_me_payload
from backend.security.auth import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    _decode_token,
    _hash_refresh_token,
    _issue_refresh_token,
    _rotate_refresh_token,
    get_current_user,
    create_access_token,
)
log = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Auth"])


class ChangePasswordPayload(BaseModel):
    current_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=8)


@router.post("/token")
async def auth_token_compat(
    request: Request,
    db: AsyncSession = Depends(get_db_async),
) -> Dict[str, Any]:
    """
    Compatibility login endpoint.

    The main login implementation lives in backend.routes.auth, but that router has
    historically been sensitive to optional imports during startup. This wrapper keeps
    `/api/v1/auth/token` available from the always-mounted auth router.
    """
    content_type = request.headers.get("content-type", "").lower()
    email = None
    password = None

    if "application/x-www-form-urlencoded" in content_type or "multipart/form-data" in content_type:
        form = await request.form()
        email = form.get("username") or form.get("email")
        password = form.get("password")
    else:
        payload = {}
        try:
            payload = await request.json()
        except Exception:
            try:
                form = await request.form()
                email = form.get("username") or form.get("email")
                password = form.get("password")
            except Exception:
                payload = {}
        if not email:
            email = payload.get("email") or payload.get("username")
        if not password:
            password = payload.get("password")

    if not email or not password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email and password are required")

    # Ensure email and password are strings before cleaning
    if hasattr(email, "filename") or hasattr(password, "filename"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid email or password type")
    if not isinstance(password, str):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid password type")
    email_clean = str(email).strip().lower()
    log.info("[auth_me] login attempt for email=%s", email_clean)

    try:
        login = email_clean
        row = await db.execute(
            text(
                """
                SELECT id, email, full_name, role, is_active,
                       COALESCE(token_version, 0) AS token_version,
                      hashed_password AS password_hash
                FROM users
                WHERE lower(email) = :login
                LIMIT 1
                """
            ),
            {"login": login},
        )
        user = row.mappings().first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        password_hash = user.get("password_hash")
        if not password_hash or not verify_password(password, password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if user.get("is_active") is False:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Account is not active",
            )

        access_token = create_access_token(
            data={
                "sub": str(user.get("id")),
                "email": user.get("email"),
                "role": user.get("role") or "user",
                "tv": int(user.get("token_version", 0) or 0),
            }
        )

        refresh_token = await _issue_refresh_token(db, int(user.get("id")))

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "user": {
                "id": user.get("id"),
                "email": user.get("email"),
                "full_name": user.get("full_name"),
                "role": user.get("role"),
            },
        }
    except HTTPException:
        raise
    except Exception as e:
        log.error("[auth_me] token compatibility login failed: %s", e, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Login is temporarily unavailable",
        ) from e


@router.get("/me")
async def auth_me(
    request: Request,
    db: AsyncSession = Depends(get_db_async),
    claims: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    logger = logging.getLogger(__name__)
    logger.info("🔍 /auth/me called for user: %s", claims.get("id"))
    logger.info("🔍 Raw current_user: %s", claims)
    role = claims.get("effective_role") or claims.get("role")
    logger.info("🔍 Role from token: %s", role)
    try:
        payload = await build_auth_me_payload(request, db, claims)
        user_payload = payload.get("user") or {}
        logger.info(
            "✅ /auth/me success - role in payload: %s",
            user_payload.get("role"),
        )
        log.info(
            "[auth_me] success user_id=%s role=%s effective_role=%s db_role=%s token_role=%s",
            user_payload.get("id"),
            user_payload.get("role"),
            user_payload.get("effective_role"),
            user_payload.get("db_role"),
            user_payload.get("token_role"),
        )
        return {"ok": True, **payload}
    except HTTPException:
        raise
    except Exception as e:
        logger.error("❌ /auth/me failed: %s", e, exc_info=True)
        log.error("[auth_me] build_auth_me_payload failed: %s", e, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Auth context is temporarily unavailable",
        ) from e


@router.post("/change-password")
async def change_password(
    payload: ChangePasswordPayload,
    db: AsyncSession = Depends(get_db_async),
    claims: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    email = str(claims.get("email") or "").strip().lower()
    if not email:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    current_hash = getattr(user, "hashed_password", None) or getattr(user, "password_hash", None)
    if not current_hash:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="User password hash is missing",
        )

    if not verify_password(payload.current_password, current_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Current password is incorrect")

    if verify_password(payload.new_password, current_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be different from the current password",
        )

    new_hash = get_password_hash(payload.new_password)
    if hasattr(user, "hashed_password"):
        setattr(user, "hashed_password", new_hash)
    if hasattr(user, "password_hash"):
        setattr(user, "password_hash", new_hash)

    now = datetime.now(timezone.utc)
    if hasattr(user, "password_changed_at"):
        setattr(user, "password_changed_at", now)
    if hasattr(user, "token_version"):
        setattr(user, "token_version", int(getattr(user, "token_version", 0) or 0) + 1)

    db.add(user)
    await db.commit()

    return {"ok": True, "message": "Password changed successfully"}


@router.post("/refresh")
async def auth_refresh(
    request: Request,
    db: AsyncSession = Depends(get_db_async),
) -> Dict[str, Any]:
    """Refresh access token using refresh token.
    
    Expected JSON body:
    {
        "refresh_token": "eyJ..."
    }
    """
    try:
        body = await request.json()
    except Exception as e:
        log.error(f"Failed to parse JSON: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid JSON body",
        ) from e
    
    refresh_token = body.get("refresh_token")
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="refresh_token is required",
        )
    
    try:
        # Refresh tokens are opaque DB-backed secrets only.
        # Reject JWT-shaped tokens so access tokens cannot be reused here.
        if refresh_token.count(".") == 2:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="JWT access tokens cannot be used as refresh tokens",
            )

        token_hash = _hash_refresh_token(refresh_token)
        result = await db.execute(
            text(
                """
                SELECT id, user_id, expires_at, revoked_at
                FROM refresh_tokens
                WHERE token_hash = :token_hash
                LIMIT 1
                """
            ),
            {"token_hash": token_hash},
        )
        rt_obj = result.mappings().first()

        if not rt_obj:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

        now = datetime.now(timezone.utc)
        if rt_obj.get("revoked_at") is not None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token revoked")

        if rt_obj.get("expires_at") and rt_obj.get("expires_at") < now:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token expired")

        user_row = await db.execute(
            text(
                """
                SELECT id, email, role, is_active, COALESCE(token_version, 0) AS token_version
                FROM users
                WHERE id = :user_id
                LIMIT 1
                """
            ),
            {"user_id": int(rt_obj.get("user_id"))},
        )
        user = user_row.mappings().first()
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

        if not user.get("is_active", True):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User not found or inactive")

        new_access_token = create_access_token(
            subject=user.get("id"),
            email=user.get("email"),
            role=user.get("role"),
            token_version=int(user.get("token_version", 0) or 0),
        )
        new_refresh_token = await _rotate_refresh_token(db, old_obj=rt_obj)

        log.info("Refresh token used for user %s", user.get("id"))

        return {
            "ok": True,
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer",
            "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # seconds
        }
    except HTTPException as exc:
        raise exc
    except Exception as e:
        log.error(f"Refresh token error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token refresh failed",
        ) from e
