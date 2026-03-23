from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field, field_validator


class ShipmentStatus(str, Enum):
    created = "created"
    picked_up = "picked_up"
    in_transit = "in_transit"
    delayed = "delayed"
    delivered = "delivered"
    cancelled = "cancelled"


class InvoiceStatus(str, Enum):
    draft = "draft"
    pending = "pending"
    sent = "sent"
    paid = "paid"
    overdue = "overdue"
    cancelled = "cancelled"


class TrackingEventData(BaseModel):
    """Tracking event payload aligned with integrationClient.js."""

    event_type: ShipmentStatus
    event_time: datetime
    location: Optional[str] = None
    description: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    external_tracking_id: str = Field(..., min_length=1)
    shipment_reference: Optional[str] = None
    carrier_code: Optional[str] = None
    driver_id: Optional[str] = None
    vehicle_id: Optional[str] = None

    @field_validator("event_time")
    @classmethod
    def _event_time_not_future(cls, value: datetime) -> datetime:
        if value > datetime.utcnow():
            raise ValueError("Event time cannot be in the future")
        return value


class WebhookPayload(BaseModel):
    event: TrackingEventData
    client_id: str
    timestamp: int
    signature: str
    idempotency_key: str = Field(default_factory=lambda: str(uuid.uuid4()))


class WebhookResponse(BaseModel):
    status: str = "accepted"
    message: str = "Webhook processing started"
    webhook_id: str
    received_at: datetime


class InvoiceResponse(BaseModel):
    id: int
    invoice_number: str
    amount: float
    currency: str = "USD"
    due_date: datetime
    status: InvoiceStatus
    pdf_url: Optional[str] = None
    created_at: datetime
    shipment_id: int
    customer_id: int
