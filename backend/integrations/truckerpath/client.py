# backend/integrations/truckerpath/client.py
import os
import hmac
import hashlib
import json
from typing import Any, Dict, Optional

import httpx

TRUCKERPATH_BASE_URL = os.getenv("TRUCKERPATH_BASE_URL", "https://api.truckerpath.com")
TRUCKERPATH_API_KEY = os.getenv("TRUCKERPATH_API_KEY", "")
TRUCKERPATH_COMPANY_ID = os.getenv("TRUCKERPATH_COMPANY_ID", "")
TRUCKERPATH_WEBHOOK_SECRET = os.getenv("TRUCKERPATH_WEBHOOK_SECRET", "")
TRUCKERPATH_SANDBOX_MODE = os.getenv("TRUCKERPATH_SANDBOX_MODE", "false").lower() in {"1", "true", "yes"}

class TruckerPathClient:
    def __init__(self) -> None:
        self.base_url = TRUCKERPATH_BASE_URL.rstrip("/")
        self.api_key = TRUCKERPATH_API_KEY
        self.company_id = TRUCKERPATH_COMPANY_ID
        self.use_sandbox = TRUCKERPATH_SANDBOX_MODE

        if not self.api_key and not self.use_sandbox:
            raise RuntimeError("TRUCKERPATH_API_KEY is required when sandbox mode is disabled.")

        self._headers = {
            "Authorization": f"Bearer {self.api_key}" if self.api_key else "",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    async def _post(self, path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        if self.use_sandbox:
            return {"ok": False, "status": 503, "error": "truckerpath_sandbox_disabled", "message": "Sandbox mode is disabled."}

        url = f"{self.base_url}{path}"
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(url, headers=self._headers, json=payload)
            resp.raise_for_status()
            return resp.json()

    async def _get(self, path: str) -> Dict[str, Any]:
        if self.use_sandbox:
            return {"ok": False, "status": 503, "error": "truckerpath_sandbox_disabled", "message": "Sandbox mode is disabled."}

        url = f"{self.base_url}{path}"
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(url, headers=self._headers)
            resp.raise_for_status()
            return resp.json()

    async def ping(self) -> Dict[str, Any]:
        if self.use_sandbox:
            return {"ok": False, "status": 503, "error": "truckerpath_sandbox_disabled", "message": "Sandbox mode is disabled."}
        # Adjust path per TruckerPath docs if different
        return await self._get("/v1/ping")

    async def register_webhook(self, url: str, events: list[str]) -> Dict[str, Any]:
        payload = {
            "company_id": self.company_id,
            "url": url,
            "events": events,
        }
        # Adjust path per TruckerPath docs if different
        return await self._post("/v1/webhooks/register", payload)

    async def post_load(self, data: Dict[str, Any]) -> Dict[str, Any]:
        payload = {
            "company_id": self.company_id,
            **data,
        }
        # Adjust path per TruckerPath docs if different
        return await self._post("/v1/loads", payload)

    @staticmethod
    def verify_signature(raw_body: bytes, provided_signature: Optional[str]) -> bool:
        if not TRUCKERPATH_WEBHOOK_SECRET:
            # If no secret, accept (use only in testing!)
            return True
        if not provided_signature:
            return False
        mac = hmac.new(TRUCKERPATH_WEBHOOK_SECRET.encode("utf-8"), raw_body, hashlib.sha256).hexdigest()
        # Many providers prefix algo, normalize if needed
        provided = provided_signature.split("=", 1)[-1].strip()
        return hmac.compare_digest(mac, provided)
