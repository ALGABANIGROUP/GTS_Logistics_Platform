from __future__ import annotations

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Index, Integer, JSON, String, Text
from sqlalchemy.sql import func

from backend.database.base import Base


class BotRegistry(Base):
    __tablename__ = "bot_registry"
    __table_args__ = (
        Index("ix_bot_registry_enabled", "enabled"),
    )

    bot_name = Column(String(100), primary_key=True)
    enabled = Column(Boolean, nullable=False, default=True)
    automation_level = Column(String(32), nullable=False, default="auto")
    schedule_cron = Column(String(100), nullable=True)
    config_json = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class BotRun(Base):
    __tablename__ = "bot_runs"
    __table_args__ = (
        Index("ix_bot_runs_bot_name", "bot_name"),
        Index("ix_bot_runs_status", "status"),
        Index("ix_bot_runs_started_at", "started_at"),
    )

    id = Column(Integer, primary_key=True)
    bot_name = Column(
        String(100),
        ForeignKey("bot_registry.bot_name", ondelete="CASCADE"),
        nullable=False,
    )
    task_type = Column(String(100), nullable=False, default="run")
    params_json = Column(JSON, nullable=True)
    status = Column(String(20), nullable=False, default="running")
    started_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    finished_at = Column(DateTime(timezone=True), nullable=True)
    result_json = Column(JSON, nullable=True)
    error = Column(Text, nullable=True)


class HumanCommand(Base):
    __tablename__ = "human_commands"
    __table_args__ = (
        Index("ix_human_commands_status", "status"),
        Index("ix_human_commands_created_at", "created_at"),
        Index("ix_human_commands_user_email", "user_email"),
    )

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=True)
    user_email = Column(String(255), nullable=True)
    natural_command = Column(Text, nullable=False)
    parsed_json = Column(JSON, nullable=True)
    technical_json = Column(JSON, nullable=True)
    status = Column(String(20), nullable=False, default="received")
    result_json = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

