from __future__ import annotations

import logging
import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import httpx

from backend.integrations.base import BaseProvider, ProviderConfig

logger = logging.getLogger(__name__)

DEFAULT_BASE_URL = "https://api.wise.com/v1"


class WiseProvider(BaseProvider):
    """
    Wise provider built on the shared BaseProvider contract.

    This provider focuses on transfer management and webhook acknowledgement
    while keeping a minimal compatibility surface for future payment routes.
    """

    name = "wise"

    def __init__(self, config: Optional[ProviderConfig] = None) -> None:
        if config is None:
            config = ProviderConfig(
                provider_id="wise",
                provider_type="payment",
                base_url=os.getenv("WISE_BASE_URL", DEFAULT_BASE_URL).rstrip("/"),
                api_key=os.getenv("WISE_API_KEY", "").strip() or None,
                api_secret=os.getenv("WISE_API_SECRET", "").strip() or None,
                webhook_secret=os.getenv("WISE_WEBHOOK_SECRET", "").strip() or None,
            )

        super().__init__(config)
        self.provider_name = self.name
        self.base_url = self.config.base_url.rstrip("/")
        self.profile_id = (os.getenv("WISE_PROFILE_ID", "").strip() or self.config.client_id or "").strip()

        self.url_profiles = os.getenv("WISE_PROFILES_URL", f"{self.base_url}/profiles")
        self.url_balances = os.getenv("WISE_BALANCES_URL", f"{self.base_url}/profiles/{{profile_id}}/balances")
        self.url_transfers = os.getenv("WISE_TRANSFERS_URL", f"{self.base_url}/profiles/{{profile_id}}/transfers")
        self.url_transfer_detail = os.getenv("WISE_TRANSFER_DETAIL_URL", f"{self.base_url}/transfers/{{transfer_id}}")
        self.url_webhook_ack = os.getenv("WISE_WEBHOOK_ACK_URL", f"{self.base_url}/webhooks/ack")

    @property
    def auth(self) -> str:
        return self.config.api_key or self._token or ""

    def _missing_credentials_response(self) -> Dict[str, Any]:
        return {
            "ok": False,
            "status": 503,
            "error": "wise_not_configured",
            "message": "Service unavailable - missing API credentials. Please configure WISE_API_KEY.",
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
            ok = response.status_code in (200, 201, 202)
            if ok:
                return {"ok": True, "status": response.status_code, "data": data}
            return {"ok": False, "status": response.status_code, "error": data}
        except Exception as exc:
            logger.error("Wise request failed for %s %s: %s", method, url, exc)
            return {"ok": False, "status": 502, "error": str(exc)}

    def _get_profile_id(self, profile_id: Optional[str] = None) -> str:
        return (profile_id or self.profile_id or "").strip()

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
            response = await self._request_auto("GET", self.url_profiles)
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
            logger.error("Wise health check failed: %s", exc)
            return {
                "ok": False,
                "status": "error",
                "provider": self.provider_name,
                "error": str(exc),
                "timestamp": timestamp,
            }

    async def list_loads(self, **filters: Any) -> List[Dict[str, Any]]:
        """Not applicable for Wise; kept only to satisfy BaseProvider."""
        return []

    async def get_shipment(self, shipment_id: str) -> Dict[str, Any]:
        """Not applicable for Wise; kept only to satisfy BaseProvider."""
        return {}

    async def update_shipment(self, shipment_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Not applicable for Wise; kept only to satisfy BaseProvider."""
        return {}

    async def list_transfers(
        self,
        *,
        profile_id: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
        status: Optional[str] = None,
        **filters: Any,
    ) -> Dict[str, Any]:
        if not self.auth:
            return {
                **self._missing_credentials_response(),
                "transfers": [],
                "source": "disabled",
                "total": 0,
            }

        resolved_profile_id = self._get_profile_id(profile_id)
        if not resolved_profile_id:
            return {
                "ok": False,
                "status": 400,
                "error": "wise_profile_missing",
                "message": "WISE_PROFILE_ID is required to list transfers.",
                "transfers": [],
                "source": "disabled",
                "total": 0,
            }

        params: Dict[str, Any] = {"limit": limit, "offset": offset, **filters}
        if status:
            params["status"] = status

        try:
            response = await self._request_auto(
                "GET",
                self.url_transfers.format(profile_id=resolved_profile_id),
                params=params,
            )
            if response.status_code != 200:
                logger.error("Failed to fetch Wise transfers: %s", response.status_code)
                return {
                    "ok": False,
                    "status": response.status_code,
                    "transfers": [],
                    "source": "live",
                    "total": 0,
                    "error": self._response_json(response),
                }

            data = self._response_json(response)
            raw_transfers = data.get("transfers", []) if isinstance(data, dict) else data
            transfers = [self._standardize_transfer(item) for item in list(raw_transfers or [])]
            return {
                "ok": True,
                "status": response.status_code,
                "transfers": transfers[:limit],
                "total": len(transfers),
                "source": "live",
            }
        except Exception as exc:
            logger.error("Error fetching Wise transfers: %s", exc)
            return {
                "ok": False,
                "status": 502,
                "transfers": [],
                "source": "live",
                "total": 0,
                "error": str(exc),
            }

    async def get_transfer(self, transfer_id: str) -> Dict[str, Any]:
        if not self.auth:
            return {}

        try:
            response = await self._request_auto(
                "GET",
                self.url_transfer_detail.format(transfer_id=transfer_id),
            )
            if response.status_code == 200:
                return self._standardize_transfer(self._response_json(response))

            logger.error("Wise transfer %s not found: %s", transfer_id, response.status_code)
            return {}
        except Exception as exc:
            logger.error("Error fetching Wise transfer %s: %s", transfer_id, exc)
            return {}

    async def create_transfer(
        self,
        quote_id: str,
        customer_transaction_id: str,
        recipient_id: str,
        *,
        profile_id: Optional[str] = None,
        **extra: Any,
    ) -> Dict[str, Any]:
        if not self.auth:
            return self._missing_credentials_response()

        resolved_profile_id = self._get_profile_id(profile_id)
        if not resolved_profile_id:
            return {
                "ok": False,
                "status": 400,
                "error": "wise_profile_missing",
                "message": "WISE_PROFILE_ID is required to create transfers.",
            }

        payload = {
            "quoteId": quote_id,
            "customerTransactionId": customer_transaction_id,
            "targetAccountId": recipient_id,
            **extra,
        }
        result = await self._request_result(
            "POST",
            self.url_transfers.format(profile_id=resolved_profile_id),
            json=payload,
        )
        if result.get("ok"):
            data = result.get("data") or {}
            return {
                "ok": True,
                "status": result.get("status", 200),
                "transfer": self._standardize_transfer(data),
            }
        return result

    async def acknowledge_webhook(self, event_id: str) -> bool:
        result = await self._request_result("POST", self.url_webhook_ack, json={"event_id": event_id})
        return bool(result.get("ok"))

    async def get_balance(self, currency: str = "CAD", *, profile_id: Optional[str] = None) -> Dict[str, Any]:
        if not self.auth:
            return self._missing_credentials_response()

        resolved_profile_id = self._get_profile_id(profile_id)
        if not resolved_profile_id:
            return {
                "ok": False,
                "status": 400,
                "error": "wise_profile_missing",
                "message": "WISE_PROFILE_ID is required to get balances.",
            }

        try:
            response = await self._request_auto(
                "GET",
                self.url_balances.format(profile_id=resolved_profile_id),
            )
            if response.status_code != 200:
                logger.error("Failed to fetch Wise balances: %s", response.status_code)
                return {
                    "ok": False,
                    "status": response.status_code,
                    "error": self._response_json(response),
                }

            balances = self._response_json(response)
            for balance in list(balances or []):
                if balance.get("currency") == currency:
                    amount = (balance.get("amount") or {}).get("value", 0)
                    return {
                        "ok": True,
                        "currency": currency,
                        "amount": amount,
                    }
            return {"ok": True, "currency": currency, "amount": 0}
        except Exception as exc:
            logger.error("Error fetching Wise balance: %s", exc)
            return {
                "ok": False,
                "status": 502,
                "error": str(exc),
            }

    def _standardize_transfer(self, external_transfer: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "external_id": external_transfer.get("id"),
            "status": external_transfer.get("status"),
            "quote_id": external_transfer.get("quoteUuid") or external_transfer.get("quoteId"),
            "customer_transaction_id": external_transfer.get("customerTransactionId"),
            "target_account_id": external_transfer.get("targetAccount") or external_transfer.get("targetAccountId"),
            "source_currency": external_transfer.get("sourceCurrency"),
            "target_currency": external_transfer.get("targetCurrency"),
            "source_amount": external_transfer.get("sourceValue"),
            "target_amount": external_transfer.get("targetValue"),
            "created_at": external_transfer.get("created") or external_transfer.get("created_at"),
            "updated_at": external_transfer.get("modified") or external_transfer.get("updated_at"),
            "source": self.provider_name,
        }
