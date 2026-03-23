from __future__ import annotations

from typing import List, Any

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from backend.database.config import get_db_async  # type: ignore[import]
from backend.models.financial import Expense  # type: ignore[import]

router = APIRouter(
    prefix="/example-finance",
    tags=["Example Finance"],
)


@router.get("/expenses")
async def list_example_expenses(
    db: AsyncSession = Depends(get_db_async),
) -> List[Any]:
    """
    Simple example endpoint that returns up to 50 Expense rows.
    This keeps the module valid and avoids missing imports.
    """
    result = await db.execute(select(Expense).limit(50))
    expenses = result.scalars().all()
    return [  # make it JSON-serializable
        {
            "id": getattr(e, "id", None),
            "category": getattr(e, "category", None),
            "amount": float(getattr(e, "amount", 0) or 0),
            "status": str(getattr(e, "status", "")),
            "created_at": getattr(e, "created_at", None),
        }
        for e in expenses
    ]

