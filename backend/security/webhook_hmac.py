from __future__ import annotations

import hashlib
import hmac
import json
import os
import time
from typing import Dict, Optional

from fastapi import HTTPException, Request
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED

DEFAULT_SKEW_SECONDS = 300  # 5 minutes


def parse_webhook_secrets(raw: Optional[str]) -> Dict[str, str]:
    """Parse webhook secrets from JSON or comma-separated key:value pairs."""
    if not raw:
        return {}
    raw = raw.strip()
    if not raw:
        return {}

    # Try JSON first
    try:
        parsed = json.loads(raw)
        if isinstance(parsed, dict):
            return {str(k): str(v) for k, v in parsed.items()}
    except Exception:
        pass

    secrets: Dict[str, str] = {}
    for part in raw.split(","):
        if ":" not in part:
            continue
        key, value = part.split(":", 1)
        key = key.strip()
        value = value.strip()
        if key and value:
            secrets[key] = value
    return secrets


def resolve_secret_store(request: Request) -> Dict[str, str]:
    """Return the cached webhook secret store from app.state or env."""
    cached = getattr(request.app.state, "webhook_secrets", None)
    if isinstance(cached, dict):
        return cached
    env_value = os.getenv("WEBHOOK_SECRETS", "")
    return parse_webhook_secrets(env_value)


class HMACVerifier:
    def __init__(self, secret_store: Dict[str, str], skew_seconds: int = DEFAULT_SKEW_SECONDS):
        self.secret_store = secret_store
        self.skew_seconds = skew_seconds

    async def verify(self, request: Request, client_id: str, signature: str, timestamp: str) -> bool:
        if not all([client_id, signature, timestamp]):
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail="Missing required headers: X-Client-ID, X-Signature, X-Timestamp",
            )

        secret = self.secret_store.get(client_id)
        if not secret:
            raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Invalid client ID")

        try:
            ts = int(timestamp)
        except ValueError:
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Invalid timestamp format")

        current_ts = int(time.time())
        if abs(current_ts - ts) > self.skew_seconds:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail="Timestamp expired",
            )

        body = await request.body()
        message = f"{timestamp}.{body.decode()}"
        expected_signature = hmac.new(secret.encode(), msg=message.encode(), digestmod=hashlib.sha256).hexdigest()

        if not hmac.compare_digest(signature, expected_signature):
            raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Invalid signature")

        return True


async def verify_webhook_hmac(request: Request) -> Dict[str, str]:
    """FastAPI dependency to validate webhook HMAC headers."""
    client_id = request.headers.get("X-Client-ID")
    signature = request.headers.get("X-Signature")
    timestamp = request.headers.get("X-Timestamp")

    verifier = HMACVerifier(resolve_secret_store(request))
    await verifier.verify(request, client_id or "", signature or "", timestamp or "")

    return {"client_id": client_id or "", "timestamp": timestamp or "", "signature": signature or ""}
