"""
Stripe Payment Service - Real payment processing
"""

import logging
import stripe
from typing import Dict, Any, Optional
from datetime import datetime

from backend.config import Settings

logger = logging.getLogger(__name__)
settings = Settings()


class StripeService:
    """Stripe payment processing service"""

    def __init__(self):
        self.api_key = settings.STRIPE_SECRET_KEY
        self.publishable_key = settings.STRIPE_PUBLISHABLE_KEY
        self.webhook_secret = settings.STRIPE_WEBHOOK_SECRET
        self.enabled = settings.STRIPE_ENABLED

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
                automatic_payment_methods={"enabled": True}
            )

            return {
                "success": True,
                "client_secret": intent.client_secret,
                "payment_intent_id": intent.id,
                "amount": amount,
                "currency": currency
            }

        except Exception as e:
            logger.error(f"Error creating payment intent: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def retrieve_payment_intent(self, payment_intent_id: str) -> Dict[str, Any]:
        """Retrieve a payment intent"""
        if not self.enabled:
            return {"success": False, "error": "Stripe not configured"}

        try:
            intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            return {
                "success": True,
                "status": intent.status,
                "amount": intent.amount / 100,
                "currency": intent.currency,
                "metadata": intent.metadata
            }
        except Exception as e:
            logger.error(f"Error retrieving payment intent: {e}")
            return {"success": False, "error": str(e)}

    async def create_customer(self, email: str, name: str = None) -> Dict[str, Any]:
        """Create a Stripe customer"""
        if not self.enabled:
            return {"success": False, "error": "Stripe not configured"}

        try:
            customer = stripe.Customer.create(
                email=email,
                name=name
            )
            return {
                "success": True,
                "customer_id": customer.id
            }
        except Exception as e:
            logger.error(f"Error creating customer: {e}")
            return {"success": False, "error": str(e)}

    def get_publishable_key(self) -> str:
        """Get the publishable key for frontend"""
        return self.publishable_key

    def is_enabled(self) -> bool:
        """Check if Stripe is enabled"""
        return self.enabled


# Singleton instance
_stripe_service = None

def get_stripe_service() -> StripeService:
    """Get the singleton Stripe service instance"""
    global _stripe_service
    if _stripe_service is None:
        _stripe_service = StripeService()
    return _stripe_service