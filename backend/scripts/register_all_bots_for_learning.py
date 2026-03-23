#!/usr/bin/env python
from __future__ import annotations

import asyncio
import sys
from pathlib import Path
from typing import Any, Dict, List

import httpx

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.services.learning_bootstrap import DEFAULT_LEARNING_BOTS

BASE_URL = "http://127.0.0.1:8000"


async def register_bot(client: httpx.AsyncClient, bot: Dict[str, Any]) -> Dict[str, Any]:
    try:
        response = await client.post(
            f"{BASE_URL}/ai/learning/register",
            params={
                "bot_id": bot["bot_id"],
                "bot_name": bot["bot_name"],
                "enabled": str(bot["enabled"]).lower(),
                "frequency": bot["frequency"],
                "intensity": bot["intensity"],
            },
            timeout=30.0,
        )
        response.raise_for_status()
        return {"bot_id": bot["bot_id"], "status": "success", "payload": response.json()}
    except Exception as exc:
        return {"bot_id": bot["bot_id"], "status": "error", "error": str(exc)}


async def main() -> None:
    print("=" * 60)
    print("Registering all bots for learning")
    print("=" * 60)

    async with httpx.AsyncClient() as client:
        results: List[Dict[str, Any]] = []
        for index, bot in enumerate(DEFAULT_LEARNING_BOTS, start=1):
            print(f"[{index}/{len(DEFAULT_LEARNING_BOTS)}] {bot['bot_name']} ...")
            result = await register_bot(client, bot)
            results.append(result)
            if result["status"] == "success":
                print("   OK")
            else:
                print(f"   ERROR: {result['error']}")
            await asyncio.sleep(0.1)

        stats_response = await client.get(f"{BASE_URL}/ai/learning/stats", timeout=30.0)
        stats_response.raise_for_status()
        stats_payload = stats_response.json()
        learning_stats = stats_payload.get("learning_stats", {})

    success_count = sum(1 for item in results if item["status"] == "success")
    error_count = sum(1 for item in results if item["status"] == "error")

    print()
    print("=" * 60)
    print("Summary")
    print("=" * 60)
    print(f"Registered successfully: {success_count}")
    print(f"Failed: {error_count}")
    print(f"total_bots_registered: {learning_stats.get('total_bots_registered', 0)}")
    print(f"enabled_bots: {learning_stats.get('enabled_bots', 0)}")
    print(f"total_samples_collected: {learning_stats.get('total_samples_collected', 0)}")
    print(f"total_adaptations: {learning_stats.get('total_adaptations', 0)}")

    if error_count:
        print("\nFailed bots:")
        for item in results:
            if item["status"] == "error":
                print(f"- {item['bot_id']}: {item['error']}")


if __name__ == "__main__":
    asyncio.run(main())
