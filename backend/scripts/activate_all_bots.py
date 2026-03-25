"""
Script to activate all bots in the database
Run: python -m backend.scripts.activate_all_bots
"""

import asyncio
import logging
from datetime import datetime
from sqlalchemy import update

from backend.database.session import get_async_session
from backend.models.subscription import AIBot

logger = logging.getLogger(__name__)

async def activate_all_bots():
    """Set all bots status to active"""
    try:
        async for session in get_async_session():
            # Update all bots to active
            result = await session.execute(
                update(AIBot).values(status='active', updated_at=datetime.now())
            )
            await session.commit()
            
            logger.info(f"Activated {result.rowcount} bots in database")
            return {"success": True, "activated": result.rowcount}
    except Exception as e:
        logger.error(f"Failed to activate bots: {e}")
        return {"success": False, "error": str(e)}

async def get_bot_statuses():
    """Get all bot statuses from database"""
    try:
        from sqlalchemy import select
        async for session in get_async_session():
            result = await session.execute(
                select(AIBot.id, AIBot.name, AIBot.status)
            )
            bots = result.all()
            return {
                "success": True,
                "bots": [{"id": b.id, "name": b.name, "status": b.status} for b in bots]
            }
    except Exception as e:
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    asyncio.run(activate_all_bots())