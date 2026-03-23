from __future__ import annotations

from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel, Field

# Pydantic v2 models

class DocumentBase(BaseModel):
    title: str = Field(..., min_length=1)
    file_url: str = Field(..., min_length=1)
    file_type: Optional[str] = None
    expires_at: Optional[datetime] = None
    notify_before_days: Optional[int] = 7
    owner_id: Optional[int] = None

class DocumentCreate(DocumentBase):
    pass

class DocumentUpdate(BaseModel):
    title: Optional[str] = None
    file_url: Optional[str] = None
    file_type: Optional[str] = None
    expires_at: Optional[datetime] = None
    notify_before_days: Optional[int] = None
    owner_id: Optional[int] = None

class DocumentOut(DocumentBase):
    id: int

    class Config:
        from_attributes = True  # ORM mode for Pydantic v2
