# backend/tools/open_web_leads/schemas.py

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr


class OpenWebLeadBase(BaseModel):
    source: str
    title: str
    origin: Optional[str] = None
    destination: Optional[str] = None
    weight_lbs: Optional[int] = None
    equipment: Optional[str] = None
    contact_email: Optional[EmailStr] = None
    contact_phone: Optional[str] = None
    contact_name: Optional[str] = None
    raw_url: str
    posted_at: Optional[datetime] = None
    score: Optional[int] = None


class OpenWebLeadCreate(OpenWebLeadBase):
    # Usually the "create" model is what's received from the adapters
    pass


class OpenWebLeadUpdateStatus(BaseModel):
    status: str  # new / contacted / closed / ignored


class OpenWebLeadOut(OpenWebLeadBase):
    id: int
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class OpenWebLeadListResponse(BaseModel):
    total: int
    items: List[OpenWebLeadOut]
