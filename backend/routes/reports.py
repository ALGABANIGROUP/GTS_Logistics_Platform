from fastapi import APIRouter

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("/")
async def list_reports():
    return {"ok": True, "reports": []}


__all__ = ["router"]
