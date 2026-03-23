from __future__ import annotations

from sqlalchemy import Column, DateTime, ForeignKey, Integer, JSON, String
from sqlalchemy.sql import func
from backend.database.base import Base


class ShipmentEvent(Base):
    __tablename__ = "shipment_events"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True)
    shipment_id = Column(Integer, ForeignKey("shipments.id", ondelete="CASCADE"), nullable=False)
    event_type = Column(String(64), nullable=False)
    payload = Column(JSON, nullable=True)
    actor_user_id = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())


