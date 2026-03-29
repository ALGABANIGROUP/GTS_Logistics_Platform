from __future__ import annotations

import hashlib
import hmac
from unittest.mock import AsyncMock

import pytest

from backend.integrations import ProviderConfig, QuoProvider, create_provider


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
        provider_id="test_quo",
        provider_type="webhook",
        base_url="https://api.openphone.com/v1",
        api_key="quo_key",
        api_secret="quo_secret",
        webhook_secret="quo_secret",
    )


@pytest.fixture
def provider(provider_config):
    return QuoProvider(provider_config)


@pytest.mark.asyncio
async def test_health_check_success(provider):
    provider._request_auto = AsyncMock(return_value=FakeResponse(200, {"data": [{"id": "PN123"}]}))

    result = await provider.health_check()

    assert result["ok"] is True
    assert result["status"] == "healthy"
    assert result["provider"] == "quo"


@pytest.mark.asyncio
async def test_list_calls_success(provider):
    provider._request_auto = AsyncMock(
        return_value=FakeResponse(
            200,
            {
                "data": [
                    {
                        "id": "AC123",
                        "phoneNumberId": "PN123",
                        "userId": "US123",
                        "direction": "incoming",
                        "status": "completed",
                        "duration": 60,
                        "participants": ["+15555555555"],
                        "createdAt": "2022-01-01T00:00:00Z",
                    }
                ],
                "nextPageToken": "next_1",
            },
        )
    )

    result = await provider.list_calls(
        phone_number_id="PN123",
        participants=["+15555555555"],
        max_results=10,
    )

    assert result["ok"] is True
    assert result["total"] == 1
    assert result["calls"][0]["external_id"] == "AC123"
    assert result["calls"][0]["source"] == "quo"
    assert result["next_page_token"] == "next_1"


@pytest.mark.asyncio
async def test_get_call_summary_success(provider):
    provider._request_auto = AsyncMock(
        return_value=FakeResponse(
            200,
            {
                "data": {
                    "callId": "AC1",
                    "status": "completed",
                    "summary": ["You talked about weather."],
                    "nextSteps": ["Bring an umbrella."],
                }
            },
        )
    )

    result = await provider.get_call_summary("AC1")

    assert result["call_id"] == "AC1"
    assert result["status"] == "completed"
    assert result["summary"] == ["You talked about weather."]
    assert result["next_steps"] == ["Bring an umbrella."]


@pytest.mark.asyncio
async def test_create_message_webhook_dispatches_to_messages_endpoint(provider):
    provider._request_result = AsyncMock(return_value={"ok": True, "status": 201, "data": {"data": {"id": "WH1"}}})

    result = await provider.create_webhook(
        url="https://example.com/webhooks/messages",
        event_types=["message.received", "message.delivered"],
        description="Messages",
    )

    assert result["ok"] is True
    provider._request_result.assert_awaited_once_with(
        "POST",
        provider.url_webhooks_messages,
        json={
            "url": "https://example.com/webhooks/messages",
            "events": ["message.received", "message.delivered"],
            "label": "Messages",
            "status": "enabled",
        },
    )


def test_verify_event_signature(provider):
    payload = b'{"event":"message.received"}'
    timestamp = "2026-03-28T12:00:00Z"
    digest = hmac.new(
        b"quo_secret",
        f"{timestamp}.{payload.decode('utf-8')}".encode(),
        hashlib.sha256,
    ).hexdigest()

    assert provider.verify_event_signature(payload, digest, timestamp) is True
    assert provider.verify_event_signature(payload, "wrong", timestamp) is False


def test_factory_creates_provider(provider_config):
    created = create_provider("quo", provider_config)

    assert isinstance(created, QuoProvider)


@pytest.mark.asyncio
async def test_missing_credentials_returns_disabled_response():
    config = ProviderConfig(
        provider_id="disabled_quo",
        provider_type="webhook",
        base_url="https://api.openphone.com/v1",
    )
    provider = QuoProvider(config)

    result = await provider.list_calls(
        phone_number_id="PN123",
        participants=["+15555555555"],
    )

    assert result["ok"] is False
    assert result["status"] == 503
    assert result["source"] == "disabled"
    assert result["calls"] == []
    assert result["error"] == "quo_not_configured"
