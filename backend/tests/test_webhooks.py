from __future__ import annotations

import hmac
import json
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List

import pytest

from backend.main import app
from backend.routes import webhooks as webhooks_module
from backend.database.config import get_db_async

CLIENT_ID = "test_client"
SECRET = "test_secret"


@pytest.fixture(autouse=True)
def _override_webhook_secrets():
    app.state.webhook_secrets = {CLIENT_ID: SECRET}
    yield


@pytest.fixture(autouse=True)
def _override_db_dependency():
    async def _fake_db():
        class DummySession:
            def __init__(self):
                self._added: List[object] = []

            def add(self, obj):
                self._added.append(obj)

            async def execute(self, statement, *args, **kwargs):
                compiled_params = {}
                try:
                    compiled_params = statement.compile().params  # type: ignore[attr-defined]
                except Exception:
                    compiled_params = {}

                idempotency_value = None
                for key, value in compiled_params.items():
                    if "idempotency_key" in str(key):
                        idempotency_value = value
                        break

                class _Result:
                    def __init__(self, scalar_value):
                        self._scalar_value = scalar_value

                    def scalar_one_or_none(self):
                        return self._scalar_value

                # Simulate idempotency hit for the duplicate test key.
                if idempotency_value == "duplicate-key-123":
                    return _Result("existing-webhook-id")
                return _Result(None)

            async def commit(self):
                return None

            async def rollback(self):
                return None

            async def close(self):
                return None

            async def flush(self):
                return None

        dummy = DummySession()
        try:
            yield dummy
        finally:
            await dummy.close()

    app.dependency_overrides[get_db_async] = _fake_db
    yield
    app.dependency_overrides.pop(get_db_async, None)


@pytest.fixture(autouse=True)
def _stub_webhook_service(monkeypatch):
    class DummyWebhookService:
        def __init__(self, _session):
            self.logged: List[str] = []

        async def is_duplicate_idempotency_key(self, key: str) -> bool:
            return False

        async def log_webhook(
            self,
            *,
            client_id: str,
            endpoint: str,
            payload: Dict,
            headers: Dict,
            idempotency_key: str,
            signature: str | None,
        ) -> str:
            webhook_id = str(uuid.uuid4())
            self.logged.append(webhook_id)
            return webhook_id

        async def mark_webhook_processed(self, webhook_id: str, status_code: int = 202) -> None:
            return None

        async def mark_webhook_failed(self, webhook_id: str, error: str, status_code: int = 500) -> None:
            return None

    monkeypatch.setattr(webhooks_module, "WebhookService", DummyWebhookService)
    monkeypatch.setattr("backend.routes.webhooks.WebhookService", DummyWebhookService)
    yield


@pytest.fixture
def task_spy(monkeypatch):
    calls: List[Dict] = []

    def _capture_add_task(self, func, *args, **kwargs):
        calls.append(
            {
                "func": getattr(func, "__name__", str(func)),
                "args": args,
                "kwargs": kwargs,
            }
        )
        return None

    monkeypatch.setattr("starlette.background.BackgroundTasks.add_task", _capture_add_task)
    return calls


@pytest.fixture
def auth_headers():
    def _build(payload: Dict) -> Dict[str, str]:
        timestamp = str(int(time.time()))
        body = json.dumps(payload, separators=(",", ":"))
        message = f"{timestamp}.{body}"
        signature = hmac.new(SECRET.encode(), msg=message.encode(), digestmod="sha256").hexdigest()
        return {
            "X-Client-ID": CLIENT_ID,
            "X-Signature": signature,
            "X-Timestamp": timestamp,
            "Content-Type": "application/json",
        }

    return _build


@pytest.mark.asyncio
async def test_webhook_happy_path(async_client, auth_headers, task_spy):
    tracking_id = f"TEST-{int(time.time())}"
    payload = {
        "event": {
            "event_type": "created",
            "event_time": datetime.utcnow().isoformat(),
            "external_tracking_id": tracking_id,
            "shipment_reference": "SHIP001",
            "location": "Toronto, ON",
        },
        "client_id": CLIENT_ID,
        "timestamp": int(time.time()),
        "signature": "placeholder",
        "idempotency_key": f"key-created-{tracking_id}",
    }

    response = await async_client.post(
        "/api/v1/webhooks/tracking",
        json=payload,
        headers=auth_headers(payload),
    )

    assert response.status_code == 202
    body = response.json()
    assert body["status"] == "accepted"
    assert task_spy, "background task should be enqueued"


@pytest.mark.asyncio
async def test_webhook_duplicate_idempotency(async_client, auth_headers, monkeypatch):
    async def _dup(self, *_args, **_kwargs):  # noqa: ANN001
        return True

    monkeypatch.setattr(webhooks_module.WebhookService, "is_duplicate_idempotency_key", _dup, raising=False)
    monkeypatch.setattr("backend.routes.webhooks.WebhookService.is_duplicate_idempotency_key", _dup, raising=False)

    payload = {
        "event": {
            "event_type": "created",
            "event_time": datetime.utcnow().isoformat(),
            "external_tracking_id": f"DUPE-{int(time.time())}",
        },
        "client_id": CLIENT_ID,
        "timestamp": int(time.time()),
        "signature": "placeholder",
        "idempotency_key": "duplicate-key-123",
    }

    response = await async_client.post(
        "/api/v1/webhooks/tracking",
        json=payload,
        headers=auth_headers(payload),
    )

    assert response.status_code == 202
    assert "Duplicate" in response.json().get("message", "")


@pytest.mark.asyncio
async def test_webhook_invalid_signature(async_client):
    payload = {"event": {"event_type": "created", "event_time": datetime.utcnow().isoformat(), "external_tracking_id": "SIGFAIL"}}
    headers = {
        "X-Client-ID": CLIENT_ID,
        "X-Signature": "invalid",
        "X-Timestamp": str(int(time.time())),
        "Content-Type": "application/json",
    }

    response = await async_client.post("/api/v1/webhooks/tracking", json=payload, headers=headers)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_webhook_expired_timestamp(async_client, auth_headers):
    expired_ts = int(time.time()) - 400
    payload = {
        "event": {
            "event_type": "created",
            "event_time": datetime.utcnow().isoformat(),
            "external_tracking_id": f"EXPIRED-{int(time.time())}",
        },
        "client_id": CLIENT_ID,
        "timestamp": expired_ts,
        "signature": "placeholder",
        "idempotency_key": f"key-expired-{expired_ts}",
    }

    timestamp_str = str(expired_ts)
    body = json.dumps(payload, separators=(",", ":"))
    signature = hmac.new(SECRET.encode(), msg=f"{timestamp_str}.{body}".encode(), digestmod="sha256").hexdigest()
    headers = {
        "X-Client-ID": CLIENT_ID,
        "X-Signature": signature,
        "X-Timestamp": timestamp_str,
        "Content-Type": "application/json",
    }

    response = await async_client.post("/api/v1/webhooks/tracking", json=payload, headers=headers)
    assert response.status_code == 400

