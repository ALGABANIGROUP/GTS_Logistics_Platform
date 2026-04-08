from __future__ import annotations

import asyncio
import email
import imaplib
import json
import logging
import os
import smtplib
import re
from datetime import datetime, timedelta, timezone
from email.message import EmailMessage as SMTPEmailMessage
from email.utils import getaddresses, parsedate_to_datetime
from typing import Any, Dict, List, Optional, Sequence

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, EmailStr
from sqlalchemy import select, update, func
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from backend.database.session import get_async_session
from backend.security.auth import get_current_user
from backend.services.email_crypto import encrypt_credentials, decrypt_credentials
from backend.models.email_center import (
    Mailbox,
    BotMailboxRule,
    MailboxCredentials,
    EmailMessage as EmailMessageModel,
    EmailAttachment,
    EmailAuditLog,
    MailboxRequest,
    EmailThread,
)
from backend.services.email_config import (
    BOT_CODE_ALIASES,
    EMAIL_DISABLED_BOTS,
    NO_REPLY_EMAIL,
    PRIMARY_DOMAIN,
    SECURITY_DOMAIN,
)
from backend.services.email_routing_engine import ActionType, ConditionOperator, EmailRoutingEngine
from backend.utils.email_utils import render_unified_email_html

router = APIRouter(prefix="/api/v1/email", tags=["Email Center"])

EMAIL_ADMIN_ROLES = {"super_admin", "owner"}
logger = logging.getLogger("email_center")
ALLOWED_EMAIL_DOMAINS = {PRIMARY_DOMAIN, SECURITY_DOMAIN}


def _user_role(user: Dict[str, Any]) -> str:
    return str(user.get("effective_role") or user.get("role") or "").strip().lower()


def _normalize_bot_code(value: Optional[str]) -> str:
    if not value:
        return ""
    return BOT_CODE_ALIASES.get(value, value)


def _is_external_recipient(addr: str) -> bool:
    if "@" not in addr:
        return True
    domain = addr.split("@", 1)[-1].strip().lower()
    return domain not in ALLOWED_EMAIL_DOMAINS


def _is_email_admin(user: Dict[str, Any]) -> bool:
    return _user_role(user) in EMAIL_ADMIN_ROLES


def _require_email_admin(user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    if not _is_email_admin(user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Email admin access required")
    return user


def _normalize_addrs(value: Optional[Sequence[str]]) -> List[str]:
    if not value:
        return []
    return [str(v).strip() for v in value if str(v).strip()]


def _get_mailbox_password(mailbox: Mailbox, *, allow_fallback: bool = False) -> Optional[str]:
    creds = mailbox.credentials
    if creds and creds.credentials_ciphertext:
        try:
            return decrypt_credentials(creds.credentials_ciphertext)
        except Exception as exc:
            logger.warning(
                "Failed to decrypt mailbox credentials for %s: %s",
                getattr(mailbox, "email_address", "unknown"),
                exc,
            )
    if allow_fallback:
        return (
            os.getenv("EMAIL_SHARED_PASSWORD")
            or os.getenv("EMAIL_PASSWORD")
            or os.getenv("SMTP_PASSWORD")
            or os.getenv("IMAP_PASSWORD")
        )
    return None


def _mailbox_to_dict(
    obj: Mailbox,
    *,
    message_count: Optional[int] = None,
    thread_count: Optional[int] = None,
) -> Dict[str, Any]:
    return {
        "id": obj.id,
        "tenant_id": obj.tenant_id,
        "owner_user_id": obj.owner_user_id,
        "bot_code": obj.bot_code,
        "email_address": obj.email_address,
        "display_name": obj.display_name,
        "mode": obj.mode,
        "direction": obj.direction,
        "imap_host": obj.imap_host,
        "imap_port": obj.imap_port,
        "imap_user": obj.imap_user,
        "imap_ssl": obj.imap_ssl,
        "smtp_host": obj.smtp_host,
        "smtp_port": obj.smtp_port,
        "smtp_user": obj.smtp_user,
        "smtp_ssl": obj.smtp_ssl,
        "use_tls": obj.use_tls,
        "inbound_enabled": obj.inbound_enabled,
        "outbound_enabled": obj.outbound_enabled,
        "is_enabled": obj.is_enabled,
        "polling_enabled": obj.polling_enabled,
        "auto_reply_enabled": obj.auto_reply_enabled,
        "package_scope": obj.package_scope,
        "last_polled_at": obj.last_polled_at,
        "last_error": obj.credentials.last_error if obj.credentials else None,
        "outbound_only": bool(obj.outbound_enabled and not obj.inbound_enabled),
        "message_count": int(message_count or 0),
        "thread_count": int(thread_count or 0),
        "has_credentials": bool(obj.credentials and obj.credentials.credentials_ciphertext),
        "created_at": obj.created_at,
        "updated_at": obj.updated_at,
    }


def _rule_to_dict(rule: BotMailboxRule) -> Dict[str, Any]:
    return {
        "id": rule.id,
        "mailbox_id": rule.mailbox_id,
        "bot_key": rule.bot_key,
        "condition_field": rule.condition_field,
        "condition_operator": rule.condition_operator,
        "condition_value": rule.condition_value,
        "condition_match_all": rule.condition_match_all,
        "action_type": rule.action_type,
        "action_config": rule.action_config,
        "priority": rule.priority,
        "is_active": rule.is_active,
        "times_matched": rule.times_matched,
        "last_matched_at": rule.last_matched_at,
        "created_at": rule.created_at,
        "updated_at": rule.updated_at,
        "created_by": rule.created_by,
    }


async def _get_mailbox_or_404(db: AsyncSession, mailbox_id: int) -> Mailbox:
    mailbox = await db.get(Mailbox, mailbox_id)
    if not mailbox:
        raise HTTPException(status_code=404, detail="Mailbox not found")
    return mailbox


async def _get_rule_or_404(db: AsyncSession, rule_id: int) -> BotMailboxRule:
    rule = await db.get(BotMailboxRule, rule_id)
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    return rule


def _user_id(user: Dict[str, Any]) -> int:
    return int(user.get("id") or 0)


def _optional_int(value: Any) -> Optional[int]:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return None
    return parsed or None


def _assert_mailbox_access(mailbox: Mailbox, user: Dict[str, Any]) -> None:
    if _is_email_admin(user):
        return
    if mailbox.owner_user_id != _user_id(user):
        raise HTTPException(status_code=403, detail="Mailbox access denied")


async def _mailbox_counts(
    db: AsyncSession, mailbox_ids: Sequence[int]
) -> Dict[int, Dict[str, int]]:
    if not mailbox_ids:
        return {}
    msg_counts = await db.execute(
        select(EmailMessageModel.mailbox_id, func.count(EmailMessageModel.id))
        .where(EmailMessageModel.mailbox_id.in_(mailbox_ids))
        .group_by(EmailMessageModel.mailbox_id)
    )
    thread_counts = await db.execute(
        select(EmailThread.mailbox_id, func.count(EmailThread.id))
        .where(EmailThread.mailbox_id.in_(mailbox_ids))
        .group_by(EmailThread.mailbox_id)
    )
    msg_map = {int(row[0]): int(row[1]) for row in msg_counts.fetchall()}
    thread_map = {int(row[0]): int(row[1]) for row in thread_counts.fetchall()}
    out: Dict[int, Dict[str, int]] = {}
    for mailbox_id in mailbox_ids:
        out[mailbox_id] = {
            "messages": int(msg_map.get(mailbox_id, 0)),
            "threads": int(thread_map.get(mailbox_id, 0)),
        }
    return out


def _attachment_to_dict(att: EmailAttachment) -> Dict[str, Any]:
    return {
        "id": att.id,
        "filename": att.filename,
        "content_type": att.content_type,
        "size": att.size,
        "storage_ref": att.storage_ref,
        "created_at": att.created_at,
    }


def _message_to_dict(
    msg: EmailMessageModel, attachments: Optional[List[EmailAttachment]] = None
) -> Dict[str, Any]:
    return {
        "id": msg.id,
        "mailbox_id": msg.mailbox_id,
        "message_id": msg.message_id,
        "thread_id": msg.thread_id,
        "direction": msg.direction,
        "from_email": msg.from_addr,
        "to_emails": msg.to_addrs or [],
        "cc_emails": msg.cc_addrs or [],
        "subject": msg.subject,
        "received_at": msg.received_at,
        "sent_at": msg.sent_at,
        "body_preview": msg.body_preview,
        "status": msg.status,
        "assigned_bot": msg.assigned_bot,
        "workflow_id": msg.workflow_id,
        "created_at": msg.created_at,
        "attachments": [_attachment_to_dict(a) for a in (attachments or [])],
    }


def _thread_to_dict(thread: EmailThread) -> Dict[str, Any]:
    return {
        "id": thread.id,
        "mailbox_id": thread.mailbox_id,
        "subject": thread.subject,
        "status": thread.status,
        "tags": thread.tags or [],
        "priority": thread.priority,
        "assigned_to_user_id": thread.assigned_to_user_id,
        "last_message_at": thread.last_message_at,
        "created_at": thread.created_at,
        "updated_at": thread.updated_at,
    }


# ============================================================================
# AI Email Bot Compatibility Endpoints (used by AIEmailBot.jsx)
# ============================================================================

@router.get("/monitoring/stats")
async def email_bot_monitoring_stats(
    db: AsyncSession = Depends(get_async_session),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    total = await db.scalar(select(func.count(EmailMessageModel.id))) or 0
    successful = await db.scalar(
        select(func.count(EmailMessageModel.id)).where(EmailMessageModel.status == "processed")
    ) or 0
    pending = await db.scalar(
        select(func.count(EmailMessageModel.id)).where(EmailMessageModel.status.in_(["pending", "new", "queued"]))
    ) or 0
    failed = await db.scalar(
        select(func.count(EmailMessageModel.id)).where(EmailMessageModel.status.in_(["failed", "error"]))
    ) or 0

    bot_rows = await db.execute(
        select(EmailMessageModel.assigned_bot, func.count(EmailMessageModel.id))
        .where(EmailMessageModel.assigned_bot.isnot(None))
        .group_by(EmailMessageModel.assigned_bot)
    )
    bot_performance = {str(row[0]): int(row[1]) for row in bot_rows.fetchall() if row[0]}

    return {
        "total_processed": int(total),
        "successful": int(successful),
        "pending": int(pending),
        "failed": int(failed),
        "bot_performance": bot_performance,
    }


@router.get("/mappings")
async def email_bot_mappings(
    db: AsyncSession = Depends(get_async_session),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    result = await db.execute(select(Mailbox).order_by(Mailbox.email_address.asc()))
    mailboxes = result.scalars().all()
    mappings = [
        {
            "email_pattern": mb.email_address,
            "bot_name": mb.bot_code or "unassigned",
            "workflow": None,
        }
        for mb in mailboxes
    ]
    return {"total": len(mappings), "mappings": mappings}


@router.get("/execution-history")
async def email_bot_execution_history(
    limit: int = 50,
    db: AsyncSession = Depends(get_async_session),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    limit = max(1, min(int(limit or 50), 500))
    result = await db.execute(
        select(EmailMessageModel)
        .order_by(EmailMessageModel.created_at.desc())
        .limit(limit)
    )
    messages = result.scalars().all()

    def _map_status(raw: Optional[str]) -> str:
        val = (raw or "").lower()
        if val in {"processed", "success", "done"}:
            return "success"
        if val in {"pending", "new", "queued", "open"}:
            return "pending"
        if val in {"failed", "error", "rejected"}:
            return "failed"
        return val or "unknown"

    history = []
    for msg in messages:
        mapped_status = _map_status(msg.status)
        history.append(
            {
                "id": msg.id,
                "email_from": msg.from_addr,
                "subject": msg.subject,
                "bot_name": msg.assigned_bot,
                "workflow": msg.workflow_id,
                "status": mapped_status,
                "timestamp": (msg.received_at or msg.created_at).isoformat() if (msg.received_at or msg.created_at) else None,
                "processed_count": 1,
                "success_count": 1 if mapped_status == "success" else 0,
                "error_count": 1 if mapped_status == "failed" else 0,
                "success_rate": 1 if mapped_status == "success" else 0,
            }
        )

    return {
        "total": len(history),
        "limit": limit,
        "history": history,
    }


async def _audit(
    db: AsyncSession,
    *,
    actor_user_id: Optional[int],
    action: str,
    mailbox_id: Optional[int] = None,
    message_id: Optional[int] = None,
    ip: Optional[str] = None,
    diff_json: Optional[Dict[str, Any]] = None,
    severity: Optional[str] = None,
) -> None:
    record = EmailAuditLog(
        actor_user_id=_optional_int(actor_user_id),
        action=action,
        mailbox_id=mailbox_id,
        message_id=message_id,
        ip=ip,
        diff_json=diff_json,
        severity=severity,
    )
    db.add(record)
    await db.commit()


class MailboxCreate(BaseModel):
    email_address: EmailStr
    display_name: Optional[str] = None
    mode: str = "HUMAN"
    direction: str = "INBOUND_OUTBOUND"
    imap_host: Optional[str] = None
    imap_port: Optional[int] = 993
    imap_user: Optional[str] = None
    imap_password: Optional[str] = None
    imap_ssl: Optional[bool] = True
    smtp_host: Optional[str] = None
    smtp_port: Optional[int] = 465
    smtp_user: Optional[str] = None
    smtp_password: Optional[str] = None
    smtp_ssl: Optional[bool] = True
    inbound_enabled: bool = True
    outbound_enabled: bool = True
    is_enabled: bool = True
    polling_enabled: bool = True
    auto_reply_enabled: bool = False
    package_scope: str = "SYSTEM"
    owner_user_id: Optional[int] = None
    bot_code: Optional[str] = None
    tenant_id: Optional[str] = None


class MailboxUpdate(BaseModel):
    display_name: Optional[str] = None
    mode: Optional[str] = None
    direction: Optional[str] = None
    imap_host: Optional[str] = None
    imap_port: Optional[int] = None
    imap_user: Optional[str] = None
    imap_password: Optional[str] = None
    imap_ssl: Optional[bool] = None
    smtp_host: Optional[str] = None
    smtp_port: Optional[int] = None
    smtp_user: Optional[str] = None
    smtp_password: Optional[str] = None
    smtp_ssl: Optional[bool] = None
    inbound_enabled: Optional[bool] = None
    outbound_enabled: Optional[bool] = None
    is_enabled: Optional[bool] = None
    polling_enabled: Optional[bool] = None
    auto_reply_enabled: Optional[bool] = None
    package_scope: Optional[str] = None


class MailboxRequestIn(BaseModel):
    requested_email: EmailStr
    desired_mode: str = "HUMAN"
    package_name: Optional[str] = None


class MailboxRequestDecision(BaseModel):
    reason: Optional[str] = None


class SendMessageIn(BaseModel):
    mailbox_id: int
    to: List[EmailStr]
    subject: str
    body: str
    html: bool = False
    send: bool = True


class ThreadUpdate(BaseModel):
    status: Optional[str] = None
    tags: Optional[List[str]] = None
    priority: Optional[str] = None
    assigned_to_user_id: Optional[int] = None


class AssignBotRequest(BaseModel):
    bot_key: Optional[str] = None
    config: Optional[Dict[str, Any]] = None


class RuleCreateRequest(BaseModel):
    bot_key: Optional[str] = None
    condition_field: str
    condition_operator: str
    condition_value: Any
    condition_match_all: bool = False
    action_type: str
    action_config: Optional[Dict[str, Any]] = None
    priority: int = 0
    is_active: bool = True


class RuleUpdateRequest(BaseModel):
    bot_key: Optional[str] = None
    condition_field: Optional[str] = None
    condition_operator: Optional[str] = None
    condition_value: Optional[Any] = None
    condition_match_all: Optional[bool] = None
    action_type: Optional[str] = None
    action_config: Optional[Dict[str, Any]] = None
    priority: Optional[int] = None
    is_active: Optional[bool] = None


def _validate_routing_payload(
    *,
    condition_operator: Optional[str] = None,
    action_type: Optional[str] = None,
) -> None:
    if condition_operator is not None and condition_operator not in ConditionOperator.ALL:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid condition operator. Allowed values: {sorted(ConditionOperator.ALL)}",
        )
    if action_type is not None and action_type not in ActionType.ALL:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid action type. Allowed values: {sorted(ActionType.ALL)}",
        )


@router.patch("/mailboxes/{mailbox_id}/assign-bot")
async def assign_bot_to_mailbox(
    mailbox_id: int,
    payload: AssignBotRequest,
    user: Dict[str, Any] = Depends(_require_email_admin),
    db: AsyncSession = Depends(get_async_session),
) -> Dict[str, Any]:
    mailbox = await _get_mailbox_or_404(db, mailbox_id)
    mailbox.assigned_bot_key = payload.bot_key
    mailbox.bot_config = payload.config
    mailbox.updated_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(mailbox)
    return {
        "mailbox_id": mailbox.id,
        "assigned_bot_key": mailbox.assigned_bot_key,
        "bot_config": mailbox.bot_config,
    }


@router.get("/mailboxes/{mailbox_id}/assigned-bot")
async def get_assigned_bot(
    mailbox_id: int,
    user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
) -> Dict[str, Any]:
    mailbox = await _get_mailbox_or_404(db, mailbox_id)
    _assert_mailbox_access(mailbox, user)
    return {
        "mailbox_id": mailbox.id,
        "assigned_bot_key": mailbox.assigned_bot_key,
        "bot_config": mailbox.bot_config,
    }


@router.post("/mailboxes/{mailbox_id}/rules")
async def create_routing_rule(
    mailbox_id: int,
    payload: RuleCreateRequest,
    user: Dict[str, Any] = Depends(_require_email_admin),
    db: AsyncSession = Depends(get_async_session),
) -> Dict[str, Any]:
    await _get_mailbox_or_404(db, mailbox_id)
    _validate_routing_payload(
        condition_operator=payload.condition_operator,
        action_type=payload.action_type,
    )

    rule = BotMailboxRule(
        mailbox_id=mailbox_id,
        bot_key=payload.bot_key,
        condition_field=payload.condition_field,
        condition_operator=payload.condition_operator,
        condition_value=payload.condition_value,
        condition_match_all=payload.condition_match_all,
        action_type=payload.action_type,
        action_config=payload.action_config,
        priority=payload.priority,
        is_active=payload.is_active,
        created_by=_user_id(user),
    )
    db.add(rule)
    await db.commit()
    await db.refresh(rule)
    return _rule_to_dict(rule)


@router.get("/mailboxes/{mailbox_id}/rules")
async def list_routing_rules(
    mailbox_id: int,
    user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
) -> Dict[str, Any]:
    mailbox = await _get_mailbox_or_404(db, mailbox_id)
    _assert_mailbox_access(mailbox, user)
    engine = EmailRoutingEngine(db)
    rules = await engine.get_rules_for_mailbox(mailbox_id)
    return {"rules": rules, "count": len(rules)}


@router.get("/rules/{rule_id}")
async def get_routing_rule(
    rule_id: int,
    user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
) -> Dict[str, Any]:
    rule = await _get_rule_or_404(db, rule_id)
    mailbox = await _get_mailbox_or_404(db, rule.mailbox_id)
    _assert_mailbox_access(mailbox, user)
    return _rule_to_dict(rule)


@router.patch("/rules/{rule_id}")
async def update_routing_rule(
    rule_id: int,
    payload: RuleUpdateRequest,
    user: Dict[str, Any] = Depends(_require_email_admin),
    db: AsyncSession = Depends(get_async_session),
) -> Dict[str, Any]:
    rule = await _get_rule_or_404(db, rule_id)
    update_data = payload.model_dump(exclude_unset=True)
    _validate_routing_payload(
        condition_operator=update_data.get("condition_operator"),
        action_type=update_data.get("action_type"),
    )
    for key, value in update_data.items():
        setattr(rule, key, value)
    rule.updated_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(rule)
    return _rule_to_dict(rule)


@router.delete("/rules/{rule_id}")
async def delete_routing_rule(
    rule_id: int,
    user: Dict[str, Any] = Depends(_require_email_admin),
    db: AsyncSession = Depends(get_async_session),
) -> Dict[str, Any]:
    rule = await _get_rule_or_404(db, rule_id)
    await db.delete(rule)
    await db.commit()
    return {"ok": True, "rule_id": rule_id}


@router.post("/messages/{message_id}/route")
async def manually_route_message(
    message_id: int,
    user: Dict[str, Any] = Depends(_require_email_admin),
    db: AsyncSession = Depends(get_async_session),
) -> Dict[str, Any]:
    engine = EmailRoutingEngine(db)
    applied, bot_key = await engine.apply_routing_to_message(message_id)
    return {
        "message_id": message_id,
        "routing_applied": applied,
        "assigned_bot": bot_key,
    }


def _package_limits() -> Dict[str, int]:
    raw = (os.getenv("EMAIL_PACKAGE_LIMITS") or "").strip()
    if raw:
        try:
            data = json.loads(raw)
            if isinstance(data, dict):
                return {str(k).lower(): int(v) for k, v in data.items()}
        except Exception:
            limits: Dict[str, int] = {}
            for token in raw.split(","):
                if "=" not in token:
                    continue
                name, value = token.split("=", 1)
                try:
                    limits[name.strip().lower()] = int(value.strip())
                except Exception:
                    continue
            if limits:
                return limits
    return {"basic": 1, "standard": 2, "pro": 3, "enterprise": 10}


def _initial_sync_settings() -> tuple[Optional[int], Optional[int]]:
    days_raw = (os.getenv("EMAIL_INITIAL_SYNC_DAYS") or "30").strip()
    limit_raw = (os.getenv("EMAIL_INITIAL_SYNC_LIMIT") or "500").strip()
    days = int(days_raw) if days_raw.isdigit() else 30
    limit = int(limit_raw) if limit_raw.isdigit() else 500
    if days <= 0:
        days = None
    if limit <= 0:
        limit = None
    return days, limit


def _poll_plan_for_mailbox(mailbox: Mailbox) -> Dict[str, Any]:
    days, limit = _initial_sync_settings()
    is_initial = mailbox.last_uid is None and mailbox.last_polled_at is None
    if is_initial:
        return {
            "initial": True,
            "min_uid": None,
            "since_days": days,
            "limit": limit,
        }
    if mailbox.last_uid is None:
        return {
            "initial": False,
            "min_uid": None,
            "since_days": None,
            "limit": None,
        }
    min_uid = int(mailbox.last_uid) + 1
    return {
        "initial": False,
        "min_uid": min_uid if min_uid > 0 else None,
        "since_days": None,
        "limit": None,
    }


async def _update_mailbox_sync_state(
    db: AsyncSession,
    mailbox: Mailbox,
    *,
    max_uid: Optional[int],
    last_message_id: Optional[str],
) -> None:
    mailbox.last_polled_at = datetime.now(timezone.utc)
    if max_uid is not None:
        mailbox.last_uid = max_uid
    if last_message_id:
        mailbox.last_message_id = last_message_id
    mailbox.updated_at = datetime.now(timezone.utc)
    await db.commit()


def _user_package(user: Dict[str, Any], requested: Optional[str]) -> str:
    if requested:
        return requested.strip().lower()
    candidate = user.get("package_name") or user.get("plan") or user.get("user_type") or "basic"
    return str(candidate).strip().lower()


async def _assert_package_limit(db: AsyncSession, user: Dict[str, Any], requested_package: Optional[str]) -> None:
    limits = _package_limits()
    package = _user_package(user, requested_package)
    limit = int(limits.get(package, limits.get("basic", 1)))
    user_id = int(user.get("id") or 0)

    if not user_id:
        raise HTTPException(status_code=400, detail="Invalid user context")

    mailbox_count = await db.execute(select(func.count(Mailbox.id)).where(Mailbox.owner_user_id == user_id))
    pending_count = await db.execute(
        select(func.count(MailboxRequest.id)).where(
            MailboxRequest.requester_user_id == user_id,
            MailboxRequest.status == "pending",
        )
    )

    total = int(mailbox_count.scalar() or 0) + int(pending_count.scalar() or 0)
    if total >= limit:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Mailbox request limit reached for package '{package}'",
        )


def _build_imap_search_criteria(since_days: Optional[int]) -> List[str]:
    if since_days and since_days > 0:
        since_date = (datetime.now(timezone.utc) - timedelta(days=since_days)).strftime("%d-%b-%Y")
        return ["SINCE", since_date]
    return ["UNSEEN"]


def _imap_fetch_messages(
    *,
    host: str,
    port: int,
    user: str,
    password: str,
    use_ssl: bool,
    min_uid: Optional[int] = None,
    since_days: Optional[int] = None,
    limit: Optional[int] = None,
) -> List[Dict[str, Any]]:
    client: Optional[imaplib.IMAP4] = None
    try:
        if use_ssl:
            client = imaplib.IMAP4_SSL(host, port)
        else:
            client = imaplib.IMAP4(host, port)
        client.login(user, password)
        client.select("INBOX")
        if min_uid:
            status, data = client.uid("search", None, f"UID {min_uid}:*")
        else:
            criteria = _build_imap_search_criteria(since_days)
            status, data = client.uid("search", None, *criteria)
        if status != "OK":
            return []
        raw_ids = data[0].split()
        uids = [int(uid) for uid in raw_ids if uid]
        if limit and len(uids) > limit:
            uids = uids[-limit:]
        messages: List[Dict[str, Any]] = []
        for uid in uids:
            status, msg_data = client.uid("fetch", str(uid), "(RFC822)")
            if status != "OK":
                continue
            for part in msg_data:
                if isinstance(part, tuple):
                    messages.append({"uid": uid, "raw": part[1]})
        return messages
    finally:
        if client is not None:
            try:
                client.logout()
            except Exception:
                pass


def _extract_body(msg: email.message.Message) -> str:
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            if content_type == "text/plain":
                try:
                    return part.get_payload(decode=True).decode(part.get_content_charset() or "utf-8", errors="ignore")
                except Exception:
                    continue
        return ""
    payload = msg.get_payload(decode=True)
    if payload is None:
        return ""
    try:
        return payload.decode(msg.get_content_charset() or "utf-8", errors="ignore")
    except Exception:
        return ""


def _extract_attachments(msg: email.message.Message) -> List[Dict[str, Any]]:
    attachments: List[Dict[str, Any]] = []
    for part in msg.walk():
        filename = part.get_filename()
        if not filename:
            continue
        payload = part.get_payload(decode=True)
        attachments.append(
            {
                "filename": filename,
                "content_type": part.get_content_type(),
                "size": len(payload) if payload else 0,
            }
        )
    return attachments


def _sanitize_headers(msg: email.message.Message) -> Dict[str, Any]:
    headers = {}
    for key in ("Message-ID", "Subject", "From", "To", "Cc", "Date", "Auto-Submitted"):
        if key in msg:
            headers[key.lower().replace("-", "_")] = msg.get(key)
    return headers


def _auto_reply_allowed(msg: email.message.Message, from_addr: str) -> bool:
    auto_submitted = (msg.get("Auto-Submitted") or "").strip().lower()
    if auto_submitted and auto_submitted != "no":
        return False
    lowered = from_addr.lower()
    if "mailer-daemon" in lowered or "no-reply" in lowered:
        return False
    return True


async def _can_auto_reply(
    db: AsyncSession, mailbox_id: int, sender: str, min_minutes: int = 30
) -> bool:
    since = datetime.now(timezone.utc) - timedelta(minutes=min_minutes)
    result = await db.execute(
        select(EmailMessageModel)
        .where(
            EmailMessageModel.mailbox_id == mailbox_id,
            EmailMessageModel.direction == "outbound",
            EmailMessageModel.created_at >= since,
        )
        .order_by(EmailMessageModel.created_at.desc())
        .limit(20)
    )
    recent = result.scalars().all()
    for msg in recent:
        if sender in (msg.to_addrs or []):
            return False
    return True


def _smtp_send(
    *,
    host: str,
    port: int,
    user: str,
    password: str,
    use_ssl: bool,
    from_addr: str,
    to_addrs: List[str],
    subject: str,
    body: str,
    html: bool,
) -> None:
    msg = SMTPEmailMessage()
    msg["Subject"] = subject
    msg["From"] = from_addr
    msg["To"] = ", ".join(to_addrs)
    if html:
        fallback = re.sub(r"<[^>]+>", "", body)
        msg.set_content(fallback)
        msg.add_alternative(
            render_unified_email_html(subject=subject, body=body, html=True),
            subtype="html",
        )
    else:
        msg.set_content(body)
        msg.add_alternative(
            render_unified_email_html(subject=subject, body=body, html=False),
            subtype="html",
        )

    if use_ssl and port == 465:
        with smtplib.SMTP_SSL(host, port) as server:
            server.login(user, password)
            server.send_message(msg)
    else:
        with smtplib.SMTP(host, port) as server:
            if use_ssl:
                server.starttls()
            server.login(user, password)
            server.send_message(msg)


async def _send_outbound(
    *,
    db: AsyncSession,
    mailbox: Mailbox,
    to_addrs: List[str],
    subject: str,
    body: str,
    html: bool,
    from_addr: Optional[str] = None,
) -> EmailMessageModel:
    password = _get_mailbox_password(mailbox, allow_fallback=True)
    if not password:
        raise HTTPException(status_code=400, detail="Mailbox credentials are missing")
    smtp_user = mailbox.smtp_user or mailbox.email_address
    smtp_host = mailbox.smtp_host or ""
    smtp_port = mailbox.smtp_port or 465
    smtp_ssl = bool(mailbox.smtp_ssl if mailbox.smtp_ssl is not None else mailbox.use_tls)

    if not smtp_host:
        raise HTTPException(status_code=400, detail="SMTP host is not configured")

    await asyncio.to_thread(
        _smtp_send,
        host=smtp_host,
        port=int(smtp_port),
        user=str(smtp_user),
        password=password,
        use_ssl=smtp_ssl,
        from_addr=from_addr or mailbox.email_address,
        to_addrs=to_addrs,
        subject=subject,
        body=body,
        html=html,
    )

    message = EmailMessageModel(
        mailbox_id=mailbox.id,
        direction="outbound",
        from_addr=from_addr or mailbox.email_address,
        to_addrs=to_addrs,
        subject=subject,
        sent_at=datetime.now(timezone.utc),
        status="processed",
        created_at=datetime.now(timezone.utc),
    )
    db.add(message)
    await db.commit()
    await db.refresh(message)
    return message


async def _ensure_thread(
    db: AsyncSession,
    mailbox_id: int,
    subject: Optional[str],
    in_reply_to: Optional[str],
) -> EmailThread:
    if in_reply_to:
        res = await db.execute(select(EmailMessageModel).where(EmailMessageModel.message_id == in_reply_to))
        parent = res.scalar_one_or_none()
        if parent and parent.thread_id:
            thread = await db.get(EmailThread, parent.thread_id)
            if thread:
                return thread

    res = await db.execute(
        select(EmailThread)
        .where(EmailThread.mailbox_id == mailbox_id, EmailThread.subject == subject)
        .order_by(EmailThread.created_at.desc())
        .limit(1)
    )
    existing = res.scalar_one_or_none()
    if existing:
        return existing

    now = datetime.now(timezone.utc)
    thread = EmailThread(
        mailbox_id=mailbox_id,
        subject=subject,
        status="open",
        created_at=now,
        updated_at=now,
    )
    db.add(thread)
    await db.commit()
    await db.refresh(thread)
    return thread


async def _route_via_operations_manager(payload: Dict[str, Any]) -> Dict[str, Any]:
    from backend.main import ai_registry

    ops = ai_registry.get("operations_manager")
    return await ops.run(payload)


async def _handle_inbound_message(
    db: AsyncSession, mailbox: Mailbox, raw_message: bytes, *, imap_uid: Optional[int]
) -> Optional[EmailMessageModel]:
    msg = email.message_from_bytes(raw_message)
    message_id = (msg.get("Message-ID") or "").strip() or None

    if imap_uid is not None:
        existing_uid = await db.execute(
            select(EmailMessageModel).where(
                EmailMessageModel.mailbox_id == mailbox.id,
                EmailMessageModel.imap_uid == imap_uid,
            )
        )
        if existing_uid.scalar_one_or_none():
            return None

    if message_id:
        exists = await db.execute(
            select(EmailMessageModel).where(
                EmailMessageModel.mailbox_id == mailbox.id,
                EmailMessageModel.message_id == message_id,
            )
        )
        if exists.scalar_one_or_none():
            return None

    subject = msg.get("Subject")
    from_addr = getaddresses([msg.get("From") or ""])[0][1]
    to_addrs = [addr for _, addr in getaddresses(msg.get_all("To", []))]
    cc_addrs = [addr for _, addr in getaddresses(msg.get_all("Cc", []))]
    received_at = None
    date_header = msg.get("Date")
    if date_header:
        try:
            received_at = parsedate_to_datetime(date_header)
        except Exception:
            received_at = None

    body_text = _extract_body(msg)
    body_preview = (body_text or "")[:500]
    thread = await _ensure_thread(db, mailbox.id, subject, msg.get("In-Reply-To"))

    record = EmailMessageModel(
        mailbox_id=mailbox.id,
        message_id=message_id,
        imap_uid=imap_uid,
        thread_id=thread.id if thread else None,
        direction="inbound",
        from_addr=from_addr,
        to_addrs=to_addrs,
        cc_addrs=cc_addrs,
        subject=subject,
        received_at=received_at,
        body_preview=body_preview,
        status="new",
        raw_headers_json=_sanitize_headers(msg),
    )
    db.add(record)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        return None
    await db.refresh(record)

    attachments = _extract_attachments(msg)
    for att in attachments:
        db.add(
            EmailAttachment(
                message_id=record.id,
                filename=att.get("filename"),
                content_type=att.get("content_type"),
                size=att.get("size"),
            )
        )
    await db.commit()

    thread.last_message_at = datetime.now(timezone.utc)
    await db.commit()

    routing_payload = {
        "workflow_name": "email_intake",
        "mailbox": mailbox.email_address,
        "sender": from_addr,
        "subject": subject,
        "body_preview": body_preview,
        "attachments": attachments,
    }

    ops_result = await _route_via_operations_manager(routing_payload)
    record.assigned_bot = ops_result.get("assigned_bot")
    record.workflow_id = ops_result.get("workflow_id")
    record.status = "processed"
    await db.commit()

    if mailbox.auto_reply_enabled and mailbox.mode == "BOT":
        if _auto_reply_allowed(msg, from_addr) and await _can_auto_reply(db, mailbox.id, from_addr):
            reply = ops_result.get("reply_draft")
            if reply:
                reply_with_footer = f"{reply}\n\n--\nAutomated response."
                await _send_outbound(
                    db=db,
                    mailbox=mailbox,
                    to_addrs=[from_addr],
                    subject=f"Re: {subject}" if subject else "Re: Message",
                    body=reply_with_footer,
                    html=False,
                )

    return record


@router.get("/mailboxes")
async def list_mailboxes(
    user: Dict[str, Any] = Depends(_require_email_admin),
    db: AsyncSession = Depends(get_async_session),
) -> List[Dict[str, Any]]:
    result = await db.execute(
        select(Mailbox)
        .options(selectinload(Mailbox.credentials))
        .order_by(Mailbox.id)
    )
    mailboxes = result.scalars().all()
    counts = await _mailbox_counts(db, [m.id for m in mailboxes])
    return [
        _mailbox_to_dict(
            m,
            message_count=counts.get(m.id, {}).get("messages"),
            thread_count=counts.get(m.id, {}).get("threads"),
        )
        for m in mailboxes
    ]


@router.get("/my/mailboxes")
async def list_my_mailboxes(
    user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
) -> List[Dict[str, Any]]:
    user_id = int(user.get("id") or 0)
    result = await db.execute(
        select(Mailbox)
        .options(selectinload(Mailbox.credentials))
        .where(Mailbox.owner_user_id == user_id)
    )
    mailboxes = result.scalars().all()
    counts = await _mailbox_counts(db, [m.id for m in mailboxes])
    return [
        _mailbox_to_dict(
            m,
            message_count=counts.get(m.id, {}).get("messages"),
            thread_count=counts.get(m.id, {}).get("threads"),
        )
        for m in mailboxes
    ]


@router.post("/mailboxes")
async def create_mailbox(
    payload: MailboxCreate,
    request: Request,
    user: Dict[str, Any] = Depends(_require_email_admin),
    db: AsyncSession = Depends(get_async_session),
) -> Dict[str, Any]:
    normalized_bot = _normalize_bot_code(payload.bot_code)
    if normalized_bot in EMAIL_DISABLED_BOTS:
        raise HTTPException(status_code=400, detail=f"Email is disabled for bot '{normalized_bot}'")

    mailbox = Mailbox(
        tenant_id=payload.tenant_id,
        owner_user_id=payload.owner_user_id,
        bot_code=normalized_bot or None,
        email_address=str(payload.email_address).lower().strip(),
        display_name=payload.display_name,
        mode=payload.mode,
        direction=payload.direction,
        imap_host=payload.imap_host,
        imap_port=payload.imap_port,
        imap_user=payload.imap_user or str(payload.email_address),
        imap_ssl=payload.imap_ssl,
        smtp_host=payload.smtp_host,
        smtp_port=payload.smtp_port,
        smtp_user=payload.smtp_user or str(payload.email_address),
        smtp_ssl=payload.smtp_ssl,
        inbound_enabled=payload.inbound_enabled,
        outbound_enabled=payload.outbound_enabled,
        is_enabled=payload.is_enabled,
        polling_enabled=payload.polling_enabled,
        auto_reply_enabled=payload.auto_reply_enabled,
        package_scope=payload.package_scope,
        created_at=datetime.now(timezone.utc),
    )
    db.add(mailbox)
    await db.commit()
    await db.refresh(mailbox)

    if payload.imap_password or payload.smtp_password:
        encrypted, key_version = encrypt_credentials(payload.imap_password or payload.smtp_password or "")
        creds = MailboxCredentials(
            mailbox_id=mailbox.id,
            credentials_ciphertext=encrypted,
            key_version=key_version,
            rotated_at=datetime.now(timezone.utc),
        )
        db.add(creds)
        await db.commit()

    await _audit(
        db,
        actor_user_id=user.get("id"),
        action="mailbox_create",
        mailbox_id=mailbox.id,
        ip=request.client.host if request.client else None,
        diff_json={"email_address": mailbox.email_address, "mode": mailbox.mode},
        severity="info",
    )
    return _mailbox_to_dict(mailbox)


@router.post("/mailboxes/self")
async def request_mailbox_self(
    payload: MailboxCreate,
    request: Request,
    user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
) -> Dict[str, Any]:
    await _assert_package_limit(db, user, payload.package_scope)
    req = MailboxRequest(
        requester_user_id=int(user.get("id") or 0),
        requested_email=str(payload.email_address).lower().strip(),
        desired_mode=payload.mode,
        package_name=payload.package_scope,
        status="pending",
        created_at=datetime.now(timezone.utc),
    )
    db.add(req)
    await db.commit()
    await db.refresh(req)
    await _audit(
        db,
        actor_user_id=user.get("id"),
        action="mailbox_request_create",
        ip=request.client.host if request.client else None,
        diff_json={"requested_email": req.requested_email},
        severity="info",
    )
    return {"request_id": req.id, "status": req.status}


@router.patch("/mailboxes/{mailbox_id}")
async def update_mailbox(
    mailbox_id: int,
    payload: MailboxUpdate,
    request: Request,
    user: Dict[str, Any] = Depends(_require_email_admin),
    db: AsyncSession = Depends(get_async_session),
) -> Dict[str, Any]:
    mailbox = await db.get(Mailbox, mailbox_id)
    if not mailbox:
        raise HTTPException(status_code=404, detail="Mailbox not found")

    for key, value in payload.dict(exclude_unset=True).items():
        if key in {"imap_password", "smtp_password"}:
            continue
        if key == "bot_code":
            normalized = _normalize_bot_code(str(value))
            if normalized in EMAIL_DISABLED_BOTS:
                raise HTTPException(status_code=400, detail=f"Email is disabled for bot '{normalized}'")
            value = normalized or None
        setattr(mailbox, key, value)
    mailbox.updated_at = datetime.now(timezone.utc)
    await db.commit()

    if payload.imap_password or payload.smtp_password:
        encrypted, key_version = encrypt_credentials(payload.imap_password or payload.smtp_password or "")
        creds = await db.get(MailboxCredentials, mailbox_id)
        if creds is None:
            creds = MailboxCredentials(mailbox_id=mailbox_id, credentials_ciphertext=encrypted, key_version=key_version)
            db.add(creds)
        else:
            creds.credentials_ciphertext = encrypted
            creds.key_version = key_version
            creds.rotated_at = datetime.now(timezone.utc)
        await db.commit()

    await _audit(
        db,
        actor_user_id=user.get("id"),
        action="mailbox_update",
        mailbox_id=mailbox_id,
        ip=request.client.host if request.client else None,
        diff_json=payload.dict(exclude_unset=True),
        severity="info",
    )
    await db.refresh(mailbox)
    return _mailbox_to_dict(mailbox)


@router.delete("/mailboxes/{mailbox_id}")
async def delete_mailbox(
    mailbox_id: int,
    request: Request,
    user: Dict[str, Any] = Depends(_require_email_admin),
    db: AsyncSession = Depends(get_async_session),
) -> Dict[str, Any]:
    mailbox = await db.get(Mailbox, mailbox_id)
    if not mailbox:
        raise HTTPException(status_code=404, detail="Mailbox not found")
    await db.delete(mailbox)
    await db.commit()
    await _audit(
        db,
        actor_user_id=user.get("id"),
        action="mailbox_delete",
        mailbox_id=mailbox_id,
        ip=request.client.host if request.client else None,
        diff_json={"email_address": mailbox.email_address},
        severity="warning",
    )
    return {"ok": True}


@router.post("/mailboxes/{mailbox_id}/rotate-credentials")
async def rotate_credentials(
    mailbox_id: int,
    payload: MailboxUpdate,
    request: Request,
    user: Dict[str, Any] = Depends(_require_email_admin),
    db: AsyncSession = Depends(get_async_session),
) -> Dict[str, Any]:
    mailbox = await db.get(Mailbox, mailbox_id)
    if not mailbox:
        raise HTTPException(status_code=404, detail="Mailbox not found")
    if not payload.imap_password and not payload.smtp_password:
        raise HTTPException(status_code=400, detail="Missing password to rotate")

    encrypted, key_version = encrypt_credentials(payload.imap_password or payload.smtp_password or "")
    creds = await db.get(MailboxCredentials, mailbox_id)
    if creds is None:
        creds = MailboxCredentials(mailbox_id=mailbox_id, credentials_ciphertext=encrypted, key_version=key_version)
        db.add(creds)
    else:
        creds.credentials_ciphertext = encrypted
        creds.key_version = key_version
        creds.rotated_at = datetime.now(timezone.utc)
    await db.commit()

    await _audit(
        db,
        actor_user_id=user.get("id"),
        action="mailbox_rotate_credentials",
        mailbox_id=mailbox_id,
        ip=request.client.host if request.client else None,
        severity="warning",
    )
    return {"ok": True}


@router.post("/mailboxes/{mailbox_id}/verify")
async def verify_mailbox(
    mailbox_id: int,
    request: Request,
    user: Dict[str, Any] = Depends(_require_email_admin),
    db: AsyncSession = Depends(get_async_session),
) -> Dict[str, Any]:
    mailbox = await db.get(Mailbox, mailbox_id)
    if not mailbox:
        raise HTTPException(status_code=404, detail="Mailbox not found")
    password = _get_mailbox_password(mailbox)
    if not password:
        raise HTTPException(status_code=400, detail="Mailbox credentials are missing")
    imap_host = mailbox.imap_host or ""
    imap_port = mailbox.imap_port or 993
    imap_user = mailbox.imap_user or mailbox.email_address
    imap_ssl = bool(mailbox.imap_ssl if mailbox.imap_ssl is not None else mailbox.use_tls)

    if not imap_host:
        raise HTTPException(status_code=400, detail="IMAP host not configured")

    error = None
    try:
        await asyncio.to_thread(
            _imap_fetch_messages,
            host=imap_host,
            port=int(imap_port),
            user=str(imap_user),
            password=password,
            use_ssl=imap_ssl,
        )
        mailbox.credentials.last_verified_at = datetime.now(timezone.utc)
        mailbox.credentials.last_error = None
    except Exception as exc:
        error = str(exc)
        mailbox.credentials.last_error = error
    await db.commit()

    await _audit(
        db,
        actor_user_id=user.get("id"),
        action="mailbox_verify",
        mailbox_id=mailbox_id,
        ip=request.client.host if request.client else None,
        diff_json={"error": error},
        severity="warning" if error else "info",
    )
    if error:
        raise HTTPException(status_code=400, detail=f"Mailbox verification failed: {error}")
    return {"ok": True, "verified_at": mailbox.credentials.last_verified_at}


@router.post("/mailboxes/{mailbox_id}/mode")
async def set_mailbox_mode(
    mailbox_id: int,
    payload: Dict[str, Any],
    user: Dict[str, Any] = Depends(_require_email_admin),
    db: AsyncSession = Depends(get_async_session),
) -> Dict[str, Any]:
    mailbox = await db.get(Mailbox, mailbox_id)
    if not mailbox:
        raise HTTPException(status_code=404, detail="Mailbox not found")
    mode = str(payload.get("mode") or "").upper()
    if mode not in {"BOT", "HUMAN"}:
        raise HTTPException(status_code=400, detail="Invalid mode")
    mailbox.mode = mode
    mailbox.updated_at = datetime.now(timezone.utc)
    await db.commit()
    return _mailbox_to_dict(mailbox)


@router.post("/mode")
async def set_global_mode(
    payload: Dict[str, Any],
    user: Dict[str, Any] = Depends(_require_email_admin),
    db: AsyncSession = Depends(get_async_session),
) -> Dict[str, Any]:
    mode = str(payload.get("mode") or "").upper()
    if mode not in {"BOT", "HUMAN"}:
        raise HTTPException(status_code=400, detail="Invalid mode")
    await db.execute(update(Mailbox).values(mode=mode))
    await db.commit()
    return {"ok": True, "mode": mode}


@router.get("/messages")
async def list_messages(
    mailbox_id: int,
    user: Dict[str, Any] = Depends(_require_email_admin),
    db: AsyncSession = Depends(get_async_session),
    limit: int = 50,
) -> List[Dict[str, Any]]:
    result = await db.execute(
        select(EmailMessageModel)
        .where(EmailMessageModel.mailbox_id == mailbox_id)
        .order_by(EmailMessageModel.created_at.desc())
        .limit(limit)
    )
    messages = result.scalars().all()
    return [_message_to_dict(msg) for msg in messages]


@router.get("/my/messages")
async def list_my_messages(
    mailbox_id: int,
    user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
    limit: int = 50,
) -> List[Dict[str, Any]]:
    user_id = int(user.get("id") or 0)
    mailbox = await db.get(Mailbox, mailbox_id)
    if not mailbox or mailbox.owner_user_id != user_id:
        raise HTTPException(status_code=403, detail="Mailbox access denied")
    result = await db.execute(
        select(EmailMessageModel)
        .where(EmailMessageModel.mailbox_id == mailbox_id)
        .order_by(EmailMessageModel.created_at.desc())
        .limit(limit)
    )
    messages = result.scalars().all()
    return [_message_to_dict(msg) for msg in messages]


@router.get("/my/messages/{message_id}")
async def get_my_message(
    message_id: int,
    user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
) -> Dict[str, Any]:
    msg = await db.get(EmailMessageModel, message_id)
    if not msg:
        raise HTTPException(status_code=404, detail="Message not found")
    mailbox = await db.get(Mailbox, msg.mailbox_id)
    if not mailbox or mailbox.owner_user_id != int(user.get("id") or 0):
        raise HTTPException(status_code=403, detail="Mailbox access denied")
    attachments = await db.execute(select(EmailAttachment).where(EmailAttachment.message_id == msg.id))
    return _message_to_dict(msg, attachments.scalars().all())


@router.get("/threads")
async def list_threads(
    mailbox_id: Optional[int] = None,
    user: Dict[str, Any] = Depends(_require_email_admin),
    db: AsyncSession = Depends(get_async_session),
    limit: int = 50,
) -> Dict[str, Any]:
    query = select(EmailThread).order_by(EmailThread.last_message_at.desc())
    if mailbox_id is not None:
        query = query.where(EmailThread.mailbox_id == mailbox_id)
    result = await db.execute(query.limit(limit))
    threads = result.scalars().all()
    return {"threads": [_thread_to_dict(t) for t in threads], "count": len(threads)}


@router.get("/threads/{thread_id}/messages")
async def get_thread_messages(
    thread_id: int,
    user: Dict[str, Any] = Depends(_require_email_admin),
    db: AsyncSession = Depends(get_async_session),
) -> Dict[str, Any]:
    messages = await db.execute(
        select(EmailMessageModel)
        .where(EmailMessageModel.thread_id == thread_id)
        .order_by(EmailMessageModel.created_at.asc())
    )
    return {"thread_id": thread_id, "messages": [_message_to_dict(m) for m in messages.scalars().all()]}


@router.get("/threads/{thread_id}")
async def get_thread(
    thread_id: int,
    user: Dict[str, Any] = Depends(_require_email_admin),
    db: AsyncSession = Depends(get_async_session),
) -> Dict[str, Any]:
    thread = await db.get(EmailThread, thread_id)
    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")
    messages = await db.execute(
        select(EmailMessageModel)
        .where(EmailMessageModel.thread_id == thread_id)
        .order_by(EmailMessageModel.created_at.asc())
    )
    return {"thread": _thread_to_dict(thread), "messages": [_message_to_dict(m) for m in messages.scalars().all()]}


@router.patch("/threads/{thread_id}")
async def update_thread(
    thread_id: int,
    payload: ThreadUpdate,
    user: Dict[str, Any] = Depends(_require_email_admin),
    db: AsyncSession = Depends(get_async_session),
) -> Dict[str, Any]:
    thread = await db.get(EmailThread, thread_id)
    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")
    for key, value in payload.dict(exclude_unset=True).items():
        setattr(thread, key, value)
    thread.updated_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(thread)
    return _thread_to_dict(thread)


@router.post("/messages/{message_id}/approve")
async def approve_message(
    message_id: int,
    user: Dict[str, Any] = Depends(_require_email_admin),
    db: AsyncSession = Depends(get_async_session),
) -> Dict[str, Any]:
    msg = await db.get(EmailMessageModel, message_id)
    if not msg:
        raise HTTPException(status_code=404, detail="Message not found")
    msg.status = "processed"
    await db.commit()
    return _message_to_dict(msg)


@router.post("/poll")
async def poll_mailboxes(
    request: Request,
    user: Dict[str, Any] = Depends(_require_email_admin),
    db: AsyncSession = Depends(get_async_session),
) -> Dict[str, Any]:
    result = await db.execute(
        select(Mailbox)
        .options(selectinload(Mailbox.credentials))
        .where(
            Mailbox.is_enabled == True,
            Mailbox.polling_enabled == True,
            Mailbox.inbound_enabled == True,
        )
    )
    mailboxes = result.scalars().all()
    processed = 0
    polled = 0
    skipped_missing_imap_host = 0
    skipped_missing_credentials = 0
    failed = 0
    mailbox_results: List[Dict[str, Any]] = []
    for mailbox in mailboxes:
        if not mailbox.imap_host:
            skipped_missing_imap_host += 1
            mailbox_results.append(
                {
                    "mailbox_id": mailbox.id,
                    "email_address": mailbox.email_address,
                    "status": "skipped",
                    "reason": "missing_imap_host",
                }
            )
            continue
        password = _get_mailbox_password(mailbox, allow_fallback=True)
        if not password:
            logger.warning("Skipping mailbox %s: missing credentials", mailbox.email_address)
            skipped_missing_credentials += 1
            mailbox_results.append(
                {
                    "mailbox_id": mailbox.id,
                    "email_address": mailbox.email_address,
                    "status": "skipped",
                    "reason": "missing_credentials",
                }
            )
            continue
        plan = _poll_plan_for_mailbox(mailbox)
        try:
            messages = await asyncio.to_thread(
                _imap_fetch_messages,
                host=mailbox.imap_host,
                port=int(mailbox.imap_port or 993),
                user=str(mailbox.imap_user or mailbox.email_address),
                password=password,
                use_ssl=bool(mailbox.imap_ssl if mailbox.imap_ssl is not None else mailbox.use_tls),
                min_uid=plan["min_uid"],
                since_days=plan["since_days"],
                limit=plan["limit"],
            )
            polled += 1
            ingested = 0
            max_uid = None
            last_message_id = None
            for raw in messages:
                imap_uid = raw.get("uid") if isinstance(raw, dict) else None
                payload = raw.get("raw") if isinstance(raw, dict) else raw
                if imap_uid is not None:
                    max_uid = imap_uid if max_uid is None else max(max_uid, imap_uid)
                saved = await _handle_inbound_message(db, mailbox, payload, imap_uid=imap_uid)
                if saved:
                    processed += 1
                    ingested += 1
                    if saved.message_id:
                        last_message_id = saved.message_id
                    await _audit(
                        db,
                        actor_user_id=user.get("id"),
                        action="email_ingested",
                        mailbox_id=mailbox.id,
                        message_id=saved.id,
                        ip=request.client.host if request.client else None,
                        severity="info",
                    )
            await _update_mailbox_sync_state(
                db,
                mailbox,
                max_uid=max_uid,
                last_message_id=last_message_id,
            )
            mailbox_results.append(
                {
                    "mailbox_id": mailbox.id,
                    "email_address": mailbox.email_address,
                    "status": "ok",
                    "fetched": len(messages),
                    "processed": ingested,
                }
            )
        except Exception as exc:
            failed += 1
            error = str(exc)
            logger.exception("Polling mailbox %s failed", mailbox.email_address)
            if mailbox.credentials:
                mailbox.credentials.last_error = error
                await db.commit()
            mailbox_results.append(
                {
                    "mailbox_id": mailbox.id,
                    "email_address": mailbox.email_address,
                    "status": "error",
                    "reason": error,
                }
            )
    return {
        "ok": True,
        "processed": processed,
        "mailboxes_checked": len(mailboxes),
        "mailboxes_polled": polled,
        "mailboxes_failed": failed,
        "skipped": {
            "missing_imap_host": skipped_missing_imap_host,
            "missing_credentials": skipped_missing_credentials,
        },
        "results": mailbox_results,
    }


@router.post("/send")
async def send_message(
    payload: SendMessageIn,
    request: Request,
    user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
) -> Dict[str, Any]:
    mailbox = await db.get(Mailbox, payload.mailbox_id)
    if not mailbox:
        raise HTTPException(status_code=404, detail="Mailbox not found")

    normalized_bot = _normalize_bot_code(mailbox.bot_code)
    if normalized_bot == "legal_consultant":
        raise HTTPException(
            status_code=403,
            detail="Legal consultant email must route via operations_manager.",
        )
    if normalized_bot in EMAIL_DISABLED_BOTS:
        raise HTTPException(status_code=403, detail=f"Email is disabled for bot '{normalized_bot}'")

    if not _is_email_admin(user) and mailbox.owner_user_id != int(user.get("id") or 0):
        raise HTTPException(status_code=403, detail="Mailbox access denied")

    if not mailbox.outbound_enabled:
        raise HTTPException(status_code=403, detail="Outbound is disabled for this mailbox")

    if mailbox.email_address and mailbox.email_address.lower() == NO_REPLY_EMAIL.lower():
        if mailbox.inbound_enabled:
            raise HTTPException(status_code=400, detail="No-reply mailbox cannot receive inbound email")

    if payload.send:
        out = await _send_outbound(
            db=db,
            mailbox=mailbox,
            to_addrs=_normalize_addrs(payload.to),
            subject=payload.subject,
            body=payload.body,
            html=payload.html,
        )
    else:
        out = EmailMessageModel(
            mailbox_id=mailbox.id,
            direction="outbound",
            from_addr=mailbox.email_address,
            to_addrs=_normalize_addrs(payload.to),
            subject=payload.subject,
            body_preview=payload.body[:500],
            status="draft",
            created_at=datetime.now(timezone.utc),
        )
        db.add(out)
        await db.commit()
        await db.refresh(out)

    await _audit(
        db,
        actor_user_id=user.get("id"),
        action="email_send",
        mailbox_id=mailbox.id,
        message_id=out.id,
        ip=request.client.host if request.client else None,
        severity="info",
    )
    return _message_to_dict(out)


@router.get("/requests")
async def list_requests(
    user: Dict[str, Any] = Depends(_require_email_admin),
    db: AsyncSession = Depends(get_async_session),
) -> List[Dict[str, Any]]:
    result = await db.execute(select(MailboxRequest).order_by(MailboxRequest.created_at.desc()))
    return [
        {
            "id": r.id,
            "requester_user_id": r.requester_user_id,
            "requested_email": r.requested_email,
            "desired_mode": r.desired_mode,
            "package_name": r.package_name,
            "status": r.status,
            "approved_by": r.approved_by,
            "decided_at": r.decided_at,
            "reason": r.reason,
            "created_at": r.created_at,
        }
        for r in result.scalars().all()
    ]


@router.post("/requests")
async def create_request(
    payload: MailboxRequestIn,
    request: Request,
    user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
) -> Dict[str, Any]:
    await _assert_package_limit(db, user, payload.package_name)
    req = MailboxRequest(
        requester_user_id=int(user.get("id") or 0),
        requested_email=str(payload.requested_email).lower().strip(),
        desired_mode=payload.desired_mode,
        package_name=payload.package_name,
        status="pending",
        created_at=datetime.now(timezone.utc),
    )
    db.add(req)
    await db.commit()
    await db.refresh(req)
    await _audit(
        db,
        actor_user_id=user.get("id"),
        action="mailbox_request_create",
        ip=request.client.host if request.client else None,
        diff_json={"requested_email": req.requested_email},
        severity="info",
    )
    return {"id": req.id, "status": req.status}


@router.post("/requests/{request_id}/approve")
async def approve_request(
    request_id: int,
    decision: MailboxRequestDecision,
    request: Request,
    user: Dict[str, Any] = Depends(_require_email_admin),
    db: AsyncSession = Depends(get_async_session),
) -> Dict[str, Any]:
    req = await db.get(MailboxRequest, request_id)
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")
    if req.status != "pending":
        raise HTTPException(status_code=400, detail="Request already processed")

    mailbox = Mailbox(
        owner_user_id=req.requester_user_id,
        email_address=req.requested_email,
        display_name=req.requested_email,
        mode=req.desired_mode,
        direction="INBOUND_OUTBOUND",
        inbound_enabled=True,
        outbound_enabled=True,
        is_enabled=True,
        polling_enabled=False,
        auto_reply_enabled=False,
        package_scope="USER",
        created_at=datetime.now(timezone.utc),
    )
    db.add(mailbox)
    req.status = "approved"
    req.approved_by = int(user.get("id") or 0)
    req.decided_at = datetime.now(timezone.utc)
    req.reason = decision.reason
    await db.commit()

    await _audit(
        db,
        actor_user_id=user.get("id"),
        action="mailbox_request_approve",
        mailbox_id=mailbox.id,
        ip=request.client.host if request.client else None,
        diff_json={"requested_email": req.requested_email},
        severity="info",
    )
    return {"ok": True, "mailbox_id": mailbox.id}


@router.post("/requests/{request_id}/reject")
async def reject_request(
    request_id: int,
    decision: MailboxRequestDecision,
    request: Request,
    user: Dict[str, Any] = Depends(_require_email_admin),
    db: AsyncSession = Depends(get_async_session),
) -> Dict[str, Any]:
    req = await db.get(MailboxRequest, request_id)
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")
    if req.status != "pending":
        raise HTTPException(status_code=400, detail="Request already processed")

    req.status = "rejected"
    req.approved_by = int(user.get("id") or 0)
    req.decided_at = datetime.now(timezone.utc)
    req.reason = decision.reason
    await db.commit()

    await _audit(
        db,
        actor_user_id=user.get("id"),
        action="mailbox_request_reject",
        ip=request.client.host if request.client else None,
        diff_json={"requested_email": req.requested_email},
        severity="warning",
    )
    return {"ok": True}


@router.get("/audit")
async def list_audit_logs(
    user: Dict[str, Any] = Depends(_require_email_admin),
    db: AsyncSession = Depends(get_async_session),
    limit: int = 100,
) -> List[Dict[str, Any]]:
    result = await db.execute(
        select(EmailAuditLog).order_by(EmailAuditLog.created_at.desc()).limit(limit)
    )
    return [
        {
            "id": log.id,
            "actor_user_id": log.actor_user_id,
            "action": log.action,
            "mailbox_id": log.mailbox_id,
            "message_id": log.message_id,
            "ip": log.ip,
            "diff_json": log.diff_json,
            "created_at": log.created_at,
            "severity": log.severity,
        }
        for log in result.scalars().all()
    ]
