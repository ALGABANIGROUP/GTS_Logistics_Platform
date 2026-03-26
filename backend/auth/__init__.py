from __future__ import annotations

"""
Lightweight password hashing helpers for auth routes.
Kept here to avoid heavy imports and optional dependencies.
"""

import bcrypt


def create_access_token(*args, **kwargs):
    from backend.security.auth import create_access_token as _create_access_token
    return _create_access_token(*args, **kwargs)


def _normalize_password(password: str) -> bytes:
    if not isinstance(password, str):
        password = str(password)
    raw = password.encode("utf-8")
    # bcrypt hard limit 72 bytes
    if len(raw) > 72:
        raw = raw[:72]
    return raw


def get_password_hash(password: str) -> str:
    safe_password = _normalize_password(password)
    hashed = bcrypt.hashpw(safe_password, bcrypt.gensalt())
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    safe_password = _normalize_password(plain_password)
    if isinstance(hashed_password, str):
        hashed_password = hashed_password.encode("utf-8")
    try:
        return bcrypt.checkpw(safe_password, hashed_password)
    except Exception:
        return False


__all__ = ["get_password_hash", "verify_password", "create_access_token"]
