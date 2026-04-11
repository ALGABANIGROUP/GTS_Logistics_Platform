# -*- coding: utf-8 -*-
"""
Payment Gateway Routes
Provides all endpoints related to payments and financial transactions.

Endpoints:
- POST /api/v1/payments/create - Create a new payment
- POST /api/v1/payments/{id}/confirm - Confirm payment
- POST /api/v1/payments/{id}/refund - Refund payment
- GET /api/v1/payments/{id} - Get payment details
- GET /api/v1/payments/invoice/{invoice_id} - Invoice payments
- GET /api/v1/payments/user/history - User payment history

Author: GTS Development Team
Date: March 2026
Version: 1.0
"""

import logging
from typing import Optional, Any, Dict, List
from datetime import date, datetime
from types import SimpleNamespace

from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field
from pydantic import ConfigDict

from backend.database.session import get_async_session
from backend.security.auth import get_current_user
from backend.models.user import User
from backend.models.payment import PaymentStatus, PaymentGateway
from backend.services.plan_invoice_service import PlanInvoiceService
from backend.services.payment_service import PaymentService

try:
    from backend.core.config import get_settings
except Exception:
    get_settings = None

logger = logging.getLogger(__name__)

_fallback_app_env = os.getenv("APP_ENV") or os.getenv("ENVIRONMENT") or "development"
_fallback_frontend_url = (
    "https://www.gtsdispatcher.com"
    if _fallback_app_env == "production"
    else "http://localhost:5173"
)

if get_settings is not None:
    try:
        settings = get_settings()
    except Exception:
        settings = SimpleNamespace(
            ENVIRONMENT=_fallback_app_env,
            FRONTEND_URL=_fallback_frontend_url,
        )
else:
    settings = SimpleNamespace(
        ENVIRONMENT=_fallback_app_env,
        FRONTEND_URL=_fallback_frontend_url,
    )

# ============================================================================
# ROUTER SETUP
# ============================================================================

router = APIRouter(
    prefix="/api/v1/payments",
    tags=["payments"],
    responses={404: {"description": "Not found"}},
)

# ============================================================================
# REQUEST / RESPONSE MODELS
# ============================================================================


class PaymentCreateRequest(BaseModel):
    """Create Payment Request"""

    invoice_id: int = Field(..., description="Invoice ID")
    amount: float = Field(..., gt=0, description="Amount")
    currency: str = Field(default="USD", description="Currency (USD/CAD/EUR)")
    gateway: str = Field(
        default="stripe",
        description="Payment gateway (stripe, paypal)"
    )
    description: Optional[str] = Field(None, description="Payment description")


class PaymentConfirmRequest(BaseModel):
    """Confirm Payment Request"""

    gateway_transaction_id: Optional[str] = Field(
        None, description="Gateway transaction ID"
    )
    metadata: Optional[dict] = Field(None, description="Additional metadata")


class PaymentRefundRequest(BaseModel):
    """Refund Request"""

    amount: Optional[float] = Field(None, description="Refund amount")
    reason: str = Field(
        default="Customer request",
        description="Refund reason"
    )


class PaymentResponse(BaseModel):
    """Payment Response"""

    id: int
    reference_id: str
    invoice_id: int
    amount: float
    currency: str
    status: str
    payment_gateway: str
    gateway_transaction_id: Optional[str]
    created_at: str
    payment_date: Optional[str]

    model_config = ConfigDict(from_attributes=True)


class PlanInvoiceCreateRequest(BaseModel):
    plan_code: str = Field(..., min_length=1, max_length=50, description="Plan code")
    amount: float = Field(..., gt=0, description="Invoice amount")
    status: Optional[str] = Field(default="pending", description="Invoice status")
    invoice_date: Optional[datetime] = Field(default=None, description="Invoice date")


class PlanInvoiceResponse(BaseModel):
    id: int
    number: str
    plan_code: str
    user_id: Optional[int]
    amount_usd: float
    status: str
    date: str
    created_at: datetime


class PlanInvoiceListResponse(BaseModel):
    items: List[PlanInvoiceResponse]
    total: int
    limit: int
    offset: int


class PlanInvoiceSummaryResponse(BaseModel):
    summary: Dict[str, Dict[str, float]]


class PaymentHistoryResponse(BaseModel):
    items: List[PaymentResponse]
    total: int
    limit: int
    offset: int


def _serialize_payment(payment: Any) -> PaymentResponse:
    return PaymentResponse(
        id=int(payment.id),
        reference_id=str(payment.reference_id),
        invoice_id=int(payment.invoice_id),
        amount=float(payment.amount),
        currency=getattr(payment.currency, "value", payment.currency),
        status=getattr(payment.status, "value", payment.status),
        payment_gateway=getattr(payment.payment_gateway, "value", payment.payment_gateway),
        gateway_transaction_id=getattr(payment, "gateway_transaction_id", None),
        created_at=getattr(payment.created_at, "isoformat", lambda: str(payment.created_at))(),
        payment_date=(
            getattr(payment.payment_date, "isoformat", lambda: str(payment.payment_date))()
            if getattr(payment, "payment_date", None)
            else None
        ),
    )


def _serialize_plan_invoice(invoice: Any) -> PlanInvoiceResponse:
    parsed = _parse_plan_invoice_number(getattr(invoice, "number", ""))
    plan_code = (
        getattr(invoice, "plan_code", None)
        or parsed["plan_code"]
    )
    user_id = getattr(invoice, "user_id", None)
    if user_id is None:
        user_id = parsed["user_id"]

    return PlanInvoiceResponse(
        id=int(invoice.id),
        number=str(invoice.number),
        plan_code=str(plan_code).upper(),
        user_id=user_id,
        amount_usd=float(invoice.amount_usd),
        status=str(invoice.status),
        date=str(invoice.date),
        created_at=invoice.created_at,
    )


# ============================================================================
# DEPENDENCIES
# ============================================================================


async def get_payment_service(
    db: AsyncSession = Depends(get_async_session),
) -> PaymentService:
    """Return payment service instance"""
    return PaymentService(db, None)


async def get_plan_invoice_service(
    db: AsyncSession = Depends(get_async_session),
) -> PlanInvoiceService:
    """Return plan invoice service instance."""
    return PlanInvoiceService(db)


def _get_user_attr(current_user: Any, key: str, default: Any = None) -> Any:
    if isinstance(current_user, dict):
        return current_user.get(key, default)
    return getattr(current_user, key, default)


def _has_admin_access(current_user: Any) -> bool:
    role = str(
        _get_user_attr(current_user, "effective_role")
        or _get_user_attr(current_user, "role")
        or ""
    ).strip().lower()
    return role in {"admin", "super_admin", "owner"}


def _ensure_payment_access(payment: Any, current_user: Any) -> None:
    if _has_admin_access(current_user):
        return

    current_user_id = _get_user_attr(current_user, "id")
    payment_user_id = getattr(payment, "user_id", None)
    if current_user_id is None or payment_user_id is None or int(current_user_id) != int(payment_user_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")


def _parse_plan_invoice_number(number: str) -> Dict[str, Optional[int]]:
    parts = (number or "").split("-")
    result: Dict[str, Optional[int]] = {"plan_code": "UNKNOWN", "user_id": None}

    if len(parts) >= 5 and parts[0] == "PLANINV":
        result["plan_code"] = parts[1]

        if parts[2].startswith("U") and parts[2][1:].isdigit():
            result["user_id"] = int(parts[2][1:])

    return result


def _build_public_payment_link(payment_id: int | str) -> str:
    frontend_base = str(getattr(settings, "FRONTEND_URL", "") or _fallback_frontend_url).rstrip("/")
    return f"{frontend_base}/pay/{payment_id}"


async def _resolve_payment_or_404(
    payment_service: PaymentService,
    payment_id: int | str,
) -> Any:
    payment = await payment_service.resolve_payment(payment_id)
    if not payment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found")
    return payment


# ============================================================================
# ROUTE: CREATE PAYMENT
# ============================================================================


@router.post("/create", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_payment(
    request: PaymentCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
    payment_service: PaymentService = Depends(get_payment_service),
) -> dict:
    """
    Create a new payment transaction

    Supported gateway:
    - Stripe
    - PayPal
    """

    try:
        if request.gateway.strip().lower() == "sudapay":
            raise HTTPException(
                status_code=status.HTTP_410_GONE,
                detail="Sudapay has been removed from GTS payments",
            )

        logger.info(
            f"Creating payment: invoice_id={request.invoice_id}, "
            f"amount={request.amount}{request.currency}, "
            f"gateway={request.gateway}"
        )

        checkout = await payment_service.create_checkout_payment(
            invoice_id=request.invoice_id,
            user_id=int(_get_user_attr(current_user, "id")),
            amount=request.amount,
            currency=request.currency,
            gateway=request.gateway.lower(),
            description=request.description,
            customer_email=_get_user_attr(current_user, "email"),
            return_url=f"{settings.FRONTEND_URL}/payment/success",
            cancel_url=f"{settings.FRONTEND_URL}/payment/cancel",
            metadata={"invoice_id": request.invoice_id},
        )
        payment = checkout["payment"]
        return {
            "payment_id": payment.id,
            "reference_id": payment.reference_id,
            "checkout_url": checkout["checkout_url"],
            "public_payment_link": checkout.get("public_payment_link") or _build_public_payment_link(payment.id),
            "amount": request.amount,
            "currency": request.currency,
            "status": checkout["status"],
            "gateway": checkout["gateway"],
        }

    except HTTPException:
        raise

    except ValueError as e:
        await db.rollback()
        detail = str(e)
        code = status.HTTP_400_BAD_REQUEST
        if "Unsupported payment gateway" in detail:
            code = status.HTTP_501_NOT_IMPLEMENTED
        raise HTTPException(status_code=code, detail=detail)

    except Exception as e:

        logger.error(f"Error creating payment: {str(e)}")

        await db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create payment",
        )


@router.post("/{payment_id}/confirm", response_model=PaymentResponse)
async def confirm_payment(
    payment_id: str,
    request: PaymentConfirmRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    payment_service: PaymentService = Depends(get_payment_service),
) -> PaymentResponse:
    try:
        payment = await payment_service.resolve_payment(payment_id)
        if not payment:
            raise ValueError(f"Payment {payment_id} not found")
        _ensure_payment_access(payment, current_user)

        updated = await payment_service.confirm_payment(
            payment_id=int(payment.id),
            gateway_transaction_id=request.gateway_transaction_id,
            metadata=request.metadata,
            payment_date=datetime.utcnow(),
        )
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found")
    return _serialize_payment(updated)


@router.post("/{payment_id}/refund", response_model=dict)
async def refund_payment(
    payment_id: str,
    request: PaymentRefundRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    payment_service: PaymentService = Depends(get_payment_service),
) -> dict:
    try:
        payment = await payment_service.resolve_payment(payment_id)
        if not payment:
            raise ValueError(f"Payment {payment_id} not found")
        _ensure_payment_access(payment, current_user)

        completed_refund = await payment_service.refund_payment(
            payment_id=int(payment.id),
            amount=request.amount,
            reason=request.reason,
        )
    except ValueError as e:
        detail = str(e)
        code = status.HTTP_404_NOT_FOUND if "not found" in detail.lower() else status.HTTP_400_BAD_REQUEST
        raise HTTPException(status_code=code, detail=detail)
    return {
        "refund_id": completed_refund.id,
        "reference_id": completed_refund.reference_id,
        "payment_id": completed_refund.payment_id,
        "amount": float(completed_refund.amount),
        "status": getattr(completed_refund.status, "value", completed_refund.status),
    }


@router.get("/invoice/{invoice_id}", response_model=List[PaymentResponse])
async def get_invoice_payments(
    invoice_id: int,
    current_user: Dict[str, Any] = Depends(get_current_user),
    payment_service: PaymentService = Depends(get_payment_service),
) -> List[PaymentResponse]:
    payments = await payment_service.get_invoice_payments(invoice_id)
    if not _has_admin_access(current_user):
        current_user_id = _get_user_attr(current_user, "id")
        if any(getattr(payment, "user_id", None) != current_user_id for payment in payments):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    return [_serialize_payment(payment) for payment in payments]


@router.get("/user/history", response_model=PaymentHistoryResponse)
async def get_user_payment_history(
    current_user: Dict[str, Any] = Depends(get_current_user),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    payment_service: PaymentService = Depends(get_payment_service),
) -> PaymentHistoryResponse:
    items, total = await payment_service.get_user_payment_history(
        user_id=int(_get_user_attr(current_user, "id")),
        limit=limit,
        offset=offset,
    )
    return PaymentHistoryResponse(
        items=[_serialize_payment(item) for item in items],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.post("/plan-invoices", response_model=PlanInvoiceResponse, status_code=status.HTTP_201_CREATED)
async def create_plan_invoice(
    request: PlanInvoiceCreateRequest,
    current_user: User = Depends(get_current_user),
    plan_invoice_service: PlanInvoiceService = Depends(get_plan_invoice_service),
) -> PlanInvoiceResponse:
    requested_status = str(request.status or "pending").strip().lower()
    if requested_status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Plan invoice status must start as pending",
        )
    invoice = await plan_invoice_service.create_plan_invoice(
        user_id=int(_get_user_attr(current_user, "id")),
        plan_code=request.plan_code.upper(),
        amount_usd=request.amount,
        status="pending",
        invoice_date=request.invoice_date,
    )
    return _serialize_plan_invoice(invoice)


@router.get("/plan-invoices", response_model=PlanInvoiceListResponse)
async def list_plan_invoices(
    plan_code: Optional[str] = Query(default=None),
    status: Optional[str] = Query(default=None),
    from_date: Optional[date] = Query(default=None),
    to_date: Optional[date] = Query(default=None),
    limit: int = Query(default=50, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    current_user: Dict[str, Any] = Depends(get_current_user),
    plan_invoice_service: PlanInvoiceService = Depends(get_plan_invoice_service),
) -> PlanInvoiceListResponse:
    items, total = await plan_invoice_service.list_plan_invoices(
        plan_code=plan_code,
        status=status,
        user_id=None if _has_admin_access(current_user) else _get_user_attr(current_user, "id"),
        from_date=from_date,
        to_date=to_date,
        limit=limit,
        offset=offset,
    )
    return PlanInvoiceListResponse(
        items=[_serialize_plan_invoice(item) for item in items],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/plan-invoices/summary", response_model=PlanInvoiceSummaryResponse)
async def get_plan_invoice_summary(
    from_date: Optional[date] = Query(default=None),
    to_date: Optional[date] = Query(default=None),
    current_user: Dict[str, Any] = Depends(get_current_user),
    plan_invoice_service: PlanInvoiceService = Depends(get_plan_invoice_service),
) -> PlanInvoiceSummaryResponse:
    summary = await plan_invoice_service.get_plan_invoice_summary(
        user_id=None if _has_admin_access(current_user) else _get_user_attr(current_user, "id"),
        from_date=from_date,
        to_date=to_date,
    )
    return PlanInvoiceSummaryResponse(summary=summary)


@router.get("/{payment_id}", response_model=PaymentResponse)
async def get_payment(
    payment_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    payment_service: PaymentService = Depends(get_payment_service),
) -> PaymentResponse:
    payment = await _resolve_payment_or_404(payment_service, payment_id)
    _ensure_payment_access(payment, current_user)
    return _serialize_payment(payment)
