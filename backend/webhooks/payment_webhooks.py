# -*- coding: utf-8 -*-
"""Payment webhook handlers for SUDAPAY and future gateways."""

from __future__ import annotations

import json
import logging
from decimal import Decimal, InvalidOperation
from datetime import datetime
from hashlib import sha256
from types import SimpleNamespace
from typing import Dict

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.session import get_async_session
from backend.models.payment import PaymentStatus
from backend.services.payment_service import PaymentService
from backend.services.sudapay_service import SudapayService
from backend.services.webhook_service import WebhookService

logger = logging.getLogger(__name__)

try:
    from backend.core.config import get_settings
except Exception:
    get_settings = None

if get_settings is not None:
    try:
        settings = get_settings()
    except Exception:
        settings = SimpleNamespace(
            SUDAPAY_API_KEY="",
            SUDAPAY_MERCHANT_ID="",
            SUDAPAY_WEBHOOK_SECRET="",
            ENVIRONMENT="development",
        )
else:
    settings = SimpleNamespace(
        SUDAPAY_API_KEY="",
        SUDAPAY_MERCHANT_ID="",
        SUDAPAY_WEBHOOK_SECRET="",
        ENVIRONMENT="development",
    )

router = APIRouter(
    prefix="/api/v1/webhooks",
    tags=["webhooks"],
    responses={404: {"description": "Not found"}},
)


async def get_sudapay_service() -> SudapayService:
    """Return SUDAPAY service instance."""
    return SudapayService(
        api_key=settings.SUDAPAY_API_KEY,
        merchant_id=settings.SUDAPAY_MERCHANT_ID,
        webhook_secret=settings.SUDAPAY_WEBHOOK_SECRET,
        sandbox=settings.ENVIRONMENT != "production",
    )


def _build_payment_service(db: AsyncSession, sudapay: SudapayService) -> PaymentService:
    return PaymentService(db, sudapay)


def _status_value(value: object) -> str:
    return str(getattr(value, "value", value) or "").strip().lower()


def _build_idempotency_key(payload: Dict, event_type: str, event_data: Dict, payload_str: str) -> str:
    explicit_id = (
        payload.get("id")
        or payload.get("event_id")
        or event_data.get("event_id")
        or event_data.get("id")
    )
    if explicit_id:
        return f"sudapay:{explicit_id}"
    return f"sudapay:{event_type}:{sha256(payload_str.encode('utf-8')).hexdigest()}"


def _amount_candidates(raw_amount: object) -> set[Decimal]:
    if raw_amount is None:
        return set()
    try:
        parsed = Decimal(str(raw_amount))
    except (InvalidOperation, TypeError, ValueError):
        return set()

    candidates = {parsed.quantize(Decimal("0.01"))}
    if parsed == parsed.to_integral():
        candidates.add((parsed / Decimal("100")).quantize(Decimal("0.01")))
    return candidates


def _matches_amount(expected_amount: object, raw_amount: object) -> bool:
    if raw_amount is None:
        return True
    try:
        expected = Decimal(str(expected_amount)).quantize(Decimal("0.01"))
    except (InvalidOperation, TypeError, ValueError):
        return False
    return expected in _amount_candidates(raw_amount)


def _validate_payment_event(payment: object, event_data: Dict) -> None:
    gateway_payment_id = event_data.get("payment_id")
    local_gateway_payment_id = getattr(payment, "gateway_transaction_id", None)
    if gateway_payment_id and local_gateway_payment_id and gateway_payment_id != local_gateway_payment_id:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Webhook payment_id mismatch")

    event_currency = str(event_data.get("currency") or "").strip().upper()
    local_currency = str(getattr(getattr(payment, "currency", None), "value", getattr(payment, "currency", "")) or "").strip().upper()
    if event_currency and local_currency and event_currency != local_currency:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Webhook currency mismatch")

    if not _matches_amount(getattr(payment, "amount", None), event_data.get("amount")):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Webhook amount mismatch")


def _validate_refund_event(payment: object, refund: object, event_data: Dict) -> None:
    _validate_payment_event(payment, {"payment_id": event_data.get("payment_id"), "currency": event_data.get("currency")})
    if not _matches_amount(getattr(refund, "amount", None), event_data.get("amount")):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Webhook refund amount mismatch")


async def _register_webhook(
    db: AsyncSession,
    *,
    payload: Dict,
    event_type: str,
    event_data: Dict,
    payload_str: str,
    signature: str,
    headers: Dict,
) -> tuple[WebhookService, str | None, bool]:
    webhook_service = WebhookService(db)
    idempotency_key = _build_idempotency_key(payload, event_type, event_data, payload_str)
    try:
        webhook_id = await webhook_service.log_webhook(
            client_id="sudapay",
            endpoint="/api/v1/webhooks/sudapay/payment",
            payload=payload,
            headers=headers,
            idempotency_key=idempotency_key,
            signature=signature,
        )
        await db.commit()
        return webhook_service, webhook_id, False
    except IntegrityError:
        await db.rollback()
        logger.info("Duplicate SUDAPAY webhook ignored: key=%s", idempotency_key)
        return webhook_service, None, True


@router.post("/sudapay/payment", status_code=status.HTTP_200_OK)
async def sudapay_payment_webhook(
    request: Request,
    db: AsyncSession = Depends(get_async_session),
    sudapay: SudapayService = Depends(get_sudapay_service),
) -> Dict:
    """Process SUDAPAY webhook events."""
    signature = request.headers.get("X-Sudapay-Signature")
    if not signature:
        logger.warning("Missing SUDAPAY webhook signature")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing webhook signature",
        )

    try:
        body = await request.body()
        payload_str = body.decode()
        if not sudapay.verify_webhook_signature(payload_str, signature):
            logger.warning("Invalid SUDAPAY webhook signature")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid webhook signature",
            )

        payload = json.loads(payload_str)
        event_type = payload.get("type", "")
        event_data = payload.get("data", {})
        payment_service = _build_payment_service(db, sudapay)
        webhook_service, webhook_id, is_duplicate = await _register_webhook(
            db,
            payload=payload,
            event_type=event_type,
            event_data=event_data,
            payload_str=payload_str,
            signature=signature,
            headers=dict(request.headers),
        )

        if is_duplicate:
            return {"status": "success", "message": "Duplicate webhook ignored"}

        logger.info("SUDAPAY webhook received: type=%s", event_type)

        if event_type == "payment.success":
            payment_reference = event_data.get("reference_id")
            sudapay_payment_id = event_data.get("payment_id")
            payment = await payment_service.get_payment_by_reference(payment_reference)
            if not payment:
                logger.warning("Payment reference not found for success webhook: %s", payment_reference)
                await webhook_service.mark_webhook_processed(webhook_id, status_code=200)
                return {"status": "success", "message": "Payment reference not found"}
            _validate_payment_event(payment, event_data)
            if _status_value(getattr(payment, "status", None)) == PaymentStatus.COMPLETED.value:
                await webhook_service.mark_webhook_processed(webhook_id, status_code=200)
                return {"status": "success", "message": "Duplicate payment success ignored", "payment_id": payment.id}

            await payment_service.record_transaction(
                payment_id=payment.id,
                transaction_type="payment",
                status="completed",
                gateway_response=event_data,
            )
            await payment_service.update_payment_status(
                payment_id=payment.id,
                status="completed",
                gateway_transaction_id=sudapay_payment_id,
            )
            await webhook_service.mark_webhook_processed(webhook_id, status_code=200)
            return {"status": "success", "message": "Payment confirmed", "payment_id": payment.id}

        if event_type == "payment.failed":
            payment_reference = event_data.get("reference_id")
            error_message = event_data.get("error", "Unknown error")
            payment = await payment_service.get_payment_by_reference(payment_reference)
            if not payment:
                logger.warning("Payment reference not found for failed webhook: %s", payment_reference)
                await webhook_service.mark_webhook_processed(webhook_id, status_code=200)
                return {"status": "success"}
            _validate_payment_event(payment, event_data)
            if _status_value(getattr(payment, "status", None)) == PaymentStatus.FAILED.value:
                await webhook_service.mark_webhook_processed(webhook_id, status_code=200)
                return {"status": "success", "message": "Duplicate payment failure ignored", "payment_id": payment.id}

            await payment_service.record_transaction(
                payment_id=payment.id,
                transaction_type="payment",
                status="failed",
                error_message=error_message,
                gateway_response=event_data,
            )
            await payment_service.update_payment_status(
                payment_id=payment.id,
                status="failed",
                metadata={"error": error_message},
            )
            return {
                "status": "success",
                "message": "Payment failure recorded",
                "payment_id": payment.id,
            }

        if event_type == "payment.cancelled":
            payment_reference = event_data.get("reference_id")
            payment = await payment_service.get_payment_by_reference(payment_reference)
            if not payment:
                await webhook_service.mark_webhook_processed(webhook_id, status_code=200)
                return {"status": "success"}
            _validate_payment_event(payment, event_data)
            if _status_value(getattr(payment, "status", None)) == PaymentStatus.CANCELLED.value:
                await webhook_service.mark_webhook_processed(webhook_id, status_code=200)
                return {"status": "success", "message": "Duplicate payment cancellation ignored"}

            await payment_service.update_payment_status(
                payment_id=payment.id,
                status="cancelled",
            )
            await webhook_service.mark_webhook_processed(webhook_id, status_code=200)
            return {"status": "success", "message": "Payment cancellation recorded"}

        if event_type == "refund.completed":
            payment_reference = event_data.get("payment_reference")
            gateway_refund_id = event_data.get("refund_id") or event_data.get("id")

            payment = await payment_service.get_payment_by_reference(payment_reference)
            if not payment:
                logger.warning("Payment reference not found for refund webhook: %s", payment_reference)
                await webhook_service.mark_webhook_processed(webhook_id, status_code=200)
                return {"status": "success"}

            refund = None
            if gateway_refund_id:
                refund = await payment_service.get_refund_by_gateway_refund_id(gateway_refund_id)
            if not refund:
                refund = await payment_service.get_latest_pending_refund_for_payment(payment.id)

            if refund:
                _validate_refund_event(payment, refund, event_data)
                if _status_value(getattr(refund, "status", None)) == PaymentStatus.COMPLETED.value:
                    await webhook_service.mark_webhook_processed(webhook_id, status_code=200)
                    return {"status": "success", "message": "Duplicate refund completion ignored"}
                if gateway_refund_id and not refund.gateway_refund_id:
                    refund.gateway_refund_id = gateway_refund_id
                await payment_service.complete_refund(refund.id)
                await webhook_service.mark_webhook_processed(webhook_id, status_code=200)
            elif _status_value(getattr(payment, "status", None)) == PaymentStatus.REFUNDED.value:
                await webhook_service.mark_webhook_processed(webhook_id, status_code=200)
                return {"status": "success", "message": "Duplicate refund completion ignored"}
            else:
                logger.error(
                    "Refund completed webhook ignored because no local refund row matched: payment_id=%s gateway_refund_id=%s",
                    payment.id,
                    gateway_refund_id,
                )
                await webhook_service.mark_webhook_failed(
                    webhook_id,
                    error="Refund completed webhook has no matching local refund row",
                    status_code=409,
                )
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Refund webhook has no matching local refund row",
                )

            return {"status": "success", "message": "Refund completed"}

        logger.warning("Unknown SUDAPAY event type: %s", event_type)
        await webhook_service.mark_webhook_processed(webhook_id, status_code=200)
        return {
            "status": "success",
            "message": f"Event {event_type} received but not processed",
        }

    except json.JSONDecodeError:
        logger.error("Invalid JSON in webhook payload")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid JSON",
        )
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Webhook processing error: %s", exc)
        # Return 200 to reduce unnecessary webhook retries while still surfacing the issue.
        return {"status": "error", "message": str(exc)}


@router.post("/stripe/payment", status_code=status.HTTP_200_OK)
async def stripe_payment_webhook(
    request: Request,
    db: AsyncSession = Depends(get_async_session),
) -> Dict:
    """Placeholder for future Stripe webhook support."""
    logger.warning("Stripe webhook not yet implemented")
    return {"status": "success", "message": "Stripe integration coming soon"}


@router.get("/health")
async def webhook_health() -> Dict:
    """Health check for payment webhooks."""
    return {
        "status": "healthy",
        "service": "payment-webhooks",
        "timestamp": datetime.utcnow().isoformat(),
        "endpoints": [
            "POST /api/v1/webhooks/sudapay/payment",
            "POST /api/v1/webhooks/stripe/payment",
        ],
    }
