from __future__ import annotations

import asyncio
from datetime import datetime
from typing import Callable, List
import logging

from .law_manager import TransportLawManager


class LawUpdateScheduler:
    def __init__(self, law_manager: TransportLawManager) -> None:
        self.law_manager = law_manager
        self.logger = logging.getLogger(__name__)
        self.update_callbacks: List[Callable] = []

    async def start_periodic_check(self, interval_hours: int = 24) -> None:
        self.logger.info("Starting periodic law update checker...")

        while True:
            try:
                await self.check_and_notify()
                await asyncio.sleep(interval_hours * 3600)
            except Exception as exc:
                self.logger.error("Error in periodic check: %s", exc)
                await asyncio.sleep(3600)

    async def check_and_notify(self) -> None:
        laws_due = await self.law_manager.check_for_updates()

        if not laws_due:
            self.logger.debug("No laws due for update")
            return

        self.logger.info("Found %s laws due for update", len(laws_due))

        for law in laws_due:
            message = {
                "law_id": law.id,
                "country": law.country_name,
                "title": law.title,
                "due_date": law.next_update_due,
                "priority": "HIGH"
                if law.safety_standards in ["high", "critical"]
                else "MEDIUM",
            }

            for callback in self.update_callbacks:
                try:
                    await callback(message)
                except Exception as exc:
                    self.logger.error("Callback error: %s", exc)

    def register_callback(self, callback: Callable) -> None:
        self.update_callbacks.append(callback)

    def get_update_schedule(self) -> List[dict]:
        all_laws = list(self.law_manager.laws.values())
        upcoming = []

        for law in all_laws:
            days_until = (law.next_update_due - datetime.now()).days
            if days_until <= 90:
                upcoming.append(
                    {
                        "law": law,
                        "days_until": days_until,
                        "priority": "URGENT" if days_until <= 30 else "UPCOMING",
                    }
                )

        return sorted(upcoming, key=lambda x: x["days_until"])
