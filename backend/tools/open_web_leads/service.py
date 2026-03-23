# backend/tools/open_web_leads/service.py

from typing import List, Tuple

from sqlalchemy.ext.asyncio import AsyncSession

from .schemas import OpenWebLeadCreate
from .crud import create_lead_if_not_exists
from .adapters.demo_acme import DemoAcmeAdapter


async def scan_open_web_leads(db: AsyncSession) -> Tuple[int, int]:
    """
    Returns a tuple (total_found, total_created)
    """
    adapters = [
        DemoAcmeAdapter(),
        # TODO: Add real adapters here
    ]

    total_found = 0
    total_created = 0

    for adapter in adapters:
        leads: List[OpenWebLeadCreate] = await adapter.fetch_leads()
        total_found += len(leads)

        for lead in leads:
            _, created = await create_lead_if_not_exists(db, lead)
            if created:
                total_created += 1

    return total_found, total_created
