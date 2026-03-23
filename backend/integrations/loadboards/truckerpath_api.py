# backend/integrations/loadboards/truckerpath.py
from __future__ import annotations

import os
from typing import Any, Dict, Optional, List

import httpx

# Optional: mock loads source
try:
    from backend.integrations.loadboards.mock_truckerpath import get_mock_loads
except Exception:
    def get_mock_loads() -> List[Dict[str, Any]]:
        return [{"id": "mock-1", "lane": "AUS,TX -> LAX,CA", "equipment": "Dry Van", "rate": 2500}]

# Base interface
try:
    from backend.integrations.loadboards.base import BaseLoadBoard
except Exception:
    class BaseLoadBoard:  # fallback to avoid import issues during early wiring
        async def ping(self) -> Dict[str, Any]: ...
        async def create_company(self, payload: Dict[str, Any]) -> Dict[str, Any]: ...
        async def post_load(self, payload: Dict[str, Any]) -> Dict[str, Any]: ...
        async def register_webhook(self, payload: Dict[str, Any]) -> Dict[str, Any]: ...
        async def register_webhook_add(self, payload: Dict[str, Any]) -> Dict[str, Any]: ...
        async def tracking_create(self, payload: Dict[str, Any]) -> Dict[str, Any]: ...
        async def push_tracking_points(self, payload: Dict[str, Any]) -> Dict[str, Any]: ...


def _bool_env(name: str, default: bool = False) -> bool:
    val = os.getenv(name, str(default)).lower()
    return val in {"1", "true", "yes"}


def _bearer(token: str) -> str:
    if not token:
        return ""
    return token if token.lower().startswith("bearer ") else f"Bearer {token}"


class TruckerPathProvider(BaseLoadBoard):
    """
    Concrete implementation of BaseLoadBoard for TruckerPath.
    Reads config from environment variables:
      - TRUCKERPATH_BASE_URL (default: https://test-api.truckerpath.com/truckload/api)
      - TRUCKERPATH_API_TOKEN (raw token, no 'Bearer' prefix required)
      - TRUCKERPATH_ENABLE_MOCK (true/false)
      - Optional endpoint overrides:
          TRUCKERPATH_POST_LOAD_URL
          TRUCKERPATH_CREATE_COMPANY_URL
          TRUCKERPATH_REGISTER_WEBHOOK_URL
          TRUCKERPATH_REGISTER_WEBHOOK_ADD_URL
          TRUCKERPATH_TRACKING_CREATE_URL
          TRUCKERPATH_TRACKING_URL
          TRUCKERPATH_LIST_LOADS_URL
    """

    def __init__(self) -> None:
        self.base_url = os.getenv("TRUCKERPATH_BASE_URL", "https://test-api.truckerpath.com/truckload/api").rstrip("/")
        token = os.getenv("TRUCKERPATH_API_TOKEN", "").strip()
        self.auth = _bearer(token)
        self.enable_mock = _bool_env("TRUCKERPATH_ENABLE_MOCK", True)

        # Primary endpoints
        self.url_post_load = os.getenv("TRUCKERPATH_POST_LOAD_URL", f"{self.base_url}/shipments/v2")
        self.url_create_company = os.getenv("TRUCKERPATH_CREATE_COMPANY_URL", f"{self.base_url}/company/create")
        self.url_register_webhook = os.getenv("TRUCKERPATH_REGISTER_WEBHOOK_URL", f"{self.base_url}/webhooks/register")
        self.url_register_webhook_add = os.getenv("TRUCKERPATH_REGISTER_WEBHOOK_ADD_URL", f"{self.base_url}/webhooks/add")
        self.url_tracking_create = os.getenv("TRUCKERPATH_TRACKING_CREATE_URL", f"{self.base_url}/tracking/").rstrip("/") + "/"
        self.url_tracking_points = os.getenv("TRUCKERPATH_TRACKING_URL", f"{self.base_url}/tracking/update")

        # Optional: list/search loads endpoint (adjust to provider docs if differs)
        self.url_list_loads = os.getenv("TRUCKERPATH_LIST_LOADS_URL", f"{self.base_url}/loads")

        self.headers = {
            "Authorization": self.auth,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    # ---------- HTTP helpers ----------
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

    async def _get(self, url: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if self.enable_mock or not self.auth:
            return {"ok": True, "mock": True, "url": url, "params": params or {}}
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(url, headers=self.headers, params=params or {})
            try:
                data = resp.json()
            except Exception:
                data = {"text": resp.text}
            if resp.status_code in (200, 201):
                return {"ok": True, "status": resp.status_code, "data": data}
            return {"ok": False, "status": resp.status_code, "error": data}

    # ---------- BaseLoadBoard API ----------
    async def ping(self) -> Dict[str, Any]:
        if self.enable_mock or not self.auth:
            return {"ok": True, "mock": True, "message": "Ping OK (mock)"}
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

    # ---------- Convenience: list/search loads ----------
    async def list_loads(self, *, limit: int = 10, **params: Any) -> Dict[str, Any]:
        """
        Optional helper to fetch available loads from TruckerPath if the API supports it.
        Defaults to GET {base}/loads?limit=...
        """
        q = {"limit": limit, **params}
        return await self._get(self.url_list_loads, params=q)


class ExternalLoadBoardAgent:
    """
    Backward-compatible facade used elsewhere in the project.
    Provides a simple 'fetch' API that returns mock loads or calls provider.list_loads().
    """

    @staticmethod
    async def fetch(source: str = "mock", *, limit: int = 10) -> List[Dict[str, Any]]:
        if source == "mock":
            return get_mock_loads()
        elif source == "truckerpath":
            provider = TruckerPathProvider()
            res = await provider.list_loads(limit=limit)
            if res.get("ok") and "data" in res:
                data = res["data"]
                # Adapt to provider’s format; assume top-level list under "loads" or the root is a list
                if isinstance(data, dict) and "loads" in data:
                    return list(data.get("loads") or [])
                if isinstance(data, list):
                    return data
                # Fallback: unknown shape
                return [data]
            # On error or mock reply
            return []
        else:
            raise ValueError(f"Unsupported load board source: {source!r}")


# Optional direct run for quick manual check (will run in mock mode if token missing)
if __name__ == "__main__":
    import asyncio

    async def main():
        agent = ExternalLoadBoardAgent()
        loads = await agent.fetch(source="mock", limit=5)
        for load in loads:
            print(load)

    asyncio.run(main())
