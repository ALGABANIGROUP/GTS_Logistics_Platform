# backend/tools/open_web_leads/scheduler.py

from typing import Callable, Awaitable

from sqlalchemy.ext.asyncio import AsyncSession

from .service import scan_open_web_leads


async def run_open_web_leads_scan(get_db_session: Callable[[], Awaitable[AsyncSession]]) -> None:
    """
    This function is triggered by the scheduler (e.g., every 30 minutes).
    get_db_session: A callable that returns an AsyncSession instance (wrapped according to your DB setup).
    """
    db = await get_db_session()
    try:
        total_found, total_created = await scan_open_web_leads(db)
        # Log output:
        print(f"[open_web_leads] found={total_found}, created={total_created}")
    finally:
        await db.close()
