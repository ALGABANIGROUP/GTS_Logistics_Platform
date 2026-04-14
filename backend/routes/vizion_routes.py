from fastapi import APIRouter

# Lazy import VIZION router - avoid any backend imports at module level
def get_vizion_router():
    try:
        # Try to import VIZION API - this will fail if backend.database is not available
        import sys
        if 'backend' in sys.modules:
            from backend.vizion_api import router as vizion_api_router
            return vizion_api_router
        else:
            raise ImportError("backend module not available")
    except ImportError as e:
        # Fallback router if VIZION is not available
        router = APIRouter(prefix="/vizion", tags=["VIZION"])
        
        @router.get("/status")
        async def vizion_status():
            return {"ok": True, "vizion": "disabled", "error": str(e)}
        
        @router.get("/board")
        async def vizion_board():
            return {"ok": True, "tasks": [], "vizion": "disabled"}
        
        return router

# Expose a usable router attribute for main.py import helpers.
router = get_vizion_router()
