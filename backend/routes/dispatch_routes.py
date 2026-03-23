from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from backend.database.config import get_db_async
from backend.security.access_context import (
    require_any_feature,
    require_module,
    require_permission,
)
from backend.security.auth import get_current_user
from backend.security.entitlements import resolve_user_from_claims
from backend.services.dispatch_service import DispatchService
from backend.security.tenant_resolver import get_tenant_id
router = APIRouter(tags=["Dispatch"])
shipments_router = APIRouter(prefix="/api/v1/shipments", tags=["Dispatch"])


class AssignmentPayload(BaseModel):
    driver_user_id: int
    eta: Optional[datetime] = None
    notes: Optional[str] = None


@router.get(
    "/api/v1/dispatch/board",
    dependencies=[
        Depends(require_module("dispatcher")),
        Depends(require_any_feature(["dispatcher.core", "dispatch.assign"])),
        Depends(require_permission("dispatch.assign")),
    ],
)
async def get_dispatch_board(
    status: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(200, ge=1, le=500),
    db=Depends(get_db_async),
    tenant_id: str = Depends(get_tenant_id),
) -> Dict[str, Any]:
    service = DispatchService(db)
    return await service.get_dispatch_board(status_filter=status, search=search, skip=skip, limit=limit)


@router.get(
    "/api/v1/dispatch/insights",
    dependencies=[
        Depends(require_module("dispatcher")),
        Depends(require_any_feature(["dispatcher.core", "dispatch.assign"])),
        Depends(require_permission("dispatch.assign")),
    ],
)
async def get_dispatch_insights(
    db=Depends(get_db_async),
    tenant_id: str = Depends(get_tenant_id),
) -> Dict[str, Any]:
    service = DispatchService(db)
    alerts = await service.get_dispatch_alerts()
    maintenance = await service.get_maintenance_overview()
    return {
        "alerts": alerts,
        "maintenance": maintenance,
    }


@router.get(
    "/api/v1/dispatch/shipments/{shipment_id}/route-plan",
    dependencies=[
        Depends(require_module("dispatcher")),
        Depends(require_any_feature(["dispatcher.core", "dispatch.assign"])),
        Depends(require_permission("dispatch.assign")),
    ],
)
async def get_route_plan(
    shipment_id: int,
    db=Depends(get_db_async),
    tenant_id: str = Depends(get_tenant_id),
) -> Dict[str, Any]:
    service = DispatchService(db)
    return await service.get_route_plan(shipment_id=shipment_id)


@router.get(
    "/api/v1/dispatch/shipments/{shipment_id}/driver-guidance",
    dependencies=[
        Depends(require_module("dispatcher")),
        Depends(require_any_feature(["dispatcher.core", "dispatch.assign"])),
        Depends(require_permission("dispatch.assign")),
    ],
)
async def get_driver_guidance(
    shipment_id: int,
    driver_user_id: Optional[int] = Query(None),
    db=Depends(get_db_async),
    tenant_id: str = Depends(get_tenant_id),
) -> Dict[str, Any]:
    service = DispatchService(db)
    return await service.get_driver_guidance(shipment_id=shipment_id, driver_user_id=driver_user_id)


@shipments_router.post(
    "/{shipment_id}/assign",
    dependencies=[
        Depends(require_module("dispatcher")),
        Depends(require_any_feature(["dispatcher.core", "dispatch.assign"])),
        Depends(require_permission("dispatch.assign")),
    ],
)
async def assign_shipment(
    shipment_id: int,
    payload: AssignmentPayload,
    claims: Dict[str, Any] = Depends(get_current_user),
    db=Depends(get_db_async),
    tenant_id: str = Depends(get_tenant_id),
) -> Dict[str, Any]:
    user = await resolve_user_from_claims(db, claims)
    dispatcher_id = getattr(user, "id", None)
    service = DispatchService(db)
    assignment = await service.assign_shipment(
        shipment_id=shipment_id,
        driver_user_id=payload.driver_user_id,
        dispatcher_user_id=dispatcher_id,
        notes=payload.notes,
        eta=payload.eta,
    )
    return {"ok": True, "assignment_id": assignment.id}


router.include_router(shipments_router)
