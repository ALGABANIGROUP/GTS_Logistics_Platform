from sqlalchemy import Column, Integer, String, Boolean, DateTime, DECIMAL, Text, ARRAY
from sqlalchemy.sql import func
from .base import Base

class Shipper(Base):
    __tablename__ = "shippers"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
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
    industry_type = Column(String(100))
    business_type = Column(String(50))  # manufacturer, distributor, retailer, etc.
    annual_shipping_volume = Column(Integer)  # Estimated annual loads
    credit_score = Column(Integer)
    payment_terms = Column(String(100), default='net_30')
    rating = Column(DECIMAL(3, 2))  # 1.00 to 5.00
    total_loads = Column(Integer, default=0)
    on_time_pickup_rate = Column(DECIMAL(5, 2))  # Percentage
    damage_claim_rate = Column(DECIMAL(5, 2))  # Percentage
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    verification_date = Column(DateTime(timezone=True))
    preferred_carriers = Column(ARRAY(String))  # Array of preferred carrier IDs
    shipping_schedule = Column(Text)  # JSON string for shipping patterns
    special_requirements = Column(Text)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now())