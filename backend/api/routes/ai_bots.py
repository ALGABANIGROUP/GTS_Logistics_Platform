from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from backend.bots import BOTS_REGISTRY

router = APIRouter(prefix="/ai/bots", tags=["AI Bots"])

@router.get("/all")
async def get_all_bots():
    """
    Returns the complete list of available AI Bots (Expects 21 bots when fully loaded).
    """
    bots_data = []
    for bot_id, bot_class in BOTS_REGISTRY.items():
        # Extract name and docstring safely
        bot_name = getattr(bot_class, "__name__", bot_id.replace("_", " ").title())
        description = (bot_class.__doc__ or "").strip().split('\n')[0] if bot_class.__doc__ else "GTS AI Bot"
        
        bots_data.append({
            "id": bot_id,
            "name": bot_name,
            "description": description,
            "status": "active",
            "version": "1.0.0"
        })
    
    return {
        "count": len(bots_data),
        "system_status": "operational",
        "bots": bots_data
    }

@router.get("")
async def get_main_bots():
    """
    Returns the 3 main ecosystem bots: General Manager, Freight Broker, Operations Manager.
    """
    main_keys = ["general_manager", "freight_broker", "operations_manager"]
    bots_data = []
    
    for key in main_keys:
        if key in BOTS_REGISTRY:
            bot_class = BOTS_REGISTRY[key]
            bots_data.append({
                "id": key,
                "name": getattr(bot_class, "__name__", key),
                "role": "core_system"
            })
            
    return {"count": len(bots_data), "bots": bots_data}

@router.get("/current-user/available")
async def get_user_bots():
    """
    Returns bots available to the current user context.
    """
    # TODO: Filter based on user roles (Admin/Broker/Driver)
    # For now, return all bots as available
    return {
        "user_context": "authenticated",
        "available_bots": [k for k in BOTS_REGISTRY.keys()]
    }