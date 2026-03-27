# -*- coding: utf-8 -*-
"""
Payment Service - Main Payment Service
Provides a unified interface for all payment and transfer operations

Covers:
- Creating new payments
- Recording transactions
- Updating payment statuses
- Processing refunds
- Retrieving payment history

Author: GTS Development Team
Date: March 2026
Version: 1.0
"""

import os
import re
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from uuid import uuid4

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.payment import (
    CurrencyCode,
    Payment,
    PaymentGateway,
    PaymentStatus,
    PaymentType,
    PaymentTransaction,
    Refund,
    TransactionType,
)
from backend.models.invoices import Invoice

logger = logging.getLogger(__name__)


# ============================================================================
# WISE BANK ACCOUNT DETAILS
# ============================================================================

WISE_CAD_ACCOUNT = {
    "account_holder": "Gabani Transport Solutions LLC",
    "account_number": "200116499651",
    "institution_number": "621",
    "transit_number": "16001",
    "swift_bic": "TRWICAW1XXX",
    "bank_name": "Wise Payments Canada Inc.",
    "bank_address": "99 Bank Street, Suite 1420, Ottawa, ON, K1P 1H4, Canada",
    "currency": "CAD"
}

WISE_USD_ACCOUNT = {
    "account_holder": "Gabani Transport Solutions LLC",
    "routing_number": "084009519",
    "account_number": "960001287651",
    "swift_bic": "TRWICAW1XXX",
    "bank_name": "Wise Payments Canada Inc.",
    "currency": "USD"
}


# ============================================================================
# PAYMENT SERVICE
# ============================================================================

class PaymentService:
    """
    Payment Service - Main Payment Service
    Provides a unified interface for payment operations
    """

    def __init__(self, db_session: AsyncSession, sudapay_service: Any | None = None):
        """
        Initialize Payment Service
        
        Args:
            db_session: AsyncSession for the database
            sudapay_service: Deprecated legacy gateway client
        """
        self.db = db_session
        self.sudapay = sudapay_service
        logger.info("✅ PaymentService initialized")

    def _normalize_currency(self, currency: str | CurrencyCode) -> CurrencyCode:
        if isinstance(currency, CurrencyCode):
            return currency
        return CurrencyCode[str(currency).upper()]

    def _normalize_gateway(self, gateway: str | PaymentGateway) -> PaymentGateway:
        if isinstance(gateway, PaymentGateway):
            return gateway
        return PaymentGateway[str(gateway).upper()]

    def build_public_payment_link(self, payment_id: int | str) -> str:
        frontend_base = str(
            os.getenv("FRONTEND_URL")
            or os.getenv("GTS_FRONTEND_URL")
            or "http://127.0.0.1:5173"
        ).rstrip("/")
        return f"{frontend_base}/pay/{payment_id}"

    # ========================================================================
    # PAYMENT CREATION - Payment Creation
    # ========================================================================

    async def create_payment(
        self,
        user_id: int,
        amount: float,
        currency: str = "USD",
        gateway: str = "stripe",
        invoice_id: Optional[int] = None,
        expense_id: Optional[int] = None,
        payment_type: str = "invoice",
        supplier_name: Optional[str] = None,
        payment_method_id: Optional[int] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict] = None,
    ) -> Payment:
        """
        Create Payment - Create a new payment
        
        Args:
            user_id: User ID
            amount: Payment amount
            currency: Currency (USD, CAD, EUR)
            gateway: Payment gateway (stripe, paypal)
            invoice_id: Invoice ID for customer collections
            expense_id: Expense ID for supplier payouts
            payment_type: invoice or expense
            supplier_name: Supplier name for expense payouts
            payment_method_id: Payment method (optional)
            description: Payment description
            metadata: Additional data
        
        Returns:
            Payment: The newly created payment object
        """
        try:
            normalized_currency = self._normalize_currency(currency)
            normalized_gateway = self._normalize_gateway(gateway)
            normalized_type = PaymentType(str(payment_type).lower())
            reference_id = self._generate_reference_id(normalized_gateway.value)

            if normalized_type is PaymentType.INVOICE:
                if invoice_id is None:
                    raise ValueError("invoice_id is required for invoice payments")
                if expense_id is not None:
                    raise ValueError("expense_id must be omitted for invoice payments")
            else:
                if expense_id is None:
                    raise ValueError("expense_id is required for expense payments")
                if invoice_id is not None:
                    raise ValueError("invoice_id must be omitted for expense payments")

            payment = Payment(
                reference_id=reference_id,
                invoice_id=invoice_id,
                expense_id=expense_id,
                user_id=user_id,
                payment_method_id=payment_method_id,
                payment_type=normalized_type,
                supplier_name=supplier_name if normalized_type is PaymentType.EXPENSE else None,
                amount=amount,
                currency=normalized_currency,
                status=PaymentStatus.PENDING,
                payment_gateway=normalized_gateway,
                description=(
                    description
                    or (
                        f"Payment for Invoice #{invoice_id}"
                        if normalized_type is PaymentType.INVOICE
                        else f"Expense payout for #{expense_id}"
                    )
                ),
                metadata_json=metadata or {},
            )

            self.db.add(payment)
            await self.db.flush()

            logger.info(
                f"✅ Payment created: ref={reference_id}, "
                f"amount={amount}{currency}, gateway={gateway}"
            )

            return payment

        except Exception as e:
            logger.error(f"❌ Failed to create payment: {str(e)}")
            await self.db.rollback()
            raise

    # ========================================================================
    # TRANSACTION RECORDING - Transaction Recording
    # ========================================================================

    async def record_transaction(
        self,
        payment_id: int,
        transaction_type: str = "payment",
        amount: Optional[float] = None,
        status: str = "pending",
        error_code: Optional[str] = None,
        error_message: Optional[str] = None,
        gateway_response: Optional[Dict] = None,
    ) -> PaymentTransaction:
        """
        Record Transaction - Record a new transaction
        
        Args:
            payment_id: Payment ID
            transaction_type: Transaction type (payment, refund, etc.)
            amount: Transaction amount (None = same as payment amount)
            status: Transaction status
            error_code: Error code (if any)
            error_message: Error message (if any)
            gateway_response: Full gateway response
        
        Returns:
            PaymentTransaction: The new transaction object
        """
        try:
            payment = await self.get_payment(payment_id)
            if not payment:
                raise ValueError(f"Payment {payment_id} not found")

            tx_amount = amount or payment.amount

            transaction = PaymentTransaction(
                payment_id=payment_id,
                transaction_type=TransactionType[transaction_type.upper()],
                amount=tx_amount,
                status=PaymentStatus[status.upper()],
                error_code=error_code,
                error_message=error_message,
                gateway_response=gateway_response or {},
            )

            self.db.add(transaction)
            await self.db.flush()

            logger.info(
                f"✅ Transaction recorded: type={transaction_type}, "
                f"payment_id={payment_id}, status={status}"
            )

            return transaction

        except Exception as e:
            logger.error(f"❌ Failed to record transaction: {str(e)}")
            await self.db.rollback()
            raise

    async def create_checkout_payment(
        self,
        *,
        invoice_id: int,
        user_id: int,
        amount: float,
        currency: str = "USD",
        gateway: str = "stripe",
        description: Optional[str] = None,
        customer_email: Optional[str] = None,
        return_url: Optional[str] = None,
        cancel_url: Optional[str] = None,
        metadata: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """Create a payment row and initialize the external checkout."""
        payment = await self.create_payment(
            user_id=user_id,
            amount=amount,
            currency=currency,
            gateway=gateway,
            invoice_id=invoice_id,
            description=description,
            metadata=metadata,
        )

        normalized_gateway = self._normalize_gateway(gateway)
        if normalized_gateway is PaymentGateway.SUDAPAY:
            raise ValueError("Sudapay has been removed from GTS")
        await self.db.commit()

        return {
            "payment": payment,
            "checkout_url": None,
            "public_payment_link": self.build_public_payment_link(payment.id),
            "gateway": normalized_gateway.value,
            "status": PaymentStatus.PENDING.value,
        }

    # ========================================================================
    # PAYMENT STATUS UPDATES - Payment Status Updates
    # ========================================================================

    async def update_payment_status(
        self,
        payment_id: int,
        status: str,
        gateway_transaction_id: Optional[str] = None,
        payment_date: Optional[datetime] = None,
        metadata: Optional[Dict] = None,
    ) -> Payment:
        """
        Update Payment Status - Update payment status
        
        Args:
            payment_id: Payment ID
            status: New status (completed, failed, etc.)
            gateway_transaction_id: Gateway transaction ID
            payment_date: Payment date
            metadata: Additional metadata
        
        Returns:
            Payment: Updated payment object
        """
        try:
            payment = await self.get_payment(payment_id)
            if not payment:
                raise ValueError(f"Payment {payment_id} not found")

            payment.status = PaymentStatus[status.upper()]
            
            if gateway_transaction_id:
                payment.gateway_transaction_id = gateway_transaction_id
            
            if payment_date:
                payment.payment_date = payment_date
            
            if metadata:
                payment.metadata_json = metadata

            if status.lower() == "completed" and payment.invoice_id is not None:
                invoice = await self.db.get(Invoice, payment.invoice_id)
                if invoice:
                    invoice.status = "paid"
                    logger.info(
                        f"✅ Invoice #{payment.invoice_id} marked as paid"
                    )

            await self.db.commit()

            logger.info(
                f"✅ Payment status updated: id={payment_id}, status={status}"
            )

            return payment

        except Exception as e:
            logger.error(f"❌ Failed to update payment status: {str(e)}")
            await self.db.rollback()
            raise

    # ========================================================================
    # REFUND OPERATIONS - Refund Operations
    # ========================================================================

    async def create_refund(
        self,
        payment_id: int,
        amount: Optional[float] = None,
        reason: str = "Customer request",
        gateway_refund_id: Optional[str] = None,
    ) -> Refund:
        """
        Create Refund - Create a refund
        
        Args:
            payment_id: Payment ID
            amount: Refund amount (None = full amount)
            reason: Refund reason
            gateway_refund_id: Gateway refund ID
        
        Returns:
            Refund: The new refund object
        """
        try:
            payment = await self.get_payment(payment_id)
            if not payment:
                raise ValueError(f"Payment {payment_id} not found")

            refund_amount = amount or payment.amount

            reference_id = self._generate_reference_id("RFD")

            refund = Refund(
                reference_id=reference_id,
                payment_id=payment_id,
                amount=refund_amount,
                reason=reason,
                gateway_refund_id=gateway_refund_id,
                status=PaymentStatus.PENDING,
            )

            self.db.add(refund)
            await self.db.flush()

            await self.record_transaction(
                payment_id=payment_id,
                transaction_type="refund",
                amount=refund_amount,
                status="pending",
            )

            logger.info(
                f"✅ Refund created: ref={reference_id}, "
                f"amount={refund_amount}, payment_id={payment_id}"
            )

            return refund

        except Exception as e:
            logger.error(f"❌ Failed to create refund: {str(e)}")
            await self.db.rollback()
            raise

    async def complete_refund(
        self,
        refund_id: int,
        completed_at: Optional[datetime] = None,
    ) -> Refund:
        """Complete Refund"""
        try:
            refund = await self.db.get(Refund, refund_id)
            if not refund:
                raise ValueError(f"Refund {refund_id} not found")

            refund.status = PaymentStatus.COMPLETED
            refund.completed_at = completed_at or datetime.utcnow()

            payment = await self.get_payment(refund.payment_id)
            if payment:
                payment.status = PaymentStatus.REFUNDED

            await self.db.commit()

            logger.info(f"✅ Refund completed: id={refund_id}")

            return refund

        except Exception as e:
            logger.error(f"❌ Failed to complete refund: {str(e)}")
            await self.db.rollback()
            raise

    async def confirm_payment(
        self,
        payment_id: int,
        *,
        gateway_transaction_id: Optional[str] = None,
        metadata: Optional[Dict] = None,
        payment_date: Optional[datetime] = None,
    ) -> Payment:
        """Confirm a payment using gateway data when available."""
        payment = await self.get_payment(payment_id)
        if not payment:
            raise ValueError(f"Payment {payment_id} not found")

        resolved_gateway_txn = gateway_transaction_id or payment.gateway_transaction_id
        gateway_metadata = metadata or {}
        payment_status = self._map_payment_gateway_status(gateway_metadata.get("status"))

        await self.record_transaction(
            payment_id=payment_id,
            transaction_type=TransactionType.PAYMENT.value,
            amount=payment.amount,
            status=payment_status.value,
            gateway_response=gateway_metadata or None,
        )

        return await self.update_payment_status(
            payment_id=payment_id,
            status=payment_status.value,
            gateway_transaction_id=resolved_gateway_txn,
            payment_date=(payment_date or datetime.utcnow()) if payment_status == PaymentStatus.COMPLETED else None,
            metadata=gateway_metadata or None,
        )

    async def refund_payment(
        self,
        payment_id: int,
        *,
        amount: Optional[float] = None,
        reason: str = "Customer request",
    ) -> Refund:
        """Create and complete a refund, calling the gateway when configured."""
        payment = await self.get_payment(payment_id)
        if not payment:
            raise ValueError(f"Payment {payment_id} not found")
        if payment.status != PaymentStatus.COMPLETED:
            raise ValueError("Only completed payments can be refunded")

        refund = await self.create_refund(
            payment_id=payment_id,
            amount=amount,
            reason=reason,
        )

        return await self.complete_refund(refund.id)

    # ========================================================================
    # PAYMENT RETRIEVAL - Payment Retrieval
    # ========================================================================

    async def get_payment(self, payment_id: int) -> Optional[Payment]:
        """Return a payment by primary key."""
        return await self.db.get(Payment, payment_id)

    async def get_payment_by_reference(self, reference_id: str) -> Optional[Payment]:
        """Return a payment by its external reference id."""
        stmt = select(Payment).where(Payment.reference_id == reference_id)
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def resolve_payment(self, payment_identifier: int | str) -> Optional[Payment]:
        """Resolve a payment by numeric id or external reference id."""
        if isinstance(payment_identifier, int):
            return await self.get_payment(payment_identifier)

        raw_identifier = str(payment_identifier or "").strip()
        if not raw_identifier:
            return None

        if raw_identifier.isdigit():
            return await self.get_payment(int(raw_identifier))

        return await self.get_payment_by_reference(raw_identifier)

    async def get_refund(self, refund_id: int) -> Optional[Refund]:
        """Return a refund by primary key."""
        return await self.db.get(Refund, refund_id)

    async def get_refund_by_gateway_refund_id(self, gateway_refund_id: str) -> Optional[Refund]:
        """Return a refund by external gateway refund id."""
        stmt = select(Refund).where(Refund.gateway_refund_id == gateway_refund_id)
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def get_latest_pending_refund_for_payment(self, payment_id: int) -> Optional[Refund]:
        """Return the most recent pending refund for a payment."""
        stmt = (
            select(Refund)
            .where(
                Refund.payment_id == payment_id,
                Refund.status == PaymentStatus.PENDING,
            )
            .order_by(Refund.created_at.desc(), Refund.id.desc())
        )
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def get_invoice_payments(self, invoice_id: int) -> List[Payment]:
        """Return all payments linked to an invoice."""
        stmt = (
            select(Payment)
            .where(Payment.invoice_id == invoice_id)
            .order_by(Payment.created_at.desc(), Payment.id.desc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_user_payment_history(
        self,
        user_id: int,
        limit: int = 50,
        offset: int = 0,
    ) -> Tuple[List[Payment], int]:
        """Return paginated payment history for a user."""
        count_stmt = select(func.count()).select_from(Payment).where(Payment.user_id == user_id)
        total = int((await self.db.execute(count_stmt)).scalar() or 0)

        stmt = (
            select(Payment)
            .where(Payment.user_id == user_id)
            .order_by(Payment.created_at.desc(), Payment.id.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all()), total

    @staticmethod
    def _map_gateway_status(
        raw_status: Optional[str],
        *,
        success_statuses: set[str],
        pending_statuses: set[str],
        failure_statuses: set[str],
        default: PaymentStatus,
    ) -> PaymentStatus:
        normalized = str(raw_status or "").strip().lower()
        if not normalized:
            return default
        if normalized in success_statuses:
            return PaymentStatus.COMPLETED
        if normalized in pending_statuses:
            return PaymentStatus.PROCESSING
        if normalized in failure_statuses:
            return PaymentStatus.CANCELLED if normalized in {"cancelled", "canceled"} else PaymentStatus.FAILED
        return default

    def _map_payment_gateway_status(self, raw_status: Optional[str]) -> PaymentStatus:
        return self._map_gateway_status(
            raw_status,
            success_statuses={"completed", "success", "succeeded", "paid"},
            pending_statuses={"pending", "processing", "initiated", "requires_action"},
            failure_statuses={"failed", "cancelled", "canceled", "declined", "expired"},
            default=PaymentStatus.PENDING,
        )

    def _map_refund_gateway_status(self, raw_status: Optional[str]) -> PaymentStatus:
        return self._map_gateway_status(
            raw_status,
            success_statuses={"completed", "success", "succeeded", "refunded"},
            pending_statuses={"pending", "processing", "initiated"},
            failure_statuses={"failed", "cancelled", "canceled", "declined"},
            default=PaymentStatus.PENDING,
        )

    def get_gateway_name(self, gateway: PaymentGateway | str) -> str:
        """Return a user-friendly gateway display name."""
        value = gateway.value if isinstance(gateway, PaymentGateway) else str(gateway or "")
        mapping = {
            PaymentGateway.SUDAPAY.value: "Sudapay (removed)",
            PaymentGateway.STRIPE.value: "Stripe",
            PaymentGateway.PAYPAL.value: "PayPal",
        }
        return mapping.get(value.lower(), value.title() if value else "Unknown")

    def _generate_reference_id(self, prefix: str) -> str:
        """Generate a compact unique reference id."""
        clean_prefix = re.sub(r"[^A-Za-z0-9]+", "-", str(prefix or "PAY")).strip("-") or "PAY"
        return f"{clean_prefix}-{datetime.utcnow():%Y%m%d%H%M%S}-{uuid4().hex[:8]}"
