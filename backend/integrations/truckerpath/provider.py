from __future__ import annotations

import logging
import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import httpx

from backend.integrations.base import BaseProvider, ProviderConfig

logger = logging.getLogger(__name__)

DEFAULT_BASE_URL = "https://test-api.truckerpath.com/truckload/api"


class TruckerPathProvider(BaseProvider):
    """
    TruckerPath integration provider built on top of BaseProvider.

    This keeps backward compatibility with the existing service and route
    layer while also exposing the normalized provider contract used by the
    new integrations package.
    """

    name = "truckerpath"

    def __init__(self, config: Optional[ProviderConfig] = None) -> None:
        if config is None:
            config = ProviderConfig(
                provider_id="truckerpath",
                provider_type="loadboard",
                base_url=os.getenv("TRUCKERPATH_BASE_URL", DEFAULT_BASE_URL).rstrip("/"),
                api_key=(
                    os.getenv("TRUCKERPATH_API_TOKEN", "").strip()
                    or os.getenv("TRUCKERPATH_API_KEY", "").strip()
                    or None
                ),
                api_secret=os.getenv("TRUCKERPATH_API_SECRET", "").strip() or None,
                webhook_secret=os.getenv("TRUCKERPATH_WEBHOOK_SECRET", "").strip() or None,
            )

        super().__init__(config)
        self.provider_name = self.name
        self.base_url = self.config.base_url.rstrip("/")

        self.url_health = os.getenv("TRUCKERPATH_HEALTH_URL", f"{self.base_url}/health")
        self.url_post_load = os.getenv("TRUCKERPATH_POST_LOAD_URL", f"{self.base_url}/shipments/v2")
        self.url_create_company = os.getenv("TRUCKERPATH_CREATE_COMPANY_URL", f"{self.base_url}/company/create")
        self.url_register_webhook = os.getenv("TRUCKERPATH_REGISTER_WEBHOOK_URL", f"{self.base_url}/webhooks/register")
        self.url_register_webhook_add = os.getenv(
            "TRUCKERPATH_REGISTER_WEBHOOK_ADD_URL",
            f"{self.base_url}/webhooks/add",
        )
        self.url_tracking_create = os.getenv("TRUCKERPATH_TRACKING_CREATE_URL", f"{self.base_url}/tracking/").rstrip("/") + "/"
        self.url_tracking_points = os.getenv("TRUCKERPATH_TRACKING_URL", f"{self.base_url}/tracking/update")
        self.url_list_loads = os.getenv("TRUCKERPATH_LIST_LOADS_URL", f"{self.base_url}/loads")
        self.url_rates = os.getenv("TRUCKERPATH_RATES_URL", f"{self.base_url}/rates")

    @property
    def auth(self) -> str:
        return self.config.api_key or self._token or ""

    def _missing_credentials_response(self) -> Dict[str, Any]:
        return {
            "ok": False,
            "status": 503,
            "error": "truckerpath_not_configured",
            "message": "Service unavailable - missing API credentials. Please configure TRUCKERPATH_API_TOKEN.",
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
            logger.error("TruckerPath request failed for %s %s: %s", method, url, exc)
            return {"ok": False, "status": 502, "error": str(exc)}

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
            response = await self._request_auto("GET", self.url_health)
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
            logger.error("TruckerPath health check failed: %s", exc)
            return {
                "ok": False,
                "status": "error",
                "provider": self.provider_name,
                "error": str(exc),
                "timestamp": timestamp,
            }

    async def create_company(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return await self._request_result("POST", self.url_create_company, json=payload)

    async def register_webhook(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return await self._request_result("POST", self.url_register_webhook, json=payload)

    async def register_webhook_add(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return await self._request_result("POST", self.url_register_webhook_add, json=payload)

    async def tracking_create(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return await self._request_result("POST", self.url_tracking_create, json=payload)

    async def push_tracking_points(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return await self._request_result("POST", self.url_tracking_points, json=payload)

    async def list_loads(
        self,
        *,
        origin: Optional[str] = None,
        destination: Optional[str] = None,
        equipment: Optional[str] = None,
        equipment_type: Optional[str] = None,
        min_rate: Optional[float] = None,
        max_rate: Optional[float] = None,
        limit: int = 100,
        offset: int = 0,
        **filters: Any,
    ) -> Dict[str, Any]:
        if not self.auth:
            return {
                **self._missing_credentials_response(),
                "loads": [],
                "source": "disabled",
                "total": 0,
            }

        params: Dict[str, Any] = {"limit": limit, "offset": offset, **filters}
        if origin:
            params["origin"] = origin
        if destination:
            params["destination"] = destination
        if equipment_type or equipment:
            params["equipment_type"] = equipment_type or equipment
        if min_rate is not None:
            params["min_rate"] = min_rate
        if max_rate is not None:
            params["max_rate"] = max_rate

        try:
            response = await self._request_auto("GET", self.url_list_loads, params=params)
            if response.status_code != 200:
                logger.error("Failed to fetch TruckerPath loads: %s", response.status_code)
                return {
                    "ok": False,
                    "status": response.status_code,
                    "loads": [],
                    "source": "live",
                    "total": 0,
                    "error": self._response_json(response),
                }

            data = self._response_json(response)
            raw_loads = data.get("loads", []) if isinstance(data, dict) else data
            loads = [self._standardize_load(load) for load in list(raw_loads or [])]
            return {
                "ok": True,
                "status": response.status_code,
                "loads": loads[:limit],
                "total": len(loads),
                "source": "live",
            }
        except Exception as exc:
            logger.error("Error fetching TruckerPath loads: %s", exc)
            return {
                "ok": False,
                "status": 502,
                "loads": [],
                "source": "live",
                "total": 0,
                "error": str(exc),
            }

    async def pull_loads(self) -> List[Dict[str, Any]]:
        result = await self.list_loads(limit=50)
        return list(result.get("loads") or [])

    async def get_shipment(self, shipment_id: str) -> Dict[str, Any]:
        if not self.auth:
            return {}

        try:
            response = await self._request_auto("GET", f"{self.base_url}/shipments/{shipment_id}")
            if response.status_code == 200:
                return self._standardize_shipment(self._response_json(response))

            logger.error("Shipment %s not found: %s", shipment_id, response.status_code)
            return {}
        except Exception as exc:
            logger.error("Error fetching shipment %s: %s", shipment_id, exc)
            return {}

    async def update_shipment(self, shipment_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        if not self.auth:
            return {}

        try:
            response = await self._request_auto("PATCH", f"{self.base_url}/shipments/{shipment_id}", json=data)
            if response.status_code == 200:
                return self._response_json(response)

            logger.error("Failed to update shipment %s: %s", shipment_id, response.status_code)
            return {}
        except Exception as exc:
            logger.error("Error updating shipment %s: %s", shipment_id, exc)
            return {}

    async def acknowledge_webhook(self, event_id: str) -> bool:
        result = await self._request_result("POST", f"{self.base_url}/webhooks/ack", json={"event_id": event_id})
        return bool(result.get("ok"))

    async def post_load(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return await self._request_result("POST", self.url_post_load, json=payload)

    async def get_rates(self, origin: str, destination: str) -> Dict[str, Any]:
        if not self.auth:
            return {}

        try:
            response = await self._request_auto(
                "GET",
                self.url_rates,
                params={"origin": origin, "destination": destination},
            )
            if response.status_code == 200:
                return self._response_json(response)

            logger.error("Failed to fetch rates: %s", response.status_code)
            return {}
        except Exception as exc:
            logger.error("Error fetching TruckerPath rates: %s", exc)
            return {}

    def _standardize_load(self, external_load: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "external_id": external_load.get("id"),
            "origin": (external_load.get("origin") or {}).get("city"),
            "origin_lat": (external_load.get("origin") or {}).get("lat"),
            "origin_lng": (external_load.get("origin") or {}).get("lng"),
            "destination": (external_load.get("destination") or {}).get("city"),
            "destination_lat": (external_load.get("destination") or {}).get("lat"),
            "destination_lng": (external_load.get("destination") or {}).get("lng"),
            "equipment_type": external_load.get("equipment_type"),
            "rate": external_load.get("rate"),
            "rate_unit": external_load.get("rate_unit", "CAD"),
            "distance_miles": external_load.get("distance_miles"),
            "pickup_date": external_load.get("pickup_date"),
            "delivery_date": external_load.get("delivery_date"),
            "carrier_requirements": external_load.get("carrier_requirements", {}),
            "status": external_load.get("status"),
            "created_at": external_load.get("created_at"),
            "updated_at": external_load.get("updated_at"),
            "source": self.provider_name,
        }

    def _standardize_shipment(self, external_shipment: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "external_id": external_shipment.get("id"),
            "load_id": external_shipment.get("load_id"),
            "carrier_id": external_shipment.get("carrier_id"),
            "status": external_shipment.get("status"),
            "tracking_number": external_shipment.get("tracking_number"),
            "current_location": external_shipment.get("current_location"),
            "last_update": external_shipment.get("last_update"),
            "estimated_delivery": external_shipment.get("estimated_delivery"),
            "actual_delivery": external_shipment.get("actual_delivery"),
            "events": external_shipment.get("events", []),
            "source": self.provider_name,
        }
