from __future__ import annotations

import re
from datetime import date, datetime
from typing import Dict, List, Optional, Tuple
from uuid import uuid4

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.invoices import Invoice


class PlanInvoiceService:
    """Service dedicated to subscription/plan invoice operations."""

    _PLAN_INVOICE_PREFIX = "PLANINV"

    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    async def create_plan_invoice(
        self,
        *,
        user_id: int,
        plan_code: str,
        amount_usd: float,
        status: str = "pending",
        invoice_date: Optional[datetime] = None,
    ) -> Invoice:
        now = invoice_date or datetime.utcnow()
        plan_code_normalized = str(plan_code or "UNKNOWN").upper()
        invoice = Invoice(
            number=self._generate_plan_invoice_number(
                plan_code=plan_code_normalized,
                user_id=user_id,
                issued_at=now,
            ),
            date=now.date(),
            amount_usd=float(amount_usd),
            status=str(status or "pending").lower(),
            plan_code=plan_code_normalized,
            user_id=int(user_id),
            created_at=now,
            updated_at=now,
        )
        self.db.add(invoice)
        await self.db.flush()
        await self.db.commit()
        return invoice

    async def ensure_subscription_cycle_invoice(
        self,
        *,
        user_id: int,
        plan_code: str,
        amount_usd: float,
        status: str = "pending",
        invoice_date: Optional[datetime] = None,
    ) -> Invoice:
        now = invoice_date or datetime.utcnow()
        plan_code_normalized = str(plan_code or "UNKNOWN").upper()
        target_date = now.date()
        stmt = (
            select(Invoice)
            .where(
                Invoice.user_id == int(user_id),
                Invoice.plan_code == plan_code_normalized,
                Invoice.date == target_date,
            )
            .order_by(Invoice.created_at.desc(), Invoice.id.desc())
        )
        result = await self.db.execute(stmt)
        existing = result.scalars().first()
        if existing:
            return existing

        return await self.create_plan_invoice(
            user_id=user_id,
            plan_code=plan_code_normalized,
            amount_usd=amount_usd,
            status=status,
            invoice_date=now,
        )

    async def list_plan_invoices(
        self,
        *,
        plan_code: Optional[str] = None,
        status: Optional[str] = None,
        user_id: Optional[int] = None,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Tuple[List[Invoice], int]:
        filters = [Invoice.number.like(f"{self._PLAN_INVOICE_PREFIX}-%")]
        if plan_code:
            filters.append(Invoice.plan_code == str(plan_code).upper())
        if status:
            filters.append(func.lower(Invoice.status) == str(status).lower())
        if user_id is not None:
            filters.append(Invoice.user_id == int(user_id))
        if from_date:
            filters.append(Invoice.date >= from_date)
        if to_date:
            filters.append(Invoice.date <= to_date)

        count_stmt = select(func.count()).select_from(Invoice).where(*filters)
        total = int((await self.db.execute(count_stmt)).scalar() or 0)

        stmt = (
            select(Invoice)
            .where(*filters)
            .order_by(Invoice.date.desc(), Invoice.created_at.desc(), Invoice.id.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all()), total

    async def get_plan_invoice_summary(
        self,
        *,
        user_id: Optional[int] = None,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
    ) -> Dict[str, Dict[str, float]]:
        filters = [Invoice.number.like(f"{self._PLAN_INVOICE_PREFIX}-%")]
        if user_id is not None:
            filters.append(Invoice.user_id == int(user_id))
        if from_date:
            filters.append(Invoice.date >= from_date)
        if to_date:
            filters.append(Invoice.date <= to_date)

        stmt = select(Invoice).where(*filters)
        rows = (await self.db.execute(stmt)).scalars().all()

        summary: Dict[str, Dict[str, float]] = {}
        for invoice in rows:
            plan_code = str(invoice.plan_code or self._parse_plan_code_from_number(invoice.number)).upper()
            bucket = summary.setdefault(
                plan_code,
                {
                    "count": 0,
                    "total_amount_usd": 0.0,
                    "paid_count": 0,
                    "pending_count": 0,
                },
            )
            bucket["count"] += 1
            bucket["total_amount_usd"] += float(invoice.amount_usd or 0)
            invoice_status = str(invoice.status or "").lower()
            if invoice_status == "paid":
                bucket["paid_count"] += 1
            elif invoice_status == "pending":
                bucket["pending_count"] += 1

        return summary

    def _generate_plan_invoice_number(
        self,
        *,
        plan_code: str,
        user_id: int,
        issued_at: Optional[datetime] = None,
    ) -> str:
        timestamp = (issued_at or datetime.utcnow()).strftime("%Y%m%d%H%M%S")
        suffix = uuid4().hex[:6].upper()
        return f"{self._PLAN_INVOICE_PREFIX}-{plan_code.upper()}-U{int(user_id)}-{timestamp}-{suffix}"

    def _parse_plan_code_from_number(self, number: Optional[str]) -> str:
        match = re.match(rf"^{self._PLAN_INVOICE_PREFIX}-([A-Z0-9_]+)-U\d+-", str(number or "").upper())
        return match.group(1) if match else "UNKNOWN"
