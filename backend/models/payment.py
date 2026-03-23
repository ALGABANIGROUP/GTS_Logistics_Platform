# -*- coding: utf-8 -*-
"""
Payment Models for GTS Platform

Supports:
- SUDAPAY (Primary for Sudan/SDG)
- Stripe (International/USD)
- PayPal (Global)
"""

from datetime import datetime
from enum import Enum

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Enum as SQLEnum,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship

from backend.database.base import Base


class PaymentStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class PaymentMethodType(str, Enum):
    CARD = "card"
    BANK_TRANSFER = "bank_transfer"
    MOBILE_WALLET = "mobile_wallet"
    SUDAPAY = "sudapay"
    STRIPE = "stripe"
    PAYPAL = "paypal"
    LOCAL_BANK = "local_bank"


class PaymentGateway(str, Enum):
    SUDAPAY = "sudapay"
    STRIPE = "stripe"
    PAYPAL = "paypal"


class PaymentType(str, Enum):
    INVOICE = "invoice"
    EXPENSE = "expense"


class TransactionType(str, Enum):
    PAYMENT = "payment"
    REFUND = "refund"
    REVERSAL = "reversal"
    CHARGEBACK = "chargeback"


class CurrencyCode(str, Enum):
    SDG = "SDG"
    USD = "USD"
    EUR = "EUR"


class PaymentMethod(Base):
    __tablename__ = "payment_methods"
    __table_args__ = (
        UniqueConstraint("user_id", "token", name="uq_user_method_token"),
        Index("idx_user_id", "user_id"),
        Index("idx_method_type", "method_type"),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    method_type = Column(SQLEnum(PaymentMethodType), nullable=False)
    token = Column(String(500), nullable=False)
    display_name = Column(String(100), nullable=True)
    brand = Column(String(50), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    is_default = Column(Boolean, default=False, nullable=False)
    gateway = Column(SQLEnum(PaymentGateway), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    payments = relationship("Payment", back_populates="payment_method")

    def __repr__(self):
        return f"<PaymentMethod(id={self.id}, user_id={self.user_id}, type={self.method_type})>"


class Payment(Base):
    __tablename__ = "payments"
    __table_args__ = (
        UniqueConstraint("reference_id", name="uq_payment_reference_id"),
        Index("idx_invoice_id", "invoice_id"),
        Index("idx_expense_id", "expense_id"),
        Index("idx_payment_type", "payment_type"),
        Index("idx_user_id", "user_id"),
        Index("idx_status", "status"),
        Index("idx_payment_date", "payment_date"),
        Index("idx_gateway_transaction_id", "gateway_transaction_id"),
        Index("idx_created_at", "created_at"),
    )

    id = Column(Integer, primary_key=True, index=True)
    reference_id = Column(String(50), unique=True, nullable=False, index=True)

    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=True)
    expense_id = Column(Integer, ForeignKey("expenses.id"), nullable=True)
    payment_method_id = Column(Integer, ForeignKey("payment_methods.id"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    payment_type = Column(SQLEnum(PaymentType), default=PaymentType.INVOICE, nullable=False)
    supplier_name = Column(String(200), nullable=True)

    amount = Column(Float, nullable=False)
    currency = Column(SQLEnum(CurrencyCode), default=CurrencyCode.SDG, nullable=False)
    status = Column(SQLEnum(PaymentStatus), default=PaymentStatus.PENDING, nullable=False, index=True)
    payment_gateway = Column(SQLEnum(PaymentGateway), nullable=False)
    gateway_transaction_id = Column(String(200), nullable=True, index=True)
    description = Column(String(500), nullable=True)
    notes = Column(Text, nullable=True)
    payment_date = Column(DateTime(timezone=True), nullable=True, index=True)
    metadata_json = Column("metadata", JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    payment_method = relationship("PaymentMethod", back_populates="payments")
    transactions = relationship("PaymentTransaction", back_populates="payment")
    refunds = relationship("Refund", back_populates="payment")

    @hybrid_property
    def is_successful(self) -> bool:
        return self.status == PaymentStatus.COMPLETED

    @hybrid_property
    def is_failed(self) -> bool:
        return self.status in [PaymentStatus.FAILED, PaymentStatus.CANCELLED]

    def __repr__(self):
        return (
            f"<Payment(id={self.id}, ref={self.reference_id}, "
            f"amount={self.amount}{self.currency}, status={self.status})>"
        )


class PaymentTransaction(Base):
    __tablename__ = "payment_transactions"
    __table_args__ = (
        Index("idx_payment_id", "payment_id"),
        Index("idx_status", "status"),
        Index("idx_transaction_type", "transaction_type"),
        Index("idx_created_at", "created_at"),
    )

    id = Column(Integer, primary_key=True, index=True)
    payment_id = Column(Integer, ForeignKey("payments.id"), nullable=False)
    transaction_type = Column(SQLEnum(TransactionType), nullable=False)
    amount = Column(Float, nullable=False)
    status = Column(SQLEnum(PaymentStatus), default=PaymentStatus.PENDING, nullable=False)
    error_code = Column(String(50), nullable=True)
    error_message = Column(String(500), nullable=True)
    gateway_response = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False, index=True)

    payment = relationship("Payment", back_populates="transactions")

    def __repr__(self):
        return (
            f"<PaymentTransaction(id={self.id}, payment_id={self.payment_id}, "
            f"type={self.transaction_type}, status={self.status})>"
        )


class Refund(Base):
    __tablename__ = "refunds"
    __table_args__ = (
        UniqueConstraint("reference_id", name="uq_refund_reference_id"),
        Index("idx_payment_id", "payment_id"),
        Index("idx_status", "status"),
        Index("idx_created_at", "created_at"),
    )

    id = Column(Integer, primary_key=True, index=True)
    reference_id = Column(String(50), unique=True, nullable=False, index=True)
    payment_id = Column(Integer, ForeignKey("payments.id"), nullable=False)
    amount = Column(Float, nullable=False)
    reason = Column(String(500), nullable=True)
    status = Column(SQLEnum(PaymentStatus), default=PaymentStatus.PENDING, nullable=False)
    gateway_refund_id = Column(String(200), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    payment = relationship("Payment", back_populates="refunds")

    def __repr__(self):
        return (
            f"<Refund(id={self.id}, payment_id={self.payment_id}, "
            f"amount={self.amount}, status={self.status})>"
        )
