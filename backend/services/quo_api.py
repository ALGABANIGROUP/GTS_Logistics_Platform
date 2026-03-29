from __future__ import annotations

import os
import logging
from typing import Any, Dict, List, Optional

from backend.integrations import ProviderConfig, QuoProvider

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
        self.provider = QuoProvider(
            ProviderConfig(
                provider_id="quo",
                provider_type="webhook",
                base_url=self.base_url,
                api_key=self.api_key or None,
                api_secret=(os.getenv("QUO_API_SECRET") or "").strip() or None,
                webhook_secret=(os.getenv("QUO_WEBHOOK_SECRET") or "").strip() or None,
            )
        )
        self.enabled = bool(self.api_key)

    @staticmethod
    def _legacy_error(result: Dict[str, Any]) -> Dict[str, Any]:
        error = result.get("error")
        if isinstance(error, dict):
            return {"error": f"status={result.get('status', 500)}", "data": error}
        if error:
            return {"error": str(error), "data": result.get("data")}
        return {"error": f"status={result.get('status', 500)}", "data": result.get("data")}

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
        result = await self.provider.make_outbound_call(
            from_number=from_number,
            to_number=to_number,
            user_id=user_id,
            call_flow=call_flow,
        )
        if result.get("ok"):
            data = result.get("data")
            return data if isinstance(data, dict) else {"data": data}
        logger.error("Quo make_outbound_call failed: %s", result)
        return self._legacy_error(result)

    async def get_call_by_id(self, call_id: str) -> Dict[str, Any]:
        if not self.enabled:
            return {"error": "QUO_API_KEY not configured"}
        try:
            result = await self.provider.get_call(call_id)
            if result:
                raw = result.get("raw")
                return raw if isinstance(raw, dict) else result
            return {"error": "status=404", "data": {}}
        except Exception as e:
            logger.exception("Quo get_call_by_id exception: %s", e)
            return {"error": str(e)}

    async def get_call_summary(self, call_id: str) -> Dict[str, Any]:
        if not self.enabled:
            return {"error": "QUO_API_KEY not configured"}
        try:
            result = await self.provider.get_call_summary(call_id)
            if result:
                raw = result.get("raw")
                return raw if isinstance(raw, dict) else result
            return {"error": "status=404", "data": {}}
        except Exception as e:
            logger.exception("Quo get_call_summary exception: %s", e)
            return {"error": str(e)}

    async def get_call_transcript(self, call_id: str) -> Dict[str, Any]:
        if not self.enabled:
            return {"error": "QUO_API_KEY not configured"}
        try:
            result = await self.provider.get_call_transcript(call_id)
            if result:
                raw = result.get("raw")
                return raw if isinstance(raw, dict) else result
            return {"error": "status=404", "data": {}}
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
        result = await self.provider.send_sms(
            from_number=from_number,
            to_numbers=to_numbers,
            content=content,
            user_id=user_id,
        )
        if result.get("ok"):
            data = result.get("data")
            return data if isinstance(data, dict) else {"data": data}
        logger.error("Quo send_sms failed: %s", result)
        return self._legacy_error(result)

    async def list_phone_numbers(self) -> List[Dict[str, Any]]:
        if not self.enabled:
            return []
        try:
            return await self.provider.list_phone_numbers()
        except Exception as e:
            logger.exception("Quo list_phone_numbers exception: %s", e)
            return []

    async def create_webhook(self, *, url: str, event_types: List[str], description: str = "AI Calls Webhook") -> Dict[str, Any]:
        if not self.enabled:
            return {"error": "QUO_API_KEY not configured"}
        result = await self.provider.create_webhook(url=url, event_types=event_types, description=description)
        if result.get("ok"):
            data = result.get("data")
            return data if isinstance(data, dict) else {"data": data}
        logger.error("Quo create_webhook failed: %s", result)
        return self._legacy_error(result)

    async def get_call_recordings(self, call_id: str) -> List[Dict[str, Any]]:
        if not self.enabled:
            return []
        try:
            return await self.provider.get_call_recordings(call_id)
        except Exception as e:
            logger.exception("Quo get_call_recordings exception: %s", e)
            return []


_client_singleton: Optional[QuoAPIClient] = None


def get_quo_client() -> QuoAPIClient:
    global _client_singleton
    if _client_singleton is None:
        _client_singleton = QuoAPIClient()
    return _client_singleton
