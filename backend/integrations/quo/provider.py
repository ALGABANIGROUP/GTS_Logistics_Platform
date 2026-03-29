from __future__ import annotations

import hashlib
import hmac
import logging
import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import httpx

from backend.integrations.base import BaseProvider, ProviderConfig

logger = logging.getLogger(__name__)

DEFAULT_BASE_URL = "https://api.openphone.com/v1"


class QuoProvider(BaseProvider):
    """
    Quo/OpenPhone provider built on the shared BaseProvider contract.

    The provider focuses on calls, messages, phone numbers, transcripts,
    summaries, and API-created webhook registration while keeping backward
    compatibility with the existing Quo service wrapper.
    """

    name = "quo"

    def __init__(self, config: Optional[ProviderConfig] = None) -> None:
        if config is None:
            config = ProviderConfig(
                provider_id="quo",
                provider_type="webhook",
                base_url=os.getenv("QUO_BASE_URL", DEFAULT_BASE_URL).rstrip("/"),
                api_key=os.getenv("QUO_API_KEY", "").strip() or None,
                api_secret=os.getenv("QUO_API_SECRET", "").strip() or None,
                webhook_secret=os.getenv("QUO_WEBHOOK_SECRET", "").strip() or None,
            )

        super().__init__(config)
        self.provider_name = self.name
        self.base_url = self.config.base_url.rstrip("/")
        self.auth_scheme = (os.getenv("QUO_AUTH_SCHEME", "bearer") or "bearer").strip().lower()

        self.url_phone_numbers = os.getenv("QUO_PHONE_NUMBERS_URL", f"{self.base_url}/phone-numbers")
        self.url_calls = os.getenv("QUO_CALLS_URL", f"{self.base_url}/calls")
        self.url_call_detail = os.getenv("QUO_CALL_DETAIL_URL", f"{self.base_url}/calls/{{call_id}}")
        self.url_call_recordings = os.getenv("QUO_CALL_RECORDINGS_URL", f"{self.base_url}/call-recordings/{{call_id}}")
        self.url_call_summaries = os.getenv("QUO_CALL_SUMMARIES_URL", f"{self.base_url}/call-summaries/{{call_id}}")
        self.url_call_transcripts = os.getenv("QUO_CALL_TRANSCRIPTS_URL", f"{self.base_url}/call-transcripts/{{call_id}}")
        self.url_messages = os.getenv("QUO_MESSAGES_URL", f"{self.base_url}/messages")
        self.url_webhooks_messages = os.getenv("QUO_WEBHOOKS_MESSAGES_URL", f"{self.base_url}/webhooks/messages")
        self.url_webhooks_calls = os.getenv("QUO_WEBHOOKS_CALLS_URL", f"{self.base_url}/webhooks/calls")
        self.url_webhooks_call_summaries = os.getenv(
            "QUO_WEBHOOKS_CALL_SUMMARIES_URL",
            f"{self.base_url}/webhooks/call-summaries",
        )
        self.url_webhooks_call_transcripts = os.getenv(
            "QUO_WEBHOOKS_CALL_TRANSCRIPTS_URL",
            f"{self.base_url}/webhooks/call-transcripts",
        )

    @property
    def auth(self) -> str:
        return self.config.api_key or self._token or ""

    async def _get_auth_headers(self) -> Dict[str, str]:
        token = self.auth
        if not token:
            return {}
        authorization = f"Bearer {token}" if self.auth_scheme == "bearer" else token
        return {
            "Authorization": authorization,
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "GTS-QuoProvider/1.0",
        }

    def _missing_credentials_response(self) -> Dict[str, Any]:
        return {
            "ok": False,
            "status": 503,
            "error": "quo_not_configured",
            "message": "Service unavailable - missing API credentials. Please configure QUO_API_KEY.",
        }

    async def _request_auto(self, method: str, url: str, **kwargs: Any) -> httpx.Response:
        if self._client:
            return await super()._request(method, url, **kwargs)

        async with self:
            return await super()._request(method, url, **kwargs)

    @staticmethod
    def _response_json(response: httpx.Response) -> Any:
        try:
            return response.json()
        except Exception:
            return {"text": response.text}

    async def _request_result(self, method: str, url: str, **kwargs: Any) -> Dict[str, Any]:
        if not self.auth and not (self.config.client_id and self.config.client_secret):
            return self._missing_credentials_response()

        try:
            response = await self._request_auto(method, url, **kwargs)
            data = self._response_json(response)
            ok = response.status_code in (200, 201, 202, 204)
            if ok:
                return {"ok": True, "status": response.status_code, "data": data}
            return {"ok": False, "status": response.status_code, "error": data}
        except Exception as exc:
            logger.error("Quo request failed for %s %s: %s", method, url, exc)
            return {"ok": False, "status": 502, "error": str(exc)}

    @staticmethod
    def _extract_data(payload: Any) -> Any:
        if isinstance(payload, dict) and "data" in payload:
            return payload.get("data")
        return payload

    async def ping(self) -> Dict[str, Any]:
        if not self.auth:
            return self._missing_credentials_response()
        return {"ok": True, "provider": self.provider_name}

    async def health(self) -> Dict[str, Any]:
        return await self.health_check()

    async def health_check(self) -> Dict[str, Any]:
        timestamp = datetime.now(timezone.utc).isoformat()
        if not self.auth:
            result = self._missing_credentials_response()
            return {
                "ok": False,
                "status": "disabled",
                "provider": self.provider_name,
                "timestamp": timestamp,
                **result,
            }

        try:
            response = await self._request_auto("GET", self.url_phone_numbers)
            data = self._response_json(response)
            if response.status_code == 200:
                return {
                    "ok": True,
                    "status": "healthy",
                    "provider": self.provider_name,
                    "timestamp": timestamp,
                    "details": data,
                }
            return {
                "ok": False,
                "status": "unhealthy",
                "provider": self.provider_name,
                "status_code": response.status_code,
                "timestamp": timestamp,
                "details": data,
            }
        except Exception as exc:
            logger.error("Quo health check failed: %s", exc)
            return {
                "ok": False,
                "status": "error",
                "provider": self.provider_name,
                "error": str(exc),
                "timestamp": timestamp,
            }

    async def list_loads(self, **filters: Any) -> List[Dict[str, Any]]:
        return []

    async def get_shipment(self, shipment_id: str) -> Dict[str, Any]:
        return {}

    async def update_shipment(self, shipment_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        return {}

    async def acknowledge_webhook(self, event_id: str) -> bool:
        return bool(event_id)

    async def list_phone_numbers(self) -> List[Dict[str, Any]]:
        if not self.auth:
            return []

        try:
            response = await self._request_auto("GET", self.url_phone_numbers)
            if response.status_code != 200:
                logger.error("Failed to fetch Quo phone numbers: %s", response.status_code)
                return []
            data = self._extract_data(self._response_json(response))
            return list(data or []) if isinstance(data, list) else []
        except Exception as exc:
            logger.error("Error fetching Quo phone numbers: %s", exc)
            return []

    async def list_calls(
        self,
        *,
        phone_number_id: str,
        participants: List[str],
        max_results: int = 10,
        page_token: Optional[str] = None,
        user_id: Optional[str] = None,
        created_after: Optional[str] = None,
        created_before: Optional[str] = None,
    ) -> Dict[str, Any]:
        if not self.auth:
            return {
                **self._missing_credentials_response(),
                "calls": [],
                "source": "disabled",
                "total": 0,
            }

        params: Dict[str, Any] = {
            "phoneNumberId": phone_number_id,
            "participants": participants,
            "maxResults": max_results,
        }
        if page_token:
            params["pageToken"] = page_token
        if user_id:
            params["userId"] = user_id
        if created_after:
            params["createdAfter"] = created_after
        if created_before:
            params["createdBefore"] = created_before

        try:
            response = await self._request_auto("GET", self.url_calls, params=params)
            data = self._response_json(response)
            if response.status_code != 200:
                logger.error("Failed to fetch Quo calls: %s", response.status_code)
                return {
                    "ok": False,
                    "status": response.status_code,
                    "calls": [],
                    "source": "live",
                    "total": 0,
                    "error": data,
                }

            raw_calls = self._extract_data(data)
            calls = [self._standardize_call(item) for item in list(raw_calls or [])]
            return {
                "ok": True,
                "status": response.status_code,
                "calls": calls[:max_results],
                "total": len(calls),
                "next_page_token": data.get("nextPageToken") if isinstance(data, dict) else None,
                "source": "live",
                "raw": data,
            }
        except Exception as exc:
            logger.error("Error fetching Quo calls: %s", exc)
            return {
                "ok": False,
                "status": 502,
                "calls": [],
                "source": "live",
                "total": 0,
                "error": str(exc),
            }

    async def make_outbound_call(
        self,
        *,
        from_number: str,
        to_number: str,
        user_id: Optional[str] = None,
        call_flow: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "from": from_number,
            "to": to_number,
            "direction": "outbound",
        }
        if user_id:
            payload["userId"] = user_id
        if call_flow:
            payload["callFlow"] = call_flow
        return await self._request_result("POST", self.url_calls, json=payload)

    async def get_call(self, call_id: str) -> Dict[str, Any]:
        if not self.auth:
            return {}

        try:
            response = await self._request_auto("GET", self.url_call_detail.format(call_id=call_id))
            if response.status_code != 200:
                logger.error("Quo call %s not found: %s", call_id, response.status_code)
                return {}

            raw = self._extract_data(self._response_json(response))
            if not isinstance(raw, dict):
                return {}
            normalized = self._standardize_call(raw)
            normalized["raw"] = raw
            return normalized
        except Exception as exc:
            logger.error("Error fetching Quo call %s: %s", call_id, exc)
            return {}

    async def get_call_recordings(self, call_id: str) -> List[Dict[str, Any]]:
        if not self.auth:
            return []

        try:
            response = await self._request_auto("GET", self.url_call_recordings.format(call_id=call_id))
            if response.status_code != 200:
                logger.error("Failed to fetch Quo call recordings %s: %s", call_id, response.status_code)
                return []

            data = self._extract_data(self._response_json(response))
            recordings = list(data or []) if isinstance(data, list) else []
            return [self._standardize_recording(item) for item in recordings]
        except Exception as exc:
            logger.error("Error fetching Quo call recordings %s: %s", call_id, exc)
            return []

    async def get_call_summary(self, call_id: str) -> Dict[str, Any]:
        if not self.auth:
            return {}

        try:
            response = await self._request_auto("GET", self.url_call_summaries.format(call_id=call_id))
            if response.status_code != 200:
                logger.error("Failed to fetch Quo call summary %s: %s", call_id, response.status_code)
                return {}

            raw = self._extract_data(self._response_json(response))
            if not isinstance(raw, dict):
                return {}
            return {
                "call_id": raw.get("callId"),
                "status": raw.get("status"),
                "summary": raw.get("summary") or [],
                "next_steps": raw.get("nextSteps") or [],
                "jobs": raw.get("jobs") or [],
                "raw": raw,
            }
        except Exception as exc:
            logger.error("Error fetching Quo call summary %s: %s", call_id, exc)
            return {}

    async def get_call_transcript(self, call_id: str) -> Dict[str, Any]:
        if not self.auth:
            return {}

        try:
            response = await self._request_auto("GET", self.url_call_transcripts.format(call_id=call_id))
            if response.status_code != 200:
                logger.error("Failed to fetch Quo call transcript %s: %s", call_id, response.status_code)
                return {}

            raw = self._extract_data(self._response_json(response))
            if not isinstance(raw, dict):
                return {}
            return {
                "call_id": raw.get("callId"),
                "created_at": raw.get("createdAt"),
                "dialogue": raw.get("dialogue") or [],
                "duration": raw.get("duration"),
                "status": raw.get("status"),
                "raw": raw,
            }
        except Exception as exc:
            logger.error("Error fetching Quo call transcript %s: %s", call_id, exc)
            return {}

    async def send_sms(
        self,
        *,
        from_number: str,
        to_numbers: List[str],
        content: str,
        user_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "from": from_number,
            "to": to_numbers,
            "content": content,
        }
        if user_id:
            payload["userId"] = user_id
        return await self._request_result("POST", self.url_messages, json=payload)

    async def create_webhook(
        self,
        *,
        url: str,
        event_types: List[str],
        description: str = "AI Calls Webhook",
        resource_ids: Optional[List[str]] = None,
        user_id: Optional[str] = None,
        status: str = "enabled",
    ) -> Dict[str, Any]:
        endpoint = self._resolve_webhook_endpoint(event_types)
        if not endpoint:
            return {
                "ok": False,
                "status": 400,
                "error": "unsupported_webhook_events",
                "message": "Webhook events must belong to a single Quo webhook family.",
            }

        payload: Dict[str, Any] = {
            "url": url,
            "events": event_types,
            "label": description,
            "status": status,
        }
        if resource_ids:
            payload["resourceIds"] = resource_ids
        if user_id:
            payload["userId"] = user_id
        return await self._request_result("POST", endpoint, json=payload)

    def verify_event_signature(
        self,
        payload: bytes,
        signature: str,
        timestamp: str,
        *,
        prefix: str = "v1=",
    ) -> bool:
        if not self.config.webhook_secret:
            logger.warning("Quo webhook secret not configured")
            return False
        if not signature or not timestamp:
            return False

        clean_signature = signature[len(prefix):] if signature.startswith(prefix) else signature
        message = f"{timestamp}.{payload.decode('utf-8', 'ignore')}"
        computed = hmac.new(
            self.config.webhook_secret.encode(),
            message.encode(),
            hashlib.sha256,
        ).hexdigest()
        return hmac.compare_digest(computed, clean_signature)

    def _resolve_webhook_endpoint(self, event_types: List[str]) -> Optional[str]:
        events = [event for event in list(event_types or []) if event]
        if not events:
            return None

        if all(event.startswith("message.") for event in events):
            return self.url_webhooks_messages
        if all(event.startswith("call.summary.") for event in events):
            return self.url_webhooks_call_summaries
        if all(event.startswith("call.transcript.") for event in events):
            return self.url_webhooks_call_transcripts
        if all(event.startswith("call.") for event in events):
            return self.url_webhooks_calls
        return None

    def _standardize_call(self, external_call: Dict[str, Any]) -> Dict[str, Any]:
        participants = external_call.get("participants") or []
        return {
            "external_id": external_call.get("id"),
            "phone_number_id": external_call.get("phoneNumberId"),
            "user_id": external_call.get("userId"),
            "direction": external_call.get("direction"),
            "status": external_call.get("status"),
            "duration": external_call.get("duration"),
            "participants": participants,
            "answered_at": external_call.get("answeredAt"),
            "answered_by": external_call.get("answeredBy"),
            "initiated_by": external_call.get("initiatedBy"),
            "completed_at": external_call.get("completedAt"),
            "created_at": external_call.get("createdAt"),
            "updated_at": external_call.get("updatedAt"),
            "call_route": external_call.get("callRoute"),
            "forwarded_from": external_call.get("forwardedFrom"),
            "forwarded_to": external_call.get("forwardedTo"),
            "ai_handled": external_call.get("aiHandled"),
            "source": self.provider_name,
        }

    def _standardize_recording(self, external_recording: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "external_id": external_recording.get("id"),
            "status": external_recording.get("status"),
            "duration": external_recording.get("duration"),
            "type": external_recording.get("type"),
            "start_time": external_recording.get("startTime"),
            "url": external_recording.get("url"),
            "source": self.provider_name,
        }
