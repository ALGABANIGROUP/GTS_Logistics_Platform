from __future__ import annotations

import hashlib
import hmac
import json
import logging
import time
from typing import Any, Dict, Tuple

import httpx

from backend.utils.crypto import decrypt_secret

logger = logging.getLogger(__name__)


def _resolve_secret(raw_secret: str) -> str:
    if not raw_secret:
        return ""
    decrypted = decrypt_secret(raw_secret)
    return decrypted or raw_secret


def _build_signature(secret: str, timestamp: str, payload_json: str) -> str:
    message = f"{timestamp}.{payload_json}"
    return hmac.new(secret.encode("utf-8"), msg=message.encode("utf-8"), digestmod=hashlib.sha256).hexdigest()


async def dispatch_platform_webhook(
    *,
    url: str,
    secret: str,
    event_type: str,
    data: Dict[str, Any],
    client_id: str = "gts-platform",
    timeout: float = 10.0,
) -> Tuple[bool, str, int]:
    if not url:
        return False, "Webhook URL not configured", 0

    timestamp = str(int(time.time()))
    payload = {
        "event": event_type,
        "timestamp": timestamp,
        "data": data,
    }
    payload_json = json.dumps(payload, separators=(",", ":"), ensure_ascii=True)

    resolved_secret = _resolve_secret(secret)
    signature = _build_signature(resolved_secret, timestamp, payload_json) if resolved_secret else ""

    headers = {
        "Content-Type": "application/json",
        "X-Client-ID": client_id,
        "X-Timestamp": timestamp,
        "X-Signature": signature,
    }

    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(url, content=payload_json, headers=headers)
        if response.status_code >= 400:
            detail = response.text[:300] if response.text else "HTTP error"
            return False, detail, response.status_code
        return True, "Delivered", response.status_code
    except Exception as exc:
        logger.warning("Webhook dispatch failed: %s", exc)
        return False, str(exc), 0


async def dispatch_from_platform_settings(
    *,
    db,
    event_type: str,
    data: Dict[str, Any],
    client_id: str = "gts-platform",
) -> Tuple[bool, str, int]:
    try:
        from backend.services.platform_settings_store import _get_platform_settings_raw

        settings = await _get_platform_settings_raw(db)
        integrations = settings.get("integrations", {})
        webhook_url = str(integrations.get("webhookUrl") or "").strip()
        webhook_secret = str(integrations.get("webhookSecret") or "")
        if not webhook_url:
            return False, "Webhook URL not configured", 0
        return await dispatch_platform_webhook(
            url=webhook_url,
            secret=webhook_secret,
            event_type=event_type,
            data=data,
            client_id=client_id,
        )
    except Exception as exc:
        logger.warning("Webhook dispatch skipped: %s", exc)
        return False, str(exc), 0
