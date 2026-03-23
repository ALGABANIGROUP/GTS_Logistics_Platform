from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from backend.security.auth import require_roles
from backend.services.llm.openai_client import get_openai_client

router = APIRouter(prefix="/ops", tags=["ops"])


@router.get("/llm/ping")
async def llm_ping(user=Depends(require_roles(["admin", "super_admin"]))):
    client = get_openai_client()
    if not client.is_available:
        raise HTTPException(status_code=503, detail="LLM client unavailable")
    healthy = await client.health_check()
    return {"ok": healthy, "available": client.is_available}
