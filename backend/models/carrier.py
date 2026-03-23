from sqlalchemy import Column, Integer, String, Boolean, DateTime, DECIMAL, Text, ARRAY
from sqlalchemy.sql import func
from .base import Base

class Carrier(Base):
    __tablename__ = "carriers"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    mc_number = Column(String(50), unique=True)
    dot_number = Column(String(50), unique=True)
    scac_code = Column(String(10), unique=True)
    tax_id = Column(String(50))
    phone = Column(String(20))
    email = Column(String(255))
    website = Column(String(255))
    address_line1 = Column(String(255))
    address_line2 = Column(String(255))
    city = Column(String(100))
    state = Column(String(50))
    zip_code = Column(String(20))
    country = Column(String(100), default='USA')
    contact_person = Column(String(255))
    contact_phone = Column(String(20))
    contact_email = Column(String(255))
    insurance_provider = Column(String(255))
    insurance_policy_number = Column(String(100))
    insurance_expiry_date = Column(DateTime(timezone=True))
    bonding_company = Column(String(255))
    bonding_amount = Column(DECIMAL(15, 2))
    bonding_expiry_date = Column(DateTime(timezone=True))
    carrier_type = Column(String(50), default='common')  # common, owner_operator, fleet
    equipment_types = Column(ARRAY(String))  # Array of equipment types
    operating_areas = Column(ARRAY(String))  # Array of operating areas/states
    preferred_lanes = Column(ARRAY(String))  # Array of preferred lanes
    credit_score = Column(Integer)
    payment_terms = Column(String(100), default='net_30')
    rating = Column(DECIMAL(3, 2))  # 1.00 to 5.00
    total_loads = Column(Integer, default=0)
    on_time_delivery_rate = Column(DECIMAL(5, 2))  # Percentage
    incident_rate = Column(DECIMAL(5, 2))  # Percentage
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    verification_date = Column(DateTime(timezone=True))
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now())
