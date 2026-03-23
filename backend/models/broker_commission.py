"""
Freight Broker Commission Models
For tracking commissions, pricing, and profit on shipments
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum as PyEnum
from backend.database.base import Base


class InvoiceType(str, PyEnum):
    """Invoice type for broker operations"""
    CLIENT_INVOICE = "client"      # Invoice to customer/shipper
    CARRIER_INVOICE = "carrier"    # Invoice from carrier
    BROKER_COMMISSION = "commission"  # Broker commission tracking


class CommissionTier(Base):
    """Commission tier configuration for different shipment types"""
    __tablename__ = "broker_commission_tiers"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)  # e.g., "Standard", "Premium", "VIP"
    shipment_type = Column(String(50), nullable=False)  # ltl, ftl, parcel, special
    commission_percentage = Column(Float, nullable=False)  # e.g., 5.5
    minimum_commission = Column(Float, nullable=False, default=0.0)
    maximum_commission = Column(Float, nullable=True)  # None = unlimited
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)


class BrokerCommission(Base):
    """Track commissions earned on each shipment"""
    __tablename__ = "broker_commissions"
    
    id = Column(Integer, primary_key=True, index=True)
    shipment_id = Column(Integer, nullable=False, index=True)
    shipment_number = Column(String(50), nullable=False)
    
    # Revenue
    client_invoice_amount = Column(Float, nullable=False)  # What customer pays
    carrier_cost = Column(Float, nullable=False)  # What we pay carrier
    
    # Commission Calculation
    commission_tier_id = Column(Integer, ForeignKey("broker_commission_tiers.id"), nullable=True)
    commission_percentage = Column(Float, nullable=False, default=5.0)
    commission_amount = Column(Float, nullable=False)  # Calculated: (client_amount - carrier_cost) * percentage
    
    # Profit
    gross_profit = Column(Float, nullable=False)  # client_amount - carrier_cost
    net_profit = Column(Float, nullable=False)  # gross_profit - commission_amount
    profit_margin_percentage = Column(Float, nullable=False)  # (gross_profit / client_amount) * 100
    
    # Status
    status = Column(String(50), default="pending")  # pending, calculated, approved, paid
    
    # Dates
    shipment_date = Column(DateTime, nullable=True)
    delivery_date = Column(DateTime, nullable=True)
    commission_payment_date = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    
    # Notes
    notes = Column(Text, nullable=True)


class EnhancedInvoice(Base):
    """Enhanced Invoice model with broker commission fields"""
    __tablename__ = "invoices_enhanced"
    
    id = Column(Integer, primary_key=True, index=True)
    number = Column(String(100), nullable=False, unique=True, index=True)
    invoice_type = Column(String(50), nullable=False)  # client, carrier, commission
    
    # Basic Info
    date = Column(DateTime, default=datetime.utcnow)
    due_date = Column(DateTime, nullable=True)
    shipment_id = Column(Integer, nullable=True, index=True)
    shipment_number = Column(String(50), nullable=True)
    
    # Parties
    from_party = Column(String(200), nullable=True)  # Company issuing invoice
    to_party = Column(String(200), nullable=True)    # Company receiving invoice
    
    # Amounts
    amount_usd = Column(Float, nullable=False)
    commission_percentage = Column(Float, nullable=True)  # For commission invoices
    commission_amount = Column(Float, nullable=True)
    
    # For broker operations
    carrier_cost = Column(Float, nullable=True)  # Cost to pay carrier
    profit_margin = Column(Float, nullable=True)  # Profit amount
    profit_margin_percentage = Column(Float, nullable=True)  # Profit %
    
    # Status tracking
    status = Column(String(50), default="draft")  # draft, sent, pending, partial, paid, overdue, cancelled
    payment_method = Column(String(50), nullable=True)  # check, bank_transfer, credit_card, cash
    payment_date = Column(DateTime, nullable=True)
    
    # Metadata
    currency = Column(String(10), default="USD")
    notes = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
