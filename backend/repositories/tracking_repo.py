from __future__ import annotations

import uuid
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from backend.models.tracking_webhook import TrackingEvent, TrackingInvoice, TrackingShipment
from backend.schemas.webhook import InvoiceStatus, ShipmentStatus, TrackingEventData


class TrackingRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_shipment_by_tracking_id(self, external_tracking_id: str) -> Optional[TrackingShipment]:
        result = await self.session.execute(
            select(TrackingShipment).where(TrackingShipment.external_tracking_id == external_tracking_id)
        )
        return result.scalar_one_or_none()

    async def create_shipment(self, event: TrackingEventData) -> TrackingShipment:
        shipment = TrackingShipment(
            external_tracking_id=event.external_tracking_id,
            shipment_reference=event.shipment_reference,
            status=event.event_type,
            created_at=event.event_time,
            metadata=event.metadata or {},
        )

        if event.event_type == ShipmentStatus.picked_up:
            shipment.picked_up_at = event.event_time
        elif event.event_type == ShipmentStatus.delivered:
            shipment.delivered_at = event.event_time

        self.session.add(shipment)
        await self.session.flush()
        return shipment

    async def update_shipment_status(self, shipment_id: int, status: ShipmentStatus, event_time: datetime) -> None:
        update_data = {"status": status, "updated_at": datetime.utcnow()}
        if status == ShipmentStatus.picked_up:
            update_data["picked_up_at"] = event_time
        elif status == ShipmentStatus.delivered:
            update_data["delivered_at"] = event_time

        await self.session.execute(
            update(TrackingShipment).where(TrackingShipment.id == shipment_id).values(**update_data)
        )

    async def create_tracking_event(self, shipment_id: int, event: TrackingEventData) -> TrackingEvent:
        tracking_event = TrackingEvent(
            shipment_id=shipment_id,
            event_type=event.event_type,
            event_time=event.event_time,
            location=event.location,
            description=event.description,
            metadata=event.metadata or {},
        )
        self.session.add(tracking_event)
        await self.session.flush()
        return tracking_event


class InvoiceRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def generate_invoice_for_shipment(self, shipment_id: int) -> TrackingInvoice:
        now = datetime.utcnow()
        invoice_number = f"INV-{now.strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:6]}"

        invoice = TrackingInvoice(
            invoice_number=invoice_number,
            shipment_id=shipment_id,
            amount=0.0,
            tax_amount=0.0,
            total_amount=0.0,
            currency="USD",
            issue_date=now,
            due_date=now + timedelta(days=30),
            status=InvoiceStatus.pending,
            line_items=[],
            metadata={},
            customer_id=0,
        )

        self.session.add(invoice)
        await self.session.flush()
        return invoice

