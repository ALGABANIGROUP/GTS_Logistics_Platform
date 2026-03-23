from __future__ import annotations

"""
FastAPI router for the TMS without new bots.
English-only code. Admin/manager gating for mutating operations.
"""

from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.tms.core.tms_core import tms_core

router = APIRouter()


class ExecuteRequest(BaseModel):
    bot: str = Field(..., description="Existing bot name to execute")
    action: str = Field(..., description="Action to run on the bot")
    payload: Optional[Dict[str, Any]] = Field(default=None, description="Optional parameters")


@router.get("/status")
async def tms_status():
    return {"ok": True, "system": "tms", "message": "TMS routes operational"}


@router.post("/execute")
async def tms_execute(req: ExecuteRequest):
    """
    Execute an action on an existing bot via TMS core.
    Manager or Admin required (enforced at mount level).
    """
    if not req.bot or not req.action:
        raise HTTPException(status_code=400, detail={"error": "invalid_request", "message": "bot and action are required"})
    return await tms_core.execute(req.bot, req.action, req.payload or {})


class ShipmentAction(BaseModel):
    shipment_id: str = Field(..., description="Shipment identifier")
    action: str = Field(..., description="Lifecycle action like 'create', 'dispatch', 'track', 'close'")
    data: Optional[Dict[str, Any]] = Field(default=None)


@router.post("/shipments/lifecycle")
async def tms_shipment_lifecycle(req: ShipmentAction):
    """
    Delegate shipment lifecycle actions to appropriate bots.
    - create/dispatch: freight_broker
    - track: customer_service
    - close: documents_manager
    """
    mapping = {
        "create": ("freight_broker", "create_shipment"),
        "dispatch": ("freight_broker", "dispatch"),
        "track": ("customer_service", "track_shipment"),
        "close": ("documents_manager", "close_shipment"),
    }
    if req.action not in mapping:
        raise HTTPException(status_code=400, detail={"error": "unsupported_action", "message": f"Unsupported action: {req.action}"})

    bot, action = mapping[req.action]
    payload = {"shipment_id": req.shipment_id, **(req.data or {})}
    return await tms_core.execute(bot, action, payload)


@router.get("/bots/available")
async def tms_bots_available():
    """
    Return a list of available existing bots exposed via TMS.
    """
    bots = [
        {"name": "freight_broker", "display": "AI Freight Broker"},
        {"name": "finance_bot", "display": "AI Finance Bot"},
        {"name": "documents_manager", "display": "AI Documents Manager"},
        {"name": "customer_service", "display": "AI Customer Service"},
        {"name": "sales_team", "display": "AI Sales Team"},
        {"name": "mapleload_canada", "display": "MapleLoad Canada"},
    ]
    return {"ok": True, "bots": bots}
