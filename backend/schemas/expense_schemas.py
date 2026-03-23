"""
Unified expense schemas for the entire application.
This file consolidates all expense-related Pydantic models to avoid duplication.
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional, Union
from pydantic import BaseModel, ConfigDict, Field
from backend.models.financial import ExpenseStatus


class ExpenseCreate(BaseModel):
    """
    Unified schema for creating expenses across all modules.
    Used in: finance_service, finance_routes, financial routes.
    """
    category: str
    amount: float = Field(..., gt=0)
    description: Optional[str] = None
    vendor: Optional[str] = None
    created_at: Optional[datetime] = None
    status: Optional[Union[str, ExpenseStatus]] = ExpenseStatus.PENDING


class ExpenseUpdate(BaseModel):
    """Schema for updating existing expenses."""
    category: Optional[str] = None
    amount: Optional[float] = Field(None, gt=0)
    description: Optional[str] = None
    vendor: Optional[str] = None
    status: Optional[Union[str, ExpenseStatus]] = None


class ExpenseOut(BaseModel):
    """
    Unified schema for expense responses across all modules.
    Serialized representation of an expense.
    """
    id: int
    category: str
    amount: float
    description: Optional[str]
    vendor: Optional[str]
    created_at: datetime
    status: str

    model_config = ConfigDict(from_attributes=True)
