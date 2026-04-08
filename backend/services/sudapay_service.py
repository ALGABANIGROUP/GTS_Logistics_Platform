# -*- coding: utf-8 -*-
"""
SUDAPAY Service - SUDAPAY Service for GTS Platform
Provides all basic operations for dealing with SUDAPAY

SUDAPAY: Unified Government Payment Platform of Sudan
- Central Bank of Sudan
- Support for Sudanese Pound (SDG) and US Dollar (USD)
- High security standards (PCI DSS compliant)
- Low fees: 1.5-2% (lower than Stripe and PayPal)

Author: GTS Development Team
Date: March 2026
Version: 1.0
"""

import logging
from datetime import datetime
from typing import Dict, Optional, List
from enum import Enum

import httpx
from pydantic import BaseModel, Field

from backend.security.webhook_signatures import verify_hmac_sha256_signature

# Configure logging
logger = logging.getLogger(__name__)


# ============================================================================
# ENUMS & MODELS - Data Models
# ============================================================================

class SudapayPaymentStatus(str, Enum):
    """SUDAPAY Payment Status"""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class SudapayPaymentRequest(BaseModel):
    """SUDAPAY Payment Request"""
    amount: float = Field(..., gt=0, description="Amount")
    currency: str = Field(default="SDG", description="Currency (SDG/USD)")
    reference_id: str = Field(..., description="Unique reference number")
    description: Optional[str] = Field(None, description="Payment description")
    customer_email: Optional[str] = Field(None, description="Customer email")
    return_url: Optional[str] = Field(None, description="Return URL after payment")
    cancel_url: Optional[str] = Field(None, description="Cancel URL")
    metadata: Optional[Dict] = Field(None, description="Additional data")


class SudapayPaymentResponse(BaseModel):
    """SUDAPAY Payment Response"""
    payment_id: str
    status: str
    checkout_url: Optional[str] = None
    amount: float
    currency: str
    created_at: str


class SudapayWebhookPayload(BaseModel):
    """SUDAPAY Webhook Payload"""
    type: str  # payment.success, payment.failed, etc.
    data: Dict


# ============================================================================
# SUDAPAY SERVICE
# ============================================================================

class SudapayService:
    """
    SUDAPAY Service - SUDAPAY Service
    Provides a unified interface for dealing with SUDAPAY
    
    Usage:
        sudapay = SudapayService(
            api_key="your_api_key",
            merchant_id="your_merchant_id",
            sandbox=True  # test mode
        )
        
        # Create payment
        payment = await sudapay.create_payment(
            amount=100000,
            currency="SDG",
            reference_id="SUP-123456"
        )
    """

    def __init__(
        self,
        api_key: str,
        merchant_id: str,
        webhook_secret: str,
        sandbox: bool = True,
        api_version: str = "v1",
        timeout: int = 30
    ):
        """
        Initialize SUDAPAY Service
        
        Args:
            api_key: API key from SUDAPAY
            merchant_id: Merchant identifier
            webhook_secret: Webhook verification secret
            sandbox: Test mode (True) or production (False)
            api_version: API version
            timeout: Request timeout in seconds
        """
        self.api_key = api_key
        self.merchant_id = merchant_id
        self.webhook_secret = webhook_secret
        self.sandbox = sandbox
        self.timeout = timeout

        # Base URLs
        self.base_url = (
            "https://sandbox.sudapay.sd"
            if sandbox
            else "https://api.sudapay.sd"
        )
        self.api_version = api_version
        self.api_url = f"{self.base_url}/api/{api_version}"

        # Headers
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
            "X-Merchant-ID": merchant_id,
            "User-Agent": "GTS-Platform/1.0",
        }

        logger.info(
            f"✅ SudapayService initialized "
            f"(sandbox={sandbox}, merchant_id={merchant_id})"
        )

    # ========================================================================
    # PAYMENT OPERATIONS
    # ========================================================================

    async def create_payment(
        self,
        amount: float,
        currency: str = "SDG",
        reference_id: Optional[str] = None,
        description: Optional[str] = None,
        customer_email: Optional[str] = None,
        return_url: Optional[str] = None,
        cancel_url: Optional[str] = None,
        metadata: Optional[Dict] = None,
    ) -> SudapayPaymentResponse:
        """
        Create Payment - Create a new payment transaction
        
        Args:
            amount: Amount (SDG or USD)
            currency: Currency (SDG/USD)
            reference_id: Unique reference number (optional - auto-generated)
            description: Payment description
            customer_email: Customer email
            return_url: Success return URL
            cancel_url: Cancel URL
            metadata: Additional data (JSON)
        
        Returns:
            SudapayPaymentResponse: Information about the new payment
        
        Raises:
            SudapayAPIError: If the request fails
        """
        try:
            # Generate reference_id if not provided
            if not reference_id:
                ref_timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
                reference_id = f"SUP-{ref_timestamp}"

            # Prepare payload
            payload = {
                "amount": int(amount * 100),  # Convert to cents/fils
                "currency": currency,
                "reference_id": reference_id,
                "description": description or "Order Payment",
                "metadata": metadata or {},
            }

            # Add optional fields
            if customer_email:
                payload["customer_email"] = customer_email
            if return_url:
                payload["return_url"] = return_url
            if cancel_url:
                payload["cancel_url"] = cancel_url

            # Make request
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.api_url}/payments",
                    json=payload,
                    headers=self.headers,
                )
                response.raise_for_status()
                data = response.json()

            # Log success
            logger.info(
                f"✅ SUDAPAY Payment Created: "
                f"ref={reference_id}, amount={amount}{currency}"
            )

            # Return response
            return SudapayPaymentResponse(
                payment_id=data.get("id"),
                status=data.get("status"),
                checkout_url=data.get("checkout_url"),
                amount=amount,
                currency=currency,
                created_at=datetime.utcnow().isoformat(),
            )

        except httpx.HTTPStatusError as e:
            error_msg = f"SUDAPAY API Error: {e.response.text}"
            logger.error(f"❌ {error_msg}")
            raise SudapayAPIError(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to create payment: {str(e)}"
            logger.error(f"❌ {error_msg}")
            raise SudapayAPIError(error_msg) from e

    async def confirm_payment(
        self,
        payment_id: str,
    ) -> Dict:
        """
        Confirm Payment - Confirm payment status
        
        Args:
            payment_id: Payment ID from SUDAPAY
        
        Returns:
            Dict: Current payment information
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.api_url}/payments/{payment_id}",
                    headers=self.headers,
                )
                response.raise_for_status()
                data = response.json()

            logger.info(
                f"✅ SUDAPAY Payment Confirmed: "
                f"payment_id={payment_id}, status={data.get('status')}"
            )

            return {
                "payment_id": data.get("id"),
                "status": data.get("status"),
                "amount": data.get("amount", 0) / 100,  # Convert from fils to currency
                "currency": data.get("currency"),
                "reference_id": data.get("reference_id"),
                "created_at": data.get("created_at"),
                "completed_at": data.get("completed_at"),
            }

        except httpx.HTTPStatusError as e:
            error_msg = f"SUDAPAY API Error: {e.response.text}"
            logger.error(f"❌ {error_msg}")
            raise SudapayAPIError(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to confirm payment: {str(e)}"
            logger.error(f"❌ {error_msg}")
            raise SudapayAPIError(error_msg) from e

    async def refund_payment(
        self,
        payment_id: str,
        amount: Optional[float] = None,
        reason: str = "Customer request",
    ) -> Dict:
        """
        Refund Payment - Refund payment
        
        Args:
            payment_id: Payment ID
            amount: Refund amount (None = full amount)
            reason: Refund reason
        
        Returns:
            Dict: Refund information
        """
        try:
            payload = {
                "reason": reason,
            }
            if amount:
                payload["amount"] = int(amount * 100)  # Convert to fils

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.api_url}/payments/{payment_id}/refund",
                    json=payload,
                    headers=self.headers,
                )
                response.raise_for_status()
                data = response.json()

            logger.info(
                f"✅ SUDAPAY Refund Created: "
                f"payment_id={payment_id}, refund_id={data.get('id')}"
            )

            return {
                "refund_id": data.get("id"),
                "payment_id": data.get("payment_id"),
                "status": data.get("status"),
                "amount": data.get("amount", 0) / 100,
                "reason": reason,
            }

        except httpx.HTTPStatusError as e:
            error_msg = f"SUDAPAY API Error: {e.response.text}"
            logger.error(f"❌ {error_msg}")
            raise SudapayAPIError(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to refund payment: {str(e)}"
            logger.error(f"❌ {error_msg}")
            raise SudapayAPIError(error_msg) from e

    # ========================================================================
    # VALIDATION & SECURITY
    # ========================================================================

    def verify_webhook_signature(
        self,
        payload: str,
        signature: str,
    ) -> bool:
        """
        Verify Webhook Signature - Verify webhook signature
        
        Args:
            payload: Payload text from SUDAPAY
            signature: Signature from headers
        
        Returns:
            bool: Whether the signature is valid
        """
        try:
            is_valid = verify_hmac_sha256_signature(
                secret=self.webhook_secret,
                payload=payload.encode("utf-8"),
                signature_header=signature,
                app_env="production",
            )

            if is_valid:
                logger.info("✅ Webhook signature verified")
            else:
                logger.warning("❌ Webhook signature verification failed")

            return is_valid

        except Exception as e:
            logger.error(f"❌ Signature verification error: {str(e)}")
            return False

    # ========================================================================
    # UTILITY METHODS - Utility Functions
    # ========================================================================

    def format_amount(self, amount: float) -> int:
        """Convert amount to fils/cents"""
        return int(amount * 100)

    def parse_amount(self, amount_in_fils: int) -> float:
        """Convert from fils/cents to amount"""
        return amount_in_fils / 100

    def generate_reference_id(self, prefix: str = "SUP") -> str:
        """Generate unique reference ID"""
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        return f"{prefix}-{timestamp}"

    @property
    def is_sandbox(self) -> bool:
        """Check if running in sandbox mode"""
        return self.sandbox

    def get_status(self) -> Dict:
        """Get service status information"""
        return {
            "service": "SUDAPAY",
            "version": "1.0",
            "sandbox": self.sandbox,
            "merchant_id": self.merchant_id,
            "base_url": self.base_url,
            "status": "✅ Active",
        }


# ============================================================================
# EXCEPTIONS
# ============================================================================

class SudapayAPIError(Exception):
    """SUDAPAY API Error"""
    pass
