from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.config import settings
from backend.database.session import get_async_session
from backend.models.invoices import Invoice
from backend.models.user import User
from backend.models.models import Shipment
from backend.services.notification_service import notification_service
from backend.services.platform_webhook_dispatcher import dispatch_from_platform_settings
import asyncio

router = APIRouter(prefix="/api/v1/invoices", tags=["Invoices"])

_ALLOWED_STATUSES = {"draft", "pending", "sent", "paid", "overdue", "cancelled"}


class InvoiceCreate(BaseModel):
    number: str = Field(..., min_length=1)
    date: date
    amount_usd: float = Field(..., gt=0)
    status: str = "pending"
    shipment_id: Optional[int] = None


class InvoiceUpdate(BaseModel):
    number: Optional[str] = None
    date: Optional[date] = None
    amount_usd: Optional[float] = Field(default=None, gt=0)
    status: Optional[str] = None
    shipment_id: Optional[int] = None


class InvoiceOut(BaseModel):
    id: int
    number: str
    date: date
    amount_usd: float
    status: str
    shipment_id: Optional[int]
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


def _validate_status(status_value: str) -> str:
    normalized = status_value.strip().lower()
    if normalized not in _ALLOWED_STATUSES:
        raise HTTPException(status_code=400, detail="Invalid invoice status")
    return normalized


async def _emit_invoice_event(db: AsyncSession, event_type: str, invoice: Invoice, extra: Optional[dict] = None) -> None:
    payload = {
        "invoice_id": invoice.id,
        "number": invoice.number,
        "status": invoice.status,
        "amount_usd": invoice.amount_usd,
        "date": invoice.date.isoformat() if invoice.date else None,
        "shipment_id": invoice.shipment_id,
    }
    if extra:
        payload.update(extra)
    await dispatch_from_platform_settings(db=db, event_type=event_type, data=payload)


async def _resolve_invoice_recipient(db: AsyncSession, invoice: Invoice) -> tuple[str | None, str]:
    user_id = getattr(invoice, "user_id", None)
    if user_id is None and getattr(invoice, "shipment_id", None):
        shipment = await db.scalar(select(Shipment).where(Shipment.id == invoice.shipment_id))
        user_id = getattr(shipment, "user_id", None)
    if user_id is not None:
        user = await db.get(User, int(user_id))
        if user and getattr(user, "email", None):
            return str(user.email), str(getattr(user, "full_name", None) or user.email)
    fallback = settings.ADMIN_EMAIL or settings.SUPPORT_EMAIL or settings.SMTP_FROM or settings.SMTP_USER
    return fallback or None, "Finance Team"


async def _build_invoice_notification_payload(db: AsyncSession, invoice: Invoice) -> tuple[str | None, str, Dict[str, Any]]:
    recipient_email, recipient_name = await _resolve_invoice_recipient(db, invoice)
    amount_value = getattr(invoice, "amount_usd", 0) or 0
    due_date = invoice.date.isoformat() if invoice.date else "N/A"
    invoice_url = f"{settings.FRONTEND_URL}/invoices/{invoice.id}"
    return recipient_email, recipient_name, {
        "invoice_number": invoice.number,
        "amount": amount_value,
        "currency": "USD",
        "due_date": due_date,
        "customer_name": recipient_name,
        "invoice_url": invoice_url,
        "payment_date": datetime.utcnow().strftime("%Y-%m-%d"),
        "payment_method": "Platform update",
        "receipt_url": invoice_url,
        "days_overdue": max((datetime.utcnow().date() - invoice.date).days, 0) if invoice.date else 0,
    }


@router.post("", response_model=InvoiceOut)
async def create_invoice(
    payload: InvoiceCreate,
    db: AsyncSession = Depends(get_async_session),
) -> InvoiceOut:
    status_value = _validate_status(payload.status)
    invoice = Invoice(
        number=payload.number,
        date=payload.date,
        amount_usd=payload.amount_usd,
        status=status_value,
        shipment_id=payload.shipment_id,
    )
    db.add(invoice)
    await db.commit()
    await db.refresh(invoice)

    try:
        await _emit_invoice_event(db, "invoice.created", invoice)
        if status_value == "paid":
            await _emit_invoice_event(db, "invoice.paid", invoice)
        elif status_value == "overdue":
            await _emit_invoice_event(db, "invoice.overdue", invoice)
    except Exception:
        pass
    try:
        recipient_email, recipient_name, invoice_context = await _build_invoice_notification_payload(db, invoice)
        asyncio.create_task(
            notification_service.send_finance_notification(
                event_type="invoice_created",
                user_email=recipient_email,
                user_name=recipient_name,
                invoice_data=invoice_context,
            )
        )
        if status_value == "paid":
            asyncio.create_task(
                notification_service.send_finance_notification(
                    event_type="invoice_paid",
                    user_email=recipient_email,
                    user_name=recipient_name,
                    invoice_data=invoice_context,
                )
            )
        elif status_value == "overdue":
            asyncio.create_task(
                notification_service.send_finance_notification(
                    event_type="invoice_overdue",
                    user_email=recipient_email,
                    user_name=recipient_name,
                    invoice_data=invoice_context,
                )
            )
    except Exception:
        pass

    return InvoiceOut.model_validate(invoice)


@router.get("", response_model=list[InvoiceOut])
async def list_invoices(db: AsyncSession = Depends(get_async_session)) -> list[InvoiceOut]:
    result = await db.execute(select(Invoice).order_by(Invoice.id.desc()))
    invoices = result.scalars().all()
    return [InvoiceOut.model_validate(inv) for inv in invoices]


@router.get("/{invoice_id}", response_model=InvoiceOut)
async def get_invoice(invoice_id: int, db: AsyncSession = Depends(get_async_session)) -> InvoiceOut:
    result = await db.execute(select(Invoice).where(Invoice.id == invoice_id))
    invoice = result.scalars().first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return InvoiceOut.model_validate(invoice)


@router.patch("/{invoice_id}", response_model=InvoiceOut)
async def update_invoice(
    invoice_id: int,
    payload: InvoiceUpdate,
    db: AsyncSession = Depends(get_async_session),
) -> InvoiceOut:
    result = await db.execute(select(Invoice).where(Invoice.id == invoice_id))
    invoice = result.scalars().first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    old_status = invoice.status
    if payload.number is not None:
        invoice.number = payload.number
    if payload.date is not None:
        invoice.date = payload.date
    if payload.amount_usd is not None:
        invoice.amount_usd = payload.amount_usd
    if payload.shipment_id is not None:
        invoice.shipment_id = payload.shipment_id
    if payload.status is not None:
        invoice.status = _validate_status(payload.status)

    invoice.updated_at = datetime.utcnow()
    db.add(invoice)
    await db.commit()
    await db.refresh(invoice)

    try:
        await _emit_invoice_event(db, "invoice.updated", invoice, {"previous_status": old_status})
        if payload.status is not None and old_status != invoice.status:
            await _emit_invoice_event(db, "invoice.status.updated", invoice, {"previous_status": old_status})
            if invoice.status == "paid":
                await _emit_invoice_event(db, "invoice.paid", invoice)
            elif invoice.status == "overdue":
                await _emit_invoice_event(db, "invoice.overdue", invoice)
    except Exception:
        pass
    try:
        if payload.status is not None and old_status != invoice.status:
            recipient_email, recipient_name, invoice_context = await _build_invoice_notification_payload(db, invoice)
            if invoice.status == "paid":
                asyncio.create_task(
                    notification_service.send_finance_notification(
                        event_type="invoice_paid",
                        user_email=recipient_email,
                        user_name=recipient_name,
                        invoice_data=invoice_context,
                    )
                )
            elif invoice.status == "overdue":
                asyncio.create_task(
                    notification_service.send_finance_notification(
                        event_type="invoice_overdue",
                        user_email=recipient_email,
                        user_name=recipient_name,
                        invoice_data=invoice_context,
                    )
                )
    except Exception:
        pass

    return InvoiceOut.model_validate(invoice)


@router.post("/{invoice_id}/mark-paid", response_model=InvoiceOut)
async def mark_invoice_paid(invoice_id: int, db: AsyncSession = Depends(get_async_session)) -> InvoiceOut:
    return await update_invoice(invoice_id, InvoiceUpdate(status="paid"), db)


@router.post("/{invoice_id}/mark-overdue", response_model=InvoiceOut)
async def mark_invoice_overdue(invoice_id: int, db: AsyncSession = Depends(get_async_session)) -> InvoiceOut:
    return await update_invoice(invoice_id, InvoiceUpdate(status="overdue"), db)
