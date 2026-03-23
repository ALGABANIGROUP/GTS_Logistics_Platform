from __future__ import annotations

import os
import logging
from typing import Any, Dict, List, Optional

import httpx

logger = logging.getLogger(__name__)


class QuoAPIClient:
    """Lightweight client for Quo (OpenPhone) API using httpx.AsyncClient.

    Notes:
    - Reads QUO_API_KEY from environment; if missing, the client is disabled and
      methods return an error dict.
    - Uses JSON responses and returns dicts consistently.
    - No exceptions are raised outward; errors are logged and returned.
    """

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None) -> None:
        self.api_key = (api_key or os.getenv("QUO_API_KEY") or "").strip()
        self.base_url = (base_url or os.getenv("QUO_BASE_URL") or "https://api.openphone.com/v1").rstrip("/")
        self.enabled = bool(self.api_key)

    def _headers(self) -> Dict[str, str]:
        token = self.api_key
        scheme = (os.getenv("QUO_AUTH_SCHEME") or "bearer").strip().lower()
        auth_header = f"Bearer {token}" if scheme == "bearer" else token
        return {
            "Authorization": auth_header,
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "GTS-QuoClient/1.0",
        }

    def _client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(timeout=httpx.Timeout(20.0, connect=10.0), follow_redirects=True)

    async def make_outbound_call(
        self,
        *,
        from_number: str,
        to_number: str,
        user_id: Optional[str] = None,
        call_flow: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        if not self.enabled:
            return {"error": "QUO_API_KEY not configured"}
        url = f"{self.base_url}/calls"
        payload: Dict[str, Any] = {
            "from": from_number,
            "to": to_number,
            "direction": "outbound",
        }
        if user_id:
            payload["userId"] = user_id
        if call_flow:
            payload["callFlow"] = call_flow
        try:
            async with self._client() as client:
                r = await client.post(url, headers=self._headers(), json=payload)
                data = r.json() if r.headers.get("content-type", "").startswith("application/json") else {"status": r.status_code, "text": await r.aread()}
                if r.status_code in (200, 201, 202):
                    return data
                logger.error("Quo make_outbound_call failed: %s %s", r.status_code, data)
                return {"error": f"status={r.status_code}", "data": data}
        except Exception as e:
            logger.exception("Quo make_outbound_call exception: %s", e)
            return {"error": str(e)}

    async def get_call_by_id(self, call_id: str) -> Dict[str, Any]:
        if not self.enabled:
            return {"error": "QUO_API_KEY not configured"}
        url = f"{self.base_url}/calls/{call_id}"
        try:
            async with self._client() as client:
                r = await client.get(url, headers=self._headers())
                return r.json() if r.status_code == 200 else {"error": f"status={r.status_code}", "data": r.text}
        except Exception as e:
            logger.exception("Quo get_call_by_id exception: %s", e)
            return {"error": str(e)}

    async def get_call_summary(self, call_id: str) -> Dict[str, Any]:
        if not self.enabled:
            return {"error": "QUO_API_KEY not configured"}
        url = f"{self.base_url}/calls/{call_id}/summary"
        try:
            async with self._client() as client:
                r = await client.get(url, headers=self._headers())
                return r.json() if r.status_code == 200 else {"error": f"status={r.status_code}", "data": r.text}
        except Exception as e:
            logger.exception("Quo get_call_summary exception: %s", e)
            return {"error": str(e)}

    async def get_call_transcript(self, call_id: str) -> Dict[str, Any]:
        if not self.enabled:
            return {"error": "QUO_API_KEY not configured"}
        url = f"{self.base_url}/calls/{call_id}/transcript"
        try:
            async with self._client() as client:
                r = await client.get(url, headers=self._headers())
                return r.json() if r.status_code == 200 else {"error": f"status={r.status_code}", "data": r.text}
        except Exception as e:
            logger.exception("Quo get_call_transcript exception: %s", e)
            return {"error": str(e)}

    async def send_sms(
        self,
        *,
        from_number: str,
        to_numbers: List[str],
        content: str,
        user_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        if not self.enabled:
            return {"error": "QUO_API_KEY not configured"}
        url = f"{self.base_url}/messages"
        payload: Dict[str, Any] = {
            "from": from_number,
            "to": to_numbers,
            "content": content,
        }
        if user_id:
            payload["userId"] = user_id
        try:
            async with self._client() as client:
                r = await client.post(url, headers=self._headers(), json=payload)
                data = r.json() if r.headers.get("content-type", "").startswith("application/json") else {"status": r.status_code, "text": await r.aread()}
                if r.status_code in (200, 201, 202):
                    return data
                logger.error("Quo send_sms failed: %s %s", r.status_code, data)
                return {"error": f"status={r.status_code}", "data": data}
        except Exception as e:
            logger.exception("Quo send_sms exception: %s", e)
            return {"error": str(e)}

    async def list_phone_numbers(self) -> List[Dict[str, Any]]:
        if not self.enabled:
            return []
        url = f"{self.base_url}/phone-numbers"
        try:
            async with self._client() as client:
                r = await client.get(url, headers=self._headers())
                data = r.json() if r.status_code == 200 else {"error": f"status={r.status_code}", "data": r.text}
                if isinstance(data, dict) and "data" in data:
                    value = data.get("data")
                    return value if isinstance(value, list) else []
                return []
        except Exception as e:
            logger.exception("Quo list_phone_numbers exception: %s", e)
            return []

    async def create_webhook(self, *, url: str, event_types: List[str], description: str = "AI Calls Webhook") -> Dict[str, Any]:
        if not self.enabled:
            return {"error": "QUO_API_KEY not configured"}
        endpoint = f"{self.base_url}/webhooks"
        payload = {
            "url": url,
            "eventTypes": event_types,
            "description": description,
        }
        try:
            async with self._client() as client:
                r = await client.post(endpoint, headers=self._headers(), json=payload)
                data = r.json() if r.headers.get("content-type", "").startswith("application/json") else {"status": r.status_code, "text": await r.aread()}
                if r.status_code in (200, 201):
                    return data
                logger.error("Quo create_webhook failed: %s %s", r.status_code, data)
                return {"error": f"status={r.status_code}", "data": data}
        except Exception as e:
            logger.exception("Quo create_webhook exception: %s", e)
            return {"error": str(e)}

    async def get_call_recordings(self, call_id: str) -> List[Dict[str, Any]]:
        if not self.enabled:
            return []
        url = f"{self.base_url}/calls/{call_id}/recordings"
        try:
            async with self._client() as client:
                r = await client.get(url, headers=self._headers())
                if r.status_code == 200:
                    data = r.json()
                    if isinstance(data, dict) and "data" in data:
                        value = data.get("data")
                        return value if isinstance(value, list) else []
                return []
        except Exception as e:
            logger.exception("Quo get_call_recordings exception: %s", e)
            return []


_client_singleton: Optional[QuoAPIClient] = None


def get_quo_client() -> QuoAPIClient:
    global _client_singleton
    if _client_singleton is None:
        _client_singleton = QuoAPIClient()
    return _client_singleton
