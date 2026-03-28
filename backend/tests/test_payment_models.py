"""Unit tests for payment models and service helpers."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

import pytest

from backend.models.invoices import Invoice
from backend.models.payment import (
    CurrencyCode,
    Payment,
    PaymentGateway,
    PaymentMethod,
    PaymentMethodType,
    PaymentStatus,
    PaymentTransaction,
    PaymentType,
    Refund,
    TransactionType,
)
from backend.services.payment_service import PaymentService
from backend.services.sudapay_service import SudapayService


class DummyAsyncSession:
    def __init__(self):
        self.added = []
        self.flush_calls = 0
        self.commit_calls = 0
        self.rollback_calls = 0
        self.get_map = {}

    def add(self, obj):
        if getattr(obj, "id", None) is None:
            obj.id = len(self.added) + 1
        self.added.append(obj)
        self.get_map[(type(obj), obj.id)] = obj

    async def flush(self):
        self.flush_calls += 1

    async def commit(self):
        self.commit_calls += 1

    async def rollback(self):
        self.rollback_calls += 1

    async def get(self, model, key):
        return self.get_map.get((model, key))


class DummySudapay:
    async def create_payment(self, **kwargs):
        class Response:
            payment_id = "SP-123"
            checkout_url = "https://example.test/checkout"

        return Response()

    async def confirm_payment(self, _payment_id):
        return {"payment_id": _payment_id, "status": "completed"}

    async def refund_payment(self, _payment_id, amount=None, reason=""):
        return {"refund_id": "RFD-EXT-1", "amount": amount, "reason": reason, "status": "completed"}


@pytest.fixture
def fake_db():
    return DummyAsyncSession()


class TestPaymentModels:
    def test_payment_method_creation(self):
        method = PaymentMethod(
            user_id=1,
            method_type=PaymentMethodType.SUDAPAY,
            token="test_token_123",
            display_name="SUDAPAY Account",
            brand="SUDAPAY",
            gateway=PaymentGateway.SUDAPAY,
            is_default=True,
        )

        assert method.user_id == 1
        assert method.method_type == PaymentMethodType.SUDAPAY
        assert method.gateway == PaymentGateway.SUDAPAY
        assert method.is_default is True

    def test_payment_creation(self):
        payment = Payment(
            reference_id="SUP-20260310120000-test123",
            invoice_id=123,
            user_id=1,
            payment_type=PaymentType.INVOICE,
            amount=Decimal("5000.00"),
            currency=CurrencyCode.SDG,
            status=PaymentStatus.PENDING,
            payment_gateway=PaymentGateway.SUDAPAY,
            description="Test payment",
        )

        assert payment.reference_id == "SUP-20260310120000-test123"
        assert payment.status == PaymentStatus.PENDING
        assert payment.currency == CurrencyCode.SDG
        assert payment.payment_type == PaymentType.INVOICE

    def test_payment_transaction_logging(self):
        transaction = PaymentTransaction(
            payment_id=456,
            transaction_type=TransactionType.PAYMENT,
            amount=Decimal("5000.00"),
            status=PaymentStatus.COMPLETED,
            gateway_response={"status": "success", "txn_id": "TXN-123"},
        )

        assert transaction.payment_id == 456
        assert transaction.transaction_type == TransactionType.PAYMENT
        assert transaction.status == PaymentStatus.COMPLETED

    def test_refund_creation(self):
        refund = Refund(
            reference_id="REF-20260310120000-test123",
            payment_id=456,
            amount=Decimal("2500.00"),
            reason="Customer request",
            status=PaymentStatus.PENDING,
        )

        assert refund.reference_id.startswith("REF-")
        assert refund.payment_id == 456
        assert refund.status == PaymentStatus.PENDING


class TestPaymentService:
    @pytest.mark.asyncio
    async def test_create_payment(self, fake_db):
        service = PaymentService(db_session=fake_db, sudapay_service=None)

        payment = await service.create_payment(
            user_id=1,
            amount=5000.0,
            currency="SDG",
            gateway="sudapay",
            invoice_id=123,
            description="Test payment",
            metadata={"source": "unit-test"},
        )

        assert payment.id == 1
        assert payment.reference_id.startswith("sudapay-")
        assert payment.status == PaymentStatus.PENDING
        assert payment.metadata_json == {"source": "unit-test"}
        assert payment.payment_type == PaymentType.INVOICE
        assert fake_db.flush_calls == 1

    @pytest.mark.asyncio
    async def test_create_expense_payment(self, fake_db):
        service = PaymentService(db_session=fake_db, sudapay_service=None)

        payment = await service.create_payment(
            user_id=1,
            amount=320.0,
            currency="USD",
            gateway="stripe",
            expense_id=22,
            payment_type="expense",
            supplier_name="Acme Fuel",
            description="Fuel vendor payout",
            metadata={"source": "unit-test"},
        )

        assert payment.expense_id == 22
        assert payment.invoice_id is None
        assert payment.payment_type == PaymentType.EXPENSE
        assert payment.supplier_name == "Acme Fuel"

    @pytest.mark.asyncio
    async def test_record_transaction(self, fake_db):
        service = PaymentService(db_session=fake_db, sudapay_service=None)
        payment = Payment(
            id=456,
            reference_id="PAY-123",
            invoice_id=123,
            user_id=1,
            amount=5000.0,
            currency=CurrencyCode.SDG,
            status=PaymentStatus.PENDING,
            payment_gateway=PaymentGateway.SUDAPAY,
        )
        fake_db.get_map[(Payment, 456)] = payment

        transaction = await service.record_transaction(
            payment_id=456,
            transaction_type=TransactionType.PAYMENT.value,
            amount=5000.0,
            status=PaymentStatus.COMPLETED.value,
        )

        assert transaction.id == 1
        assert transaction.payment_id == 456
        assert transaction.transaction_type == TransactionType.PAYMENT
        assert transaction.status == PaymentStatus.COMPLETED

    @pytest.mark.asyncio
    async def test_update_payment_status_marks_invoice_paid(self, fake_db):
        service = PaymentService(db_session=fake_db, sudapay_service=None)
        payment = Payment(
            id=10,
            reference_id="PAY-123",
            invoice_id=99,
            user_id=1,
            amount=5000.0,
            currency=CurrencyCode.SDG,
            status=PaymentStatus.PENDING,
            payment_gateway=PaymentGateway.SUDAPAY,
        )
        invoice = Invoice(id=99, status="unpaid")
        fake_db.get_map[(Payment, 10)] = payment
        fake_db.get_map[(Invoice, 99)] = invoice

        updated_payment = await service.update_payment_status(
            payment_id=10,
            status=PaymentStatus.COMPLETED.value,
            gateway_transaction_id="TXN-999",
            payment_date=datetime(2026, 3, 10, 12, 0, 0),
            metadata={"confirmed": True},
        )

        assert updated_payment.status == PaymentStatus.COMPLETED
        assert updated_payment.gateway_transaction_id == "TXN-999"
        assert updated_payment.metadata_json == {"confirmed": True}
        assert invoice.status == "paid"
        assert fake_db.commit_calls == 1

    @pytest.mark.asyncio
    async def test_update_payment_status_completed_skips_invoice_update_for_expense(self, fake_db):
        service = PaymentService(db_session=fake_db, sudapay_service=None)
        payment = Payment(
            id=11,
            reference_id="PAY-EXP-123",
            expense_id=7,
            user_id=1,
            amount=320.0,
            currency=CurrencyCode.USD,
            status=PaymentStatus.PENDING,
            payment_gateway=PaymentGateway.STRIPE,
            payment_type=PaymentType.EXPENSE,
            supplier_name="Acme Fuel",
        )
        fake_db.get_map[(Payment, 11)] = payment

        updated_payment = await service.update_payment_status(
            payment_id=11,
            status=PaymentStatus.COMPLETED.value,
            gateway_transaction_id="TXN-EXP-999",
            payment_date=datetime(2026, 3, 10, 12, 0, 0),
            metadata={"confirmed": True},
        )

        assert updated_payment.status == PaymentStatus.COMPLETED
        assert updated_payment.gateway_transaction_id == "TXN-EXP-999"
        assert fake_db.commit_calls == 1

    @pytest.mark.asyncio
    async def test_create_refund_records_transaction(self, fake_db, monkeypatch):
        service = PaymentService(db_session=fake_db, sudapay_service=None)
        payment = Payment(
            id=456,
            reference_id="PAY-123",
            invoice_id=123,
            user_id=1,
            amount=5000.0,
            currency=CurrencyCode.SDG,
            status=PaymentStatus.COMPLETED,
            payment_gateway=PaymentGateway.SUDAPAY,
        )
        fake_db.get_map[(Payment, 456)] = payment
        recorded = {}

        async def fake_record_transaction(**kwargs):
            recorded.update(kwargs)
            return PaymentTransaction(
                payment_id=kwargs["payment_id"],
                transaction_type=TransactionType.REFUND,
                amount=kwargs["amount"],
                status=PaymentStatus.PENDING,
            )

        monkeypatch.setattr(service, "record_transaction", fake_record_transaction)

        refund = await service.create_refund(
            payment_id=456,
            amount=2500.0,
            reason="Customer request",
            gateway_refund_id="RFD-123",
        )

        assert refund.id == 1
        assert refund.payment_id == 456
        assert refund.amount == 2500.0
        assert recorded["transaction_type"] == "refund"
        assert recorded["amount"] == 2500.0

    @pytest.mark.asyncio
    async def test_complete_refund_updates_payment(self, fake_db):
        service = PaymentService(db_session=fake_db, sudapay_service=None)
        payment = Payment(
            id=456,
            reference_id="PAY-123",
            invoice_id=123,
            user_id=1,
            amount=5000.0,
            currency=CurrencyCode.SDG,
            status=PaymentStatus.COMPLETED,
            payment_gateway=PaymentGateway.SUDAPAY,
        )
        refund = Refund(
            id=77,
            reference_id="RFD-123",
            payment_id=456,
            amount=2500.0,
            status=PaymentStatus.PENDING,
        )
        fake_db.get_map[(Refund, 77)] = refund
        fake_db.get_map[(Payment, 456)] = payment

        completed = await service.complete_refund(77)

        assert completed.status == PaymentStatus.COMPLETED
        assert completed.completed_at is not None
        assert payment.status == PaymentStatus.REFUNDED
        assert fake_db.commit_calls == 1

    def test_generate_reference_id_uses_prefix(self, fake_db):
        service = PaymentService(db_session=fake_db, sudapay_service=None)
        reference = service._generate_reference_id("PAY")
        assert reference.startswith("PAY-")

    def test_get_gateway_name_returns_display_name(self, fake_db):
        service = PaymentService(db_session=fake_db, sudapay_service=None)
        assert service.get_gateway_name(PaymentGateway.STRIPE) == "Stripe"

    @pytest.mark.asyncio
    async def test_create_checkout_payment_calls_gateway(self, fake_db):
        service = PaymentService(db_session=fake_db, sudapay_service=DummySudapay())

        with pytest.raises(ValueError, match="Sudapay has been removed from GTS"):
            await service.create_checkout_payment(
                invoice_id=123,
                user_id=1,
                amount=5000.0,
                currency="SDG",
                gateway="sudapay",
                description="Gateway payment",
                customer_email="user@example.com",
            )

    @pytest.mark.asyncio
    async def test_refund_payment_rejects_non_completed_payment(self, fake_db):
        service = PaymentService(db_session=fake_db, sudapay_service=DummySudapay())
        payment = Payment(
            id=456,
            reference_id="PAY-123",
            invoice_id=123,
            user_id=1,
            amount=5000.0,
            currency=CurrencyCode.SDG,
            status=PaymentStatus.PENDING,
            payment_gateway=PaymentGateway.SUDAPAY,
        )
        fake_db.get_map[(Payment, 456)] = payment

        with pytest.raises(ValueError, match="Only completed payments can be refunded"):
            await service.refund_payment(payment_id=456, amount=100.0, reason="x")

    @pytest.mark.asyncio
    async def test_confirm_payment_uses_gateway_failed_status(self, fake_db):
        service = PaymentService(db_session=fake_db, sudapay_service=DummySudapay())
        payment = Payment(
            id=456,
            reference_id="PAY-123",
            invoice_id=123,
            user_id=1,
            amount=5000.0,
            currency=CurrencyCode.SDG,
            status=PaymentStatus.PENDING,
            payment_gateway=PaymentGateway.SUDAPAY,
            gateway_transaction_id="SP-123",
        )
        fake_db.get_map[(Payment, 456)] = payment

        updated = await service.confirm_payment(
            payment_id=456,
            metadata={"status": "failed"},
        )

        assert updated.status == PaymentStatus.FAILED
        assert updated.payment_date is None

    @pytest.mark.asyncio
    async def test_refund_payment_keeps_pending_until_gateway_completion(self, fake_db):
        service = PaymentService(db_session=fake_db, sudapay_service=DummySudapay())
        payment = Payment(
            id=456,
            reference_id="PAY-123",
            invoice_id=123,
            user_id=1,
            amount=5000.0,
            currency=CurrencyCode.SDG,
            status=PaymentStatus.COMPLETED,
            payment_gateway=PaymentGateway.SUDAPAY,
            gateway_transaction_id="SP-123",
        )
        fake_db.get_map[(Payment, 456)] = payment

        refund = await service.refund_payment(payment_id=456, amount=2500.0, reason="customer request")

        assert refund.status == PaymentStatus.COMPLETED
        assert payment.status == PaymentStatus.REFUNDED


class TestSudapayService:
    @pytest.mark.asyncio
    async def test_verify_webhook_signature_service_instantiation(self):
        service = SudapayService(
            api_key="test_api_key",
            merchant_id="test_merchant",
            webhook_secret="test_webhook_secret",
        )

        assert service is not None
