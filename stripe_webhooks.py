"""
Stripe Webhook Handler - Process payment events
"""

from fastapi import APIRouter, Request, HTTPException, Depends
import logging
import stripe
import os
from typing import Dict, Any
from datetime import datetime
from sqlalchemy import update

from backend.services.stripe_service import get_stripe_service
from backend.database.session import get_async_session

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/webhooks/stripe", tags=["Stripe Webhooks"])

webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET", "")


@router.post("/")
async def stripe_webhook(request: Request, session=Depends(get_async_session)):
    """Handle Stripe webhook events"""
    if not webhook_secret:
        logger.warning("Stripe webhook secret not configured")
        raise HTTPException(status_code=400, detail="Webhook not configured")

    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, webhook_secret
        )
    except ValueError as e:
        logger.error(f"Invalid payload: {e}")
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"Invalid signature: {e}")
        raise HTTPException(status_code=400, detail="Invalid signature")

    event_type = event["type"]
    event_data = event["data"]["object"]

    logger.info(f"Stripe webhook: {event_type}")

    # Handle different event types
    if event_type == "payment_intent.succeeded":
        await handle_payment_success(event_data, session)
    elif event_type == "payment_intent.payment_failed":
        await handle_payment_failure(event_data, session)
    elif event_type == "charge.refunded":
        await handle_refund(event_data, session)
    elif event_type == "customer.subscription.created":
        await handle_subscription_created(event_data, session)
    elif event_type == "customer.subscription.updated":
        await handle_subscription_updated(event_data, session)
    elif event_type == "customer.subscription.deleted":
        await handle_subscription_cancelled(event_data, session)

    return {"status": "success"}


async def handle_payment_success(payment_intent: Dict[str, Any], session):
    """Handle successful payment"""
    try:
        from backend.models.payment import Payment

        payment_id = payment_intent.get("metadata", {}).get("payment_id")
        if payment_id:
            # Update payment status in database
            result = await session.execute(
                update(Payment)
                .where(Payment.id == int(payment_id))
                .values(
                    status="completed",
                    gateway_transaction_id=payment_intent["id"],
                    payment_date=datetime.now(),
                    updated_at=datetime.now()
                )
            )
            await session.commit()
            logger.info(f"Payment {payment_id} marked as completed")

    except Exception as e:
        logger.error(f"Failed to update payment status: {e}")


async def handle_payment_failure(payment_intent: Dict[str, Any], session):
    """Handle failed payment"""
    try:
        from backend.models.payment import Payment

        payment_id = payment_intent.get("metadata", {}).get("payment_id")
        if payment_id:
            result = await session.execute(
                update(Payment)
                .where(Payment.id == int(payment_id))
                .values(
                    status="failed",
                    error_message=payment_intent.get("last_payment_error", {}).get("message"),
                    updated_at=datetime.now()
                )
            )
            await session.commit()
            logger.info(f"Payment {payment_id} marked as failed")

    except Exception as e:
        logger.error(f"Failed to update payment status: {e}")


async def handle_refund(charge: Dict[str, Any], session):
    """Handle refund event"""
    logger.info(f"Refund processed for charge: {charge.get('id')}")


async def handle_subscription_created(subscription: Dict[str, Any], session):
    """Handle subscription created"""
    logger.info(f"Subscription created: {subscription.get('id')}")


async def handle_subscription_updated(subscription: Dict[str, Any], session):
    """Handle subscription updated"""
    logger.info(f"Subscription updated: {subscription.get('id')}")


async def handle_subscription_cancelled(subscription: Dict[str, Any], session):
    """Handle subscription cancelled"""
    logger.info(f"Subscription cancelled: {subscription.get('id')}")