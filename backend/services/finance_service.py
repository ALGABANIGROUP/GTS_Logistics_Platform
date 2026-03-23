# backend/services/finance_service.py
from __future__ import annotations

from datetime import datetime
from typing import Sequence, Dict, Any

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from backend.models.financial import Expense, ExpenseStatus

# Import unified expense schemas
from backend.schemas.expense_schemas import ExpenseCreate, ExpenseOut


async def list_expenses(db: AsyncSession) -> Sequence[Expense]:
    """
    Return all expenses ordered by creation date (newest first).
    """
    result = await db.execute(
        select(Expense).order_by(Expense.created_at.desc())
    )
    return result.scalars().all()


async def create_expense(db: AsyncSession, payload: ExpenseCreate) -> Expense:
    """
    Create a new Expense row and return the ORM object.
    """
    created_at = payload.created_at or datetime.utcnow()
    status_label = (payload.status or ExpenseStatus.PENDING.value).upper()

    if status_label not in ("PENDING", "PAID"):
        status_label = "PENDING"

    dedupe_key = Expense.make_dedupe_key(
        category=payload.category,
        amount=payload.amount,
        description=payload.description,
        vendor=payload.vendor,
        created_at_iso=created_at.isoformat(),
    )

    obj = Expense(
        category=payload.category,
        amount=payload.amount,
        description=payload.description or None,
        vendor=payload.vendor or None,
        status=status_label,
        created_at=created_at,
        updated_at=datetime.utcnow(),
        dedupe_key=dedupe_key,
    )

    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj


async def finance_summary(db: AsyncSession) -> Dict[str, Any]:
    """
    Simple summarized view of expenses grouped by status.
    """
    total_q = await db.execute(
        select(func.coalesce(func.sum(Expense.amount), 0.0))
    )
    total_expenses = float(total_q.scalar() or 0.0)

    by_status_q = await db.execute(
        select(Expense.status, func.coalesce(func.sum(Expense.amount), 0.0))
        .group_by(Expense.status)
    )
    by_status: Dict[str, float] = {
        str(status): float(amount) for status, amount in by_status_q.all()
    }

    return {
        "total_expenses": round(total_expenses, 2),
        "by_status": by_status,
    }

