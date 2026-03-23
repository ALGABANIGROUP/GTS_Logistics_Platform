"""
System Switcher Module
Allows users to navigate between GTS and TMS systems
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from backend.auth.unified_auth import unified_auth
from backend.database.session import wrap_session_factory
from backend.models.unified_models import UserSystemsAccess
from sqlalchemy.ext.asyncio import AsyncSession
from backend.database.config import get_sessionmaker, init_engines
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/systems", tags=["System Switcher"])


# Database dependency
async def get_db():
    """Get database session"""
    
    init_engines()
    maker = get_sessionmaker()
    if maker is None:
        raise RuntimeError("Database not initialized")
    
    async with maker() as session:
        yield session


@router.get("/available", summary="Get available systems")
async def get_available_systems(
    request: Request,
    session: AsyncSession = Depends(get_db)
):
    """
    Return all systems available for the current authenticated user.
    """
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization token is required"
        )
    
    payload = unified_auth.verify_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    user_systems = payload.get("systems", [])
    
    # Build UI-friendly system metadata
    enriched_systems = []
    for system in user_systems:
        system_info = {
            "type": system.get("system_type"),
            "name": "Gabani Transport Solutions (GTS)" if system.get("system_type") == "gts_main" else "Transport Management System (TMS)",
            "description": "Core GTS operations dashboard" if system.get("system_type") == "gts_main" else "TMS shipment and operations workspace",
            "icon": "🏢" if system.get("system_type") == "gts_main" else "🚚",
            "access_level": system.get("access_level"),
            "subscription_plan": system.get("subscription_plan"),
            "url": f"/system/{system.get('system_type')}/dashboard"
        }
        enriched_systems.append(system_info)
    
    return {
        "status": "success",
        "systems": enriched_systems,
        "current_system": payload.get("current_system"),
        "total_systems": len(enriched_systems)
    }


@router.post("/switch", summary="Switch active system")
async def switch_system(
    request: Request,
    body: dict,
    session: AsyncSession = Depends(get_db)
):
    """
    Switch the currently active user system and return a refreshed token.
    
    Body:
    {
        "new_system": "tms" or "gts_main"
    }
    """
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    new_system = body.get("new_system")
    
    if not token or not new_system:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token and target system are required"
        )
    
    # Issue a new token with updated current_system
    new_token = unified_auth.switch_system(token, new_system)
    
    if not new_token:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"User does not have access to system '{new_system}'"
        )
    
    logger.info(f"System switched successfully: {new_system}")
    
    return {
        "status": "success",
        "message": f"Active system switched to {new_system}",
        "token": new_token,
        "current_system": new_system
    }


@router.get("/selector", summary="Get system selector UI data")
async def get_system_selector_data(
    request: Request,
    session: AsyncSession = Depends(get_db)
):
    """
    Return card metadata used by the frontend system selector.
    """
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    
    payload = unified_auth.verify_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    systems = payload.get("systems", [])
    is_admin = any(s.get("access_level") in ["admin", "super_admin"] for s in systems)
    
    system_cards = [
        {
            "id": "gts_main",
            "title": "🏢 Gabani Transport Solutions (GTS)",
            "description": "Freight platform and business operations",
            "color": "blue",
            "icon": "🏢",
            "available": any(s.get("system_type") == "gts_main" for s in systems)
        },
        {
            "id": "tms",
            "title": "🚚 Transport Management System (TMS)",
            "description": "Shipment execution, dispatch, and tracking",
            "color": "green",
            "icon": "🚚",
            "available": any(s.get("system_type") == "tms" for s in systems)
        }
    ]
    
    # Add admin tools card when user has admin-level access
    if is_admin:
        system_cards.append({
            "id": "admin",
            "title": "⚙️ Administration",
            "description": "Admin controls, governance, and platform settings",
            "color": "purple",
            "icon": "⚙️",
            "available": True,
            "admin_only": True
        })
    
    return {
        "status": "success",
        "user": {
            "name": payload.get("email"),
            "is_admin": is_admin
        },
        "systems": system_cards,
        "current_system": payload.get("current_system")
    }


@router.get("/current", summary="Get current active system")
async def get_current_system(request: Request):
    """Return the currently active system for the authenticated user."""
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    
    payload = unified_auth.verify_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    current = payload.get("current_system")
    
    return {
        "status": "success",
        "current_system": current,
        "system_name": "Gabani Transport Solutions (GTS)" if current == "gts_main" else "Transport Management System (TMS)" if current == "tms" else "Unknown system"
    }

