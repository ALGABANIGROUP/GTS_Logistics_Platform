from fastapi import APIRouter

router = APIRouter(prefix="/vizion", tags=["VIZION"])

@router.get("/status")
async def vizion_status():
    return {"ok": True, "vizion": "disabled or external"}
