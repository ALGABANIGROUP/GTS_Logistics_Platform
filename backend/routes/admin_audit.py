from __future__ import annotations

from typing import Any, Dict, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, Query

from backend.security.auth import get_current_user

router = APIRouter(prefix="/api/v1/admin/audit", tags=["admin", "audit"])


@router.get("")
async def list_audit_logs(
    action: Optional[str] = None,
    severity: Optional[str] = None,
    start_at: Optional[str] = Query(None, alias="start_at"),
    end_at: Optional[str] = Query(None, alias="end_at"),
    limit: int = Query(50, le=200),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    # Compatibility endpoint for admin audit logs UI
    return {
        "source": "security_bot",
        "timestamp": datetime.utcnow().isoformat(),
        "filters_applied": {
            "action": action,
            "severity": severity,
            "start_at": start_at,
            "end_at": end_at,
            "limit": limit,
        },
        "logs": [],
    }
