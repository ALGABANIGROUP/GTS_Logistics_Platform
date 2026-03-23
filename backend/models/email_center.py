from __future__ import annotations

from datetime import datetime
from typing import Optional, List, Dict, Any

from sqlalchemy import (
    String,
    Integer,
    BigInteger,
    Boolean,
    DateTime,
    ForeignKey,
    Text,
    JSON,
    UniqueConstraint,
    Index,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from backend.database.base import Base


class Mailbox(Base):
    __tablename__ = "mailboxes"
    __table_args__ = (
        UniqueConstraint("tenant_id", "email_address", name="uq_mailboxes_tenant_email"),
        Index("ix_mailboxes_owner_user_id", "owner_user_id"),
        Index("ix_mailboxes_bot_code", "bot_code"),
        Index("ix_mailboxes_assigned_bot_key", "assigned_bot_key"),
        Index("ix_mailboxes_enabled", "is_enabled"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tenant_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    owner_user_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    bot_code: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    email_address: Mapped[str] = mapped_column(String(255), nullable=False)
    display_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    mode: Mapped[str] = mapped_column(String(20), nullable=False, default="HUMAN")
    direction: Mapped[str] = mapped_column(String(30), nullable=False, default="INBOUND_OUTBOUND")

    imap_host: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    imap_port: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    imap_user: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    imap_ssl: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True, default=True)

    smtp_host: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    smtp_port: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    smtp_user: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    smtp_ssl: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True, default=True)

    use_tls: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True, default=True)
    inbound_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    outbound_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    is_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    polling_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    auto_reply_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    package_scope: Mapped[str] = mapped_column(String(20), nullable=False, default="SYSTEM")
    assigned_bot_key: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    bot_config: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)

    last_polled_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    last_uid: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    last_message_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    credentials: Mapped["MailboxCredentials"] = relationship(
        "MailboxCredentials",
        back_populates="mailbox",
        uselist=False,
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    routing_rules: Mapped[List["BotMailboxRule"]] = relationship(
        "BotMailboxRule",
        back_populates="mailbox",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="BotMailboxRule.priority.asc()",
    )


class MailboxCredentials(Base):
    __tablename__ = "mailbox_credentials"

    mailbox_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("mailboxes.id", ondelete="CASCADE"), primary_key=True
    )
    credentials_ciphertext: Mapped[str] = mapped_column(Text, nullable=False)
    key_version: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    rotated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    last_verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    last_error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    mailbox: Mapped[Mailbox] = relationship("Mailbox", back_populates="credentials")


class EmailThread(Base):
    __tablename__ = "email_threads"
    __table_args__ = (
        Index("ix_email_threads_mailbox_id", "mailbox_id"),
        Index("ix_email_threads_created_at", "created_at"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    mailbox_id: Mapped[int] = mapped_column(Integer, ForeignKey("mailboxes.id", ondelete="CASCADE"), nullable=False)
    subject: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="open")
    tags: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    priority: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    assigned_to_user_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    last_message_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        onupdate=func.now(),
    )


class EmailMessage(Base):
    __tablename__ = "email_messages"
    __table_args__ = (
        Index("ix_email_messages_mailbox_id", "mailbox_id"),
        Index("ix_email_messages_status", "status"),
        Index("ix_email_messages_applied_rule_id", "applied_rule_id"),
        Index("ix_email_messages_processed_by_bot", "processed_by_bot"),
        Index("ix_email_messages_created_at", "created_at"),
        UniqueConstraint("mailbox_id", "message_id", name="uq_email_messages_mailbox_message_id"),
        UniqueConstraint("mailbox_id", "imap_uid", name="uq_email_messages_mailbox_imap_uid"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    mailbox_id: Mapped[int] = mapped_column(Integer, ForeignKey("mailboxes.id", ondelete="CASCADE"), nullable=False)
    message_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    imap_uid: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    thread_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("email_threads.id"), nullable=True)

    direction: Mapped[str] = mapped_column(String(20), nullable=False)
    from_addr: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    to_addrs: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    cc_addrs: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    subject: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    received_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    body_preview: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    body_storage_ref: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    status: Mapped[str] = mapped_column(String(50), nullable=False, default="new")
    assigned_bot: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    workflow_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    raw_headers_json: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    analyzed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    analysis_result: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    applied_rule_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("bot_mailbox_rules.id", ondelete="SET NULL"),
        nullable=True,
    )
    processed_by_bot: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    processed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    applied_rule: Mapped[Optional["BotMailboxRule"]] = relationship(
        "BotMailboxRule",
        back_populates="matched_messages",
        foreign_keys=[applied_rule_id],
    )
    attachments: Mapped[List["EmailAttachment"]] = relationship(
        "EmailAttachment",
        back_populates="message",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class BotMailboxRule(Base):
    __tablename__ = "bot_mailbox_rules"
    __table_args__ = (
        Index("ix_bot_mailbox_rules_mailbox_id", "mailbox_id"),
        Index("ix_bot_mailbox_rules_bot_key", "bot_key"),
        Index("ix_bot_mailbox_rules_priority", "priority"),
        Index("ix_bot_mailbox_rules_is_active", "is_active"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    mailbox_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("mailboxes.id", ondelete="CASCADE"),
        nullable=False,
    )
    bot_key: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    condition_field: Mapped[str] = mapped_column(String(50), nullable=False)
    condition_operator: Mapped[str] = mapped_column(String(20), nullable=False)
    condition_value: Mapped[Any] = mapped_column(JSON, nullable=False)
    condition_match_all: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    action_type: Mapped[str] = mapped_column(String(50), nullable=False)
    action_config: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    priority: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    times_matched: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    last_matched_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    created_by: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    mailbox: Mapped[Mailbox] = relationship("Mailbox", back_populates="routing_rules")
    matched_messages: Mapped[List[EmailMessage]] = relationship(
        "EmailMessage",
        back_populates="applied_rule",
        foreign_keys="EmailMessage.applied_rule_id",
    )


class EmailAttachment(Base):
    __tablename__ = "email_attachments"
    __table_args__ = (
        Index("ix_email_attachments_message_id", "message_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    message_id: Mapped[int] = mapped_column(Integer, ForeignKey("email_messages.id", ondelete="CASCADE"), nullable=False)
    filename: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    content_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    size: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    storage_ref: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    message: Mapped[EmailMessage] = relationship("EmailMessage", back_populates="attachments")


class EmailAuditLog(Base):
    __tablename__ = "email_audit_logs"
    __table_args__ = (
        Index("ix_email_audit_logs_created_at", "created_at"),
        Index("ix_email_audit_logs_actor_user_id", "actor_user_id"),
        Index("ix_email_audit_logs_action", "action"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    actor_user_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    mailbox_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("mailboxes.id"), nullable=True)
    message_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("email_messages.id"), nullable=True)
    ip: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    diff_json: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    severity: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)


class MailboxRequest(Base):
    __tablename__ = "mailbox_requests"
    __table_args__ = (
        Index("ix_mailbox_requests_status", "status"),
        Index("ix_mailbox_requests_requester", "requester_user_id"),
        Index("ix_mailbox_requests_created_at", "created_at"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    requester_user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    requested_email: Mapped[str] = mapped_column(String(255), nullable=False)
    desired_mode: Mapped[str] = mapped_column(String(20), nullable=False, default="HUMAN")
    package_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    approved_by: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    decided_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

