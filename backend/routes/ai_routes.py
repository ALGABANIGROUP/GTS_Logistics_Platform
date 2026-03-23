from fastapi import APIRouter, HTTPException
from backend.ai.ai_operations_manager import AIOperationsManager

router = APIRouter(prefix="/ai", tags=["ai-operations"])

ai_manager = AIOperationsManager()


@router.get("/operations/status")
async def operations_status():
    return await ai_manager.monitor_mock_truckerpath()


@router.post("/analyze-shipment")
async def analyze_shipment(payload: dict):
    shipment_id = payload.get("id")
    if not shipment_id:
        raise HTTPException(status_code=400, detail="Missing shipment id")

    return await ai_manager.analyze_shipment_with_ai(shipment_id)


@router.get("/daily-report")
async def daily_report():
    return await ai_manager.generate_daily_report()


@router.get("/test-integration")
async def test_ai_integration():
    return {
        "openai_available": bool(
            getattr(ai_manager, "OPENAI_AVAILABLE", False)
        ),
        "status": "ok"
    }
