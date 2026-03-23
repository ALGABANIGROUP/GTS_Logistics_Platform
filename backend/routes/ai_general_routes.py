from __future__ import annotations

from datetime import datetime
from typing import Any, Dict

from fastapi import APIRouter

router = APIRouter(prefix="/ai/general", tags=["AI General"])


@router.get("/status")
async def ai_general_status() -> Dict[str, Any]:
    return {
        "ok": True,
        "module": "ai_general_routes",
        "generated_at": datetime.utcnow().isoformat() + "Z",
    }


__all__ = ["router"]
print("[ai_general_routes] router loaded")
