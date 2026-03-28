import asyncio
import hashlib
import hmac
import logging
from abc import ABC, abstractmethod
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

import httpx
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

DEFAULT_RATE_LIMITS: Dict[str, int] = {
    "loadboard": 60,
    "carrier": 120,
    "payment": 30,
    "tracking": 300,
    "webhook": 500,
}


class ProviderConfig(BaseModel):
    """Base configuration for any integration provider."""

    provider_id: str
    provider_type: str  # loadboard, carrier, payment, tracking, webhook
    base_url: str
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    webhook_secret: Optional[str] = None
    timeout_connect: int = 5
    timeout_read: int = 30
    max_retries: int = 3
    rate_limit_per_minute: Optional[int] = None
    retry_on_status: List[int] = Field(default_factory=lambda: [429, 500, 502, 503, 504])

    @property
    def effective_rate_limit_per_minute(self) -> int:
        if self.rate_limit_per_minute is not None:
            return self.rate_limit_per_minute
        return DEFAULT_RATE_LIMITS.get(self.provider_type.lower(), 60)


class BaseProvider(ABC):
    """Abstract base class for all integration providers."""

    def __init__(self, config: ProviderConfig):
        self.config = config
        self._token: Optional[str] = None
        self._token_expiry: Optional[datetime] = None
        self._client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self):
        self._client = httpx.AsyncClient(
            base_url=self.config.base_url,
            timeout=httpx.Timeout(
                connect=self.config.timeout_connect,
                read=self.config.timeout_read,
                write=self.config.timeout_read,
                pool=self.config.timeout_read,
            ),
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._client:
            await self._client.aclose()

    async def _get_auth_headers(self) -> Dict[str, str]:
        """Return authentication headers based on configured auth type."""
        if self.config.api_key:
            return {"Authorization": f"Bearer {self.config.api_key}"}
        if self._token:
            return {"Authorization": f"Bearer {self._token}"}
        return {}

    async def _refresh_token(self) -> bool:
        """Refresh OAuth2 token if needed. Override for provider-specific OAuth2 logic."""
        if self.config.client_id and self.config.client_secret:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(
                    f"{self.config.base_url}/oauth/token",
                    data={
                        "grant_type": "client_credentials",
                        "client_id": self.config.client_id,
                        "client_secret": self.config.client_secret,
                    },
                )
                if response.status_code == 200:
                    data = response.json()
                    self._token = data.get("access_token")
                    expires_in = int(data.get("expires_in", 3600))
                    self._token_expiry = datetime.now(timezone.utc) + timedelta(seconds=max(0, expires_in - 300))
                    return True
        return False

    async def _request(self, method: str, path: str, **kwargs) -> httpx.Response:
        """Make HTTP request with retry logic and optional token refresh."""
        if not self._client:
            raise RuntimeError("Provider not opened. Use async context manager.")

        retries = 0
        last_error: Optional[Exception] = None

        while retries <= self.config.max_retries:
            try:
                headers = dict(kwargs.pop("headers", {}) or {})
                headers.update(await self._get_auth_headers())

                response = await self._client.request(
                    method=method,
                    url=path,
                    headers=headers,
                    **kwargs,
                )

                if response.status_code == 401 and retries < self.config.max_retries:
                    if await self._refresh_token():
                        retries += 1
                        continue

                if response.status_code in self.config.retry_on_status:
                    retries += 1
                    wait_time = 2**retries
                    logger.warning(
                        "Retry %s/%s for %s %s after status=%s",
                        retries,
                        self.config.max_retries,
                        method,
                        path,
                        response.status_code,
                    )
                    await self._async_sleep(wait_time)
                    continue

                return response

            except Exception as exc:  # pragma: no cover - network path
                last_error = exc
                retries += 1
                if retries <= self.config.max_retries:
                    wait_time = 2**retries
                    logger.warning("Retry %s after error: %s", retries, exc)
                    await self._async_sleep(wait_time)
                else:
                    break

        raise RuntimeError(
            f"Request failed after {self.config.max_retries} retries: {last_error}"
        )

    @staticmethod
    async def _async_sleep(seconds: int) -> None:
        await asyncio.sleep(seconds)

    def verify_webhook_signature(
        self,
        payload: bytes,
        signature: str,
        timestamp: Optional[str] = None,
    ) -> bool:
        """Verify HMAC SHA256 signature for incoming webhooks."""
        if not self.config.webhook_secret:
            logger.warning("Webhook secret not configured")
            return False

        if timestamp:
            try:
                parsed_ts = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                if parsed_ts.tzinfo is None:
                    parsed_ts = parsed_ts.replace(tzinfo=timezone.utc)
                now_utc = datetime.now(timezone.utc)
                if now_utc - parsed_ts > timedelta(minutes=5):
                    logger.warning("Webhook timestamp outside replay window")
                    return False
            except Exception:
                logger.warning("Webhook timestamp parsing failed")
                return False

        clean_signature = signature.replace("sha256=", "")
        computed = hmac.new(
            self.config.webhook_secret.encode(),
            payload,
            hashlib.sha256,
        ).hexdigest()

        return hmac.compare_digest(computed, clean_signature)

    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """Check provider health."""

    @abstractmethod
    async def list_loads(self, **filters: Any) -> List[Dict[str, Any]]:
        """List available loads."""

    @abstractmethod
    async def get_shipment(self, shipment_id: str) -> Dict[str, Any]:
        """Get shipment details."""

    @abstractmethod
    async def update_shipment(self, shipment_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update shipment status."""

    @abstractmethod
    async def acknowledge_webhook(self, event_id: str) -> bool:
        """Acknowledge webhook receipt."""