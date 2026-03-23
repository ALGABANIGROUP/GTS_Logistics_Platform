from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, Query

from backend.security.auth import require_roles
from backend.services.scheduler import sync_external_sources
from backend.services.sources import get_sources_manager

router = APIRouter(tags=["external"])


@router.post("/api/v1/external/sync")
async def trigger_external_sync(
    limit_per_source: int = Query(5, ge=1, le=50),
    province: Optional[str] = Query(None, description="Province filter for sync"),
    force: bool = Query(False, description="Force sync even if another one is running"),
    _: dict = Depends(require_roles(["admin", "super_admin"])),
) -> dict[str, object]:
    result = await sync_external_sources(
        limit_per_source=limit_per_source,
        province=province,
        force=force,
    )
    return {"ok": True, "result": result}


@router.get("/api/v1/external/search")
async def search_external_data(
    source: Optional[str] = Query(None),
    entity_type: Optional[str] = Query(None, alias="type"),
    query: Optional[str] = Query(None, alias="q"),
    province: Optional[str] = Query(None),
    limit: int = Query(10, ge=1, le=50),
    _: dict = Depends(require_roles(["admin", "super_admin"])),
) -> dict[str, object]:
    manager = get_sources_manager()
    items = await manager.search(
        source=source,
        entity_type=entity_type,
        query=query,
        province=province,
        limit=limit,
    )
    return {"ok": True, "count": len(items), "items": [item.dict() for item in items]}
