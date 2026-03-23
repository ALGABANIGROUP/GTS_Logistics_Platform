from fastapi import APIRouter

router = APIRouter(prefix="/finance", tags=["finance"])

@router.get("/ping")
async def ping():
    return {"ok": True, "area": "finance"}
