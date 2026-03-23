from __future__ import annotations

import base64
import hashlib
import os
from typing import Tuple

from cryptography.fernet import Fernet, InvalidToken


def _is_prod() -> bool:
    env = (os.getenv("ENV") or "").strip().lower()
    env2 = (os.getenv("ENVIRONMENT") or os.getenv("APP_ENV") or "").strip().lower()
    is_prod_flag = (os.getenv("IS_PRODUCTION") or "").strip().lower()
    return env in {"prod", "production"} or env2 in {"prod", "production"} or is_prod_flag in {
        "1",
        "true",
        "yes",
    }


def _normalize_key(raw: str) -> bytes:
    try:
        raw_bytes = raw.encode("utf-8")
    except Exception:
        raw_bytes = str(raw).encode("utf-8", errors="ignore")

    if len(raw_bytes) == 44:
        try:
            decoded = base64.urlsafe_b64decode(raw_bytes)
            if len(decoded) == 32:
                return raw_bytes
        except Exception:
            pass

    digest = hashlib.sha256(raw_bytes).digest()
    return base64.urlsafe_b64encode(digest)


def _get_fernet() -> Fernet:
    master = os.getenv("EMAIL_CRED_MASTER_KEY", "").strip()
    if not master:
        if _is_prod():
            raise RuntimeError("EMAIL_CRED_MASTER_KEY is required in production.")
        master = "dev-email-cred-key"
    key = _normalize_key(master)
    return Fernet(key)


def encrypt_credentials(password: str) -> Tuple[str, str]:
    f = _get_fernet()
    token = f.encrypt(password.encode("utf-8")).decode("utf-8")
    key_version = os.getenv("EMAIL_CRED_KEY_VERSION", "v1")
    return token, key_version


def decrypt_credentials(ciphertext: str) -> str:
    f = _get_fernet()
    try:
        return f.decrypt(ciphertext.encode("utf-8")).decode("utf-8")
    except InvalidToken as exc:
        raise RuntimeError("Invalid credentials ciphertext.") from exc
