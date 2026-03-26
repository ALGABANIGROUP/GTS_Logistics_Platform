from __future__ import annotations

import importlib
import json
from types import SimpleNamespace

import pytest
from sqlalchemy.exc import IntegrityError

from backend.main import app
from backend.models.payment import PaymentStatus
from backend.services import payment_service as payment_service_module
from backend.webhooks import payment_webhooks

runtime_payment_webhooks = importlib.import_module("webhooks.payment_webhooks")


class DummySudapay:
    def __init__(self, valid_signature: bool = True):
        self.valid_signature = valid_signature

    def verify_webhook_signature(self, payload: str, signature: str) -> bool:
        return self.valid_signature and signature == "valid-signature"


@pytest.fixture(autouse=True)
def _clear_overrides():
    original = dict(app.dependency_overrides)
    yield
    app.dependency_overrides = original


@pytest.fixture
def fake_db():
    class DummySession:
        def __init__(self):
            self.logged_keys = set()

        def add(self, obj):
            key = getattr(obj, "idempotency_key", None)
            if key is not None:
                if key in self.logged_keys:
                    raise IntegrityError("duplicate webhook", params=None, orig=Exception("duplicate"))
                self.logged_keys.add(key)
            if getattr(obj, "id", None) is None:
                obj.id = f"wh-{len(self.logged_keys)}"

        async def flush(self):
            return None

        async def execute(self, *args, **kwargs):
            return None

        async def commit(self):
            return None

        async def rollback(self):
            return None

        async def close(self):
            return None

    return DummySession()


@pytest.fixture
def override_payment_webhook_dependencies(fake_db):
    async def _fake_db():
        try:
            yield fake_db
        finally:
            await fake_db.close()

    async def _fake_sudapay():
        return DummySudapay(valid_signature=True)

    app.dependency_overrides[payment_webhooks.get_async_session] = _fake_db
    app.dependency_overrides[payment_webhooks.get_sudapay_service] = _fake_sudapay
    app.dependency_overrides[runtime_payment_webhooks.get_async_session] = _fake_db
    app.dependency_overrides[runtime_payment_webhooks.get_sudapay_service] = _fake_sudapay


@pytest.fixture(autouse=True)
def _force_valid_signature(monkeypatch):
    monkeypatch.setattr(
        runtime_payment_webhooks.SudapayService,
        "verify_webhook_signature",
        lambda self, payload, signature: signature == "valid-signature",
    )


def _headers(signature: str = "valid-signature") -> dict[str, str]:
    return {
        "Content-Type": "application/json",
        "X-Sudapay-Signature": signature,
    }


@pytest.mark.asyncio
async def test_payment_success_webhook(async_client, override_payment_webhook_dependencies, monkeypatch):
    calls: dict[str, object] = {}
    payment = SimpleNamespace(id=11, status=PaymentStatus.PENDING, amount=25.0, currency="SDG", gateway_transaction_id=None)

    async def _get_payment_by_reference(self, reference_id: str):
        calls["reference_id"] = reference_id
        return payment

    async def _record_transaction(self, **kwargs):
        calls["record_transaction"] = kwargs
        return None

    async def _update_payment_status(self, **kwargs):
        calls["update_payment_status"] = kwargs
        return None

    monkeypatch.setattr(payment_service_module.PaymentService, "get_payment_by_reference", _get_payment_by_reference)
    monkeypatch.setattr(payment_service_module.PaymentService, "record_transaction", _record_transaction)
    monkeypatch.setattr(payment_service_module.PaymentService, "update_payment_status", _update_payment_status)

    payload = {
        "type": "payment.success",
        "id": "evt-pay-success-1",
        "data": {"reference_id": "PAY-123", "payment_id": "SP-123", "amount": 2500, "currency": "SDG"},
    }
    response = await async_client.post(
        "/api/v1/webhooks/sudapay/payment",
        content=json.dumps(payload),
        headers=_headers(),
    )

    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert calls["reference_id"] == "PAY-123"
    assert calls["record_transaction"]["status"] == "completed"
    assert calls["update_payment_status"]["gateway_transaction_id"] == "SP-123"


@pytest.mark.asyncio
async def test_payment_failed_webhook(async_client, override_payment_webhook_dependencies, monkeypatch):
    calls: dict[str, object] = {}
    payment = SimpleNamespace(id=12, status=PaymentStatus.PENDING, amount=25.0, currency="SDG", gateway_transaction_id=None)

    async def _get_payment_by_reference(self, reference_id: str):
        return payment

    async def _record_transaction(self, **kwargs):
        calls["record_transaction"] = kwargs
        return None

    async def _update_payment_status(self, **kwargs):
        calls["update_payment_status"] = kwargs
        return None

    monkeypatch.setattr(payment_service_module.PaymentService, "get_payment_by_reference", _get_payment_by_reference)
    monkeypatch.setattr(payment_service_module.PaymentService, "record_transaction", _record_transaction)
    monkeypatch.setattr(payment_service_module.PaymentService, "update_payment_status", _update_payment_status)

    payload = {
        "type": "payment.failed",
        "id": "evt-pay-failed-1",
        "data": {"reference_id": "PAY-ERR", "error": "declined", "amount": 2500, "currency": "SDG"},
    }
    response = await async_client.post(
        "/api/v1/webhooks/sudapay/payment",
        content=json.dumps(payload),
        headers=_headers(),
    )

    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert calls["record_transaction"]["status"] == "failed"
    assert calls["update_payment_status"]["metadata"] == {"error": "declined"}


@pytest.mark.asyncio
async def test_refund_completed_webhook_completes_local_refund(
    async_client,
    override_payment_webhook_dependencies,
    monkeypatch,
):
    calls: dict[str, object] = {}
    payment = SimpleNamespace(id=13, status=PaymentStatus.COMPLETED, amount=50.0, currency="SDG", gateway_transaction_id=None)
    refund = SimpleNamespace(id=55, gateway_refund_id=None, status=PaymentStatus.PENDING, amount=25.0)

    async def _get_payment_by_reference(self, reference_id: str):
        return payment

    async def _get_refund_by_gateway_refund_id(self, gateway_refund_id: str):
        calls["gateway_refund_id"] = gateway_refund_id
        return refund

    async def _get_latest_pending_refund_for_payment(self, payment_id: int):
        calls["latest_pending_payment_id"] = payment_id
        return None

    async def _complete_refund(self, refund_id: int):
        calls["completed_refund_id"] = refund_id
        return refund

    monkeypatch.setattr(payment_service_module.PaymentService, "get_payment_by_reference", _get_payment_by_reference)
    monkeypatch.setattr(payment_service_module.PaymentService, "get_refund_by_gateway_refund_id", _get_refund_by_gateway_refund_id)
    monkeypatch.setattr(payment_service_module.PaymentService, "get_latest_pending_refund_for_payment", _get_latest_pending_refund_for_payment)
    monkeypatch.setattr(payment_service_module.PaymentService, "complete_refund", _complete_refund)

    payload = {
        "type": "refund.completed",
        "id": "evt-refund-completed-1",
        "data": {
            "payment_reference": "PAY-123",
            "refund_id": "RFD-EXT-1",
            "amount": 2500,
        },
    }
    response = await async_client.post(
        "/api/v1/webhooks/sudapay/payment",
        content=json.dumps(payload),
        headers=_headers(),
    )

    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert calls["gateway_refund_id"] == "RFD-EXT-1"
    assert calls["completed_refund_id"] == 55
    assert refund.gateway_refund_id == "RFD-EXT-1"


@pytest.mark.asyncio
async def test_payment_success_webhook_is_idempotent(async_client, override_payment_webhook_dependencies, monkeypatch):
    calls = {"record_transaction": 0, "update_payment_status": 0}
    payment = SimpleNamespace(id=21, status=PaymentStatus.COMPLETED, gateway_transaction_id="SP-123", amount=25.0, currency="SDG")

    async def _get_payment_by_reference(self, reference_id: str):
        return payment

    async def _record_transaction(self, **kwargs):
        calls["record_transaction"] += 1
        return None

    async def _update_payment_status(self, **kwargs):
        calls["update_payment_status"] += 1
        return None

    monkeypatch.setattr(payment_service_module.PaymentService, "get_payment_by_reference", _get_payment_by_reference)
    monkeypatch.setattr(payment_service_module.PaymentService, "record_transaction", _record_transaction)
    monkeypatch.setattr(payment_service_module.PaymentService, "update_payment_status", _update_payment_status)

    payload = {
        "type": "payment.success",
        "id": "evt-pay-success-duplicate",
        "data": {"reference_id": "PAY-123", "payment_id": "SP-123", "amount": 2500, "currency": "SDG"},
    }
    response = await async_client.post(
        "/api/v1/webhooks/sudapay/payment",
        content=json.dumps(payload),
        headers=_headers(),
    )

    assert response.status_code == 200
    assert calls["record_transaction"] == 0
    assert calls["update_payment_status"] == 0


@pytest.mark.asyncio
async def test_refund_completed_webhook_is_idempotent(async_client, override_payment_webhook_dependencies, monkeypatch):
    calls = {"complete_refund": 0}
    payment = SimpleNamespace(id=22, status=PaymentStatus.COMPLETED, amount=50.0, currency="SDG", gateway_transaction_id=None)
    refund = SimpleNamespace(id=56, gateway_refund_id="RFD-EXT-2", status=PaymentStatus.COMPLETED, amount=25.0)

    async def _get_payment_by_reference(self, reference_id: str):
        return payment

    async def _get_refund_by_gateway_refund_id(self, gateway_refund_id: str):
        return refund

    async def _get_latest_pending_refund_for_payment(self, payment_id: int):
        return None

    async def _complete_refund(self, refund_id: int):
        calls["complete_refund"] += 1
        return refund

    monkeypatch.setattr(payment_service_module.PaymentService, "get_payment_by_reference", _get_payment_by_reference)
    monkeypatch.setattr(payment_service_module.PaymentService, "get_refund_by_gateway_refund_id", _get_refund_by_gateway_refund_id)
    monkeypatch.setattr(payment_service_module.PaymentService, "get_latest_pending_refund_for_payment", _get_latest_pending_refund_for_payment)
    monkeypatch.setattr(payment_service_module.PaymentService, "complete_refund", _complete_refund)

    payload = {
        "type": "refund.completed",
        "id": "evt-refund-completed-duplicate",
        "data": {
            "payment_reference": "PAY-123",
            "refund_id": "RFD-EXT-2",
            "amount": 2500,
        },
    }
    response = await async_client.post(
        "/api/v1/webhooks/sudapay/payment",
        content=json.dumps(payload),
        headers=_headers(),
    )

    assert response.status_code == 200
    assert calls["complete_refund"] == 0


@pytest.mark.asyncio
async def test_payment_success_webhook_rejects_mismatched_amount(async_client, override_payment_webhook_dependencies, monkeypatch):
    payment = SimpleNamespace(id=31, status=PaymentStatus.PENDING, amount=25.0, currency="SDG", gateway_transaction_id=None)

    async def _get_payment_by_reference(self, reference_id: str):
        return payment

    monkeypatch.setattr(payment_service_module.PaymentService, "get_payment_by_reference", _get_payment_by_reference)

    payload = {
        "type": "payment.success",
        "id": "evt-pay-success-mismatch",
        "data": {"reference_id": "PAY-123", "payment_id": "SP-123", "amount": 9999, "currency": "SDG"},
    }
    response = await async_client.post(
        "/api/v1/webhooks/sudapay/payment",
        content=json.dumps(payload),
        headers=_headers(),
    )

    assert response.status_code == 409


@pytest.mark.asyncio
async def test_refund_completed_webhook_rejects_missing_local_refund(async_client, override_payment_webhook_dependencies, monkeypatch):
    payment = SimpleNamespace(id=32, status=PaymentStatus.COMPLETED, amount=50.0, currency="SDG", gateway_transaction_id=None)

    async def _get_payment_by_reference(self, reference_id: str):
        return payment

    async def _get_refund_by_gateway_refund_id(self, gateway_refund_id: str):
        return None

    async def _get_latest_pending_refund_for_payment(self, payment_id: int):
        return None

    monkeypatch.setattr(payment_service_module.PaymentService, "get_payment_by_reference", _get_payment_by_reference)
    monkeypatch.setattr(payment_service_module.PaymentService, "get_refund_by_gateway_refund_id", _get_refund_by_gateway_refund_id)
    monkeypatch.setattr(payment_service_module.PaymentService, "get_latest_pending_refund_for_payment", _get_latest_pending_refund_for_payment)

    payload = {
        "type": "refund.completed",
        "id": "evt-refund-missing-local",
        "data": {
            "payment_reference": "PAY-123",
            "refund_id": "RFD-EXT-404",
            "amount": 2500,
        },
    }
    response = await async_client.post(
        "/api/v1/webhooks/sudapay/payment",
        content=json.dumps(payload),
        headers=_headers(),
    )

    assert response.status_code == 409


@pytest.mark.asyncio
async def test_payment_webhook_duplicate_event_id_is_ignored(async_client, override_payment_webhook_dependencies, monkeypatch):
    calls = {"record_transaction": 0}
    payment = SimpleNamespace(id=41, status=PaymentStatus.PENDING, amount=25.0, currency="SDG", gateway_transaction_id=None)

    async def _get_payment_by_reference(self, reference_id: str):
        return payment

    async def _record_transaction(self, **kwargs):
        calls["record_transaction"] += 1
        return None

    async def _update_payment_status(self, **kwargs):
        return None

    monkeypatch.setattr(payment_service_module.PaymentService, "get_payment_by_reference", _get_payment_by_reference)
    monkeypatch.setattr(payment_service_module.PaymentService, "record_transaction", _record_transaction)
    monkeypatch.setattr(payment_service_module.PaymentService, "update_payment_status", _update_payment_status)

    payload = {
        "type": "payment.success",
        "id": "evt-pay-dup-1",
        "data": {"reference_id": "PAY-123", "payment_id": "SP-123", "amount": 2500, "currency": "SDG"},
    }

    first = await async_client.post(
        "/api/v1/webhooks/sudapay/payment",
        content=json.dumps(payload),
        headers=_headers(),
    )
    second = await async_client.post(
        "/api/v1/webhooks/sudapay/payment",
        content=json.dumps(payload),
        headers=_headers(),
    )

    assert first.status_code == 200
    assert second.status_code == 200
    assert second.json()["message"] == "Duplicate webhook ignored"
    assert calls["record_transaction"] == 1


@pytest.mark.asyncio
async def test_payment_webhook_rejects_invalid_signature(async_client, fake_db):
    async def _fake_db():
        try:
            yield fake_db
        finally:
            await fake_db.close()

    async def _fake_sudapay():
        return DummySudapay(valid_signature=False)

    app.dependency_overrides[payment_webhooks.get_async_session] = _fake_db
    app.dependency_overrides[payment_webhooks.get_sudapay_service] = _fake_sudapay

    payload = {"type": "payment.success", "data": {"reference_id": "PAY-123"}}
    response = await async_client.post(
        "/api/v1/webhooks/sudapay/payment",
        content=json.dumps(payload),
        headers=_headers(signature="bad-signature"),
    )

    assert response.status_code == 401
