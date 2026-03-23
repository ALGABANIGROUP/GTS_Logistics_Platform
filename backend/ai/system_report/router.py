# backend/ai/system_report/router.py

from fastapi import APIRouter, Depends
from backend.security.auth import require_roles
from .generator import generate_system_report

router = APIRouter(
    prefix="/ai/system-report",
    tags=["AI System Report"],
    dependencies=[Depends(require_roles(["manager", "admin"]))]
)


@router.get("/")
async def get_report():
    """
    Returns the full AI-generated system report (JSON).
    """
    return await generate_system_report()
