from __future__ import annotations

from typing import Any, Dict, Literal, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from backend.database.config import get_db_async
from backend.security.access_context import (
    require_any_feature,
    require_any_module,
    require_permission,
)
from backend.security.auth import get_current_user
from backend.security.entitlements import resolve_user_from_claims
from backend.services.dispatch_service import DispatchService

driver_router = APIRouter(prefix="/api/v1/driver", tags=["Driver"])

# ✅ IMPORTANT: backend.main expects "router"
router = driver_router


class CheckpointPayload(BaseModel):
    type: Literal["arrived_pickup", "loaded", "departed_pickup", "arrived_dropoff", "delivered"]
    note: Optional[str] = None


class LocationPayload(BaseModel):
    shipment_id: int
    lat: float
    lng: float
    accuracy: Optional[float] = None
    speed: Optional[float] = None
    heading: Optional[float] = None


def _extract_user_id(claims: Dict[str, Any]) -> Optional[int]:
    raw_id = claims.get("user_id")
    if isinstance(raw_id, int):
        return raw_id
    if isinstance(raw_id, str) and raw_id.isdigit():
        return int(raw_id)

    sub = claims.get("sub")
    if isinstance(sub, str) and sub.isdigit():
        return int(sub)

    return None


@driver_router.get(
    "/shipments",
    dependencies=[
        Depends(require_any_module(["tms", "dispatcher"])),
        Depends(require_any_feature(["tms.fleet", "dispatcher.core"])),
        Depends(require_permission("drivers.view")),
    ],
)
async def get_driver_shipments(
    claims: Dict[str, Any] = Depends(get_current_user),
    db=Depends(get_db_async),
):
    user = await resolve_user_from_claims(db, claims)
    driver_id = getattr(user, "id", None) or _extract_user_id(claims)

    if driver_id is None:
        return []

    service = DispatchService(db)
    return await service.get_driver_shipments(driver_user_id=driver_id)


@driver_router.post(
    "/shipments/{shipment_id}/checkpoint",
    dependencies=[
        Depends(require_any_module(["tms", "dispatcher"])),
        Depends(require_any_feature(["tms.fleet", "dispatcher.core"])),
        Depends(require_permission("drivers.manage")),
    ],
)
async def checkpoint(
    shipment_id: int,
    payload: CheckpointPayload,
    claims: Dict[str, Any] = Depends(get_current_user),
    db=Depends(get_db_async),
):
    user = await resolve_user_from_claims(db, claims)
    driver_id = getattr(user, "id", None) or _extract_user_id(claims)

    if driver_id is None:
        raise HTTPException(status_code=403, detail="Driver identity missing.")

    service = DispatchService(db)
    await service.record_checkpoint(
        shipment_id=shipment_id,
        driver_user_id=driver_id,
        checkpoint=payload.type.lower(),
        note=payload.note,
    )
    return {"ok": True}


@driver_router.post(
    "/location",
    dependencies=[
        Depends(require_any_module(["tms", "dispatcher"])),
        Depends(require_any_feature(["tms.fleet", "dispatcher.core"])),
        Depends(require_permission("drivers.manage")),
    ],
)
async def location_ping(
    payload: LocationPayload,
    claims: Dict[str, Any] = Depends(get_current_user),
    db=Depends(get_db_async),
):
    user = await resolve_user_from_claims(db, claims)
    driver_id = getattr(user, "id", None) or _extract_user_id(claims)

    if driver_id is None:
        raise HTTPException(status_code=403, detail="Driver identity missing.")

    service = DispatchService(db)
    await service.record_location_ping(
        shipment_id=payload.shipment_id,
        driver_user_id=driver_id,
        lat=payload.lat,
        lng=payload.lng,
        accuracy=payload.accuracy,
        speed=payload.speed,
        heading=payload.heading,
    )
    return {"ok": True}

