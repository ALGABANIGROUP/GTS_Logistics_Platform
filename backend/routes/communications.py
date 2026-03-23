from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.session import get_async_session
from backend.models.email_center import EmailMessage
from backend.security.auth import get_current_user
from backend.services.push_service import push_service
from backend.services.quo_service_enhanced import quo_service
from backend.services.sms_service import sms_service
from backend.services.whatsapp_service import whatsapp_service

router = APIRouter(prefix="/api/v1/communications", tags=["Communications"])


def _start_date(range_name: str) -> datetime:
    now = datetime.utcnow()
    if range_name == "today":
        return now.replace(hour=0, minute=0, second=0, microsecond=0)
    if range_name == "month":
        return now - timedelta(days=30)
    if range_name == "quarter":
        return now - timedelta(days=90)
    return now - timedelta(days=7)


async def _safe_email_count(db: AsyncSession, start_date: datetime, bot_name: str | None = None) -> int:
    try:
        stmt = select(func.count()).select_from(EmailMessage).where(EmailMessage.created_at >= start_date)
        if bot_name:
            stmt = stmt.where(
                (EmailMessage.processed_by_bot == bot_name) | (EmailMessage.assigned_bot == bot_name)
            )
        value = await db.scalar(stmt)
        return int(value or 0)
    except Exception:
        return 0


@router.get("/stats")
async def get_communication_stats(
    range: str = Query("week", pattern="^(today|week|month|quarter)$"),
    db: AsyncSession = Depends(get_async_session),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    del current_user
    start_date = _start_date(range)
    email_count = await _safe_email_count(db, start_date)
    call_history = await quo_service.get_call_history(days=90)
    call_count = sum(
        1
        for item in call_history
        if str(item.get("started_at") or item.get("created_at") or "") >= start_date.isoformat()
    )
    sms_count = 0
    whatsapp_count = 0
    push_count = sum(len(tokens) for tokens in push_service.device_tokens.values()) if push_service.device_tokens else 0
    total = email_count + call_count + sms_count + whatsapp_count + push_count
    return {
        "total": total,
        "emails": email_count,
        "calls": call_count,
        "sms": sms_count,
        "whatsapp": whatsapp_count,
        "push": push_count,
        "services": {
            "sms_enabled": sms_service.enabled,
            "whatsapp_enabled": whatsapp_service.enabled,
            "push_enabled": push_service.enabled,
        },
        "period": range,
    }


@router.get("/bot-stats")
async def get_bot_communication_stats(
    db: AsyncSession = Depends(get_async_session),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    del current_user
    bots = [
        "customer_service",
        "freight_broker",
        "finance_bot",
        "documents_manager",
        "safety_manager",
        "security_manager",
        "operations_manager",
        "general_manager",
        "system_admin",
        "sales_team",
        "partner_manager",
        "maintenance_dev",
        "legal_consultant",
        "strategy_advisor",
        "information_coordinator",
        "mapleload_canada",
    ]
    history = await quo_service.get_call_history(days=30)
    results: List[Dict[str, Any]] = []
    start_date = _start_date("month")
    for bot in bots:
        email_count = await _safe_email_count(db, start_date, bot)
        bot_calls = [item for item in history if item.get("bot_name") == bot]
        sentiments = [
            (
                item.get("sentiment", {}).get("overall_sentiment")
                if isinstance(item.get("sentiment"), dict)
                else None
            )
            for item in bot_calls
        ]
        sentiments = [s for s in sentiments if s]
        avg_sentiment = sentiments[0] if sentiments else "neutral"
        results.append(
            {
                "bot_name": bot,
                "email_count": email_count,
                "call_count": len(bot_calls),
                "sms_count": 0,
                "whatsapp_count": 0,
                "push_count": 0,
                "status": "active",
                "avg_sentiment": avg_sentiment,
            }
        )
    return {"bots": results}


@router.get("/recent")
async def get_recent_communications(
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_async_session),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    del current_user
    communications: List[Dict[str, Any]] = []
    try:
        result = await db.execute(
            select(EmailMessage).order_by(EmailMessage.created_at.desc()).limit(limit)
        )
        for email in result.scalars().all():
            communications.append(
                {
                    "timestamp": email.created_at.isoformat() if email.created_at else None,
                    "channel": "email",
                    "direction": "incoming" if email.direction == "inbound" else "outgoing",
                    "bot_name": email.processed_by_bot or email.assigned_bot or "unknown",
                    "status": email.status or "success",
                    "sentiment": "neutral",
                    "summary": email.subject or "No subject",
                }
            )
    except Exception:
        pass

    for call in (await quo_service.get_call_history(days=7))[:limit]:
        sentiment = call.get("sentiment")
        if isinstance(sentiment, dict):
            sentiment_value = sentiment.get("overall_sentiment", "neutral")
        else:
            sentiment_value = "neutral"
        communications.append(
            {
                "timestamp": call.get("started_at") or call.get("created_at"),
                "channel": "call",
                "direction": call.get("direction", "outgoing"),
                "bot_name": call.get("bot_name") or "customer_service",
                "status": call.get("status", "completed"),
                "sentiment": sentiment_value,
                "summary": call.get("summary") or call.get("purpose") or "Customer call",
            }
        )

    communications.sort(key=lambda item: item.get("timestamp") or "", reverse=True)
    return {"communications": communications[:limit]}


@router.get("/sentiment-trends")
async def get_sentiment_trends(
    range: str = Query("week", pattern="^(today|week|month|quarter)$"),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    del current_user
    days = {"today": 1, "week": 7, "month": 30, "quarter": 90}.get(range, 7)
    history = await quo_service.get_call_history(days=days)
    positive = neutral = negative = 0
    trend_map: Dict[str, Dict[str, Any]] = {}
    for item in history:
        raw_ts = str(item.get("started_at") or item.get("created_at") or "")
        date_key = raw_ts.split("T")[0] if "T" in raw_ts else raw_ts[:10] or datetime.utcnow().date().isoformat()
        trend_entry = trend_map.setdefault(date_key, {"date": date_key, "positive": 0, "neutral": 0, "negative": 0})
        sentiment = item.get("sentiment")
        if isinstance(sentiment, dict):
            value = sentiment.get("overall_sentiment", "neutral")
        else:
            value = "neutral"
        if value == "positive":
            positive += 1
            trend_entry["positive"] += 1
        elif value == "negative":
            negative += 1
            trend_entry["negative"] += 1
        else:
            neutral += 1
            trend_entry["neutral"] += 1
    trend = [trend_map[key] for key in sorted(trend_map.keys())]
    return {"positive": positive, "neutral": neutral, "negative": negative, "trend": trend}


@router.get("/test/{channel}")
async def send_test_communication(
    channel: str,
    to: str | None = None,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    del current_user
    target = (to or "").strip()
    results: Dict[str, Any] = {}
    if channel in {"email", "all"}:
        results["email"] = {"status": "ready", "to": target or "set ?to=email@example.com"}
    if channel in {"call", "all"}:
        results["call"] = {"status": "ready", "to": target or "set ?to=+15551234567"}
    if channel in {"sms", "all"}:
        results["sms"] = {"status": "enabled" if sms_service.enabled else "disabled", "to": target or "set ?to=+15551234567"}
    if channel in {"whatsapp", "all"}:
        results["whatsapp"] = {"status": "enabled" if whatsapp_service.enabled else "disabled", "to": target or "set ?to=+15551234567"}
    if channel in {"push", "all"}:
        results["push"] = {"status": "enabled" if push_service.enabled else "disabled", "registered_devices": sum(len(tokens) for tokens in push_service.device_tokens.values())}
    return {"success": True, "channel": channel, "results": results}
