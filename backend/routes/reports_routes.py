from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from backend.utils.safe_execute import safe_execute

try:
    from backend.database.session import get_async_session  # type: ignore
except Exception:
    from backend.database.session import get_async_session  # type: ignore


router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("/health")
async def reports_health(db: AsyncSession = Depends(get_async_session)) -> Dict[str, Any]:
    row = (await safe_execute(db, text("SELECT 1"))).first()
    return {"ok": True, "db_ok": bool(row and row[0] == 1)}


@router.get("/weekly")
async def weekly_report(days: int = 7) -> Dict[str, Any]:
    days = max(1, min(int(days), 90))
    return {
        "ok": True,
        "period": f"Last {days} days",
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "summary": {
            "note": "Placeholder weekly report endpoint. Replace with real data later.",
        },
    }


__all__ = ["router"]
print("[reports_routes] router loaded")

