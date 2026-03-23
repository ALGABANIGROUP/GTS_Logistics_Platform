from fastapi import APIRouter

router = APIRouter()

@router.get("/dashboard/summary")
async def get_dashboard_summary():
    return {
        "status": "ok",
        "total_shipments": 42,
        "active_drivers": 12,
        "pending_tasks": 3,
        "last_sync": "2025-05-02T15:00:00Z"
    }
