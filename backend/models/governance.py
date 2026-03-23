from __future__ import annotations

from sqlalchemy import Column, String, DateTime, Integer, JSON, ForeignKey, Text, Index, Boolean
from sqlalchemy.sql import func

from .base import Base


class GovernanceBot(Base):
    __tablename__ = "governance_bots"
    __table_args__ = (
        Index("ix_governance_bots_status", "status"),
        Index("ix_governance_bots_created_at", "created_at"),
    )

    bot_id = Column(String(150), primary_key=True)
    name = Column(String(150), nullable=False)
    version = Column(String(50), nullable=True)
    description = Column(Text, nullable=True)
    author = Column(String(150), nullable=True)
    status = Column(String(32), nullable=False, default="under_review")
    approvals_count = Column(Integer, nullable=False, default=0)

    manifest_json = Column(JSON, nullable=True)  # stores permissions, external_apis, db_access, constraints
    code_hash = Column(String(256), nullable=True)
    config_hash = Column(String(256), nullable=True)
    signature = Column(String(512), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class GovernanceApproval(Base):
    __tablename__ = "governance_approvals"
    __table_args__ = (
        Index("ix_governance_approvals_bot_id", "bot_id"),
        Index("ix_governance_approvals_created_at", "created_at"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    bot_id = Column(String(150), ForeignKey("governance_bots.bot_id", ondelete="CASCADE"), nullable=False)
    approver = Column(String(150), nullable=True)
    role = Column(String(100), nullable=True)
    decision = Column(String(32), nullable=False, default="approved")
    comments = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class GovernanceActivity(Base):
    __tablename__ = "governance_activity"
    __table_args__ = (
        Index("ix_governance_activity_bot_id", "bot_id"),
        Index("ix_governance_activity_created_at", "created_at"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    bot_id = Column(String(150), ForeignKey("governance_bots.bot_id", ondelete="CASCADE"), nullable=False)
    action = Column(String(100), nullable=False)
    environment = Column(String(50), nullable=True)
    details = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
