from __future__ import annotations

import logging
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from backend.repositories.tracking_repo import InvoiceRepository, TrackingRepository
from backend.schemas.webhook import ShipmentStatus, TrackingEventData

logger = logging.getLogger(__name__)


class TrackingService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.tracking_repo = TrackingRepository(session)
        self.invoice_repo = InvoiceRepository(session)

    async def process_tracking_event(self, event_data: TrackingEventData) -> None:
        shipment = await self.tracking_repo.get_shipment_by_tracking_id(event_data.external_tracking_id)

        if shipment is None:
            shipment = await self.tracking_repo.create_shipment(event_data)
            logger.info("Created tracking shipment %s", shipment.id)
        else:
            await self.tracking_repo.update_shipment_status(shipment.id, event_data.event_type, event_data.event_time)

        await self.tracking_repo.create_tracking_event(shipment.id, event_data)

        if event_data.event_type == ShipmentStatus.delivered and not shipment.invoice_id:
            invoice = await self.invoice_repo.generate_invoice_for_shipment(shipment.id)
            shipment.invoice_id = invoice.id
            logger.info("Generated invoice %s for shipment %s", invoice.invoice_number, shipment.id)

        await self.session.commit()

    async def ensure_shipment(self, event_data: TrackingEventData) -> Optional[int]:
        shipment = await self.tracking_repo.get_shipment_by_tracking_id(event_data.external_tracking_id)
        if shipment is None:
            shipment = await self.tracking_repo.create_shipment(event_data)
            await self.session.commit()
        return shipment.id if shipment else None
