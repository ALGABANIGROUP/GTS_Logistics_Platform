# backend/routes/bots_mock_api.py
"""Mock Bots API for Bot Operating System"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from datetime import datetime
from typing import Dict, Any, Optional

from backend.database.session import get_async_session

router = APIRouter(prefix="/api/v1/bots", tags=["Bots"])


class BotStatsResponse(BaseModel):
    total_runs: int
    by_status: Dict[str, int]
    human_commands: int
    active_bots: int


MOCK_BOTS = [
    {
        "bot_name": "AI General Manager",
        "automation_level": 3,
        "status": "idle",
        "enabled": True,
        "last_run": {
            "status": "completed",
            "started_at": "2025-02-05T10:30:00Z",
            "completed_at": "2025-02-05T10:45:00Z",
        },
    },
    {
        "bot_name": "Freight Broker Bot",
        "automation_level": 4,
        "status": "running",
        "enabled": True,
        "last_run": {
            "status": "completed",
            "started_at": "2025-02-05T11:00:00Z",
            "completed_at": "2025-02-05T11:15:00Z",
        },
    },
    {
        "bot_name": "AI Finance Bot",
        "automation_level": 2,
        "status": "idle",
        "enabled": True,
        "last_run": {
            "status": "completed",
            "started_at": "2025-02-05T09:00:00Z",
            "completed_at": "2025-02-05T09:20:00Z",
        },
    },
    {
        "bot_name": "Safety Manager Bot",
        "automation_level": 3,
        "status": "idle",
        "enabled": False,
        "last_run": None,
    },
    {
        "bot_name": "Email Bot",
        "automation_level": 2,
        "status": "running",
        "enabled": True,
        "last_run": {
            "status": "completed",
            "started_at": "2025-02-05T11:30:00Z",
            "completed_at": "2025-02-05T11:35:00Z",
        },
    },
]

MOCK_EXECUTION_HISTORY = [
    {
        "id": 1,
        "bot": "AI General Manager",
        "task": "Daily Report Generation",
        "status": "completed",
        "started": "2025-02-05T10:30:00Z",
        "error": None,
    },
    {
        "id": 2,
        "bot": "Freight Broker Bot",
        "task": "Load Optimization",
        "status": "completed",
        "started": "2025-02-05T11:00:00Z",
        "error": None,
    },
    {
        "id": 3,
        "bot": "AI Finance Bot",
        "task": "Invoice Processing",
        "status": "completed",
        "started": "2025-02-05T09:00:00Z",
        "error": None,
    },
    {
        "id": 4,
        "bot": "Email Bot",
        "task": "Send Daily Digest",
        "status": "completed",
        "started": "2025-02-05T11:30:00Z",
        "error": None,
    },
    {
        "id": 5,
        "bot": "Freight Broker Bot",
        "task": "Market Analysis",
        "status": "failed",
        "started": "2025-02-04T15:00:00Z",
        "error": "Database connection timeout",
    },
]


@router.get("/mock", response_model=Dict[str, Any])
async def get_bots(session: AsyncSession = Depends(get_async_session)):
    return {"ok": True, "bots": MOCK_BOTS}


@router.get("/mock/stats", response_model=BotStatsResponse)
async def get_bot_stats(session: AsyncSession = Depends(get_async_session)):
    history = MOCK_EXECUTION_HISTORY
    by_status = {
        "completed": sum(1 for h in history if h["status"] == "completed"),
        "failed": sum(1 for h in history if h["status"] == "failed"),
        "running": sum(1 for h in history if h["status"] == "running"),
        "pending": sum(1 for h in history if h["status"] == "pending"),
    }
    active_bots = sum(1 for b in MOCK_BOTS if b["enabled"])
    return BotStatsResponse(
        total_runs=len(history),
        by_status=by_status,
        human_commands=3,
        active_bots=active_bots,
    )


@router.get("/mock/history", response_model=Dict[str, Any])
async def get_bot_history(limit: int = 20, session: AsyncSession = Depends(get_async_session)):
    return {"ok": True, "runs": MOCK_EXECUTION_HISTORY[:limit]}


@router.post("/commands/human", response_model=Dict[str, Any])
async def execute_human_command(data: Dict[str, str], session: AsyncSession = Depends(get_async_session)):
    command = data.get("command", "").strip()
    if not command:
        raise HTTPException(status_code=400, detail="Command cannot be empty")
    return {
        "ok": True,
        "message": f"Command executed: {command}",
        "timestamp": datetime.now().isoformat(),
    }


@router.post("/{bot_name}/pause", response_model=Dict[str, Any])
async def pause_bot(bot_name: str, session: AsyncSession = Depends(get_async_session)):
    bot = next((b for b in MOCK_BOTS if b["bot_name"] == bot_name), None)
    if not bot:
        raise HTTPException(status_code=404, detail=f"Bot '{bot_name}' not found")
    bot["status"] = "paused"
    return {"ok": True, "message": f"Bot '{bot_name}' paused"}


@router.post("/{bot_name}/resume", response_model=Dict[str, Any])
async def resume_bot(bot_name: str, session: AsyncSession = Depends(get_async_session)):
    bot = next((b for b in MOCK_BOTS if b["bot_name"] == bot_name), None)
    if not bot:
        raise HTTPException(status_code=404, detail=f"Bot '{bot_name}' not found")
    bot["status"] = "running"
    return {"ok": True, "message": f"Bot '{bot_name}' resumed"}


@router.post("/{bot_name}/restart", response_model=Dict[str, Any])
async def restart_bot(bot_name: str, session: AsyncSession = Depends(get_async_session)):
    bot = next((b for b in MOCK_BOTS if b["bot_name"] == bot_name), None)
    if not bot:
        raise HTTPException(status_code=404, detail=f"Bot '{bot_name}' not found")
    bot["status"] = "running"
    bot["last_run"] = {
        "status": "running",
        "started_at": datetime.now().isoformat(),
    }
    return {"ok": True, "message": f"Bot '{bot_name}' restarted"}


__all__ = ["router"]
