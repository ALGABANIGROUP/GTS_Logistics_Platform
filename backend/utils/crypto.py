from __future__ import annotations

import os
from typing import Optional

from cryptography.fernet import Fernet, InvalidToken


def _get_fernet() -> Optional[Fernet]:
    key = os.getenv("EMAIL_CREDENTIALS_KEY", "").strip()
    if not key:
        return None
    try:
        return Fernet(key)
    except Exception:
        return None


def encrypt_secret(value: Optional[str]) -> Optional[str]:
    if not value:
        return None
    fernet = _get_fernet()
    if not fernet:
        raise RuntimeError("EMAIL_CREDENTIALS_KEY is not configured")
    token = fernet.encrypt(value.encode("utf-8"))
    return token.decode("utf-8")


def decrypt_secret(token: Optional[str]) -> Optional[str]:
    if not token:
        return None
    fernet = _get_fernet()
    if not fernet:
        return None
    try:
        return fernet.decrypt(token.encode("utf-8")).decode("utf-8")
    except InvalidToken:
        return None
