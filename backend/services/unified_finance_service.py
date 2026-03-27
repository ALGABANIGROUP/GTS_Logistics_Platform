from __future__ import annotations

from datetime import date, datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.financial import Expense
from backend.models.invoices import Invoice
from backend.models.payment import Payment, PaymentStatus, PaymentType
from backend.schemas.expense_schemas import ExpenseCreate
from backend.services.accounting_service import AccountingService
from backend.services.payment_service import PaymentService
from backend.models.accounting_models import JournalEntry


class UnifiedFinanceService:
    """Canonical finance facade over invoices, expenses, payments, and ledger reports."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.accounting = AccountingService(db)
        self.payment_service = PaymentService(db, None)  # type: ignore[arg-type]

    async def get_dashboard(self) -> Dict[str, Any]:
        invoices = await self.list_invoices(limit=500)
        expenses = await self.list_expenses(limit=500)
        payments = await self.list_payments(limit=500)

        total_revenue = round(sum(float(item["amount_usd"]) for item in invoices), 2)
        total_expenses = round(sum(float(item["amount"]) for item in expenses), 2)
        completed_payments = [item for item in payments if item["status"] == PaymentStatus.COMPLETED.value]
        pending_invoices = [
            item for item in invoices if item["status"] in {"pending", "sent", "overdue", "draft"}
        ]

        return {
            "success": True,
            "metrics": {
                "total_revenue": total_revenue,
                "total_expenses": total_expenses,
                "net_profit": round(total_revenue - total_expenses, 2),
                "accounts_receivable": round(sum(float(item["amount_usd"]) for item in pending_invoices), 2),
                "payments_collected": round(sum(float(item["amount"]) for item in completed_payments), 2),
                "invoice_count": len(invoices),
                "expense_count": len(expenses),
                "payment_count": len(payments),
            },
            "recent": {
                "invoices": invoices[:10],
                "expenses": expenses[:10],
                "payments": payments[:10],
            },
        }

    async def bootstrap_demo_data(self, *, user_id: int, posted_by: str = "system") -> Dict[str, Any]:
        journal_count = await self.db.scalar(select(func.count(JournalEntry.id)))
        if int(journal_count or 0) > 0:
            return {
                "success": True,
                "created": False,
                "message": "Ledger already contains journal entries.",
            }

        created: Dict[str, Any] = {}
        invoice_result = await self.create_invoice(
            invoice_date=date.today(),
            amount_usd=5000.0,
            customer_name="Acme Corporation",
            status="pending",
            posted_by=posted_by,
            user_id=user_id,
        )
        if not invoice_result.get("success"):
            return invoice_result
        created["invoice"] = invoice_result.get("invoice")

        expense_result = await self.create_expense(
            category="fuel",
            amount=1500.0,
            description="Diesel for truck fleet",
            vendor="Saudi Aramco",
            status="PENDING",
            created_at=datetime.utcnow(),
            posted_by=posted_by,
        )
        if not expense_result.get("success"):
            return expense_result
        created["expense"] = expense_result.get("expense")

        payment_result = await self.create_payment(
            user_id=user_id,
            payment_type="invoice",
            invoice_id=int(created["invoice"]["id"]),
            amount=5000.0,
            currency="USD",
            gateway="stripe",
            description="Demo invoice settlement",
            posted_by=posted_by,
        )
        if not payment_result.get("success"):
            return payment_result
        created["payment"] = payment_result.get("payment")

        return {
            "success": True,
            "created": True,
            "message": "Demo finance data created successfully.",
            "data": created,
        }

    async def list_invoices(self, limit: int = 100) -> List[Dict[str, Any]]:
        stmt = select(Invoice).order_by(Invoice.id.desc()).limit(limit)
        result = await self.db.execute(stmt)
        rows = result.scalars().all()
        return [
            {
                "id": int(item.id),
                "number": str(item.number),
                "date": item.date.isoformat() if item.date else None,
                "amount_usd": float(item.amount_usd),
                "status": str(item.status),
                "shipment_id": getattr(item, "shipment_id", None),
                "created_at": item.created_at.isoformat() if getattr(item, "created_at", None) else None,
                "updated_at": item.updated_at.isoformat() if getattr(item, "updated_at", None) else None,
            }
            for item in rows
        ]

    async def list_expenses(self, limit: int = 100) -> List[Dict[str, Any]]:
        stmt = select(Expense).order_by(Expense.created_at.desc()).limit(limit)
        result = await self.db.execute(stmt)
        rows = result.scalars().all()
        return [
            {
                "id": int(item.id),
                "category": str(item.category),
                "description": item.description,
                "vendor": item.vendor,
                "amount": float(item.amount),
                "status": str(item.status),
                "created_at": item.created_at.isoformat() if item.created_at else None,
                "updated_at": item.updated_at.isoformat() if item.updated_at else None,
            }
            for item in rows
        ]

    async def list_payments(self, limit: int = 100) -> List[Dict[str, Any]]:
        stmt = select(Payment).order_by(Payment.created_at.desc()).limit(limit)
        result = await self.db.execute(stmt)
        rows = result.scalars().all()
        return [
            {
                "id": int(item.id),
                "reference_id": str(item.reference_id),
                "invoice_id": int(item.invoice_id) if item.invoice_id is not None else None,
                "expense_id": int(item.expense_id) if item.expense_id is not None else None,
                "payment_type": getattr(item.payment_type, "value", item.payment_type),
                "supplier_name": item.supplier_name,
                "amount": float(item.amount),
                "currency": getattr(item.currency, "value", item.currency),
                "status": getattr(item.status, "value", item.status),
                "payment_gateway": getattr(item.payment_gateway, "value", item.payment_gateway),
                "gateway_transaction_id": item.gateway_transaction_id,
                "created_at": item.created_at.isoformat() if item.created_at else None,
                "payment_date": item.payment_date.isoformat() if item.payment_date else None,
            }
            for item in rows
        ]

    async def get_summary_report(self) -> Dict[str, Any]:
        invoice_totals = await self.db.execute(
            select(
                func.coalesce(func.sum(Invoice.amount_usd), 0.0),
                func.coalesce(func.count(Invoice.id), 0),
            )
        )
        total_invoice_amount, invoice_count = invoice_totals.one()

        expense_totals = await self.db.execute(
            select(
                func.coalesce(func.sum(Expense.amount), 0.0),
                func.coalesce(func.count(Expense.id), 0),
            )
        )
        total_expense_amount, expense_count = expense_totals.one()

        payment_totals = await self.db.execute(
            select(
                func.coalesce(func.sum(Payment.amount), 0.0),
                func.coalesce(func.count(Payment.id), 0),
            ).where(Payment.status == PaymentStatus.COMPLETED)
        )
        total_payment_amount, payment_count = payment_totals.one()

        return {
            "success": True,
            "invoices": {
                "count": int(invoice_count or 0),
                "total_amount_usd": round(float(total_invoice_amount or 0.0), 2),
            },
            "expenses": {
                "count": int(expense_count or 0),
                "total_amount": round(float(total_expense_amount or 0.0), 2),
            },
            "payments": {
                "count": int(payment_count or 0),
                "completed_amount": round(float(total_payment_amount or 0.0), 2),
            },
            "net_position": round(float(total_invoice_amount or 0.0) - float(total_expense_amount or 0.0), 2),
        }

    async def get_trial_balance(self, as_of_date: date, generated_by: str = "system") -> Dict[str, Any]:
        return await self.accounting.generate_trial_balance(as_of_date, generated_by=generated_by)

    async def get_income_statement(
        self,
        start_date: date,
        end_date: date,
        generated_by: str = "system",
    ) -> Dict[str, Any]:
        return await self.accounting.generate_income_statement(start_date, end_date, generated_by=generated_by)

    async def get_balance_sheet(self, as_of_date: date, generated_by: str = "system") -> Dict[str, Any]:
        return await self.accounting.generate_balance_sheet(as_of_date, generated_by=generated_by)

    async def create_invoice(
        self,
        *,
        invoice_date: date,
        amount_usd: float,
        customer_name: Optional[str],
        status: str = "pending",
        number: Optional[str] = None,
        shipment_id: Optional[int] = None,
        user_id: Optional[int] = None,
        posted_by: str = "system",
    ) -> Dict[str, Any]:
        invoice = Invoice(
            number=number or f"INV-{datetime.utcnow():%Y%m%d}-{Invoice.__name__[:3].upper()}{int(datetime.utcnow().timestamp())}",
            date=invoice_date,
            amount_usd=float(amount_usd),
            status=str(status or "pending").lower(),
            shipment_id=shipment_id,
            user_id=user_id,
        )
        self.db.add(invoice)
        await self.db.flush()

        accounts = await self.accounting._get_accounts_by_codes(  # noqa: SLF001
            {"receivable": "1.2", "revenue": "4.1"}
        )
        if "receivable" not in accounts or "revenue" not in accounts:
            await self.db.rollback()
            return {"success": False, "error": "Required ledger accounts are missing."}

        journal = await self.accounting.create_journal_entry(
            entry_date=invoice_date,
            description=f"Invoice {invoice.number} for {customer_name or 'customer'}",
            lines=[
                {"account_id": accounts["receivable"], "debit": float(amount_usd), "credit": 0.0},
                {"account_id": accounts["revenue"], "debit": 0.0, "credit": float(amount_usd)},
            ],
            reference_type="invoice",
            reference_id=invoice.number,
            posted_by=posted_by,
        )
        if not journal.get("success"):
            return journal

        return {
            "success": True,
            "invoice": {
                "id": int(invoice.id),
                "number": invoice.number,
                "date": invoice.date.isoformat(),
                "amount_usd": float(invoice.amount_usd),
                "status": invoice.status,
                "journal_entry": journal.get("entry_number"),
            },
        }

    async def create_expense(
        self,
        *,
        category: str,
        amount: float,
        description: Optional[str] = None,
        vendor: Optional[str] = None,
        created_at: Optional[datetime] = None,
        status: str = "PENDING",
        posted_by: str = "system",
    ) -> Dict[str, Any]:
        created_at = created_at or datetime.utcnow()
        normalized_status = str(status or "PENDING").upper()
        expense_payload = ExpenseCreate(
            category=category,
            amount=amount,
            description=description,
            vendor=vendor,
            created_at=created_at,
            status=normalized_status,
        )

        dedupe_key = Expense.make_dedupe_key(
            category=expense_payload.category,
            amount=expense_payload.amount,
            description=expense_payload.description,
            vendor=expense_payload.vendor,
            created_at_iso=created_at.isoformat(),
        )
        expense = Expense(
            category=expense_payload.category,
            amount=expense_payload.amount,
            description=expense_payload.description or None,
            vendor=expense_payload.vendor or None,
            status=normalized_status,
            created_at=created_at,
            updated_at=datetime.utcnow(),
            dedupe_key=dedupe_key,
        )
        self.db.add(expense)
        await self.db.flush()

        expense_account_code = self._map_expense_account_code(category)
        offset_code = "1.1.2" if normalized_status == "PAID" else "2.1"
        accounts = await self.accounting._get_accounts_by_codes(  # noqa: SLF001
            {"expense": expense_account_code, "offset": offset_code}
        )
        if "expense" not in accounts:
            accounts["expense"] = (await self.accounting._get_accounts_by_codes({"expense": "5"})).get("expense")  # noqa: SLF001
        if "offset" not in accounts:
            await self.db.rollback()
            return {"success": False, "error": "Required offset ledger account is missing."}

        journal = await self.accounting.create_journal_entry(
            entry_date=created_at.date(),
            description=description or f"{category.title()} expense",
            lines=[
                {"account_id": accounts["expense"], "debit": float(amount), "credit": 0.0},
                {"account_id": accounts["offset"], "debit": 0.0, "credit": float(amount)},
            ],
            reference_type="expense",
            reference_id=str(expense.id),
            posted_by=posted_by,
        )
        if not journal.get("success"):
            return journal

        return {
            "success": True,
            "expense": {
                "id": int(expense.id),
                "category": expense.category,
                "amount": float(expense.amount),
                "status": expense.status,
                "journal_entry": journal.get("entry_number"),
            },
        }

    async def create_payment(
        self,
        *,
        user_id: int,
        amount: float,
        payment_type: str = "invoice",
        reference_id: Optional[int] = None,
        invoice_id: Optional[int] = None,
        expense_id: Optional[int] = None,
        currency: str = "USD",
        gateway: str = "stripe",
        description: Optional[str] = None,
        payment_date: Optional[datetime] = None,
        metadata: Optional[Dict[str, Any]] = None,
        supplier_name: Optional[str] = None,
        posted_by: str = "system",
    ) -> Dict[str, Any]:
        normalized_type = PaymentType(str(payment_type).lower())
        effective_invoice_id = invoice_id
        effective_expense_id = expense_id
        if reference_id is not None:
            if normalized_type is PaymentType.INVOICE and effective_invoice_id is None:
                effective_invoice_id = reference_id
            if normalized_type is PaymentType.EXPENSE and effective_expense_id is None:
                effective_expense_id = reference_id

        invoice: Invoice | None = None
        expense: Expense | None = None
        journal_description: str
        journal_lines: list[dict[str, float | int]]

        if normalized_type is PaymentType.INVOICE:
            if effective_invoice_id is None:
                return {"success": False, "error": "invoice_id is required for invoice payments."}
            invoice = await self.db.get(Invoice, effective_invoice_id)
            if not invoice:
                return {"success": False, "error": "Invoice not found."}
        else:
            if effective_expense_id is None:
                return {"success": False, "error": "expense_id is required for expense payments."}
            expense = await self.db.get(Expense, effective_expense_id)
            if not expense:
                return {"success": False, "error": "Expense not found."}

        payment = await self.payment_service.create_payment(
            user_id=user_id,
            amount=amount,
            currency=currency,
            gateway=gateway,
            invoice_id=effective_invoice_id,
            expense_id=effective_expense_id,
            payment_type=normalized_type.value,
            supplier_name=supplier_name or (expense.vendor if expense else None),
            description=description
            or (
                f"Payment for invoice {invoice.number}"
                if invoice is not None
                else f"Expense payout to {supplier_name or (expense.vendor if expense else 'supplier')}"
            ),
            metadata=metadata or {},
        )
        await self.payment_service.record_transaction(
            payment_id=int(payment.id),
            transaction_type="payment",
            amount=float(amount),
            status=PaymentStatus.COMPLETED.value,
            gateway_response={"source": "unified_finance"},
        )
        await self.payment_service.update_payment_status(
            payment_id=int(payment.id),
            status=PaymentStatus.COMPLETED.value,
            payment_date=payment_date or datetime.utcnow(),
            metadata={
                **(metadata or {}),
                "posted_by": posted_by,
                "source": "unified_finance",
            },
        )

        if normalized_type is PaymentType.INVOICE:
            accounts = await self.accounting._get_accounts_by_codes(  # noqa: SLF001
                {"cash": "1.1.2", "receivable": "1.2"}
            )
            if "cash" not in accounts or "receivable" not in accounts:
                return {"success": False, "error": "Required ledger accounts are missing."}
            journal_description = f"Payment received for invoice {invoice.number}"
            journal_lines = [
                {"account_id": accounts["cash"], "debit": float(amount), "credit": 0.0},
                {"account_id": accounts["receivable"], "debit": 0.0, "credit": float(amount)},
            ]
        else:
            accounts = await self.accounting._get_accounts_by_codes(  # noqa: SLF001
                {"cash": "1.1.2", "payable": "2.1"}
            )
            if "cash" not in accounts or "payable" not in accounts:
                return {"success": False, "error": "Required ledger accounts are missing."}
            if expense is not None:
                expense.status = "PAID"
            journal_description = f"Payment made to {supplier_name or (expense.vendor if expense else 'supplier')}"
            journal_lines = [
                {"account_id": accounts["payable"], "debit": float(amount), "credit": 0.0},
                {"account_id": accounts["cash"], "debit": 0.0, "credit": float(amount)},
            ]

        journal = await self.accounting.create_journal_entry(
            entry_date=(payment_date or datetime.utcnow()).date(),
            description=journal_description,
            lines=journal_lines,
            reference_type="payment",
            reference_id=payment.reference_id,
            posted_by=posted_by,
        )
        if not journal.get("success"):
            return journal

        return {
            "success": True,
            "payment": {
                "id": int(payment.id),
                "reference_id": payment.reference_id,
                "invoice_id": int(payment.invoice_id) if payment.invoice_id is not None else None,
                "expense_id": int(payment.expense_id) if payment.expense_id is not None else None,
                "payment_type": getattr(payment.payment_type, "value", payment.payment_type),
                "supplier_name": payment.supplier_name,
                "amount": float(payment.amount),
                "currency": getattr(payment.currency, "value", payment.currency),
                "status": getattr(payment.status, "value", payment.status),
                "journal_entry": journal.get("entry_number"),
            },
        }

    @staticmethod
    def _map_expense_account_code(category: Optional[str]) -> str:
        normalized = str(category or "").strip().lower()
        mapping = {
            "fuel": "5.1",
            "maintenance": "5.2",
            "salary": "5.3",
            "salaries": "5.3",
            "payroll": "5.3",
        }
        return mapping.get(normalized, "5")
