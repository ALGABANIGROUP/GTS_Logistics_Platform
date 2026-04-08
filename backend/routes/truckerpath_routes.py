from __future__ import annotations

from typing import Any, Dict, Optional

from fastapi import APIRouter, Body, HTTPException, Query
from pydantic import BaseModel, Field

from backend.services.truckerpath_service import TruckerPathService


async def _noop_broadcast(*args, **kwargs) -> None:
    return None


broadcast_event = _noop_broadcast
try:
    from backend.routes.ws_routes import broadcast_event as _broadcast_event  # type: ignore

    broadcast_event = _broadcast_event
except Exception:
    try:
        from backend.routes.ws_routes import broadcast_event as _broadcast_event  # type: ignore

        broadcast_event = _broadcast_event
    except Exception:
        pass


router = APIRouter(prefix="/truckerpath", tags=["TruckerPath"])
compat_router = APIRouter(prefix="/integrations/truckerpath", tags=["TruckerPath"])


class PostLoadRequest(BaseModel):
    company_id: Optional[str] = None
    contact_info: Dict[str, Any] = Field(default_factory=dict)
    shipment_info: Dict[str, Any] = Field(default_factory=dict)


def _provider_error_status(result: dict[str, Any]) -> int:
    if result.get("error") == "truckerpath_not_configured":
        return 503
    return int(result.get("status") or 502)


def _unwrap_provider_result(result: Any, default_error: str) -> dict[str, Any]:
    if isinstance(result, dict):
        if result.get("ok", True):
            return result
        raise HTTPException(
            status_code=_provider_error_status(result),
            detail=result.get("message") or result.get("error") or default_error,
        )
    return {"ok": True, "result": result}


async def _status_payload() -> dict[str, Any]:
    health = await TruckerPathService.ping()
    ok = bool(health.get("ok", False))
    return {
        "ok": ok,
        "provider": "truckerpath",
        "health": health,
    }


@router.get("/status")
async def status():
    return await _status_payload()


@compat_router.get("/status")
async def compat_status():
    return await _status_payload()


@compat_router.get("/ping")
async def compat_ping():
    return await _status_payload()


@router.get("/loads")
async def list_loads(
    limit: int = Query(10, ge=1, le=100),
    origin: Optional[str] = None,
    destination: Optional[str] = None,
    equipment: Optional[str] = None,
):
    filters = {"origin": origin, "destination": destination, "equipment": equipment}
    result = await TruckerPathService.list_loads(limit=limit, **{k: v for k, v in filters.items() if v})
    data = _unwrap_provider_result(result, "Failed to fetch loads")
    loads = list(data.get("loads") or [])
    return {
        "ok": True,
        "count": len(loads),
        "loads": loads,
        "filters": {k: v for k, v in filters.items() if v},
        "source": data.get("source"),
    }


@compat_router.get("/loads")
async def compat_list_loads(
    limit: int = Query(10, ge=1, le=100),
    company_id: Optional[str] = None,
    equipment: Optional[str] = None,
    origin: Optional[str] = None,
    destination: Optional[str] = None,
):
    del company_id
    return await list_loads(limit=limit, origin=origin, destination=destination, equipment=equipment)


@router.post("/post-load")
async def post_load(payload: PostLoadRequest = Body(...)):
    result = _unwrap_provider_result(
        await TruckerPathService.post_load(payload.model_dump()),
        "TruckerPath post failed",
    )
    try:
        await broadcast_event(channel="events.truckerpath.posted", payload={"result": result})
    except Exception:
        pass
    return {"ok": True, "result": result}


@compat_router.post("/load")
async def compat_post_load(payload: PostLoadRequest = Body(...)):
    return await post_load(payload)


@router.post("/company")
async def create_company(payload: dict[str, Any] = Body(...)):
    return _unwrap_provider_result(
        await TruckerPathService.create_company(payload),
        "Create company failed",
    )


@compat_router.post("/company")
async def compat_create_company(payload: dict[str, Any] = Body(...)):
    return await create_company(payload)


@router.post("/webhook/register")
async def register_webhook(payload: dict[str, Any] = Body(...)):
    return _unwrap_provider_result(
        await TruckerPathService.register_webhook(payload),
        "Register webhook failed",
    )


@compat_router.post("/webhook/register")
async def compat_register_webhook(payload: dict[str, Any] = Body(...)):
    return await register_webhook(payload)


@router.post("/webhook/add")
async def register_webhook_add(payload: dict[str, Any] = Body(...)):
    return _unwrap_provider_result(
        await TruckerPathService.register_webhook_add(payload),
        "Register webhook(add) failed",
    )


@compat_router.post("/webhook/add")
async def compat_register_webhook_add(payload: dict[str, Any] = Body(...)):
    return await register_webhook_add(payload)


@router.post("/tracking/create")
async def tracking_create(payload: dict[str, Any] = Body(...)):
    return _unwrap_provider_result(
        await TruckerPathService.tracking_create(payload),
        "Tracking create failed",
    )


@compat_router.post("/tracking/create")
async def compat_tracking_create(payload: dict[str, Any] = Body(...)):
    return await tracking_create(payload)


@router.post("/tracking/points")
async def push_tracking_points(payload: dict[str, Any] = Body(...)):
    return _unwrap_provider_result(
        await TruckerPathService.push_tracking_points(payload),
        "Push tracking points failed",
    )


@compat_router.post("/tracking/points")
async def compat_push_tracking_points(payload: dict[str, Any] = Body(...)):
    return await push_tracking_points(payload)
