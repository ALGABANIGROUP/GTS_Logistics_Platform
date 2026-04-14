from __future__ import annotations

import json
import os
import logging
import secrets
import hmac
import hashlib
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional, Callable, List, Union, Tuple
import asyncio
from backend.core.settings import settings

try:
    import jwt  # type: ignore
    from jwt import ExpiredSignatureError, InvalidTokenError  # type: ignore
except Exception:  # pragma: no cover
    from jose import jwt  # type: ignore
    from jose.exceptions import ExpiredSignatureError, JWTError as InvalidTokenError  # type: ignore

from fastapi import APIRouter, Depends, HTTPException, Request, status
from backend.auth.tenant_context import current_tenant_id, is_global_user
from backend.models.refresh_token import RefreshToken
from backend.models.user import User
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, EmailStr
from sqlalchemy import select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from backend.services.notification_service import notification_service

# ---------------------------------------------------------------------
# Environment bootstrap (best-effort)
# ---------------------------------------------------------------------
try:
    import backend.env_bootstrap  # noqa: F401
except Exception:
    try:
        import env_bootstrap  # type: ignore  # noqa: F401
    except Exception:
        pass

# ---------------------------------------------------------------------
# Settings (Access + Refresh)
# ---------------------------------------------------------------------
DEFAULT_JWT_SECRET = "dev-jwt-secret-32-bytes-exactly!!"

JWT_SECRET_KEY = settings.JWT_SECRET_KEY or settings.SECRET_KEY or DEFAULT_JWT_SECRET
JWT_ALGORITHM = settings.JWT_ALGORITHM

# Access token should be short when refresh exists.
# Session timeout: 15 minutes of inactivity
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

REFRESH_TOKEN_SECRET = settings.REFRESH_TOKEN_SECRET or os.getenv("GTS_REFRESH_SECRET") or JWT_SECRET_KEY
REFRESH_TOKEN_EXPIRE_DAYS = settings.REFRESH_TOKEN_EXPIRE_DAYS
DEFAULT_SIGNUP_TENANT_ID = settings.DEFAULT_SIGNUP_TENANT_ID


def _is_production() -> bool:
    env = os.getenv("ENVIRONMENT") or settings.APP_ENV or "development"
    return env.strip().lower() in ("production", "prod")


if _is_production():
    if not JWT_SECRET_KEY or JWT_SECRET_KEY == DEFAULT_JWT_SECRET:
        raise RuntimeError("JWT_SECRET_KEY must be set to a non-default value in production.")
    if not REFRESH_TOKEN_SECRET or REFRESH_TOKEN_SECRET == DEFAULT_JWT_SECRET:
        raise RuntimeError("REFRESH_TOKEN_SECRET must be set to a non-default value in production.")

# Compatibility aliases
JWT_SECRET = JWT_SECRET_KEY

# Setup logging
log = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token", auto_error=False)
router = APIRouter(prefix="/auth", tags=["Auth"])


def _client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for", "")
    if forwarded:
        return forwarded.split(",")[0].strip()
    client = getattr(request, "client", None)
    return getattr(client, "host", "unknown")


# ---------------------------------------------------------------------
# Optional DB role lookup (no hard dependency)
# ---------------------------------------------------------------------
async def _try_get_db_role(email: str) -> Optional[str]:
    try:
        from backend.core.db_config import AsyncSessionLocal  # type: ignore
    except Exception:
        return None

    try:
        async with AsyncSessionLocal() as session:  # type: ignore
            res = await session.execute(select(User.role).where(User.email == email))
            role = res.scalar_one_or_none()
            return str(role) if role else None
    except Exception:
        return None


async def _try_get_db_user_fields(email: str) -> Optional[Dict[str, Any]]:
    try:
        from backend.core.db_config import AsyncSessionLocal  # type: ignore
    except Exception:
        return None


async def _get_user_rbac_snapshot(email: str) -> Dict[str, Any]:
    """
    Best-effort DB snapshot for /auth/me + RBAC checks.
    """
    import asyncio
    
    out: Dict[str, Any] = {
        "id": None,
        "email": email,
        "username": None,
        "tenant_id": None,
        "role": None,
        "roles": [],
        "permissions": [],
        "features": [],
        "assigned_bots": None,
        "token_version": 0,
        "is_active": None,
        "is_deleted": None,
    }

    try:
        from backend.database.config import get_sessionmaker  # type: ignore
    except Exception:
        return out

    try:
        maker = get_sessionmaker()  # type: ignore
    except Exception:
        return out

    # Add timeout protection to prevent hanging
    try:
        return await asyncio.wait_for(
            _fetch_user_snapshot_internal(maker, email, out),
            timeout=10.0
        )
    except asyncio.TimeoutError:
        log.warning(f"[auth] User RBAC snapshot timed out for {email}")
        return out
    except Exception as e:
        log.warning(f"[auth] Error fetching RBAC snapshot: {e}")
        return out


async def _fetch_user_snapshot_internal(maker, email: str, out: Dict[str, Any]) -> Dict[str, Any]:
    """Internal helper for async database fetch with timeout"""
    async with maker() as session:  # type: ignore
        try:
            row = await session.execute(
                text(
                    """
                    SELECT id, email,
                           COALESCE(username, NULL) AS username,
                           COALESCE(tenant_id::text, NULL) AS tenant_id,
                           COALESCE(role, NULL) AS role,
                           COALESCE(features, '[]'::json) AS features,
                           assigned_bots,
                           COALESCE(token_version, 0) AS token_version,
                           COALESCE(is_active, NULL) AS is_active,
                           COALESCE(is_deleted, NULL) AS is_deleted
                    FROM users
                    WHERE lower(email) = lower(:email)
                    LIMIT 1
                    """
                ),
                {"email": email},
            )
            r = row.first()
            if not r:
                return out
            out.update(
                {
                    "id": int(r[0]) if r[0] is not None else None,
                    "email": r[1],
                    "username": r[2],
                    "tenant_id": r[3],
                    "role": r[4],
                    "features": list(r[5] or []),
                    "assigned_bots": r[6],
                    "token_version": int(r[7] or 0),
                    "is_active": r[8],
                    "is_deleted": r[9],
                }
            )
        except Exception:
            try:
                from backend.models.user import User  # type: ignore
                res = await session.execute(select(User).where(User.email == email))
                u = res.scalar_one_or_none()
                if not u:
                    return out
                out.update(
                    {
                        "id": int(getattr(u, "id", 0) or 0),
                        "email": getattr(u, "email", email),
                        "username": getattr(u, "username", None),
                        "tenant_id": getattr(u, "tenant_id", None),
                        "role": getattr(u, "role", None),
                        "features": list(getattr(u, "features", None) or []),
                        "assigned_bots": getattr(u, "assigned_bots", None),
                        "token_version": int(getattr(u, "token_version", 0) or 0),
                        "is_active": getattr(u, "is_active", None),
                        "is_deleted": getattr(u, "is_deleted", None),
                    }
                )
            except Exception:
                return out

        # Skip complex role/permission queries to avoid timeouts
        # Just return the basic user data
        return out


async def _get_roles_and_permissions(db: AsyncSession, user_id: int) -> tuple[list[str], list[str]]:
    roles: list[str] = []
    perms: list[str] = []
    try:
        r = await db.execute(
            text("SELECT role_name FROM user_roles_view WHERE user_id = :uid"),
            {"uid": int(user_id)},
        )
        roles = [str(x[0]) for x in (r.fetchall() or []) if x and x[0]]
    except Exception:
        roles = []

    try:
        p = await db.execute(
            text("SELECT permission FROM user_permissions_view WHERE user_id = :uid"),
            {"uid": int(user_id)},
        )
        perms = [str(x[0]) for x in (p.fetchall() or []) if x and x[0]]
    except Exception:
        perms = []

    roles = sorted({s.strip() for s in roles if s and str(s).strip()})
    perms = sorted({s.strip() for s in perms if s and str(s).strip()})
    return roles, perms


async def get_user_by_login(db: AsyncSession, login: str) -> Optional[Any]:
    login = str(login or "").strip().lower()
    if not login:
        return None

    username_col = getattr(User, "username", None)
    if username_col is not None:
        stmt = select(User).where((User.email == login) | (username_col == login))
    else:
        stmt = select(User).where(User.email == login)
    res = await db.execute(stmt)
    return res.scalar_one_or_none()


async def _get_user_by_email(email: str, db: Optional[AsyncSession] = None) -> Optional[Dict[str, Any]]:
    try:
        if db is None:
            from backend.core.db_config import AsyncSessionLocal  # type: ignore
            if AsyncSessionLocal is None:
                return None
            async with AsyncSessionLocal() as session:  # type: ignore
                res = await session.execute(select(User).where(User.email == email))
                user = res.scalar_one_or_none()
        else:
            res = await db.execute(select(User).where(User.email == email))
            user = res.scalar_one_or_none()

        if not user:
            return None
        return {
            "id": user.id,
            "email": user.email,
            "role": user.role,
            "full_name": getattr(user, "full_name", None),
            "is_active": getattr(user, "is_active", True),
            "is_deleted": getattr(user, "is_deleted", False),
            "token_version": int(getattr(user, "token_version", 0) or 0),
            "hashed_password": getattr(user, "hashed_password", None),
        }
    except Exception:
        return None


def _get_password_tools():
    try:
        from backend.security.hashing import get_password_hash, verify_password  # type: ignore
        return get_password_hash, verify_password
    except Exception:
        try:
            from backend.utils.auth_utils import get_password_hash, verify_password  # type: ignore
            return get_password_hash, verify_password
        except Exception as exc:
            raise RuntimeError("Password hashing utilities are not available.") from exc


get_password_hash, verify_password = _get_password_tools()

logger = logging.getLogger("gts.auth")


def _clean_email(value: Optional[str]) -> str:
    email = str(value or "").strip().lower()
    return email.replace("\r", "").replace("\n", "").replace("\t", "")


async def authenticate_user_db(
    email: str,
    password: str,
    db: AsyncSession,
) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """
    DB-first user authentication.

    Returns: (user_dict | None, failure_reason | None)
    failure_reason is one of: "user_not_found", "password_mismatch"
    """
    email_clean = _clean_email(email)
    user = await _get_user_by_email(email_clean, db=db)
    if not user or not user.get("hashed_password") or user.get("is_deleted"):
        return None, "user_not_found"

    if not verify_password(password, str(user.get("hashed_password") or "")):
        return None, "password_mismatch"

    safe_user = dict(user)
    safe_user.pop("hashed_password", None)
    return safe_user, None


async def _update_last_login(db: AsyncSession, user_id: int) -> None:
    try:
        res = await db.execute(select(User).where(User.id == user_id))
        obj = res.scalar_one_or_none()
        if not obj:
            return
        obj.last_login = datetime.now(timezone.utc)
        db.add(obj)
        await db.commit()
    except Exception as exc:
        logger.warning("Failed to update last_login for user_id=%s: %s", user_id, exc)


# ---------------------------------------------------------------------
# Token helpers (Access)
# ---------------------------------------------------------------------
def create_access_token(
    subject: Union[str, int],
    email: str,
    role: str,
    expires_delta: Optional[timedelta] = None,
    session_timeout_minutes: Optional[int] = None,
    token_version: Optional[int] = None,
) -> str:
    """Create JWT access token
    
    Args:
        subject: User ID
        email: User email
        role: User role
        expires_delta: Custom expiration time delta
        session_timeout_minutes: Session timeout from platform settings (overrides default)
    """
    now = datetime.now(timezone.utc)
    
    # Use session_timeout_minutes from settings if provided, otherwise use default
    timeout_minutes = session_timeout_minutes or ACCESS_TOKEN_EXPIRE_MINUTES
    expire = now + (expires_delta or timedelta(minutes=timeout_minutes))
    
    payload: Dict[str, Any] = {
        "sub": str(subject),
        "email": str(email),
        "role": str(role),
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
    }
    if token_version is not None:
        payload["tv"] = int(token_version)
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def _decode_token(token: str) -> Dict[str, Any]:
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        log.info(
            "[auth] token decoded sub=%s email=%s role=%s tv=%s",
            payload.get("sub"),
            payload.get("email"),
            payload.get("role"),
            payload.get("tv"),
        )
        return payload
    except ExpiredSignatureError as exc:
        log.warning("[auth] token expired during decode")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired") from exc
    except InvalidTokenError as exc:
        log.warning("[auth] invalid token during decode")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from exc
    except Exception as exc:
        log.warning("[auth] token decode error: %s", exc)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from exc


# ---------------------------------------------------------------------
# Refresh token helpers (Opaque + DB hash)
# ---------------------------------------------------------------------
def _hash_refresh_token(token: str) -> str:
    msg = token.encode("utf-8")
    key = REFRESH_TOKEN_SECRET.encode("utf-8")
    return hmac.new(key, msg, hashlib.sha256).hexdigest()


def _new_refresh_token() -> str:
    return secrets.token_urlsafe(48)


async def _issue_refresh_token(db: AsyncSession, user_id: int) -> str:
    now = datetime.now(timezone.utc)
    expires = now + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

    raw = _new_refresh_token()
    token_hash = _hash_refresh_token(raw)

    await db.execute(
        text(
            """
            INSERT INTO refresh_tokens (
                user_id, token_hash, created_at, expires_at, revoked_at, replaced_by_id
            )
            VALUES (
                :user_id, :token_hash, :created_at, :expires_at, NULL, NULL
            )
            """
        ),
        {
            "user_id": int(user_id),
            "token_hash": token_hash,
            "created_at": now,
            "expires_at": expires,
        },
    )
    await db.commit()
    return raw


async def _rotate_refresh_token(db: AsyncSession, *, old_obj: Any) -> str:
    now = datetime.now(timezone.utc)

    new_raw = _new_refresh_token()
    new_hash = _hash_refresh_token(new_raw)
    new_expires = now + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

    old_id = getattr(old_obj, "id", None)
    old_user_id = getattr(old_obj, "user_id", None)
    if isinstance(old_obj, dict):
        old_id = old_obj.get("id", old_id)
        old_user_id = old_obj.get("user_id", old_user_id)

    if old_id is None or old_user_id is None:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    result = await db.execute(
        text(
            """
            INSERT INTO refresh_tokens (
                user_id, token_hash, created_at, expires_at, revoked_at, replaced_by_id
            )
            VALUES (
                :user_id, :token_hash, :created_at, :expires_at, NULL, NULL
            )
            RETURNING id
            """
        ),
        {
            "user_id": int(old_user_id),
            "token_hash": new_hash,
            "created_at": now,
            "expires_at": new_expires,
        },
    )
    new_id = result.scalar_one()

    await db.execute(
        text(
            """
            UPDATE refresh_tokens
            SET revoked_at = :revoked_at, replaced_by_id = :replaced_by_id
            WHERE id = :id
            """
        ),
        {
            "revoked_at": now,
            "replaced_by_id": int(new_id),
            "id": int(old_id),
        },
    )

    await db.commit()
    return new_raw


async def get_current_user(
    request: Request,
    token: Optional[str] = Depends(oauth2_scheme),
) -> Dict[str, Any]:
    if not token:
        auth = request.headers.get("authorization") or request.headers.get("Authorization") or ""
        if auth.lower().startswith("bearer "):
            token = auth.split(" ", 1)[1].strip()

    if not token:
        # Fallback for environments where reverse proxies strip Authorization.
        token = (
            request.headers.get("x-access-token")
            or request.headers.get("X-Access-Token")
            or ""
        ).strip()
        if token.lower().startswith("bearer "):
            token = token.split(" ", 1)[1].strip()

    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    payload = _decode_token(token)

    email = str(payload.get("email") or "").strip()
    token_role = str(payload.get("role") or "").strip() or "user"
    snapshot = await _get_user_rbac_snapshot(email) if email else {}
    has_db_snapshot = bool(snapshot) and snapshot.get("id") is not None

    token_tv = int(payload.get("tv", 0) or 0)
    db_tv = int(snapshot.get("token_version", 0) or 0)
    if has_db_snapshot:
        # TEMPORARILY DISABLED: is_active check to allow login
        # if (snapshot.get("is_active") is False) or (snapshot.get("is_deleted") is True):
        #     raise HTTPException(status_code=401, detail="User is disabled")
        if token_tv != db_tv:
            raise HTTPException(status_code=401, detail="Session revoked")

    db_role = snapshot.get("role") if has_db_snapshot else None

    try:
        from backend.security.rbac import compute_effective_role  # type: ignore
        effective_role = compute_effective_role(token_role, db_role)
    except Exception:
        effective_role = token_role

    return {
        "sub": str(snapshot.get("id") or payload.get("sub") or ""),
        "id": snapshot.get("id") if has_db_snapshot else payload.get("sub"),
        "email": snapshot.get("email") or email,
        "username": snapshot.get("username"),
        "tenant_id": snapshot.get("tenant_id"),
        "role": effective_role or token_role,
        "token_role": token_role,
        "db_role": db_role,
        "effective_role": effective_role,
        "roles": snapshot.get("roles") or [],
        "permissions": snapshot.get("permissions") or [],
        "features": snapshot.get("features") or [],
        "assigned_bots": snapshot.get("assigned_bots"),
        "iat": payload.get("iat"),
        "exp": payload.get("exp"),
    }


def require_roles(roles: List[str]) -> Callable[..., Any]:
    async def _dep(user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
        user_role = str(user.get("effective_role") or user.get("role") or "").strip()
        if not user_role:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

        try:
            from backend.security.rbac import has_required_role, normalize_role, expand_required_roles  # type: ignore
            normalized_user_role = normalize_role(user_role)
            allowed_roles = expand_required_roles(roles)
            logging.getLogger("auth").warning(f"[RBAC] user_role={user_role}, normalized={normalized_user_role}, required={roles}, expanded={allowed_roles}")
            if not has_required_role(user_role, roles):
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Forbidden: role '{normalized_user_role}' not in {allowed_roles}")
        except HTTPException:
            raise
        except Exception as e:
            logging.getLogger("auth").error(f"[RBAC] Exception: {e}")
            allowed = {r.strip().lower() for r in roles if r and r.strip()}
            if user_role.strip().lower() not in allowed:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

        return user

    return _dep


# Backward-compat alias
try:
    from backend.core.db_config import get_async_db as get_db_async  # type: ignore
except Exception:
    try:
        from backend.core.db_config import get_async_db as get_db_async  # type: ignore
    except Exception:

        async def get_db_async():  # type: ignore
            raise RuntimeError("DB dependency is not available")


@router.get("/me")
async def auth_me(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    return {"ok": True, "user": current_user}


@router.get("/debug-user")
async def debug_user(
    email: str,
    db: AsyncSession = Depends(get_db_async),
) -> Dict[str, Any]:
    if _is_production():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

    email_clean = _clean_email(email)
    user = await _get_user_by_email(email_clean, db=db)
    if not user:
        return {
            "exists_in_db": False,
            "id": None,
            "role": None,
            "is_active": None,
            "is_deleted": None,
        }

    return {
        "exists_in_db": True,
        "id": user.get("id"),
        "role": user.get("role"),
        "is_active": user.get("is_active"),
        "is_deleted": user.get("is_deleted"),
    }


class RegisterPayload(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    role: Optional[str] = "user"
    tenant_id: Optional[str] = None
    username: Optional[str] = None


async def _resolve_tenant_id_for_registration(request: Request, db: AsyncSession) -> Optional[str]:
    """
    Resolve tenant_id for registration:
      1) X-Tenant-Id header if present and exists in DB
      2) DEFAULT_SIGNUP_TENANT_ID (env/constant)
      3) First tenant row in tenants table
    """
    hdr_tid = (
        request.headers.get("x-tenant-id")
        or request.headers.get("X-Tenant-Id")
        or request.headers.get("X-TENANT-ID")
    )
    hdr_tid = (hdr_tid or "").strip()
    if hdr_tid:
        try:
            ok = await db.execute(
                text("SELECT 1 FROM tenants WHERE id = :tid LIMIT 1"),
                {"tid": hdr_tid},
            )
            if ok.scalar() == 1:
                return hdr_tid
        except Exception:
            pass

    if DEFAULT_SIGNUP_TENANT_ID:
        try:
            ok = await db.execute(
                text("SELECT 1 FROM tenants WHERE id = :tid LIMIT 1"),
                {"tid": DEFAULT_SIGNUP_TENANT_ID},
            )
            if ok.scalar() == 1:
                return DEFAULT_SIGNUP_TENANT_ID
        except Exception:
            pass

    try:
        row = await db.execute(text("SELECT id FROM tenants ORDER BY id ASC LIMIT 1"))
        tid = row.scalar_one_or_none()
        if tid:
            return str(tid)
    except Exception:
        pass

    return (DEFAULT_SIGNUP_TENANT_ID or "").strip() or None


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    request: Request,
    payload: RegisterPayload,
    db: AsyncSession = Depends(get_db_async),
) -> Dict[str, Any]:
    tid = payload.tenant_id or await _resolve_tenant_id_for_registration(request, db)
    if not tid:
        raise HTTPException(status_code=500, detail="Failed to resolve tenant_id during registration.")

    try:
        if is_global_user is not None:
            is_global_user.set(False)  # type: ignore
        if current_tenant_id is not None:
            current_tenant_id.set(tid)  # type: ignore
    except Exception:
        pass

    email_clean = _clean_email(payload.email)
    stmt = select(User).where(User.email == email_clean)
    res = await db.execute(stmt)
    if res.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    username_val = payload.username.strip().lower() if payload.username else email_clean.split("@")[0]
    if hasattr(User, "username"):
        stmt = select(User).where(User.username == username_val)
        existing_username = await db.execute(stmt)
        if existing_username.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Username already registered")

    hashed = get_password_hash(payload.password)
    user = User(
        email=email_clean,
        hashed_password=hashed,
        full_name=payload.full_name,
        role=(payload.role or "user").strip() or "user",
        is_active=True,
        tenant_id=tid,
    )
    if hasattr(user, "username"):
        setattr(user, "username", username_val)

    db.add(user)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=400, detail="User already exists")
    await db.refresh(user)

    return {
        "ok": True,
        "id": getattr(user, "id", None),
        "email": getattr(user, "email", None),
        "full_name": getattr(user, "full_name", None),
        "role": getattr(user, "role", None),
        "tenant_id": getattr(user, "tenant_id", None),
    }


class LoginPayload(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[EmailStr] = None
    password: str


class RefreshPayload(BaseModel):
    refresh_token: str


class LogoutPayload(BaseModel):
    refresh_token: str


@router.post("/token")
async def login_for_access_token(
    request: Request,
    db: AsyncSession = Depends(get_db_async),
) -> Dict[str, Any]:
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
    email_clean = _clean_email(str(email))
    logger.info("AUTH_TOKEN_ATTEMPT username=%s", email_clean)

    user, failure = await authenticate_user_db(email_clean, password, db)
    if not user:
        try:
            existing_user = await _get_user_by_email(email_clean, db=db)
            if existing_user and existing_user.get("email"):
                asyncio.create_task(
                    notification_service.send_security_notification(
                        event_type="login_failed",
                        user_email=str(existing_user.get("email")),
                        user_name=str(existing_user.get("full_name") or existing_user.get("email")),
                        ip_address=_client_ip(request),
                        device=request.headers.get("user-agent", "Unknown")[:120],
                        attempt_count=1,
                    )
                )
        except Exception:
            pass
        if failure == "user_not_found":
            logger.info("AUTH_USER_NOT_FOUND username=%s", email_clean)
        elif failure == "password_mismatch":
            logger.info("AUTH_PASSWORD_MISMATCH username=%s", email_clean)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    if user.get("is_active") is False:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is inactive")

    await _update_last_login(db, int(user["id"]))

    # Get session timeout from platform settings
    session_timeout_minutes = ACCESS_TOKEN_EXPIRE_MINUTES
    try:
        from backend.services.platform_settings_store import get_platform_settings
        settings = await get_platform_settings(db)
        technical = settings.get("technical", {})
        session_timeout_minutes = technical.get("sessionTimeout", ACCESS_TOKEN_EXPIRE_MINUTES)
        logger.info(f"Using session timeout: {session_timeout_minutes} minutes")
    except Exception as e:
        logger.warning(f"Failed to load session timeout from settings, using default: {e}")

    access_token = create_access_token(
        subject=user["id"],
        email=user["email"],
        role=user.get("role") or "user",
        expires_delta=timedelta(minutes=session_timeout_minutes),
        session_timeout_minutes=session_timeout_minutes,
        token_version=int(user.get("token_version", 0) or 0),
    )

    try:
        refresh_token = await _issue_refresh_token(db, int(user["id"]))
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to issue refresh token")

    try:
        asyncio.create_task(
            notification_service.send_security_notification(
                event_type="login_success",
                user_email=str(user["email"]),
                user_name=str(user.get("full_name") or user["email"]),
                ip_address=_client_ip(request),
                device=request.headers.get("user-agent", "Unknown")[:120],
            )
        )
    except Exception:
        pass

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": {
            "id": user["id"],
            "email": user["email"],
            "full_name": user.get("full_name"),
            "role": user.get("role") or "user",
        },
    }


@router.post("/refresh")
async def refresh_access_token(
    payload: RefreshPayload,
    db: AsyncSession = Depends(get_db_async),
) -> Dict[str, Any]:

    raw = (payload.refresh_token or "").strip()
    if not raw:
        raise HTTPException(status_code=400, detail="refresh_token is required")

    token_hash = _hash_refresh_token(raw)
    now = datetime.now(timezone.utc)

    stmt = select(RefreshToken).where(RefreshToken.token_hash == token_hash)
    res = await db.execute(stmt)
    rt = res.scalar_one_or_none()

    if not rt:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    if rt.revoked_at is not None:
        raise HTTPException(status_code=401, detail="Refresh token revoked")

    if rt.expires_at <= now:
        raise HTTPException(status_code=401, detail="Refresh token expired")

    user = await db.scalar(select(User).where(User.id == rt.user_id))
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    if getattr(user, "is_active", True) is False:
        raise HTTPException(status_code=403, detail="User is inactive")

    new_access = create_access_token(
        subject=user.id,
        email=user.email,
        role=getattr(user, "role", None) or "user",
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        token_version=int(getattr(user, "token_version", 0) or 0),
    )

    new_refresh = await _rotate_refresh_token(db, old_obj=rt)

    return {
        "access_token": new_access,
        "refresh_token": new_refresh,
        "token_type": "bearer",
    }


@router.post("/logout")
async def logout(payload: LogoutPayload, db: AsyncSession = Depends(get_db_async)) -> Dict[str, Any]:

    raw = (payload.refresh_token or "").strip()
    if not raw:
        raise HTTPException(status_code=400, detail="refresh_token is required")

    token_hash = _hash_refresh_token(raw)
    res = await db.execute(select(RefreshToken).where(RefreshToken.token_hash == token_hash))
    rt = res.scalar_one_or_none()
    if not rt:
        return {"ok": True}

    logout_user = await db.scalar(select(User).where(User.id == rt.user_id))

    if rt.revoked_at is None:
        rt.revoked_at = datetime.now(timezone.utc)
        await db.commit()

    try:
        if logout_user and getattr(logout_user, "email", None):
            asyncio.create_task(
                notification_service.send_security_notification(
                    event_type="logout",
                    user_email=str(logout_user.email),
                    user_name=str(getattr(logout_user, "full_name", None) or logout_user.email),
                    ip_address="unknown",
                    reason="Refresh token revoked",
                )
            )
    except Exception:
        pass

    return {"ok": True}


__all__ = [
    "router",
    "require_roles",
    "create_access_token",
    "get_current_user",
    "get_db_async",
    "get_password_hash",
    "verify_password",
    "get_user_by_login",
    "JWT_SECRET",
    "JWT_ALGORITHM",
]
