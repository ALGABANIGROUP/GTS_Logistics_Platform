"""
Stripe Payment Service - Real payment processing
"""

import os
import logging
import stripe
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class StripeService:
    """Stripe payment processing service"""

    def __init__(self):
        self.api_key = os.getenv("STRIPE_SECRET_KEY", "")
        self.publishable_key = os.getenv("STRIPE_PUBLISHABLE_KEY", "")
        self.webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET", "")
        self.enabled = bool(self.api_key)

        if self.enabled:
            stripe.api_key = self.api_key
            logger.info("Stripe service initialized")
        else:
            logger.warning("Stripe service disabled - no API key")

    async def create_payment_intent(
        self,
        amount: float,
        currency: str = "usd",
        customer_id: Optional[str] = None,
        metadata: Optional[Dict] = None,
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a payment intent"""
        if not self.enabled:
            return {
                "success": False,
                "error": "Stripe is not configured. Set STRIPE_SECRET_KEY to enable."
            }

        try:
            intent = stripe.PaymentIntent.create(
                amount=int(amount * 100),  # Convert to cents
                currency=currency.lower(),
                customer=customer_id,
                metadata=metadata or {},
                description=description,
                payment_method_types=["card"],
                capture_method="automatic"
            )

            return {
                "success": True,
                "client_secret": intent.client_secret,
                "payment_intent_id": intent.id,
                "amount": amount,
                "currency": currency,
                "status": intent.status
            }

        except stripe.error.StripeError as e:
            logger.error(f"Stripe error: {e}")
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__
            }
        except Exception as e:
            logger.error(f"Payment intent creation failed: {e}")
            return {
                "success": False,
                "error": "Payment processing failed. Please try again."
            }

    async def confirm_payment_intent(
        self,
        payment_intent_id: str,
        payment_method_id: str
    ) -> Dict[str, Any]:
        """Confirm a payment intent"""
        if not self.enabled:
            return {"success": False, "error": "Stripe not configured"}

        try:
            intent = stripe.PaymentIntent.confirm(
                payment_intent_id,
                payment_method=payment_method_id
            )

            return {
                "success": True,
                "payment_intent_id": intent.id,
                "status": intent.status,
                "amount": intent.amount / 100,
                "currency": intent.currency
            }

        except stripe.error.StripeError as e:
            logger.error(f"Stripe confirmation error: {e}")
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__
            }

    async def get_payment_intent(self, payment_intent_id: str) -> Dict[str, Any]:
        """Get payment intent details"""
        if not self.enabled:
            return {"success": False, "error": "Stripe not configured"}

        try:
            intent = stripe.PaymentIntent.retrieve(payment_intent_id)

            return {
                "success": True,
                "payment_intent_id": intent.id,
                "amount": intent.amount / 100,
                "currency": intent.currency,
                "status": intent.status,
                "customer_id": intent.customer,
                "metadata": intent.metadata,
                "created_at": datetime.fromtimestamp(intent.created).isoformat()
            }

        except stripe.error.StripeError as e:
            logger.error(f"Stripe retrieve error: {e}")
            return {"success": False, "error": str(e)}

    async def refund_payment(
        self,
        payment_intent_id: str,
        amount: Optional[float] = None,
        reason: str = "requested_by_customer"
    ) -> Dict[str, Any]:
        """Refund a payment"""
        if not self.enabled:
            return {"success": False, "error": "Stripe not configured"}

        try:
            refund_params = {
                "payment_intent": payment_intent_id,
                "reason": reason
            }
            if amount:
                refund_params["amount"] = int(amount * 100)

            refund = stripe.Refund.create(**refund_params)

            return {
                "success": True,
                "refund_id": refund.id,
                "amount": refund.amount / 100,
                "currency": refund.currency,
                "status": refund.status,
                "reason": refund.reason
            }

        except stripe.error.StripeError as e:
            logger.error(f"Stripe refund error: {e}")
            return {"success": False, "error": str(e)}


# Singleton instance
_stripe_service = None


def get_stripe_service() -> StripeService:
    """Get Stripe service instance"""
    global _stripe_service
    if _stripe_service is None:
        _stripe_service = StripeService()
    return _stripe_service