# backend/integrations/truckerpath/provider.py
from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

try:
    import httpx
except Exception:  # pragma: no cover
    httpx = None

DEFAULT_BASE_URL = "https://test-api.truckerpath.com/truckload/api"


def _bool_env(name: str, default: bool = False) -> bool:
    val = os.getenv(name, str(default)).lower()
    return val in {"1", "true", "yes", "on"}


def _bearer(token: str) -> str:
    if not token:
        return ""
    return token if token.lower().startswith("bearer ") else f"Bearer {token}"


class TruckerPathProvider:
    """
    Unified TruckerPath provider (mock-friendly).
    Implements the interface expected by:
      - backend/routes/loadboards_routes.py (generic)
      - backend/services/truckerpath_service.py (service facade)

    Reads env:
      TRUCKERPATH_BASE_URL
      TRUCKERPATH_API_TOKEN
      TRUCKERPATH_ENABLE_MOCK
      TRUCKERPATH_POST_LOAD_URL
      TRUCKERPATH_CREATE_COMPANY_URL
      TRUCKERPATH_REGISTER_WEBHOOK_URL
      TRUCKERPATH_REGISTER_WEBHOOK_ADD_URL
      TRUCKERPATH_TRACKING_CREATE_URL
      TRUCKERPATH_TRACKING_URL
      TRUCKERPATH_LIST_LOADS_URL
    """

    name: str = "truckerpath"

    def __init__(self) -> None:
        self.base_url = os.getenv("TRUCKERPATH_BASE_URL", DEFAULT_BASE_URL).rstrip("/")
        token = os.getenv("TRUCKERPATH_API_TOKEN", "").strip()
        self.auth = _bearer(token)
        self.mock_enabled = _bool_env("TRUCKERPATH_ENABLE_MOCK", True)

        # Endpoints
        self.url_post_load = os.getenv("TRUCKERPATH_POST_LOAD_URL", f"{self.base_url}/shipments/v2")
        self.url_create_company = os.getenv("TRUCKERPATH_CREATE_COMPANY_URL", f"{self.base_url}/company/create")
        self.url_register_webhook = os.getenv("TRUCKERPATH_REGISTER_WEBHOOK_URL", f"{self.base_url}/webhooks/register")
        self.url_register_webhook_add = os.getenv("TRUCKERPATH_REGISTER_WEBHOOK_ADD_URL", f"{self.base_url}/webhooks/add")
        self.url_tracking_create = os.getenv("TRUCKERPATH_TRACKING_CREATE_URL", f"{self.base_url}/tracking/").rstrip("/") + "/"
        self.url_tracking_points = os.getenv("TRUCKERPATH_TRACKING_URL", f"{self.base_url}/tracking/update")
        self.url_list_loads = os.getenv("TRUCKERPATH_LIST_LOADS_URL", f"{self.base_url}/loads")

        self.headers = {
            "Authorization": self.auth,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    # ---------------- HTTP helpers ----------------
    async def _post(self, url: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        if self.mock_enabled or not self.auth or not httpx:
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
        if self.mock_enabled or not self.auth or not httpx:
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

    # ---------------- Public API ----------------
    async def ping(self) -> Dict[str, Any]:
        # No official ping endpoint; return consistent stub/mock
        return {"ok": True, "provider": self.name, "mock": self.mock_enabled}

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

    async def list_loads(self, *, limit: int = 10, **params: Any) -> Dict[str, Any]:
        """
        Return normalized loads shape:
          { "ok": True, "loads": [...], "source": "mock"|"live" }
        """
        if self.mock_enabled or not self.auth or not httpx:
            try:
                from backend.integrations.loadboards.mock_truckerpath import get_mock_loads
                loads = get_mock_loads()
            except Exception:
                loads = []
            return {"ok": True, "loads": loads[:limit], "source": "mock"}

        q = {"limit": limit, **params}
        res = await self._get(self.url_list_loads, params=q)
        if not res.get("ok"):
            return {"ok": False, "error": res.get("error")}

        data = res.get("data")
        loads: List[Dict[str, Any]] = []
        if isinstance(data, dict) and "loads" in data:
            loads = list(data.get("loads") or [])
        elif isinstance(data, list):
            loads = data
        elif isinstance(res, dict) and "mock" in res:
            # When provider returned a mock GET response; just surface params
            loads = []
        return {"ok": True, "loads": loads[:limit], "source": "live" if self.auth else "mock"}

    # Backward-compat (service may call pull_loads)
    async def pull_loads(self) -> List[Dict[str, Any]]:
        out = await self.list_loads(limit=50)
        return list(out.get("loads") or [])
