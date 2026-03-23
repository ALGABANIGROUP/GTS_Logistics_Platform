"""Tests for payment gateway schemas and mounted API routes."""

from __future__ import annotations

from datetime import datetime, date
from types import SimpleNamespace

import pytest
from pydantic import ValidationError

from backend.main import app
from backend.routes import payment_gateway as payment_module
from backend.routes.payment_gateway import (
    PaymentConfirmRequest,
    PaymentCreateRequest,
    PaymentRefundRequest,
    PaymentResponse,
    get_plan_invoice_service,
    get_payment_service,
)
from backend.models.payment import CurrencyCode, Payment, PaymentGateway, PaymentStatus, Refund
from backend.services.payment_service import PaymentService


class TestPaymentGatewaySchemas:
    def test_create_request_defaults(self):
        payload = PaymentCreateRequest(invoice_id=123, amount=5000.0)

        assert payload.currency == "SDG"
        assert payload.gateway == "sudapay"
        assert payload.invoice_id == 123

    def test_create_request_rejects_negative_amount(self):
        with pytest.raises(ValidationError):
            PaymentCreateRequest(invoice_id=123, amount=-1)

    def test_confirm_request_allows_optional_fields(self):
        payload = PaymentConfirmRequest(
            gateway_transaction_id="TXN-123",
            metadata={"status": "completed"},
        )

        assert payload.gateway_transaction_id == "TXN-123"
        assert payload.metadata == {"status": "completed"}

    def test_refund_request_defaults_reason(self):
        payload = PaymentRefundRequest()
        assert payload.reason == "Customer request"

    def test_response_serializes_enum_like_values(self):
        response = PaymentResponse(
            id=1,
            reference_id="PAY-123",
            invoice_id=99,
            amount=5000.0,
            currency="SDG",
            status="pending",
            payment_gateway="sudapay",
            gateway_transaction_id=None,
            created_at=datetime(2026, 3, 10, 12, 0, 0).isoformat(),
            payment_date=None,
        )

        dumped = response.model_dump()
        assert dumped["reference_id"] == "PAY-123"
        assert dumped["payment_gateway"] == "sudapay"


@pytest.mark.asyncio
async def test_get_payment_service_returns_payment_service_instance():
    class DummySession:
        pass

    class DummySudapay:
        pass

    service = await get_payment_service(db=DummySession(), sudapay=DummySudapay())
    assert isinstance(service, PaymentService)
    assert service.db.__class__.__name__ == "DummySession"


@pytest.fixture(autouse=True)
def _clear_overrides():
    original = dict(app.dependency_overrides)
    yield
    app.dependency_overrides = original


@pytest.fixture
def fake_payment_service():
    class FakePaymentService:
        def __init__(self):
            self.payment = Payment(
                id=1,
                reference_id="PAY-123",
                invoice_id=123,
                user_id=1,
                amount=5000.0,
                currency=CurrencyCode.SDG,
                status=PaymentStatus.PENDING,
                payment_gateway=PaymentGateway.SUDAPAY,
                created_at=datetime(2026, 3, 10, 12, 0, 0),
            )
            self.refund = Refund(
                id=5,
                reference_id="RFD-123",
                payment_id=1,
                amount=2500.0,
                status=PaymentStatus.PENDING,
            )
        async def create_payment(self, **kwargs):
            self.payment.invoice_id = kwargs["invoice_id"]
            self.payment.user_id = kwargs["user_id"]
            self.payment.amount = kwargs["amount"]
            return self.payment

        async def create_checkout_payment(self, **kwargs):
            await self.create_payment(**kwargs)
            self.payment.gateway_transaction_id = "SP-123"
            return {
                "payment": self.payment,
                "checkout_url": "https://example.test/checkout",
                "gateway": "sudapay",
                "status": "pending",
            }

        async def get_payment(self, payment_id: int):
            return self.payment if payment_id == self.payment.id else None

        async def get_payment_by_reference(self, reference_id: str):
            return self.payment if reference_id == self.payment.reference_id else None

        async def resolve_payment(self, payment_identifier):
            if isinstance(payment_identifier, str) and not payment_identifier.isdigit():
                return await self.get_payment_by_reference(payment_identifier)
            try:
                return await self.get_payment(int(payment_identifier))
            except (TypeError, ValueError):
                return None

        async def update_payment_status(self, **kwargs):
            self.payment.status = PaymentStatus[kwargs["status"].upper()]
            self.payment.payment_date = kwargs.get("payment_date")
            return self.payment

        async def confirm_payment(self, **kwargs):
            return await self.update_payment_status(
                payment_id=kwargs["payment_id"],
                status=PaymentStatus.COMPLETED.value,
                payment_date=kwargs.get("payment_date"),
            )

        async def create_refund(self, **kwargs):
            self.refund.amount = kwargs["amount"] or self.payment.amount
            return self.refund

        async def complete_refund(self, refund_id: int):
            self.refund.status = PaymentStatus.COMPLETED
            return self.refund

        async def refund_payment(self, **kwargs):
            self.refund.amount = kwargs["amount"] or self.payment.amount
            self.refund.status = PaymentStatus.COMPLETED
            return self.refund

        async def get_invoice_payments(self, invoice_id: int):
            return [self.payment] if invoice_id == self.payment.invoice_id else []

        async def get_user_payment_history(self, user_id: int, limit: int = 50, offset: int = 0):
            if user_id != self.payment.user_id:
                return [], 0
            return [self.payment], 1

    return FakePaymentService()


@pytest.fixture
def fake_plan_invoice_service():
    class FakePlanInvoiceService:
        def __init__(self):
            self.plan_invoice = SimpleNamespace(
                id=77,
                number="PLANINV-PRO-U1-20260310120000-ABC123",
                amount_usd=49.99,
                status="pending",
                date=date(2026, 3, 10),
                created_at=datetime(2026, 3, 10, 12, 0, 0),
                plan_code="PRO",
                user_id=1,
            )
            self.last_plan_list_kwargs = None
            self.last_plan_summary_kwargs = None

        async def create_plan_invoice(self, **kwargs):
            self.plan_invoice.number = f"PLANINV-{kwargs['plan_code'].upper()}-U{kwargs['user_id']}-20260310120000-ABC123"
            self.plan_invoice.amount_usd = kwargs["amount_usd"]
            self.plan_invoice.status = kwargs.get("status") or "pending"
            self.plan_invoice.plan_code = kwargs["plan_code"].upper()
            self.plan_invoice.user_id = kwargs["user_id"]
            return self.plan_invoice

        async def list_plan_invoices(self, **kwargs):
            self.last_plan_list_kwargs = kwargs
            if kwargs.get("plan_code") and kwargs["plan_code"].upper() != "PRO":
                return [], 0
            return [self.plan_invoice], 1

        async def get_plan_invoice_summary(self, **kwargs):
            self.last_plan_summary_kwargs = kwargs
            return {
                "PRO": {
                    "count": 1,
                    "total_amount_usd": float(self.plan_invoice.amount_usd),
                    "paid_count": 0,
                    "pending_count": 1,
                }
            }

    return FakePlanInvoiceService()


@pytest.fixture
def override_payment_dependencies(fake_payment_service, fake_plan_invoice_service, monkeypatch):
    async def fake_current_user():
        return {"id": 1, "email": "user@example.com", "role": "user"}

    async def fake_payment_service_dep():
        return fake_payment_service

    async def fake_plan_invoice_service_dep():
        return fake_plan_invoice_service

    async def fake_db():
        class DummySession:
            async def commit(self):
                return None

            async def rollback(self):
                return None

            async def close(self):
                return None

        dummy = DummySession()
        try:
            yield dummy
        finally:
            await dummy.close()

    class DummySudapay:
        async def create_payment(self, **kwargs):
            return SimpleNamespace(
                payment_id="SP-123",
                checkout_url="https://example.test/checkout",
            )

        async def confirm_payment(self, _payment_id: str):
            return {
                "status": "completed",
                "amount": 5000.0,
                "currency": "SDG",
                "reference_id": "PAY-123",
            }

        async def refund_payment(self, _payment_id: str, amount: float | None = None, reason: str = ""):
            return {"refund_id": "RFD-123", "amount": amount or 2500.0, "status": "completed"}

    async def fake_sudapay_service():
        return DummySudapay()

    app.dependency_overrides[payment_module.get_current_user] = fake_current_user
    app.dependency_overrides[payment_module.get_payment_service] = fake_payment_service_dep
    app.dependency_overrides[get_plan_invoice_service] = fake_plan_invoice_service_dep
    app.dependency_overrides[payment_module.get_async_session] = fake_db
    monkeypatch.setattr(payment_module, "get_sudapay_service", fake_sudapay_service)
    return SimpleNamespace(
        payment_service=fake_payment_service,
        plan_invoice_service=fake_plan_invoice_service,
    )


class TestPaymentRoutes:
    @pytest.mark.asyncio
    async def test_create_payment_endpoint(self, async_client, override_payment_dependencies):
        response = await async_client.post(
            "/api/v1/payments/create",
            json={
                "invoice_id": 123,
                "amount": 5000.0,
                "currency": "SDG",
                "gateway": "sudapay",
                "description": "Test payment",
            },
        )

        assert response.status_code == 201
        body = response.json()
        assert body["payment_id"] == 1
        assert body["checkout_url"] == "https://example.test/checkout"
        assert body["public_payment_link"].endswith("/pay/1")
        assert body["status"] == "pending"

    @pytest.mark.asyncio
    async def test_confirm_payment_endpoint(self, async_client, override_payment_dependencies):
        response = await async_client.post(
            "/api/v1/payments/1/confirm",
            json={"gateway_transaction_id": "TXN-20260310-123", "metadata": {"confirmed": True}},
        )

        assert response.status_code == 200
        assert response.json()["status"] == "completed"

    @pytest.mark.asyncio
    async def test_confirm_payment_endpoint_accepts_reference_id(self, async_client, override_payment_dependencies):
        response = await async_client.post(
            "/api/v1/payments/PAY-123/confirm",
            json={"gateway_transaction_id": "TXN-20260310-123", "metadata": {"confirmed": True}},
        )

        assert response.status_code == 200
        assert response.json()["reference_id"] == "PAY-123"

    @pytest.mark.asyncio
    async def test_refund_payment_endpoint(self, async_client, override_payment_dependencies, fake_payment_service):
        fake_payment_service.payment.status = PaymentStatus.COMPLETED
        fake_payment_service.payment.gateway_transaction_id = "TXN-123"

        response = await async_client.post(
            "/api/v1/payments/1/refund",
            json={"amount": 2500.0, "reason": "Customer request"},
        )

        assert response.status_code == 200
        assert response.json()["refund_id"] == 5
        assert response.json()["status"] == "completed"

    @pytest.mark.asyncio
    async def test_get_payment_endpoint(self, async_client, override_payment_dependencies):
        response = await async_client.get("/api/v1/payments/1")

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_get_payment_endpoint_accepts_reference_id(self, async_client, override_payment_dependencies):
        response = await async_client.get("/api/v1/payments/PAY-123")

        assert response.status_code == 200
        assert response.json()["reference_id"] == "PAY-123"
        assert response.json()["id"] == 1
        assert response.json()["reference_id"] == "PAY-123"

    @pytest.mark.asyncio
    async def test_get_invoice_payments_endpoint(self, async_client, override_payment_dependencies):
        response = await async_client.get("/api/v1/payments/invoice/123")

        assert response.status_code == 200
        assert isinstance(response.json(), list)
        assert response.json()[0]["reference_id"] == "PAY-123"

    @pytest.mark.asyncio
    async def test_payment_not_found(self, async_client, override_payment_dependencies):
        response = await async_client.get("/api/v1/payments/99999")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_get_user_payment_history_endpoint(self, async_client, override_payment_dependencies):
        response = await async_client.get("/api/v1/payments/user/history?limit=10&offset=0")

        assert response.status_code == 200
        body = response.json()
        assert body["total"] == 1
        assert body["limit"] == 10
        assert body["offset"] == 0
        assert body["items"][0]["reference_id"] == "PAY-123"

    @pytest.mark.asyncio
    async def test_get_payment_forbidden_for_other_user(
        self,
        async_client,
        override_payment_dependencies,
        fake_payment_service,
    ):
        fake_payment_service.payment.user_id = 2

        response = await async_client.get("/api/v1/payments/1")

        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_create_plan_invoice_endpoint(self, async_client, override_payment_dependencies):
        response = await async_client.post(
            "/api/v1/payments/plan-invoices",
            json={
                "plan_code": "pro",
                "amount": 49.99,
                "status": "pending",
            },
        )

        assert response.status_code == 201
        body = response.json()
        assert body["plan_code"] == "PRO"
        assert body["user_id"] == 1
        assert body["amount_usd"] == 49.99

    @pytest.mark.asyncio
    async def test_create_plan_invoice_rejects_non_pending_status(self, async_client, override_payment_dependencies):
        response = await async_client.post(
            "/api/v1/payments/plan-invoices",
            json={
                "plan_code": "pro",
                "amount": 49.99,
                "status": "paid",
            },
        )

        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_list_plan_invoices_endpoint(self, async_client, override_payment_dependencies):
        response = await async_client.get(
            "/api/v1/payments/plan-invoices?plan_code=PRO&status=pending&from_date=2026-03-01&to_date=2026-03-31"
        )

        assert response.status_code == 200
        body = response.json()
        assert body["total"] == 1
        assert body["items"][0]["plan_code"] == "PRO"
        assert override_payment_dependencies.plan_invoice_service.last_plan_list_kwargs["from_date"].isoformat() == "2026-03-01"
        assert override_payment_dependencies.plan_invoice_service.last_plan_list_kwargs["to_date"].isoformat() == "2026-03-31"
        assert override_payment_dependencies.plan_invoice_service.last_plan_list_kwargs["user_id"] == 1

    @pytest.mark.asyncio
    async def test_plan_invoice_summary_endpoint(self, async_client, override_payment_dependencies):
        response = await async_client.get(
            "/api/v1/payments/plan-invoices/summary?from_date=2026-03-01&to_date=2026-03-31"
        )

        assert response.status_code == 200
        body = response.json()
        assert "PRO" in body["summary"]
        assert body["summary"]["PRO"]["count"] == 1
        assert override_payment_dependencies.plan_invoice_service.last_plan_summary_kwargs["from_date"].isoformat() == "2026-03-01"
        assert override_payment_dependencies.plan_invoice_service.last_plan_summary_kwargs["to_date"].isoformat() == "2026-03-31"
        assert override_payment_dependencies.plan_invoice_service.last_plan_summary_kwargs["user_id"] == 1
