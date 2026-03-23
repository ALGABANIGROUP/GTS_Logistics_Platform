from __future__ import annotations

import asyncio
import json
import random
from datetime import datetime

from fastapi import APIRouter, WebSocket

router = APIRouter()


@router.websocket("/ws/system/monitor")
async def websocket_monitor(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            payload = {
                "uptime": f"{random.randint(1, 24)} hrs",
                "cpu_usage": f"{random.randint(5, 90)}%",
                "memory_usage": f"{random.randint(10, 95)}%",
                "active_bots": random.randint(5, 12),
                "timestamp": datetime.utcnow().isoformat() + "Z",
            }
            await websocket.send_text(json.dumps(payload))
            await asyncio.sleep(5)
    except Exception:
        pass
    finally:
        try:
            await websocket.close()
        except Exception:
            pass
