from __future__ import annotations

import logging
from datetime import date, datetime
from typing import Any, Dict, List, Optional
from uuid import uuid4

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.accounting_models import (
    Account,
    AccountBalance,
    AccountingInvoice,
    AccountingInvoiceStatus,
    AccountType,
    FinancialReport,
    FinancialReportType,
    JournalEntry,
    JournalEntryLine,
    NormalBalance,
)

logger = logging.getLogger(__name__)


class AccountingService:
    """Async accounting service for general ledger and financial reports."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_accounts(self, active_only: bool = False) -> List[Account]:
        stmt = select(Account).order_by(Account.account_code.asc())
        if active_only:
            stmt = stmt.where(Account.is_active.is_(True))
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def create_journal_entry(
        self,
        *,
        entry_date: date,
        description: str,
        lines: List[Dict[str, Any]],
        reference_type: Optional[str] = None,
        reference_id: Optional[str] = None,
        posted_by: str = "system",
    ) -> Dict[str, Any]:
        total_debit = round(sum(float(line.get("debit") or 0.0) for line in lines), 2)
        total_credit = round(sum(float(line.get("credit") or 0.0) for line in lines), 2)

        if total_debit <= 0 or total_credit <= 0 or total_debit != total_credit:
            return {
                "success": False,
                "error": f"Journal entry must balance. debit={total_debit}, credit={total_credit}",
            }

        entry_number = f"JE-{datetime.utcnow():%Y%m%d}-{uuid4().hex[:6].upper()}"
        entry = JournalEntry(
            entry_number=entry_number,
            entry_date=entry_date,
            description=description,
            reference_type=reference_type,
            reference_id=reference_id,
            posted_by=posted_by,
            is_posted=True,
        )
        self.db.add(entry)
        await self.db.flush()

        for line in lines:
            journal_line = JournalEntryLine(
                entry_id=entry.id,
                account_id=int(line["account_id"]),
                debit=float(line.get("debit") or 0.0),
                credit=float(line.get("credit") or 0.0),
                description=line.get("description") or description,
            )
            self.db.add(journal_line)
            await self._update_account_balance(
                account_id=journal_line.account_id,
                balance_date=entry_date,
                debit=journal_line.debit,
                credit=journal_line.credit,
            )

        await self.db.commit()
        return {
            "success": True,
            "entry_id": entry.id,
            "entry_number": entry_number,
            "total_debit": total_debit,
            "total_credit": total_credit,
        }

    async def create_invoice(
        self,
        invoice_data: Dict[str, Any],
        auto_post: bool = True,
        posted_by: str = "system",
    ) -> Dict[str, Any]:
        invoice_date = invoice_data["invoice_date"]
        total_amount = float(invoice_data["total_amount"])
        tax_amount = float(invoice_data.get("tax_amount") or 0.0)
        discount_amount = float(invoice_data.get("discount_amount") or 0.0)
        net_amount = round(total_amount + tax_amount - discount_amount, 2)
        invoice_number = f"INV-{datetime.utcnow():%Y%m%d}-{uuid4().hex[:6].upper()}"

        invoice = AccountingInvoice(
            invoice_number=invoice_number,
            invoice_date=invoice_date,
            due_date=invoice_data.get("due_date"),
            customer_id=invoice_data.get("customer_id"),
            customer_name=invoice_data.get("customer_name"),
            total_amount=total_amount,
            tax_amount=tax_amount,
            discount_amount=discount_amount,
            net_amount=net_amount,
            status=AccountingInvoiceStatus.POSTED if auto_post else AccountingInvoiceStatus.DRAFT,
        )
        self.db.add(invoice)
        await self.db.flush()

        journal_entry_number = None
        if auto_post:
            accounts = await self._get_accounts_by_codes(
                {
                    "receivable": "1.2",
                    "revenue": "4.1",
                    "tax_liability": "2.1",
                    "discount": "5.4",
                }
            )
            if "receivable" not in accounts or "revenue" not in accounts:
                await self.db.rollback()
                return {
                    "success": False,
                    "error": "Required accounting accounts are missing from the chart of accounts.",
                }

            lines: List[Dict[str, Any]] = [
                {"account_id": accounts["receivable"], "debit": net_amount, "credit": 0.0},
                {"account_id": accounts["revenue"], "debit": 0.0, "credit": total_amount},
            ]
            if tax_amount > 0 and "tax_liability" in accounts:
                lines.append({"account_id": accounts["tax_liability"], "debit": 0.0, "credit": tax_amount})
            if discount_amount > 0:
                discount_account = accounts.get("discount") or accounts["revenue"]
                lines.append({"account_id": discount_account, "debit": discount_amount, "credit": 0.0})

            journal_result = await self.create_journal_entry(
                entry_date=invoice_date,
                description=f"Invoice {invoice_number} for {invoice.customer_name or 'customer'}",
                lines=lines,
                reference_type="invoice",
                reference_id=invoice_number,
                posted_by=posted_by,
            )
            if not journal_result["success"]:
                return journal_result

            invoice.journal_entry_id = journal_result["entry_id"]
            journal_entry_number = journal_result["entry_number"]
            await self.db.commit()
        else:
            await self.db.commit()

        return {
            "success": True,
            "invoice": {
                "id": invoice.id,
                "number": invoice.invoice_number,
                "net_amount": invoice.net_amount,
                "status": invoice.status.value,
                "journal_entry": journal_entry_number,
            },
        }

    async def generate_trial_balance(self, as_of_date: date, generated_by: str = "system") -> Dict[str, Any]:
        accounts = await self.list_accounts(active_only=True)
        rows: List[Dict[str, Any]] = []
        total_debit = 0.0
        total_credit = 0.0

        for account in accounts:
            balance = await self._get_account_balance_from_entries(account.id, as_of_date)
            if round(balance, 2) == 0:
                continue

            debit_balance = round(balance, 2) if account.normal_balance == NormalBalance.DEBIT and balance > 0 else 0.0
            credit_balance = round(balance, 2) if account.normal_balance == NormalBalance.CREDIT and balance > 0 else 0.0

            rows.append(
                {
                    "account_code": account.account_code,
                    "account_name": account.account_name,
                    "debit_balance": debit_balance,
                    "credit_balance": credit_balance,
                }
            )
            total_debit += debit_balance
            total_credit += credit_balance

        payload = {
            "success": True,
            "as_of_date": as_of_date.isoformat(),
            "trial_balance": rows,
            "total_debit": round(total_debit, 2),
            "total_credit": round(total_credit, 2),
            "is_balanced": round(total_debit, 2) == round(total_credit, 2),
        }
        await self._store_report(FinancialReportType.TRIAL_BALANCE, as_of_date, None, None, payload, generated_by)
        return payload

    async def generate_income_statement(
        self,
        start_date: date,
        end_date: date,
        generated_by: str = "system",
    ) -> Dict[str, Any]:
        revenues = await self._collect_accounts_for_period(AccountType.REVENUE, start_date, end_date)
        expenses = await self._collect_accounts_for_period(AccountType.EXPENSE, start_date, end_date)
        total_revenue = round(sum(item["amount"] for item in revenues), 2)
        total_expense = round(sum(item["amount"] for item in expenses), 2)
        net_income = round(total_revenue - total_expense, 2)

        payload = {
            "success": True,
            "period": {"start_date": start_date.isoformat(), "end_date": end_date.isoformat()},
            "revenues": revenues,
            "total_revenue": total_revenue,
            "expenses": expenses,
            "total_expense": total_expense,
            "net_income": net_income,
            "net_income_percent": round((net_income / total_revenue) * 100, 2) if total_revenue else 0.0,
        }
        await self._store_report(
            FinancialReportType.INCOME_STATEMENT,
            end_date,
            start_date,
            end_date,
            payload,
            generated_by,
        )
        return payload

    async def generate_balance_sheet(self, as_of_date: date, generated_by: str = "system") -> Dict[str, Any]:
        assets, total_assets = await self._collect_accounts_as_of(AccountType.ASSET, as_of_date)
        liabilities, total_liabilities = await self._collect_accounts_as_of(AccountType.LIABILITY, as_of_date)
        equity, total_equity = await self._collect_accounts_as_of(AccountType.EQUITY, as_of_date)

        payload = {
            "success": True,
            "as_of_date": as_of_date.isoformat(),
            "assets": assets,
            "total_assets": total_assets,
            "liabilities": liabilities,
            "total_liabilities": total_liabilities,
            "equity": equity,
            "total_equity": total_equity,
            "is_balanced": round(total_assets, 2) == round(total_liabilities + total_equity, 2),
        }
        await self._store_report(FinancialReportType.BALANCE_SHEET, as_of_date, None, None, payload, generated_by)
        return payload

    async def _collect_accounts_as_of(self, account_type: AccountType, as_of_date: date) -> tuple[List[Dict[str, Any]], float]:
        stmt = select(Account).where(Account.account_type == account_type, Account.is_active.is_(True)).order_by(Account.account_code.asc())
        result = await self.db.execute(stmt)
        accounts = list(result.scalars().all())

        rows: List[Dict[str, Any]] = []
        total = 0.0
        for account in accounts:
            balance = await self._get_account_balance_from_entries(account.id, as_of_date)
            if round(balance, 2) == 0:
                continue
            rows.append(
                {
                    "account_code": account.account_code,
                    "account_name": account.account_name,
                    "amount": round(balance, 2),
                }
            )
            total += round(balance, 2)
        return rows, round(total, 2)

    async def _collect_accounts_for_period(
        self,
        account_type: AccountType,
        start_date: date,
        end_date: date,
    ) -> List[Dict[str, Any]]:
        stmt = select(Account).where(Account.account_type == account_type, Account.is_active.is_(True)).order_by(Account.account_code.asc())
        result = await self.db.execute(stmt)
        accounts = list(result.scalars().all())

        rows: List[Dict[str, Any]] = []
        for account in accounts:
            amount = await self._get_account_balance_for_period(account.id, account.normal_balance, start_date, end_date)
            if round(amount, 2) == 0:
                continue
            rows.append(
                {
                    "account_code": account.account_code,
                    "account_name": account.account_name,
                    "amount": round(abs(amount), 2),
                }
            )
        return rows

    async def _update_account_balance(
        self,
        *,
        account_id: int,
        balance_date: date,
        debit: float,
        credit: float,
    ) -> None:
        stmt = select(AccountBalance).where(
            AccountBalance.account_id == account_id,
            AccountBalance.balance_date == balance_date,
        )
        result = await self.db.execute(stmt)
        balance = result.scalars().first()

        if balance is None:
            prev_stmt = (
                select(AccountBalance)
                .where(AccountBalance.account_id == account_id, AccountBalance.balance_date < balance_date)
                .order_by(AccountBalance.balance_date.desc())
                .limit(1)
            )
            prev_result = await self.db.execute(prev_stmt)
            previous = prev_result.scalars().first()
            opening_balance = float(previous.closing_balance if previous else 0.0)
            balance = AccountBalance(
                account_id=account_id,
                balance_date=balance_date,
                opening_balance=opening_balance,
                total_debit=0.0,
                total_credit=0.0,
                closing_balance=opening_balance,
            )
            self.db.add(balance)
            await self.db.flush()

        balance.total_debit = float(balance.total_debit or 0.0) + float(debit or 0.0)
        balance.total_credit = float(balance.total_credit or 0.0) + float(credit or 0.0)
        balance.closing_balance = round(
            float(balance.opening_balance or 0.0) + float(balance.total_debit) - float(balance.total_credit),
            2,
        )

    async def _get_account_balance_from_entries(self, account_id: int, as_of_date: date) -> float:
        stmt = (
            select(
                func.coalesce(func.sum(JournalEntryLine.debit), 0.0),
                func.coalesce(func.sum(JournalEntryLine.credit), 0.0),
                Account.normal_balance,
            )
            .join(JournalEntry, JournalEntry.id == JournalEntryLine.entry_id)
            .join(Account, Account.id == JournalEntryLine.account_id)
            .where(
                JournalEntryLine.account_id == account_id,
                JournalEntry.entry_date <= as_of_date,
                JournalEntry.is_posted.is_(True),
            )
            .group_by(Account.normal_balance)
        )
        result = await self.db.execute(stmt)
        row = result.first()
        if not row:
            return 0.0

        debit_total, credit_total, normal_balance = row
        if normal_balance == NormalBalance.DEBIT:
            return round(float(debit_total or 0.0) - float(credit_total or 0.0), 2)
        return round(float(credit_total or 0.0) - float(debit_total or 0.0), 2)

    async def _get_account_balance_for_period(
        self,
        account_id: int,
        normal_balance: NormalBalance,
        start_date: date,
        end_date: date,
    ) -> float:
        stmt = (
            select(
                func.coalesce(func.sum(JournalEntryLine.debit), 0.0),
                func.coalesce(func.sum(JournalEntryLine.credit), 0.0),
            )
            .join(JournalEntry, JournalEntry.id == JournalEntryLine.entry_id)
            .where(
                JournalEntryLine.account_id == account_id,
                JournalEntry.entry_date >= start_date,
                JournalEntry.entry_date <= end_date,
                JournalEntry.is_posted.is_(True),
            )
        )
        result = await self.db.execute(stmt)
        debit_total, credit_total = result.one()
        if normal_balance == NormalBalance.DEBIT:
            return round(float(debit_total or 0.0) - float(credit_total or 0.0), 2)
        return round(float(credit_total or 0.0) - float(debit_total or 0.0), 2)

    async def _get_accounts_by_codes(self, codes: Dict[str, str]) -> Dict[str, int]:
        result: Dict[str, int] = {}
        for key, code in codes.items():
            stmt = select(Account).where(Account.account_code == code).limit(1)
            row = await self.db.execute(stmt)
            account = row.scalars().first()
            if account:
                result[key] = int(account.id)
        return result

    async def _store_report(
        self,
        report_type: FinancialReportType,
        report_date: date,
        start_date: Optional[date],
        end_date: Optional[date],
        data: Dict[str, Any],
        generated_by: str,
    ) -> None:
        report = FinancialReport(
            report_type=report_type,
            report_date=report_date,
            start_date=start_date,
            end_date=end_date,
            data=data,
            generated_by=generated_by,
        )
        self.db.add(report)
        await self.db.commit()
