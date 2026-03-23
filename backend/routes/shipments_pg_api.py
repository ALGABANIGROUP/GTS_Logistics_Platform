from __future__ import annotations

from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy import or_, select
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.ext.asyncio import AsyncSession
from backend.database.config import get_db_async
from backend.models.shipment import Shipment as EnhancedShipment
from backend.models.truck_location import TruckLocation
from backend.models.user import User
from backend.schemas.shipment_schema import ShipmentBase, ShipmentCreate, ShipmentUpdate
from backend.security.access_context import (
    require_any_feature,
    require_module,
    require_permission,
)
from backend.security.auth import get_current_user
from backend.security.entitlements import resolve_user_from_claims
from backend.services import shipment_service

router = APIRouter(prefix="/api/v1/shipments", tags=["Shipments"])


class ShipmentCreateIn(ShipmentBase):
    user_id: Optional[int] = None


def _shipment_guard():
    return [
        Depends(require_module("tms")),
        Depends(require_any_feature(["tms.core", "tms.shipments"])),
    ]


def _serialize_shipment(shipment: Any) -> Dict[str, Any]:
    return jsonable_encoder(
        {
            "id": getattr(shipment, "id", None),
            "user_id": getattr(shipment, "user_id", None),
            "pickup_location": getattr(shipment, "pickup_location", None),
            "dropoff_location": getattr(shipment, "dropoff_location", None),
            "trailer_type": getattr(shipment, "trailer_type", None),
            "rate": getattr(shipment, "rate", None),
            "weight": getattr(shipment, "weight", None),
            "length": getattr(shipment, "length", None),
            "load_size": getattr(shipment, "load_size", None),
            "description": getattr(shipment, "description", None),
            "status": getattr(shipment, "status", None),
            "latitude": getattr(shipment, "latitude", None),
            "longitude": getattr(shipment, "longitude", None),
            "recurring_type": getattr(shipment, "recurring_type", None),
            "days": getattr(shipment, "days", None),
            "created_at": getattr(shipment, "created_at", None),
            "updated_at": getattr(shipment, "updated_at", None),
        }
    )


def _live_shipment_payload(
    legacy_shipment: Any,
    enhanced_shipment: Any = None,
    truck: Any = None,
    driver: Any = None,
) -> Dict[str, Any]:
    shipment_number = (
        getattr(enhanced_shipment, "shipment_number", None)
        or getattr(legacy_shipment, "reference_number", None)
        or getattr(legacy_shipment, "shipment_number", None)
        or f"SH-{getattr(legacy_shipment, 'id', 'N/A')}"
    )
    pickup_label = (
        getattr(legacy_shipment, "pickup_location", None)
        or getattr(enhanced_shipment, "origin_address", None)
        or getattr(enhanced_shipment, "origin_city", None)
        or "Origin"
    )
    dropoff_label = (
        getattr(legacy_shipment, "dropoff_location", None)
        or getattr(enhanced_shipment, "destination_address", None)
        or getattr(enhanced_shipment, "destination_city", None)
        or "Destination"
    )

    current_latitude = (
        getattr(enhanced_shipment, "current_latitude", None)
        or getattr(truck, "latitude", None)
        or getattr(legacy_shipment, "latitude", None)
    )
    current_longitude = (
        getattr(enhanced_shipment, "current_longitude", None)
        or getattr(truck, "longitude", None)
        or getattr(legacy_shipment, "longitude", None)
    )

    driver_name = (
        getattr(driver, "full_name", None)
        or getattr(driver, "username", None)
        or getattr(enhanced_shipment, "driver_name", None)
        or getattr(truck, "driver_name", None)
        or "Unassigned"
    )
    driver_phone = (
        getattr(driver, "phone_number", None)
        or getattr(enhanced_shipment, "driver_phone", None)
        or "N/A"
    )

    truck_label = (
        getattr(truck, "truck_number", None)
        or getattr(truck, "license_plate", None)
        or getattr(enhanced_shipment, "truck_id", None)
        or "N/A"
    )

    return jsonable_encoder(
        {
            "shipment": {
                "id": getattr(legacy_shipment, "id", None),
                "reference": shipment_number,
                "status": getattr(enhanced_shipment, "status", None)
                or getattr(legacy_shipment, "status", None),
                "origin": {
                    "city": getattr(enhanced_shipment, "origin_city", None),
                    "address": pickup_label,
                    "lat": getattr(enhanced_shipment, "origin_latitude", None)
                    or getattr(legacy_shipment, "latitude", None),
                    "lng": getattr(enhanced_shipment, "origin_longitude", None)
                    or getattr(legacy_shipment, "longitude", None),
                },
                "destination": {
                    "city": getattr(enhanced_shipment, "destination_city", None),
                    "address": dropoff_label,
                    "lat": getattr(enhanced_shipment, "destination_latitude", None),
                    "lng": getattr(enhanced_shipment, "destination_longitude", None),
                },
                "current_location": {
                    "lat": current_latitude,
                    "lng": current_longitude,
                    "updated_at": getattr(truck, "last_update", None)
                    or getattr(enhanced_shipment, "updated_at", None)
                    or getattr(legacy_shipment, "updated_at", None),
                    "description": getattr(enhanced_shipment, "current_location_description", None)
                    or getattr(truck, "status", None),
                },
                "eta": getattr(enhanced_shipment, "delivery_scheduled", None)
                or getattr(enhanced_shipment, "delivery_deadline", None),
                "cargo": {
                    "type": getattr(enhanced_shipment, "shipment_type", None)
                    or getattr(legacy_shipment, "trailer_type", None),
                    "weight": getattr(enhanced_shipment, "weight_kg", None)
                    or getattr(legacy_shipment, "weight", None),
                    "dimensions": getattr(enhanced_shipment, "dimensions_meter", None)
                    or getattr(legacy_shipment, "length", None),
                    "description": getattr(enhanced_shipment, "goods_description", None)
                    or getattr(legacy_shipment, "description", None),
                },
                "progress": {
                    "percentage": getattr(enhanced_shipment, "progress_percentage", None),
                    "distance_remaining_km": getattr(
                        enhanced_shipment, "distance_remaining_km", None
                    ),
                    "distance_traveled_km": getattr(
                        enhanced_shipment, "distance_traveled_km", None
                    ),
                },
            },
            "driver": {
                "id": getattr(driver, "id", None) or getattr(enhanced_shipment, "driver_id", None),
                "name": driver_name,
                "phone": driver_phone,
                "photo": None,
                "rating": None,
            },
            "vehicle": {
                "id": getattr(truck, "id", None) or getattr(enhanced_shipment, "truck_id", None),
                "plate": getattr(truck, "license_plate", None),
                "type": getattr(legacy_shipment, "trailer_type", None)
                or getattr(enhanced_shipment, "shipment_type", None),
                "speed": getattr(truck, "speed", None),
                "truck_number": truck_label,
                "status": getattr(truck, "status", None),
            },
        }
    )


@router.get("/", dependencies=_shipment_guard() + [Depends(require_permission("shipments.view"))])
async def list_shipments(
    db: AsyncSession = Depends(get_db_async),
    skip: int = Query(0, ge=0),
    limit: int = Query(200, ge=1, le=500),
) -> Dict[str, Any]:
    shipments = await shipment_service.get_all_shipments(db)
    if skip or limit:
        shipments = shipments[skip : skip + limit]
    return {"ok": True, "shipments": [_serialize_shipment(s) for s in shipments]}


@router.get("/stats", dependencies=_shipment_guard() + [Depends(require_permission("shipments.view"))])
async def get_shipment_stats(
    db: AsyncSession = Depends(get_db_async),
) -> Dict[str, Any]:
    """Get shipment statistics for dashboard"""
    stats = await shipment_service.get_shipment_stats(db)
    return stats


@router.get(
    "/{shipment_id}",
    dependencies=_shipment_guard() + [Depends(require_permission("shipments.view"))],
)
async def get_shipment(
    shipment_id: int,
    db: AsyncSession = Depends(get_db_async),
) -> Dict[str, Any]:
    shipment = await shipment_service.get_shipment_by_id(shipment_id, db)
    if shipment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shipment not found")
    return {"ok": True, "data": shipment}


@router.get(
    "/{shipment_id}/live",
    dependencies=_shipment_guard() + [Depends(require_permission("shipments.view"))],
)
async def get_shipment_live_data(
    shipment_id: int,
    db: AsyncSession = Depends(get_db_async),
) -> Dict[str, Any]:
    shipment = await shipment_service.get_shipment_by_id(shipment_id, db)
    if shipment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shipment not found")

    enhanced_shipment = None
    try:
        enhanced_stmt = select(EnhancedShipment).where(
            or_(
                EnhancedShipment.id == shipment_id,
                EnhancedShipment.reference_number == str(shipment_id),
            )
        )
        enhanced_shipment = (await db.execute(enhanced_stmt)).scalar_one_or_none()
    except ProgrammingError:
        enhanced_shipment = None

    truck_filters = [TruckLocation.current_shipment_id == shipment_id]
    truck_id = getattr(enhanced_shipment, "truck_id", None)
    if truck_id is not None:
        truck_filters.append(TruckLocation.id == truck_id)

    truck = (await db.execute(select(TruckLocation).where(or_(*truck_filters)))).scalars().first()

    driver_id = getattr(enhanced_shipment, "driver_id", None) or getattr(truck, "driver_id", None)
    driver = None
    if driver_id is not None:
        driver = (await db.execute(select(User).where(User.id == driver_id))).scalar_one_or_none()

    return {
        "ok": True,
        "data": _live_shipment_payload(
            legacy_shipment=shipment,
            enhanced_shipment=enhanced_shipment,
            truck=truck,
            driver=driver,
        ),
    }


@router.post(
    "/",
    dependencies=_shipment_guard() + [Depends(require_permission("shipments.create"))],
)
async def create_shipment(
    payload: ShipmentCreateIn,
    claims: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_async),
) -> Dict[str, Any]:
    user_id = payload.user_id
    if user_id is None:
        user = await resolve_user_from_claims(db, claims)
        user_id = getattr(user, "id", None)
    if user_id is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="user_id is required")

    shipment_payload = ShipmentCreate(**payload.model_dump(), user_id=int(user_id))
    shipment = await shipment_service.create_shipment(db, shipment_payload)
    return {"ok": True, "shipment": shipment}


@router.patch(
    "/{shipment_id}",
    dependencies=_shipment_guard() + [Depends(require_permission("shipments.update"))],
)
async def update_shipment(
    shipment_id: int,
    payload: ShipmentUpdate,
    db: AsyncSession = Depends(get_db_async),
) -> Dict[str, Any]:
    shipment = await shipment_service.get_shipment_by_id(shipment_id, db)
    if shipment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shipment not found")

    updated = payload.model_dump(exclude_unset=True)
    await shipment_service.update_shipment(shipment_id, updated, db)
    return {"ok": True, "message": f"Shipment {shipment_id} updated"}


@router.delete(
    "/{shipment_id}",
    dependencies=_shipment_guard() + [Depends(require_permission("shipments.delete"))],
)
async def delete_shipment(
    shipment_id: int,
    db: AsyncSession = Depends(get_db_async),
) -> Dict[str, Any]:
    shipment = await shipment_service.get_shipment_by_id(shipment_id, db)
    if shipment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shipment not found")

    await shipment_service.delete_shipment(shipment_id, db)
    return {"ok": True, "message": f"Shipment {shipment_id} deleted"}
