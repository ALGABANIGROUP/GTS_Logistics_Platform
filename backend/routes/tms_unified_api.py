"""
FastAPI router for the new TMS Unified API (adapts Flask Blueprint logic)
"""
from fastapi import APIRouter, HTTPException, Request, Body
from fastapi.responses import JSONResponse
from backend.tms.core import TMSCore

router = APIRouter(prefix="/api/v1/tms-unified", tags=["TMS Unified"])
tms_core = TMSCore()

@router.get("/shipment/{shipment_id}")
async def get_unified_shipment(shipment_id: str):
    try:
        shipment_data = tms_core.get_unified_shipment_view(shipment_id)
        return {"success": True, "data": shipment_data, "message": "Shipment data retrieved from all sources"}
    except Exception as e:
        raise HTTPException(status_code=500, detail={"success": False, "error": str(e), "message": "Failed to retrieve unified shipment data"})

@router.get("/shipments/status/{status}")
async def get_shipments_by_status(status: str):
    try:
        # Placeholder: replace with real dispatch integration
        dispatch_shipments = []
        enhanced_shipments = []
        for shipment in dispatch_shipments:
            enhanced = {
                **shipment,
                'driver_info': tms_core.get_driver_for_shipment(shipment['id']),
                'tracking_info': tms_core.get_live_tracking(shipment['id']),
                'partner_info': tms_core.get_partner_info(shipment['id'])
            }
            enhanced_shipments.append(enhanced)
        return {"success": True, "count": len(enhanced_shipments), "data": enhanced_shipments}
    except Exception as e:
        raise HTTPException(status_code=500, detail={"success": False, "error": str(e)})

@router.get("/dashboard/overview")
async def get_tms_dashboard():
    try:
        stats = {
            'total_shipments': tms_core.get_total_shipments(),
            'active_shipments': tms_core.get_active_shipments(),
            'available_drivers': tms_core.get_available_drivers(),
            'delivered_today': tms_core.get_delivered_today(),
            'revenue_today': tms_core.get_revenue_today(),
            'alerts': tms_core.get_system_alerts()
        }
        return {"success": True, "dashboard": stats, "timestamp": tms_core.get_current_time()}
    except Exception as e:
        raise HTTPException(status_code=500, detail={"success": False, "error": str(e)})

@router.get("/shipment/{shipment_id}/lifecycle")
async def get_shipment_lifecycle(shipment_id: str):
    try:
        lifecycle = tms_core.get_shipment_lifecycle(shipment_id)
        return {"success": True, "shipment_id": shipment_id, "lifecycle": lifecycle}
    except Exception as e:
        raise HTTPException(status_code=500, detail={"success": False, "error": str(e)})

@router.post("/ai/suggestions")
async def get_ai_suggestions(request: Request, body: dict = Body(...)):
    try:
        shipment_id = body.get('shipment_id')
        suggestions = tms_core.get_ai_suggestions(shipment_id)
        return {"success": True, "suggestions": suggestions, "generated_by": "GTS AI Engine"}
    except Exception as e:
        raise HTTPException(status_code=500, detail={"success": False, "error": str(e)})



