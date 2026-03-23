from __future__ import annotations

from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends
from pydantic import BaseModel, ConfigDict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from backend.database.config import get_db_async  # type: ignore[import]
from backend.models.ai_bot_issues import AIBotIssue  # type: ignore[import]

router = APIRouter(prefix="/dev_maintenance", tags=["DevMaintenance"])


class IssueOut(BaseModel):
    id: int
    bot_name: str
    title: str
    description: str
    severity: str
    status: str
    reported_by: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


@router.get("/issues", response_model=List[IssueOut])
async def get_all_issues(
    db: AsyncSession = Depends(get_db_async),
):
    result = await db.execute(select(AIBotIssue))
    return result.scalars().all()

