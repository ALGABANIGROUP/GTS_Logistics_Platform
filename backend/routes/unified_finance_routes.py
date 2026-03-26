from __future__ import annotations

from datetime import date
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.session import get_async_session
from backend.security.auth import get_current_user
from backend.services.unified_finance_service import UnifiedFinanceService

router = APIRouter(prefix="/api/v1/finance", tags=["Unified Finance"])


class UnifiedInvoiceCreateRequest(BaseModel):
    invoice_date: date
    amount_usd: float = Field(..., gt=0)
    customer_name: str = Field(..., min_length=1)
    number: str | None = None
    status: str = "pending"
    shipment_id: int | None = None


class UnifiedExpenseCreateRequest(BaseModel):
    category: str = Field(..., min_length=1)
    amount: float = Field(..., gt=0)
    description: str | None = None
    vendor: str | None = None
    created_at: date | None = None
    status: str = "PENDING"


class UnifiedPaymentCreateRequest(BaseModel):
    payment_type: str = "invoice"
    reference_id: int | None = Field(default=None, gt=0)
    invoice_id: int | None = Field(default=None, gt=0)
    expense_id: int | None = Field(default=None, gt=0)
    amount: float = Field(..., gt=0)
    currency: str = "SDG"
    gateway: str = "sudapay"
    description: str | None = None
    supplier_name: str | None = None
    payment_date: date | None = None


def _user_email(current_user: Any) -> str:
    if isinstance(current_user, dict):
        return str(current_user.get("email") or "system")
    return str(getattr(current_user, "email", None) or "system")


async def get_unified_finance_service(
    db: AsyncSession = Depends(get_async_session),
) -> UnifiedFinanceService:
    return UnifiedFinanceService(db)


@router.get("/dashboard")
async def get_dashboard(
    service: UnifiedFinanceService = Depends(get_unified_finance_service),
) -> Dict[str, Any]:
    return await service.get_dashboard()


@router.get("/invoices")
async def get_invoices(
    limit: int = Query(default=100, ge=1, le=500),
    service: UnifiedFinanceService = Depends(get_unified_finance_service),
) -> Dict[str, Any]:
    items = await service.list_invoices(limit=limit)
    return {"items": items, "total": len(items)}


@router.get("/expenses")
async def get_expenses(
    limit: int = Query(default=100, ge=1, le=500),
    service: UnifiedFinanceService = Depends(get_unified_finance_service),
) -> Dict[str, Any]:
    items = await service.list_expenses(limit=limit)
    return {"items": items, "total": len(items)}


@router.get("/payments")
async def get_payments(
    limit: int = Query(default=100, ge=1, le=500),
    service: UnifiedFinanceService = Depends(get_unified_finance_service),
) -> Dict[str, Any]:
    items = await service.list_payments(limit=limit)
    return {"items": items, "total": len(items)}


@router.post("/invoices", status_code=status.HTTP_201_CREATED)
async def create_invoice(
    request: UnifiedInvoiceCreateRequest,
    current_user: Any = Depends(get_current_user),
    service: UnifiedFinanceService = Depends(get_unified_finance_service),
) -> Dict[str, Any]:
    user_id = current_user.get("id") if isinstance(current_user, dict) else getattr(current_user, "id", None)
    result = await service.create_invoice(
        invoice_date=request.invoice_date,
        amount_usd=request.amount_usd,
        customer_name=request.customer_name,
        status=request.status,
        number=request.number,
        shipment_id=request.shipment_id,
        user_id=user_id,
        posted_by=_user_email(current_user),
    )
    if not result.get("success"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result.get("error", "Failed to create invoice"))
    return result


@router.post("/expenses", status_code=status.HTTP_201_CREATED)
async def create_expense(
    request: UnifiedExpenseCreateRequest,
    current_user: Any = Depends(get_current_user),
    service: UnifiedFinanceService = Depends(get_unified_finance_service),
) -> Dict[str, Any]:
    created_at = None
    if request.created_at:
        from datetime import datetime, time
        created_at = datetime.combine(request.created_at, time.min)
    result = await service.create_expense(
        category=request.category,
        amount=request.amount,
        description=request.description,
        vendor=request.vendor,
        created_at=created_at,
        status=request.status,
        posted_by=_user_email(current_user),
    )
    if not result.get("success"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result.get("error", "Failed to create expense"))
    return result


@router.post("/payments", status_code=status.HTTP_201_CREATED)
async def create_payment(
    request: UnifiedPaymentCreateRequest,
    current_user: Any = Depends(get_current_user),
    service: UnifiedFinanceService = Depends(get_unified_finance_service),
) -> Dict[str, Any]:
    user_id = current_user.get("id") if isinstance(current_user, dict) else getattr(current_user, "id", None)
    if user_id is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing current user id")
    payment_dt = None
    if request.payment_date:
        from datetime import datetime, time
        payment_dt = datetime.combine(request.payment_date, time.min)
    result = await service.create_payment(
        user_id=int(user_id),
        amount=request.amount,
        payment_type=request.payment_type,
        reference_id=request.reference_id,
        invoice_id=request.invoice_id,
        expense_id=request.expense_id,
        currency=request.currency,
        gateway=request.gateway,
        description=request.description,
        payment_date=payment_dt,
        supplier_name=request.supplier_name,
        posted_by=_user_email(current_user),
    )
    if not result.get("success"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result.get("error", "Failed to create payment"))
    return result


@router.get("/reports/summary")
async def get_summary_report(
    service: UnifiedFinanceService = Depends(get_unified_finance_service),
) -> Dict[str, Any]:
    return await service.get_summary_report()


@router.get("/ledger/trial-balance")
async def get_trial_balance(
    as_of_date: date,
    current_user: Any = Depends(get_current_user),
    service: UnifiedFinanceService = Depends(get_unified_finance_service),
) -> Dict[str, Any]:
    return await service.get_trial_balance(as_of_date, generated_by=_user_email(current_user))


@router.get("/ledger/income-statement")
async def get_income_statement(
    start_date: date,
    end_date: date,
    current_user: Any = Depends(get_current_user),
    service: UnifiedFinanceService = Depends(get_unified_finance_service),
) -> Dict[str, Any]:
    return await service.get_income_statement(start_date, end_date, generated_by=_user_email(current_user))


@router.get("/ledger/balance-sheet")
async def get_balance_sheet(
    as_of_date: date,
    current_user: Any = Depends(get_current_user),
    service: UnifiedFinanceService = Depends(get_unified_finance_service),
) -> Dict[str, Any]:
    return await service.get_balance_sheet(as_of_date, generated_by=_user_email(current_user))
