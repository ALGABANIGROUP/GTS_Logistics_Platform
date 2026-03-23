from fastapi import APIRouter, Depends

from backend.security.access_context import require_feature, require_module

router = APIRouter(prefix="/loadboards", tags=["Loadboards"])


@router.get("/", dependencies=[Depends(require_module("loadboard")), Depends(require_feature("loadboard.core"))])
async def list_boards():
    return {"ok": True, "boards": []}
