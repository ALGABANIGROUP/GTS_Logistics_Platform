# -*- coding: utf-8 -*-
"""
SUDAPAY Service - خدمة SUDAPAY لمنصة GTS
يوفر جميع العمليات الأساسية للتعامل مع SUDAPAY

SUDAPAY: منصة الدفع الموحدة الحكومية السودانية
- البنك المركزي السوداني
- دعم جنيه سوداني (SDG) ودولار أمريكي (USD)
- معايير أمان عالية (PCI DSS متوافق)
- رسوم منخفضة: 1.5-2% (أقل من Stripe و PayPal)

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

# Configure logging
logger = logging.getLogger(__name__)


# ============================================================================
# ENUMS & MODELS - أنماط البيانات
# ============================================================================

class SudapayPaymentStatus(str, Enum):
    """SUDAPAY Payment Status"""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class SudapayPaymentRequest(BaseModel):
    """SUDAPAY Payment Request - طلب دفع"""
    amount: float = Field(..., gt=0, description="المبلغ")
    currency: str = Field(default="SDG", description="العملة (SDG/USD)")
    reference_id: str = Field(..., description="رقم مرجعي فريد")
    description: Optional[str] = Field(None, description="وصف الدفع")
    customer_email: Optional[str] = Field(None, description="بريد المستخدم")
    return_url: Optional[str] = Field(None, description="رابط العودة بعد الدفع")
    cancel_url: Optional[str] = Field(None, description="رابط الإلغاء")
    metadata: Optional[Dict] = Field(None, description="بيانات إضافية")


class SudapayPaymentResponse(BaseModel):
    """SUDAPAY Payment Response - رد الدفع"""
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
    SUDAPAY Service - خدمة SUDAPAY
    توفر واجهة موحدة للتعامل مع SUDAPAY
    
    Usage:
        sudapay = SudapayService(
            api_key="your_api_key",
            merchant_id="your_merchant_id",
            sandbox=True  # وضع الاختبار
        )
        
        # إنشاء دفعة
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
            api_key: مفتاح API من SUDAPAY
            merchant_id: معرّف التاجر
            webhook_secret: سر التحقق من Webhooks
            sandbox: وضع الاختبار (True) أم الإنتاج (False)
            api_version: إصدار API
            timeout: timeout للطلبات بالثواني
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
    # PAYMENT OPERATIONS - عمليات الدفع
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
        Create Payment - إنشاء عملية دفع جديدة
        
        Args:
            amount: المبلغ (SDG أو USD)
            currency: العملة (SDG/USD)
            reference_id: رقم مرجعي فريد (اختياري - يتم الإنشاء تلقائياً)
            description: وصف الدفعة
            customer_email: بريد العميل
            return_url: رابط العودة الناجح
            cancel_url: رابط الإلغاء
            metadata: بيانات إضافية (JSON)
        
        Returns:
            SudapayPaymentResponse: معلومات الدفعة الجديدة
        
        Raises:
            SudapayAPIError: إذا فشل الطلب
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
        Confirm Payment - تأكيد حالة الدفعة
        
        Args:
            payment_id: معرّف الدفعة من SUDAPAY
        
        Returns:
            Dict: معلومات الدفعة الحالية
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
        Refund Payment - استرجاع الأموال
        
        Args:
            payment_id: معرّف الدفعة
            amount: مبلغ الاسترجاع (None = كامل المبلغ)
            reason: سبب الاسترجاع
        
        Returns:
            Dict: معلومات الاسترجاع
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
    # VALIDATION & SECURITY - التحقق والأمان
    # ========================================================================

    def verify_webhook_signature(
        self,
        payload: str,
        signature: str,
    ) -> bool:
        """
        Verify Webhook Signature - التحقق من توقيع Webhook
        
        Args:
            payload: نص payload من SUDAPAY
            signature: التوقيع من headers
        
        Returns:
            bool: هل التوقيع صحيح
        """
        import hmac
        import hashlib

        try:
            expected_signature = hmac.new(
                self.webhook_secret.encode(),
                payload.encode(),
                hashlib.sha256,
            ).hexdigest()

            is_valid = hmac.compare_digest(expected_signature, signature)

            if is_valid:
                logger.info("✅ Webhook signature verified")
            else:
                logger.warning("❌ Webhook signature verification failed")

            return is_valid

        except Exception as e:
            logger.error(f"❌ Signature verification error: {str(e)}")
            return False

    # ========================================================================
    # UTILITY METHODS - دوال مساعدة
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
