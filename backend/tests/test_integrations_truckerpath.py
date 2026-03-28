from __future__ import annotations

import hashlib
import hmac
from unittest.mock import AsyncMock

import pytest

from backend.integrations import ProviderConfig, create_provider
from backend.integrations.truckerpath.provider import TruckerPathProvider


class FakeResponse:
    def __init__(self, status_code: int, data):
        self.status_code = status_code
        self._data = data
        self.text = str(data)

    def json(self):
        return self._data


@pytest.fixture
def provider_config():
    return ProviderConfig(
        provider_id="test_truckerpath",
        provider_type="truckerpath",
        base_url="https://api.truckerpath.com/v1",
        api_key="test_key",
        api_secret="test_secret",
        webhook_secret="test_secret",
    )


@pytest.fixture
def provider(provider_config):
    return TruckerPathProvider(provider_config)


@pytest.mark.asyncio
async def test_health_check_success(provider):
    provider._request_auto = AsyncMock(return_value=FakeResponse(200, {"status": "ok"}))

    result = await provider.health_check()

    assert result["ok"] is True
    assert result["status"] == "healthy"
    assert result["provider"] == "truckerpath"
    assert result["details"] == {"status": "ok"}


@pytest.mark.asyncio
async def test_list_loads_success(provider):
    provider._request_auto = AsyncMock(
        return_value=FakeResponse(
            200,
            {
                "loads": [
                    {
                        "id": "load_1",
                        "origin": {"city": "Toronto"},
                        "destination": {"city": "Montreal"},
                        "equipment_type": "dry_van",
                        "rate": 2500,
                        "status": "posted",
                    }
                ]
            },
        )
    )

    result = await provider.list_loads(origin="Toronto", limit=10)

    assert result["ok"] is True
    assert result["total"] == 1
    assert len(result["loads"]) == 1
    assert result["loads"][0]["external_id"] == "load_1"
    assert result["loads"][0]["origin"] == "Toronto"
    assert result["loads"][0]["source"] == "truckerpath"


@pytest.mark.asyncio
async def test_get_shipment_success(provider):
    provider._request_auto = AsyncMock(
        return_value=FakeResponse(
            200,
            {
                "id": "ship_1",
                "status": "in_transit",
                "load_id": "load_1",
            },
        )
    )

    shipment = await provider.get_shipment("ship_1")

    assert shipment["external_id"] == "ship_1"
    assert shipment["status"] == "in_transit"
    assert shipment["load_id"] == "load_1"


def test_webhook_signature_validation(provider):
    payload = b'{"event":"test"}'
    signature = hmac.new(b"test_secret", payload, hashlib.sha256).hexdigest()

    assert provider.verify_webhook_signature(payload, signature) is True
    assert provider.verify_webhook_signature(payload, "wrong") is False


def test_factory_creates_provider(provider_config):
    created = create_provider("truckerpath", provider_config)

    assert isinstance(created, TruckerPathProvider)


@pytest.mark.asyncio
async def test_missing_credentials_returns_disabled_response():
    config = ProviderConfig(
        provider_id="disabled_truckerpath",
        provider_type="truckerpath",
        base_url="https://api.truckerpath.com/v1",
    )
    provider = TruckerPathProvider(config)

    result = await provider.list_loads(limit=5)

    assert result["ok"] is False
    assert result["status"] == 503
    assert result["source"] == "disabled"
    assert result["loads"] == []
    assert result["error"] == "truckerpath_not_configured"
