from __future__ import annotations

import hashlib
import hmac
from unittest.mock import AsyncMock

import pytest

from backend.integrations import ProviderConfig, WiseProvider, create_provider


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
        provider_id="test_wise",
        provider_type="payment",
        base_url="https://api.wise.com/v1",
        api_key="wise_key",
        api_secret="wise_secret",
        client_id="profile_123",
        webhook_secret="wise_secret",
    )


@pytest.fixture
def provider(provider_config):
    return WiseProvider(provider_config)


@pytest.mark.asyncio
async def test_health_check_success(provider):
    provider._request_auto = AsyncMock(return_value=FakeResponse(200, [{"id": "profile_123"}]))

    result = await provider.health_check()

    assert result["ok"] is True
    assert result["status"] == "healthy"
    assert result["provider"] == "wise"


@pytest.mark.asyncio
async def test_list_transfers_success(provider):
    provider._request_auto = AsyncMock(
        return_value=FakeResponse(
            200,
            [
                {
                    "id": "transfer_1",
                    "status": "processing",
                    "quoteUuid": "quote_1",
                    "customerTransactionId": "txn_1",
                    "sourceCurrency": "CAD",
                    "targetCurrency": "USD",
                }
            ],
        )
    )

    result = await provider.list_transfers(limit=10)

    assert result["ok"] is True
    assert result["total"] == 1
    assert result["transfers"][0]["external_id"] == "transfer_1"
    assert result["transfers"][0]["source"] == "wise"


@pytest.mark.asyncio
async def test_get_transfer_success(provider):
    provider._request_auto = AsyncMock(
        return_value=FakeResponse(
            200,
            {
                "id": "transfer_9",
                "status": "outgoing_payment_sent",
                "quoteUuid": "quote_9",
            },
        )
    )

    transfer = await provider.get_transfer("transfer_9")

    assert transfer["external_id"] == "transfer_9"
    assert transfer["status"] == "outgoing_payment_sent"


@pytest.mark.asyncio
async def test_create_transfer_success(provider):
    provider._request_result = AsyncMock(
        return_value={
            "ok": True,
            "status": 201,
            "data": {
                "id": "transfer_created",
                "status": "incoming_payment_waiting",
                "quoteUuid": "quote_2",
            },
        }
    )

    result = await provider.create_transfer("quote_2", "txn_2", "recipient_2")

    assert result["ok"] is True
    assert result["transfer"]["external_id"] == "transfer_created"


@pytest.mark.asyncio
async def test_get_balance_success(provider):
    provider._request_auto = AsyncMock(
        return_value=FakeResponse(
            200,
            [
                {"currency": "USD", "amount": {"value": 45}},
                {"currency": "CAD", "amount": {"value": 1250.5}},
            ],
        )
    )

    result = await provider.get_balance("CAD")

    assert result["ok"] is True
    assert result["currency"] == "CAD"
    assert result["amount"] == 1250.5


def test_webhook_signature_validation(provider):
    payload = b'{"event":"test"}'
    signature = hmac.new(b"wise_secret", payload, hashlib.sha256).hexdigest()

    assert provider.verify_webhook_signature(payload, signature) is True
    assert provider.verify_webhook_signature(payload, "wrong") is False


def test_factory_creates_provider(provider_config):
    created = create_provider("wise", provider_config)

    assert isinstance(created, WiseProvider)
