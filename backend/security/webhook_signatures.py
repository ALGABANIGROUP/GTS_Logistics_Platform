from __future__ import annotations

import hashlib
import hmac
from typing import Iterable, Optional


def is_production(app_env: str | None = None) -> bool:
    return (app_env or "development").strip().lower() in {"production", "prod"}


def build_hmac_sha256(secret: str, payload: bytes) -> str:
    return hmac.new(secret.encode("utf-8"), payload, hashlib.sha256).hexdigest()


def build_timestamped_message(timestamp: str, payload: bytes) -> bytes:
    return f"{timestamp}.".encode("utf-8") + payload


def extract_signature_value(
    signature_header: str | None,
    *,
    preferred_keys: Iterable[str] = (),
) -> str:
    if not signature_header:
        return ""

    header = signature_header.strip()
    if not header:
        return ""

    preferred = tuple(key.strip() for key in preferred_keys if key and key.strip())
    if preferred:
        parts: dict[str, str] = {}
        for chunk in header.split(","):
            if "=" not in chunk:
                continue
            key, value = chunk.split("=", 1)
            parts[key.strip()] = value.strip()
        for key in preferred:
            value = parts.get(key)
            if value:
                return value

    if "=" in header and "," not in header:
        _, value = header.split("=", 1)
        if value.strip():
            return value.strip()

    return header


def verify_hmac_sha256_signature(
    *,
    secret: str | None,
    payload: bytes,
    signature_header: str | None,
    app_env: str | None = None,
    preferred_signature_keys: Iterable[str] = (),
    allow_missing_secret: bool = False,
) -> bool:
    if not secret:
        if allow_missing_secret:
            return True
        return not is_production(app_env)

    provided_signature = extract_signature_value(
        signature_header,
        preferred_keys=preferred_signature_keys,
    )
    if not provided_signature:
        return False

    expected_signature = build_hmac_sha256(secret, payload)
    return hmac.compare_digest(expected_signature, provided_signature)
