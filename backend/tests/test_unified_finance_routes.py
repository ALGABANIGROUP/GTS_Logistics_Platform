from __future__ import annotations

import pytest

from backend.main import app
from backend.routes import unified_finance_routes as unified_finance_module


@pytest.fixture(autouse=True)
def _clear_overrides():
    original = dict(app.dependency_overrides)
    yield
    app.dependency_overrides = original


@pytest.fixture
def fake_unified_finance_service():
    class FakeUnifiedFinanceService:
        async def get_dashboard(self):
            return {
                "success": True,
                "metrics": {
                    "total_revenue": 1000.0,
                    "total_expenses": 250.0,
                    "net_profit": 750.0,
                    "accounts_receivable": 300.0,
                    "payments_collected": 700.0,
                    "invoice_count": 2,
                    "expense_count": 1,
                    "payment_count": 1,
                },
                "recent": {
                    "invoices": [{"id": 1, "number": "INV-1", "amount_usd": 500.0, "status": "pending"}],
                    "expenses": [{"id": 1, "category": "fuel", "amount": 250.0, "status": "PAID"}],
                    "payments": [{"id": 1, "reference_id": "PAY-1", "amount": 700.0, "status": "completed"}],
                },
            }

        async def list_invoices(self, limit=100):
            return [{"id": 1, "number": "INV-1", "amount_usd": 500.0, "status": "pending"}]

        async def list_expenses(self, limit=100):
            return [{"id": 1, "category": "fuel", "amount": 250.0, "status": "PAID"}]

        async def list_payments(self, limit=100):
            return [{"id": 1, "reference_id": "PAY-1", "amount": 700.0, "status": "completed"}]

        async def get_summary_report(self):
            return {
                "success": True,
                "invoices": {"count": 2, "total_amount_usd": 1000.0},
                "expenses": {"count": 1, "total_amount": 250.0},
                "payments": {"count": 1, "completed_amount": 700.0},
                "net_position": 750.0,
            }

        async def get_trial_balance(self, as_of_date, generated_by="system"):
            return {"success": True, "as_of_date": as_of_date.isoformat(), "is_balanced": True}

        async def get_income_statement(self, start_date, end_date, generated_by="system"):
            return {"success": True, "period": {"start_date": start_date.isoformat(), "end_date": end_date.isoformat()}}

        async def get_balance_sheet(self, as_of_date, generated_by="system"):
            return {"success": True, "as_of_date": as_of_date.isoformat(), "is_balanced": True}

        async def create_invoice(self, **kwargs):
            return {
                "success": True,
                "invoice": {
                    "id": 3,
                    "number": "INV-NEW-001",
                    "amount_usd": kwargs["amount_usd"],
                    "status": kwargs.get("status", "pending"),
                    "journal_entry": "JE-NEW-001",
                },
            }

        async def create_expense(self, **kwargs):
            return {
                "success": True,
                "expense": {
                    "id": 4,
                    "category": kwargs["category"],
                    "amount": kwargs["amount"],
                    "status": kwargs.get("status", "PENDING"),
                    "journal_entry": "JE-EXP-001",
                },
            }

        async def create_payment(self, **kwargs):
            payment_type = kwargs.get("payment_type", "invoice")
            return {
                "success": True,
                "payment": {
                    "id": 5,
                    "reference_id": "PAY-NEW-001",
                    "invoice_id": kwargs.get("invoice_id"),
                    "expense_id": kwargs.get("expense_id"),
                    "payment_type": payment_type,
                    "supplier_name": kwargs.get("supplier_name"),
                    "amount": kwargs["amount"],
                    "status": "completed",
                    "journal_entry": "JE-PAY-001",
                },
            }

        async def bootstrap_demo_data(self, **kwargs):
            return {
                "success": True,
                "created": True,
                "message": "Demo finance data created successfully.",
                "data": {
                    "invoice": {"id": 10},
                    "expense": {"id": 11},
                    "payment": {"id": 12},
                },
            }

    return FakeUnifiedFinanceService()


@pytest.fixture
def override_unified_finance_dependencies(fake_unified_finance_service):
    async def fake_current_user():
        return {"id": 1, "email": "manager@example.com", "role": "admin"}

    async def fake_service_dep():
        return fake_unified_finance_service

    app.dependency_overrides[unified_finance_module.get_current_user] = fake_current_user
    app.dependency_overrides[unified_finance_module.get_unified_finance_service] = fake_service_dep


class TestUnifiedFinanceRoutes:
    @pytest.mark.asyncio
    async def test_dashboard(self, async_client, override_unified_finance_dependencies):
        response = await async_client.get("/api/v1/finance/dashboard")

        assert response.status_code == 200
        assert response.json()["metrics"]["net_profit"] == 750.0

    @pytest.mark.asyncio
    async def test_list_invoices(self, async_client, override_unified_finance_dependencies):
        response = await async_client.get("/api/v1/finance/invoices")

        assert response.status_code == 200
        body = response.json()
        assert body["total"] == 1
        assert body["items"][0]["number"] == "INV-1"

    @pytest.mark.asyncio
    async def test_summary_report(self, async_client, override_unified_finance_dependencies):
        response = await async_client.get("/api/v1/finance/reports/summary")

        assert response.status_code == 200
        assert response.json()["net_position"] == 750.0

    @pytest.mark.asyncio
    async def test_create_invoice(self, async_client, override_unified_finance_dependencies):
        response = await async_client.post(
            "/api/v1/finance/invoices",
            json={
                "invoice_date": "2026-03-21",
                "amount_usd": 500.0,
                "customer_name": "Acme Logistics",
                "status": "pending",
            },
        )

        assert response.status_code == 201
        assert response.json()["invoice"]["journal_entry"] == "JE-NEW-001"

    @pytest.mark.asyncio
    async def test_create_expense(self, async_client, override_unified_finance_dependencies):
        response = await async_client.post(
            "/api/v1/finance/expenses",
            json={
                "category": "fuel",
                "amount": 125.0,
                "description": "Fuel top-up",
                "status": "PAID",
            },
        )

        assert response.status_code == 201
        assert response.json()["expense"]["journal_entry"] == "JE-EXP-001"

    @pytest.mark.asyncio
    async def test_create_payment(self, async_client, override_unified_finance_dependencies):
        response = await async_client.post(
            "/api/v1/finance/payments",
            json={
                "payment_type": "invoice",
                "invoice_id": 1,
                "amount": 500.0,
                "currency": "USD",
                "gateway": "sudapay",
            },
        )

        assert response.status_code == 201
        assert response.json()["payment"]["reference_id"] == "PAY-NEW-001"

    @pytest.mark.asyncio
    async def test_create_expense_payment(self, async_client, override_unified_finance_dependencies):
        response = await async_client.post(
            "/api/v1/finance/payments",
            json={
                "payment_type": "expense",
                "expense_id": 7,
                "amount": 125.0,
                "currency": "USD",
                "gateway": "stripe",
                "supplier_name": "Acme Fuel",
            },
        )

        assert response.status_code == 201
        body = response.json()["payment"]
        assert body["payment_type"] == "expense"
        assert body["expense_id"] == 7
        assert body["supplier_name"] == "Acme Fuel"

    @pytest.mark.asyncio
    async def test_bootstrap_demo_data(self, async_client, override_unified_finance_dependencies):
        response = await async_client.post("/api/v1/finance/bootstrap-demo")

        assert response.status_code == 201
        body = response.json()
        assert body["created"] is True
        assert body["data"]["invoice"]["id"] == 10
