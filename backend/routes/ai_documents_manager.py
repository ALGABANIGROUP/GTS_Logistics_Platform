from __future__ import annotations

from datetime import datetime, timedelta
from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from backend.database.config import get_db_async
from backend.models.document import Document
from pydantic import BaseModel, ConfigDict

router = APIRouter()


class DocumentStatusOut(BaseModel):
    id: int
    file_url: str
    expires_at: str | None
    status: str

    model_config = ConfigDict(from_attributes=True)


@router.get("/ai/documents/expiring", response_model=List[DocumentStatusOut])
async def get_expiring_documents(db: AsyncSession = Depends(get_db_async)):
    now = datetime.utcnow()
    upcoming = now + timedelta(days=30)
    result = await db.execute(
        select(Document).where(Document.expires_at.isnot(None), Document.expires_at <= upcoming)
    )
    docs = result.scalars().all()
    output: List[DocumentStatusOut] = []
    for doc in docs:
        expires_at = doc.expires_at
        status = (
            "expired" if expires_at and expires_at < now else "expiring soon"
        )
        expires_str = expires_at.strftime("%Y-%m-%d") if expires_at else None
        output.append(
            DocumentStatusOut(
                id=doc.id,
                file_url=doc.file_url,
                expires_at=expires_str,
                status=status,
            )
        )
    return output


@router.get("/ai/documents/status")
async def get_documents_summary(db: AsyncSession = Depends(get_db_async)):
    now = datetime.utcnow()
    soon = now + timedelta(days=30)
    result = await db.execute(select(Document).where(Document.expires_at.isnot(None)))
    all_docs = result.scalars().all()
    expired = len([d for d in all_docs if d.expires_at and d.expires_at < now])
    soon_expiring = len(
        [
            d
            for d in all_docs
            if d.expires_at and now <= d.expires_at <= soon
        ]
    )
    valid = len([d for d in all_docs if d.expires_at and d.expires_at > soon])
    return {"expired": expired, "expiring_soon": soon_expiring, "valid": valid}
