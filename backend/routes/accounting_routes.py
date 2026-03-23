from __future__ import annotations

from datetime import date
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.session import get_async_session
from backend.security.auth import get_current_user
from backend.services.accounting_service import AccountingService

router = APIRouter(prefix="/api/v1/accounting", tags=["Accounting"])


class JournalEntryLineInput(BaseModel):
    account_id: int = Field(..., gt=0)
    debit: float = Field(default=0.0, ge=0.0)
    credit: float = Field(default=0.0, ge=0.0)
    description: Optional[str] = None


class JournalEntryCreateRequest(BaseModel):
    entry_date: date
    description: str = Field(..., min_length=1)
    lines: List[JournalEntryLineInput] = Field(..., min_length=2)
    reference_type: Optional[str] = None
    reference_id: Optional[str] = None


class AccountingInvoiceCreateRequest(BaseModel):
    invoice_date: date
    due_date: Optional[date] = None
    customer_id: Optional[int] = None
    customer_name: str = Field(..., min_length=1)
    total_amount: float = Field(..., gt=0.0)
    tax_amount: float = Field(default=0.0, ge=0.0)
    discount_amount: float = Field(default=0.0, ge=0.0)


async def get_accounting_service(
    db: AsyncSession = Depends(get_async_session),
) -> AccountingService:
    return AccountingService(db)


def _user_email(current_user: Any) -> str:
    if isinstance(current_user, dict):
        return str(current_user.get("email") or "system")
    return str(getattr(current_user, "email", None) or "system")


@router.get("/accounts")
async def list_accounts(
    active_only: bool = Query(default=False),
    service: AccountingService = Depends(get_accounting_service),
) -> Dict[str, Any]:
    accounts = await service.list_accounts(active_only=active_only)
    return {
        "items": [
            {
                "id": account.id,
                "account_code": account.account_code,
                "account_name": account.account_name,
                "account_type": account.account_type.value,
                "normal_balance": account.normal_balance.value,
                "level": account.level,
                "parent_id": account.parent_id,
                "is_active": account.is_active,
            }
            for account in accounts
        ],
        "total": len(accounts),
    }


@router.post("/journal-entries", status_code=status.HTTP_201_CREATED)
async def create_journal_entry(
    request: JournalEntryCreateRequest,
    current_user: Any = Depends(get_current_user),
    service: AccountingService = Depends(get_accounting_service),
) -> Dict[str, Any]:
    result = await service.create_journal_entry(
        entry_date=request.entry_date,
        description=request.description,
        lines=[line.model_dump() for line in request.lines],
        reference_type=request.reference_type,
        reference_id=request.reference_id,
        posted_by=_user_email(current_user),
    )
    if not result.get("success"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result.get("error", "Failed to create journal entry"))
    return result


@router.post("/invoices", status_code=status.HTTP_201_CREATED)
async def create_invoice(
    request: AccountingInvoiceCreateRequest,
    auto_post: bool = Query(default=True),
    current_user: Any = Depends(get_current_user),
    service: AccountingService = Depends(get_accounting_service),
) -> Dict[str, Any]:
    result = await service.create_invoice(
        invoice_data=request.model_dump(),
        auto_post=auto_post,
        posted_by=_user_email(current_user),
    )
    if not result.get("success"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result.get("error", "Failed to create invoice"))
    return result


@router.get("/trial-balance")
async def get_trial_balance(
    as_of_date: date,
    current_user: Any = Depends(get_current_user),
    service: AccountingService = Depends(get_accounting_service),
) -> Dict[str, Any]:
    generated_by = _user_email(current_user)
    return await service.generate_trial_balance(as_of_date, generated_by=generated_by)


@router.get("/income-statement")
async def get_income_statement(
    start_date: date,
    end_date: date,
    current_user: Any = Depends(get_current_user),
    service: AccountingService = Depends(get_accounting_service),
) -> Dict[str, Any]:
    generated_by = _user_email(current_user)
    return await service.generate_income_statement(start_date, end_date, generated_by=generated_by)


@router.get("/balance-sheet")
async def get_balance_sheet(
    as_of_date: date,
    current_user: Any = Depends(get_current_user),
    service: AccountingService = Depends(get_accounting_service),
) -> Dict[str, Any]:
    generated_by = _user_email(current_user)
    return await service.generate_balance_sheet(as_of_date, generated_by=generated_by)
