from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.database.base import Base
from datetime import datetime

class Invoice(Base):
    __tablename__ = 'invoices'
    id = Column(Integer, primary_key=True)
    number = Column(String, nullable=False)
    date = Column(Date, nullable=False)
    amount_usd = Column(Float, nullable=False)
    status = Column(String, nullable=False)
    plan_code = Column(String(50), nullable=True, index=True)
    user_id = Column(Integer, nullable=True, index=True)
    shipment_id = Column(Integer, nullable=True)  # FK disabled until Shipment model exists
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), onupdate=datetime.utcnow)
    # shipment = relationship('Shipment', backref='invoices')  # Disabled until Shipment model exists
