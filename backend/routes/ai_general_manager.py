# backend/routes/ai_general_manager.py

from fastapi import APIRouter

router = APIRouter(
    prefix="/ai/general-manager",
    tags=["ai-general-manager"],
)


@router.get("/report")
async def get_general_manager_report():
    """
    Static AI General Manager report in the same shape as the frontend DEMO_REPORT.
    Later we'll connect it to real data and actual AI.
    """
    return {
        "title": "AI General Manager – Backend Report",
        "backend": {
            "status": "healthy",
            "details": [
                "Backend /healthz returns ok: true.",
                "Finance and Documents services are loaded and responding.",
                "Auth /auth/dev-token is issuing valid JWT tokens (role=admin).",
            ],
        },
        "frontend": {
            "status": "partially_connected",
            "details": [
                "Vite frontend is running on http://localhost:5175.",
                "Some API calls may still be pointing to port 5175 instead of backend 8000.",
                "WebSocket and Shipments endpoints should use VITE_API_BASE_URL / VITE_WS_BASE_URL.",
            ],
        },
        "ai_bots": {
            "status": "registered",
            "details": [
                "AI core bots registered on startup (general_manager, freight_broker, operations_manager, finance_bot, documents_manager, maintenance_dev).",
                "This endpoint is currently returning a static summary (no real AI pipeline wired yet).",
            ],
        },
        "next_actions": [
            "Refine frontend API URLs to all use VITE_API_BASE_URL / VITE_WS_BASE_URL.",
            "Wire this endpoint to the actual GeneralManagerBot for dynamic analysis.",
            "Gradually phase out the trial fallback in the frontend once this is stable.",
        ],
    }
