# backend/integrations/loadboards/truckerpath_provider.py
import os
import httpx
from typing import Any, Dict

from .base import BaseLoadBoard

def _bool_env(name: str, default: bool = False) -> bool:
    val = os.getenv(name, str(default)).lower()
    return val in {"1", "true", "yes"}

class TruckerPathProvider(BaseLoadBoard):
    def __init__(self) -> None:
        self.base_url = os.getenv("TRUCKERPATH_BASE_URL", "https://test-api.truckerpath.com/truckload/api").rstrip("/")
        token = os.getenv("TRUCKERPATH_API_TOKEN", "").strip()
        # Add Bearer if user gave raw token
        self.auth = f"Bearer {token}" if token and not token.lower().startswith("bearer ") else token
        self.enable_mock = _bool_env("TRUCKERPATH_ENABLE_MOCK", True)

        self.url_post_load = os.getenv("TRUCKERPATH_POST_LOAD_URL", f"{self.base_url}/shipments/v2")
        self.url_create_company = os.getenv("TRUCKERPATH_CREATE_COMPANY_URL", f"{self.base_url}/company/create")
        self.url_register_webhook = os.getenv("TRUCKERPATH_REGISTER_WEBHOOK_URL", f"{self.base_url}/webhooks/register")
        self.url_register_webhook_add = os.getenv("TRUCKERPATH_REGISTER_WEBHOOK_ADD_URL", f"{self.base_url}/webhooks/add")
        self.url_tracking_create = os.getenv("TRUCKERPATH_TRACKING_CREATE_URL", f"{self.base_url}/tracking/").rstrip("/") + "/"
        self.url_tracking_points = os.getenv("TRUCKERPATH_TRACKING_URL", f"{self.base_url}/tracking/update")

        self.headers = {
            "Authorization": self.auth,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    async def _post(self, url: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        if self.enable_mock or not self.auth:
            return {"ok": True, "mock": True, "url": url, "payload": payload}
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(url, headers=self.headers, json=payload)
            try:
                data = resp.json()
            except Exception:
                data = {"text": resp.text}
            if resp.status_code in (200, 201, 202):
                return {"ok": True, "status": resp.status_code, "data": data}
            return {"ok": False, "status": resp.status_code, "error": data}

    async def _get(self, url: str) -> Dict[str, Any]:
        if self.enable_mock or not self.auth:
            return {"ok": True, "mock": True, "url": url}
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(url, headers=self.headers)
            try:
                data = resp.json()
            except Exception:
                data = {"text": resp.text}
            if resp.status_code in (200, 201):
                return {"ok": True, "status": resp.status_code, "data": data}
            return {"ok": False, "status": resp.status_code, "error": data}

    async def ping(self) -> Dict[str, Any]:
        # No official ping; return offline/ok
        if self.enable_mock or not self.auth:
            return {"ok": True, "mock": True, "message": "Ping OK (offline)"}
        return {"ok": True, "message": "Ping OK (no provider ping)"}

    async def create_company(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return await self._post(self.url_create_company, payload)

    async def post_load(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return await self._post(self.url_post_load, payload)

    async def register_webhook(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return await self._post(self.url_register_webhook, payload)

    async def register_webhook_add(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return await self._post(self.url_register_webhook_add, payload)

    async def tracking_create(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return await self._post(self.url_tracking_create, payload)

    async def push_tracking_points(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return await self._post(self.url_tracking_points, payload)
