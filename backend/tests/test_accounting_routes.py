from __future__ import annotations

from types import SimpleNamespace

import pytest

from backend.main import app
from backend.routes import accounting_routes as accounting_module


@pytest.fixture(autouse=True)
def _clear_overrides():
    original = dict(app.dependency_overrides)
    yield
    app.dependency_overrides = original


@pytest.fixture
def fake_accounting_service():
    class FakeAccountingService:
        async def list_accounts(self, active_only: bool = False):
            return [
                SimpleNamespace(
                    id=1,
                    account_code="1.2",
                    account_name="Accounts Receivable",
                    account_type=SimpleNamespace(value="asset"),
                    normal_balance=SimpleNamespace(value="debit"),
                    level=2,
                    parent_id=None,
                    is_active=True,
                ),
                SimpleNamespace(
                    id=2,
                    account_code="4.1",
                    account_name="Shipping Revenue",
                    account_type=SimpleNamespace(value="revenue"),
                    normal_balance=SimpleNamespace(value="credit"),
                    level=2,
                    parent_id=None,
                    is_active=True,
                ),
            ]

        async def create_journal_entry(self, **kwargs):
            return {
                "success": True,
                "entry_id": 10,
                "entry_number": "JE-20260321-ABC123",
                "total_debit": 100.0,
                "total_credit": 100.0,
            }

        async def create_invoice(self, **kwargs):
            return {
                "success": True,
                "invoice": {
                    "id": 7,
                    "number": "INV-20260321-XYZ123",
                    "net_amount": 100.0,
                    "status": "posted",
                    "journal_entry": "JE-20260321-ABC123",
                },
            }

        async def generate_trial_balance(self, as_of_date, generated_by="system"):
            return {
                "success": True,
                "as_of_date": as_of_date.isoformat(),
                "trial_balance": [
                    {
                        "account_code": "1.2",
                        "account_name": "Accounts Receivable",
                        "debit_balance": 100.0,
                        "credit_balance": 0.0,
                    },
                    {
                        "account_code": "4.1",
                        "account_name": "Shipping Revenue",
                        "debit_balance": 0.0,
                        "credit_balance": 100.0,
                    },
                ],
                "total_debit": 100.0,
                "total_credit": 100.0,
                "is_balanced": True,
            }

        async def generate_income_statement(self, start_date, end_date, generated_by="system"):
            return {
                "success": True,
                "period": {"start_date": start_date.isoformat(), "end_date": end_date.isoformat()},
                "revenues": [{"account_code": "4.1", "account_name": "Shipping Revenue", "amount": 100.0}],
                "total_revenue": 100.0,
                "expenses": [],
                "total_expense": 0.0,
                "net_income": 100.0,
                "net_income_percent": 100.0,
            }

        async def generate_balance_sheet(self, as_of_date, generated_by="system"):
            return {
                "success": True,
                "as_of_date": as_of_date.isoformat(),
                "assets": [{"account_code": "1.2", "account_name": "Accounts Receivable", "amount": 100.0}],
                "total_assets": 100.0,
                "liabilities": [],
                "total_liabilities": 0.0,
                "equity": [{"account_code": "3.2", "account_name": "Retained Earnings", "amount": 100.0}],
                "total_equity": 100.0,
                "is_balanced": True,
            }

    return FakeAccountingService()


@pytest.fixture
def override_accounting_dependencies(fake_accounting_service):
    async def fake_current_user():
        return {"id": 1, "email": "manager@example.com", "role": "admin"}

    async def fake_accounting_service_dep():
        return fake_accounting_service

    app.dependency_overrides[accounting_module.get_current_user] = fake_current_user
    app.dependency_overrides[accounting_module.get_accounting_service] = fake_accounting_service_dep


class TestAccountingRoutes:
    @pytest.mark.asyncio
    async def test_list_accounts(self, async_client, override_accounting_dependencies):
        response = await async_client.get("/api/v1/accounting/accounts")

        assert response.status_code == 200
        body = response.json()
        assert body["total"] == 2
        assert body["items"][0]["account_code"] == "1.2"

    @pytest.mark.asyncio
    async def test_create_journal_entry(self, async_client, override_accounting_dependencies):
        response = await async_client.post(
            "/api/v1/accounting/journal-entries",
            json={
                "entry_date": "2026-03-21",
                "description": "Customer invoice posting",
                "lines": [
                    {"account_id": 1, "debit": 100.0, "credit": 0.0},
                    {"account_id": 2, "debit": 0.0, "credit": 100.0},
                ],
            },
        )

        assert response.status_code == 201
        assert response.json()["entry_number"] == "JE-20260321-ABC123"

    @pytest.mark.asyncio
    async def test_get_trial_balance(self, async_client, override_accounting_dependencies):
        response = await async_client.get("/api/v1/accounting/trial-balance", params={"as_of_date": "2026-03-21"})

        assert response.status_code == 200
        body = response.json()
        assert body["is_balanced"] is True
        assert body["total_debit"] == 100.0
