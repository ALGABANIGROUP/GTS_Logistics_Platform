# backend/security/hashing.py
"""
Password hashing utilities using bcrypt directly.
Avoids passlib/bcrypt version incompatibility issues.
"""

import bcrypt


def _normalize_password(password: str) -> bytes:
    """
    Normalize password string and avoid bcrypt 72-byte limit issues.
    Returns bytes ready for bcrypt.
    """
    if not isinstance(password, str):
        password = str(password)

    # bcrypt works on bytes and has a hard limit of 72 bytes
    raw_bytes = password.encode("utf-8")
    if len(raw_bytes) > 72:
        raw_bytes = raw_bytes[:72]

    return raw_bytes


def get_password_hash(password: str) -> str:
    """
    Return a secure hash for the given password using bcrypt.
    """
    safe_password = _normalize_password(password)
    hashed = bcrypt.hashpw(safe_password, bcrypt.gensalt())
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify that a given plain password matches the stored hash.
    """
    safe_password = _normalize_password(plain_password)
    if isinstance(hashed_password, str):
        hashed_password = hashed_password.encode("utf-8")
    try:
        return bcrypt.checkpw(safe_password, hashed_password)
    except Exception:
        return False
