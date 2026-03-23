from __future__ import annotations

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, Query, Body
from pydantic import BaseModel, Field

# Provider registry (dynamic import to support multiple layouts)
try:
    from backend.integrations.loadboards.registry import get_provider  # type: ignore
except Exception:
    try:
        from integrations.loadboards.registry import get_provider  # type: ignore
    except Exception:
        get_provider = None  # type: ignore

# Optional: WebSocket broadcast (best-effort)
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

# ------------------------- Models -------------------------
class LoadFilters(BaseModel):
    origin: Optional[str] = None
    destination: Optional[str] = None
    equipment: Optional[str] = None

class PostLoadRequest(BaseModel):
    # Minimal viable payload for posting a load
    company_id: Optional[str] = None
    contact_info: Dict[str, Any] = Field(default_factory=dict)
    shipment_info: Dict[str, Any] = Field(default_factory=dict)

# ------------------------- Helpers -------------------------
def _get_provider_or_503():
    if get_provider is None:
        raise HTTPException(status_code=503, detail="Provider registry not available")
    try:
        ProviderClass = get_provider("truckerpath")
        return ProviderClass()
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"TruckerPath provider unavailable: {e}")

async def _maybe_await(obj):
    try:
        import inspect
        if inspect.isawaitable(obj):
            return await obj
    except Exception:
        pass
    return obj

# ------------------------- Routes -------------------------
@router.get("/status")
async def status():
    provider = _get_provider_or_503()
    try:
        health = await _maybe_await(getattr(provider, "health")()) if hasattr(provider, "health") else {"ok": True}
        ok = bool(health.get("ok", True)) if isinstance(health, dict) else True
        return {"ok": ok, "provider": "truckerpath", "health": health}
    except Exception as e:
        return {"ok": False, "provider": "truckerpath", "error": str(e)}

@router.get("/loads")
async def list_loads(
    limit: int = Query(10, ge=1, le=100),
    origin: Optional[str] = None,
    destination: Optional[str] = None,
    equipment: Optional[str] = None,
):
    provider = _get_provider_or_503()
    filters = {"origin": origin, "destination": destination, "equipment": equipment}
    try:
        res = await _maybe_await(provider.list_loads(limit=limit, **{k: v for k, v in filters.items() if v}))
        # Expected provider response: {"ok": True, "loads": [...]} OR a plain list
        if isinstance(res, dict) and "loads" in res:
            loads = list(res.get("loads") or [])
        elif isinstance(res, list):
            loads = res
        else:
            loads = []
        return {"ok": True, "count": len(loads), "loads": loads, "filters": {k: v for k, v in filters.items() if v}}
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Failed to fetch loads: {e}")

@router.post("/post-load")
async def post_load(payload: PostLoadRequest = Body(...)):
    provider = _get_provider_or_503()
    try:
        result = await _maybe_await(provider.post_load(payload.dict()))
        ok = bool(result.get("ok", False)) if isinstance(result, dict) else False
        if ok:
            try:
                await broadcast_event(channel="events.truckerpath.posted", payload={"result": result})
            except Exception:
                pass
            return {"ok": True, "result": result}
        raise HTTPException(status_code=502, detail=f"TruckerPath returned failure: {result}")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Failed to post load: {e}")

