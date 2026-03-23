from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

# Correct import for Shipment
from backend.models.models import Shipment  # type: ignore[import]


async def create_shipment(
    db: AsyncSession,
    tracking_number: str,
    origin: str,
    destination: str,
    weight: float,
    cost: float,
):
    shipment = Shipment(
        tracking_number=tracking_number,
        origin=origin,
        destination=destination,
        weight=weight,
        cost=cost,
    )
    db.add(shipment)
    await db.commit()
    await db.refresh(shipment)
    return shipment


async def get_all_shipments(db: AsyncSession):
    result = await db.execute(select(Shipment))
    return result.scalars().all()


async def get_shipment_by_tracking_number(db: AsyncSession, tracking_number: str):
    result = await db.execute(
        select(Shipment).where(Shipment.tracking_number == tracking_number)
    )
    return result.scalar_one_or_none()

