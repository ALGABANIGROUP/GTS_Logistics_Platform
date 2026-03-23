from __future__ import annotations

import os
from typing import Dict, Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.db_config import get_db_async
from backend.models.financial import Expense, ExpenseStatus  # type: ignore[import]

try:
    from backend.ai.openai_safe_client import (  # type: ignore[import]
        get_openai_client as _get_openai_client,
    )
except Exception:
    _get_openai_client = None


def get_openai_client() -> Any:
    if _get_openai_client is None:
        return None
    return _get_openai_client()


router = APIRouter(prefix="/ai", tags=["AI Finance Bot"])

OPENAI_ENABLED = os.getenv("OPENAI_ENABLED", "0").lower() in ("1", "true", "yes", "on")
EXTERNAL_APIS_ENABLED = os.getenv("EXTERNAL_APIS_ENABLED", "0").lower() in ("1", "true", "yes", "on")


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
        gpt_output = "AI temporarily disabled."

        if OPENAI_ENABLED and EXTERNAL_APIS_ENABLED:
            client = get_openai_client()
            if client is not None:
                summary_text = "\n".join(
                    f"{cat}: ${amt:.2f}" for (cat, amt) in category_summary.items()
                )

                prompt = (
                    "Company expenses summary:\n"
                    f"{summary_text}\n\n"
                    f"Total expenses: ${total_expenses:.2f}\n"
                    "Provide 3 financial insights and 2 cost-saving suggestions."
                )

                client_any: Any = client
                resp = await client_any.chat.completions.create(  # type: ignore[call-arg]
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "You are a financial advisor AI."},
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.5,
                    max_tokens=400,
                )

                content = resp.choices[0].message.content if resp and resp.choices else ""
                gpt_output = (content or "").strip() or "No recommendations available."

        return {
            "total_expenses": total_expenses,
            "by_category": category_summary,
            "gpt_analysis": gpt_output,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Finance analysis failed: {e}")


