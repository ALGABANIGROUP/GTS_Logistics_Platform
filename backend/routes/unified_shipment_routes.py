from __future__ import annotations

import logging
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.config import get_db_async
from backend.routes.map_entities import _collect_entities

router = APIRouter(prefix="/api/v1/unified", tags=["Unified Shipments"])
logger = logging.getLogger(__name__)


async def _collect_vehicles(db: AsyncSession) -> list[dict[str, Any]]:
    try:
        result = await db.execute(
            text(
                """
                SELECT
                    v.id,
                    v.vehicle_code,
                    v.plate_number,
                    v.type,
                    v.status,
                    vl.lat,
                    vl.lng,
                    vl.speed,
                    vl.updated_at
                FROM fleet_vehicles v
                LEFT JOIN fleet_vehicle_locations vl ON vl.vehicle_id = v.id
                WHERE COALESCE(v.status, '') <> 'inactive'
                ORDER BY v.id DESC
                LIMIT 200
                """
            )
        )
        return [dict(row) for row in result.mappings().all()]
    except Exception:
        return []


@router.get("/shipments")
async def get_unified_shipments(
    status: Optional[str] = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db_async),
) -> dict[str, Any]:
    try:
        entities = await _collect_entities(db)
        vehicles = await _collect_vehicles(db)
    except Exception as exc:
        logger.error("failed to collect unified shipment data: %s", exc)
        raise HTTPException(status_code=500, detail="Internal server error fetching shipment data") from exc

    shipments = list(entities.get("shipments") or [])
    if status:
        normalized = status.strip().lower()
        shipments = [
            shipment
            for shipment in shipments
            if str(shipment.get("status") or "").strip().lower() == normalized
        ]

    total = len(shipments)
    paginated_shipments = shipments[offset : offset + limit]
    if total == 0:
        raise HTTPException(status_code=503, detail="No shipment data available from any source")

    return {
        "status": "success",
        "data": {
            "shipments": paginated_shipments,
            "drivers": entities.get("drivers") or [],
            "tenants": entities.get("tenants") or [],
            "brokers": entities.get("brokers") or [],
            "carriers": entities.get("carriers") or [],
            "companies": entities.get("tenants") or [],
            "vehicles": vehicles,
        },
        "meta": {
            "total": total,
            "limit": limit,
            "offset": offset,
            "sources": ["shipments", "map_entities", "fleet_vehicles"],
        },
    }
