from __future__ import annotations

from typing import Dict, Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.db_config import get_db_async
from backend.models.financial import Expense, ExpenseStatus  # type: ignore[import]

router = APIRouter()


@router.get("/finance-analysis")
async def finance_analysis(db: AsyncSession = Depends(get_db_async)) -> Dict[str, Any]:
    try:
        paid_value = getattr(ExpenseStatus.PAID, "value", str(ExpenseStatus.PAID))

        result = await db.execute(
            select(Expense).where(Expense.status == paid_value)
        )
        expenses = result.scalars().all()

        if not expenses:
            return {
                "total_expenses": 0.0,
                "by_category": {},
                "gpt_analysis": "No paid expenses found.",
            }

        category_summary: Dict[str, float] = {}
        total_expenses = 0.0

        for exp in expenses:
            amount = float(getattr(exp, "amount", 0) or 0)
            category = getattr(exp, "category", None) or "Uncategorized"
            category_summary[category] = category_summary.get(category, 0.0) + amount
            total_expenses += amount

        total_expenses = round(total_expenses, 2)

        return {
            "total_expenses": total_expenses,
            "by_category": category_summary,
            "gpt_analysis": "AI temporarily disabled.",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Finance analysis failed: {e}")


