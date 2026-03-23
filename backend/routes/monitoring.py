from __future__ import annotations

from fastapi import APIRouter

from backend.services.email_scheduler import is_polling_running, last_poll_cycle_at

router = APIRouter(prefix="/api/v1", tags=["monitoring"])


@router.get("/email/status")
async def get_email_status() -> dict:
    return {
        "is_running": is_polling_running(),
        "status": "active" if is_polling_running() else "inactive",
        "last_cycle_at": last_poll_cycle_at(),
    }
