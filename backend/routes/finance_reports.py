from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from backend.database.session import get_async_session as get_session
from backend.models.financial import Expense, ExpenseStatus
router = APIRouter(prefix='/finance/reports', tags=['Finance Reports'])

@router.get('/summary')
async def get_summary(db: AsyncSession=Depends(get_session)):
    try:
        rows = await db.execute(select(func.coalesce(func.sum(Expense.amount), 0.0), Expense.category).where(Expense.status == ExpenseStatus.PAID).group_by(Expense.category))
        data = rows.all()
        total = float(sum((amt for (amt, _) in data)))
        by_category = {category or 'Uncategorized': float(amt) for (amt, category) in data}
        return {'total_expenses': round(total, 2), 'by_category': by_category}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Summary failed: {e}')
