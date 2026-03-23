from __future__ import annotations

import asyncio
import json
import random

import psutil  # type: ignore
from fastapi import APIRouter, WebSocket

router = APIRouter()


@router.websocket("/ws/system/admin/monitor")
async def system_admin_monitor_websocket(websocket: WebSocket):
    await websocket.accept()

    try:
        while True:
            cpu = psutil.cpu_percent()
            memory = psutil.virtual_memory().percent
            disk = psutil.disk_usage("/").percent
            requests_today = random.randint(100, 1000)
            failed_logins = random.randint(0, 10)

            warnings = []
            if cpu > 80:
                warnings.append(f"High CPU usage: {cpu}%")
            if memory > 80:
                warnings.append(f"High Memory usage: {memory}%")
            if disk > 85:
                warnings.append(f"High Disk usage: {disk}%")

            payload = {
                "cpu_usage": cpu,
                "memory_usage": memory,
                "disk_usage": disk,
                "requests_today": requests_today,
                "failed_logins": failed_logins,
                "warnings": warnings,
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
