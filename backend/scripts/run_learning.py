#!/usr/bin/env python
from __future__ import annotations

import asyncio
import sys
from pathlib import Path
from typing import List

import httpx

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.services.learning_bootstrap import DEFAULT_LEARNING_BOTS

BASE_URL = "http://127.0.0.1:8000"


async def trigger_learning(client: httpx.AsyncClient, bot_id: str) -> tuple[str, bool]:
    try:
        response = await client.post(f"{BASE_URL}/ai/learning/trigger/{bot_id}", timeout=30.0)
        response.raise_for_status()
        return bot_id, True
    except Exception:
        return bot_id, False


async def main() -> None:
    bot_ids: List[str] = [item["bot_id"] for item in DEFAULT_LEARNING_BOTS]
    async with httpx.AsyncClient() as client:
        tasks = [trigger_learning(client, bot_id) for bot_id in bot_ids]
        results = await asyncio.gather(*tasks)

        stats_response = await client.get(f"{BASE_URL}/ai/learning/stats", timeout=30.0)
        stats_response.raise_for_status()
        stats_payload = stats_response.json().get("learning_stats", {})

    success_count = sum(1 for _, ok in results if ok)
    print(f"Triggered learning for {success_count}/{len(bot_ids)} bots")
    print(f"total_bots_registered: {stats_payload.get('total_bots_registered', 0)}")
    print(f"enabled_bots: {stats_payload.get('enabled_bots', 0)}")
    print(f"total_samples_collected: {stats_payload.get('total_samples_collected', 0)}")
    print(f"total_adaptations: {stats_payload.get('total_adaptations', 0)}")


if __name__ == "__main__":
    asyncio.run(main())
