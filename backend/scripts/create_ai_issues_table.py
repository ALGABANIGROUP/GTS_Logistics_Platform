# [TODO: Translate]

import sys
import os
import asyncio
from sqlalchemy import Column, Integer, String, Text, DateTime, Enum
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine

import enum

Base = declarative_base()

class IssueSeverity(str, enum.Enum):
    critical = "critical"
    high = "high"
    medium = "medium"
    low = "low"

class IssueStatus(str, enum.Enum):
    open = "open"
    in_progress = "in_progress"
    resolved = "resolved"
    closed = "closed"

class AIBotIssue(Base):
    __tablename__ = "ai_bot_issues"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True)
    bot_name = Column(String, nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    severity = Column(Enum(IssueSeverity), default=IssueSeverity.low)
    status = Column(Enum(IssueStatus), default=IssueStatus.open)
    reported_by = Column(String, default="system")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

# [TODO: Translate]
DATABASE_URL = (
    "postgresql+asyncpg://gabani_transport_solutions_user:"
    "__SET_IN_SECRET_MANAGER__"
    "@dpg-cuicq2qj1k6c73asm5c0-a.oregon-postgres.render.com:5432/"
    "gabani_transport_solutions"
)

engine = create_async_engine(DATABASE_URL, echo=True)

async def create_table():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        print("✅ ai_bot_issues table created successfully.")

if __name__ == "__main__":
    asyncio.run(create_table())
