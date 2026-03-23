from typing import List, Any, cast

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from backend.database.config import get_db, get_db_async  # type: ignore[import]
from backend.models.platform_expense import PlatformExpense  # type: ignore[import]
from backend.utils.rbac_utils import require_roles  # type: ignore[import]

router = APIRouter()


@router.get(
    "/financial/summary",
    dependencies=[require_roles(["admin", "finance"])],
)
async def get_financial_summary(
    db: Session = Depends(get_db),
):
    try:
        financial_data = {
            "total_revenue": 120000.0,
            "total_expenses": 75000.0,
            "net_profit": 45000.0,
            "profit_margin": "37.5%",
        }
        return financial_data
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching financial summary: {str(e)}",
        )


@router.get(
    "/financial/tax-filing",
    dependencies=[require_roles(["admin", "finance"])],
)
async def get_tax_filing_status(
    db: Session = Depends(get_db),
):
    try:
        return {
            "business_tax_filing_status": "Completed",
            "personal_tax_filing_status": "Pending",
            "next_deadline": "April 15, 2025",
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching tax filing details: {str(e)}",
        )


@router.get(
    "/financial/tax-planning",
    dependencies=[require_roles(["admin", "finance"])],
)
async def get_tax_planning_advice(
    db: Session = Depends(get_db),
):
    try:
        return {
            "recommended_deductions": [
                "Home Office Deduction",
                "Business Travel Expenses",
                "Health Insurance Premiums",
            ],
            "savings_potential": "Estimated $5,000 in tax savings",
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching tax planning advice: {str(e)}",
        )


@router.get(
    "/financial/retirement-planning",
    dependencies=[require_roles(["admin", "finance"])],
)
async def get_retirement_planning_advice(
    db: Session = Depends(get_db),
):
    try:
        return {
            "current_savings": 50000.0,
            "recommended_annual_contribution": 10000.0,
            "expected_retirement_age": 65,
            "projected_savings_at_retirement": 750000.0,
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching retirement planning details: {str(e)}",
        )


@router.get(
    "/financial/accounting-software",
    dependencies=[require_roles(["admin", "finance"])],
)
async def get_accounting_software_features(
    db: Session = Depends(get_db),
):
    try:
        return {
            "automatic_transaction_sync": True,
            "expense_tracking": True,
            "invoicing_and_payments": True,
            "financial_reporting": True,
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching accounting software details: {str(e)}",
        )


@router.get(
    "/financial/support",
    dependencies=[require_roles(["admin", "finance"])],
)
async def get_financial_support(
    db: Session = Depends(get_db),
):
    try:
        return {
            "accountant_availability": "Monday - Friday, 9 AM - 5 PM",
            "contact_methods": ["Chat", "Email", "Phone"],
            "response_time": "Within 24 hours",
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching financial support details: {str(e)}",
        )


# Import unified expense schemas
from backend.schemas.expense_schemas import ExpenseCreate, ExpenseOut


@router.get(
    "/financial/platform-expenses",
    response_model=List[ExpenseOut],
    dependencies=[require_roles(["admin", "finance"])],
)
async def get_expenses(
    db: AsyncSession = Depends(get_db_async),
):
    result = await db.execute(select(PlatformExpense))
    return result.scalars().all()


@router.post(
    "/financial/platform-expenses",
    response_model=ExpenseOut,
    dependencies=[require_roles(["admin", "finance"])],
)
async def create_expense(
    payload: ExpenseCreate,
    db: AsyncSession = Depends(get_db_async),
):
    new_expense = PlatformExpense(**payload.dict())
    db.add(new_expense)
    await db.commit()
    await db.refresh(new_expense)
    return new_expense


@router.put(
    "/financial/platform-expenses/{expense_id}",
    response_model=ExpenseOut,
    dependencies=[require_roles(["admin", "finance"])],
)
async def update_expense(
    expense_id: int,
    payload: ExpenseCreate,
    db: AsyncSession = Depends(get_db_async),
):
    result = await db.execute(
        select(PlatformExpense).where(PlatformExpense.id == expense_id)
    )
    expense = result.scalars().first()
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")

    expense.category = payload.category
    expense.amount = cast(Any, payload.amount)
    expense.description = payload.description
    await db.commit()
    await db.refresh(expense)
    return expense


@router.delete(
    "/financial/platform-expenses/{expense_id}",
    dependencies=[require_roles(["admin", "finance"])],
)
async def delete_expense(
    expense_id: int,
    db: AsyncSession = Depends(get_db_async),
):
    result = await db.execute(
        select(PlatformExpense).where(PlatformExpense.id == expense_id)
    )
    expense = result.scalars().first()
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")

    await db.delete(expense)
    await db.commit()
    return {"message": "Expense deleted successfully"}

