from __future__ import annotations

from typing import Optional

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Integer,
    JSON,
    String,
    Text,
    func,
)
from database.base import Base


class ExternalRecord(Base):
    __tablename__ = "external_records"

    id = Column(Integer, primary_key=True, index=True)
    source = Column(String(128), nullable=False, index=True)
    entity_type = Column(String(64), nullable=False)
    title = Column(String(512), nullable=False)
    location = Column(String(256), nullable=True)
    tags = Column(JSON, nullable=False, default=list)
    raw = Column(JSON, nullable=False, default=dict)
    fetched_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    is_real = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    def __repr__(self) -> str:
        return f"<ExternalRecord source={self.source} title={self.title[:40]!r}>"


class BotExecution(Base):
    __tablename__ = "bot_executions"

    id = Column(Integer, primary_key=True, index=True)
    source = Column(String(128), nullable=False)
    records_synced = Column(Integer, nullable=False, default=0)
    succeeded = Column(Boolean, nullable=False, default=True)
    notes = Column(Text, nullable=True)
    executed_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    def __repr__(self) -> str:
        status = "ok" if self.succeeded else "failed"
        return f"<BotExecution source={self.source} status={status} records={self.records_synced}>"

