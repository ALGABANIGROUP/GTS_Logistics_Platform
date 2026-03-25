"""
Stripe Webhook Handler - Process payment events
"""

from fastapi import APIRouter, Request, HTTPException, Depends
import logging
import hmac
import hashlib
import os
from typing import Dict, Any
from datetime import datetime
from sqlalchemy import update

from backend.database.session import get_async_session
from backend.models.invoices import Invoice
from backend.models.payment import Payment, PaymentStatus
from backend.config import Settings
from backend.services.stripe_service import get_stripe_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/webhooks/stripe", tags=["Stripe Webhooks"])

settings = Settings()
stripe_service = get_stripe_service()
webhook_secret = settings.STRIPE_WEBHOOK_SECRET


def verify_signature(payload: bytes, signature: str) -> bool:
    """Verify webhook signature from Stripe"""
    if not webhook_secret:
        logger.warning("STRIPE_WEBHOOK_SECRET not configured - skipping signature verification")
        return True  # Skip verification if no secret configured

    try:
        # Stripe sends signature in format: t=1492774577,v1=5257a869e7ecebeda32affa62cdca3fa51cad7e77a0e56ff536d0ce8e108d8bd,v0=...
        # We need the v1 signature
        signature_parts = dict(part.split('=', 1) for part in signature.split(','))
        expected_signature = signature_parts.get('v1')

        if not expected_signature:
            logger.error("No v1 signature found in Stripe webhook")
            return False

        # Create expected signature
        signed_payload = payload
        expected = hmac.new(
            webhook_secret.encode(),
            signed_payload,
            hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(expected, expected_signature)

    except Exception as e:
        logger.error(f"Error verifying Stripe webhook signature: {e}")
        return False


@router.post("/")
async def stripe_webhook(
    request: Request,
    session=Depends(get_async_session)
):
    """Handle Stripe webhook events"""
    payload = await request.body()
    signature = request.headers.get("stripe-signature", "")

    if not verify_signature(payload, signature):
        logger.warning("Invalid Stripe webhook signature")
        raise HTTPException(status_code=401, detail="Invalid signature")

    try:
        data = await request.json()
        event_type = data.get("type")
        event_data = data.get("data", {}).get("object", {})

        logger.info(f"Received Stripe webhook: {event_type}")

        # Handle different event types
        if event_type == "payment_intent.succeeded":
            await handle_payment_intent_succeeded(event_data, session)

        elif event_type == "payment_intent.payment_failed":
            await handle_payment_intent_failed(event_data, session)

        elif event_type == "charge.refunded":
            await handle_charge_refunded(event_data, session)

        else:
            logger.info(f"Unhandled Stripe event type: {event_type}")

        return {"status": "success"}

    except Exception as e:
        logger.error(f"Error processing Stripe webhook: {e}")
        raise HTTPException(status_code=500, detail="Webhook processing failed")


async def handle_payment_intent_succeeded(payment_intent: Dict[str, Any], session):
    """Handle successful payment intent"""
    payment_intent_id = payment_intent.get("id")
    amount = payment_intent.get("amount_received", 0) / 100  # Convert from cents
    currency = payment_intent.get("currency", "usd").upper()
    metadata = payment_intent.get("metadata", {})

    logger.info(f"Payment succeeded: {payment_intent_id}, amount: {amount} {currency}")

    # Update payment status to completed
    await session.execute(
        update(Payment)
        .where(Payment.gateway_transaction_id == payment_intent_id)
        .values(
            status=PaymentStatus.COMPLETED,
            payment_date=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
    )

    # Also update invoice status if invoice_id is in metadata
    invoice_id = metadata.get("invoice_id")
    if invoice_id:
        await session.execute(
            update(Invoice)
            .where(Invoice.id == invoice_id)
            .values(
                status="paid",
                updated_at=datetime.utcnow()
            )
        )
        logger.info(f"Updated invoice {invoice_id} to paid status")

    await session.commit()


async def handle_payment_intent_failed(payment_intent: Dict[str, Any], session):
    """Handle failed payment intent"""
    payment_intent_id = payment_intent.get("id")
    last_payment_error = payment_intent.get("last_payment_error", {})
    error_message = last_payment_error.get("message", "Payment failed")

    logger.warning(f"Payment failed: {payment_intent_id}, error: {error_message}")

    # Could update payment status or send notifications here


async def handle_charge_refunded(charge: Dict[str, Any], session):
    """Handle charge refund"""
    charge_id = charge.get("id")
    refund_amount = charge.get("amount_refunded", 0) / 100
    payment_intent_id = charge.get("payment_intent")

    logger.info(f"Charge refunded: {charge_id}, amount: {refund_amount}, payment_intent: {payment_intent_id}")

    # Update payment status for refunds
    # This would require tracking refunds in the database</content>
<parameter name="filePath">c:\Users\enjoy\dev\GTS\backend\routes\stripe_webhooks.py