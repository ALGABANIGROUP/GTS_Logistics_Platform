# backend/ai/system_report/scheduler.py

import asyncio
import httpx
from backend.security.auth import create_access_token


async def system_report_scheduler_loop():
    """
    Runs weekly (or daily) to generate the AI system report and send/store it.
    """
    while True:
        try:
            token = create_access_token(
                {"sub": "scheduler", "role": "admin"},
                expires_minutes=1440
            )
            headers = {"Authorization": f"Bearer {token}"}

            # Call the report endpoint internally
            async with httpx.AsyncClient(timeout=30) as client:
                await client.get(
                    "http://127.0.0.1:8000/ai/system-report/",
                    headers=headers
                )
        except Exception as e:
            print(f"[system_report_scheduler] ERROR: {e}")

        # Run every 24 hours (86400 seconds)
        await asyncio.sleep(86400)
