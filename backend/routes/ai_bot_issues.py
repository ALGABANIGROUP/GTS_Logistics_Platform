from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from backend.database.config import get_db_async
from backend.models.ai_bot_issues import AIBotIssue, IssueSeverity, IssueStatus
from backend.utils.email_utils import send_bot_email

router = APIRouter(prefix="/ai_issues", tags=["AI Bot Issues"])


class IssueCreate(BaseModel):
    bot_name: str
    title: str
    description: str
    severity: IssueSeverity = IssueSeverity.low
    reported_by: Optional[str] = "System"


class IssueUpdate(BaseModel):
    status: IssueStatus
    description: Optional[str] = None


class IssueOut(BaseModel):
    id: int
    bot_name: str
    title: str
    description: str
    severity: IssueSeverity
    status: IssueStatus
    reported_by: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


@router.post("/", response_model=IssueOut)
async def create_issue(issue: IssueCreate, db: AsyncSession = Depends(get_db_async)):
    new_issue = AIBotIssue(**issue.dict())
    db.add(new_issue)
    await db.commit()
    await db.refresh(new_issue)

    if new_issue.severity == IssueSeverity.critical:
        try:
            send_bot_email(
                bot_name=new_issue.bot_name,
                subject="Critical AI Issue Reported",
                body=(
                    f"A critical issue was reported by {new_issue.reported_by or 'system'}\n\n"
                    f"Title: {new_issue.title}\n\n"
                    f"Description:\n{new_issue.description}"
                ),
                to=["operations@gabanilogistics.com"],
            )
        except Exception as exc:
            print("Failed to send alert email:", exc)

    return new_issue


@router.get("/", response_model=List[IssueOut])
async def get_all_issues(db: AsyncSession = Depends(get_db_async)):
    result = await db.execute(select(AIBotIssue))
    return result.scalars().all()


@router.get("/{issue_id}", response_model=IssueOut)
async def get_issue(issue_id: int, db: AsyncSession = Depends(get_db_async)):
    result = await db.execute(select(AIBotIssue).where(AIBotIssue.id == issue_id))
    issue = result.scalar_one_or_none()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    return issue


@router.put("/{issue_id}", response_model=IssueOut)
async def update_issue(
    issue_id: int,
    update: IssueUpdate,
    db: AsyncSession = Depends(get_db_async),
):
    result = await db.execute(select(AIBotIssue).where(AIBotIssue.id == issue_id))
    issue = result.scalar_one_or_none()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")

    issue.status = update.status
    if update.description:
        issue.description = update.description
    issue.updated_at = datetime.utcnow()
    db.add(issue)
    await db.commit()
    await db.refresh(issue)
    return issue


@router.delete("/{issue_id}")
async def delete_issue(issue_id: int, db: AsyncSession = Depends(get_db_async)):
    result = await db.execute(select(AIBotIssue).where(AIBotIssue.id == issue_id))
    issue = result.scalar_one_or_none()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    await db.delete(issue)
    await db.commit()
    return {"message": "Issue deleted successfully"}

