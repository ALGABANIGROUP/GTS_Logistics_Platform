from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

# Import the canonical Base from backend.database.base
from backend.database.base import Base

# ✅ User Model - REMOVED (use canonical from backend/models/user.py)
# The User model was moved to backend/models/user.py with TenantScopedMixin
# to support multi-tenant architecture. This file should NOT redefine it.


# Shipment Model (updated)
class Shipment(Base):
    __tablename__ = "shipments"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True)
    pickup_location = Column(String, nullable=False)
    dropoff_location = Column(String, nullable=False)
    trailer_type = Column(String, nullable=True)
    rate = Column(Float, nullable=True)               # Changed from String to Float
    recurring_type = Column(String, nullable=True)
    days = Column(String, nullable=True)
    weight = Column(Float, nullable=True)             # Changed from String to Float
    length = Column(Float, nullable=True)             # Changed from String to Float
    load_size = Column(String, nullable=True)
    description = Column(String, nullable=True)
    status = Column(String, default="on_the_way")
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    distance_km = Column(Float, nullable=True)
    duration_hours = Column(Float, nullable=True)
    price_usd = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("backend.models.user.User", back_populates="shipments")

    # Partner relationships
    carrier_id = Column(Integer, ForeignKey("logistics_partners.id"), nullable=True)
    shipper_id = Column(Integer, ForeignKey("logistics_partners.id"), nullable=True)
    broker_id = Column(Integer, ForeignKey("logistics_partners.id"), nullable=True)

    carrier_partner = relationship("LogisticsPartner", foreign_keys=[carrier_id], back_populates="shipments_as_carrier")
    shipper_partner = relationship("LogisticsPartner", foreign_keys=[shipper_id], back_populates="shipments_as_shipper")
    broker_partner = relationship("LogisticsPartner", foreign_keys=[broker_id], back_populates="shipments_as_broker")

# ✅ MessageLog Model
class MessageLog(Base):
    __tablename__ = "message_logs"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True)
    sender = Column(String, nullable=False)
    message = Column(String, nullable=False)
    context = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
# ✅ Expense Model
