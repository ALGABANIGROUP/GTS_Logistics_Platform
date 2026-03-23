from __future__ import annotations

from collections import Counter
from typing import Any, Dict, List, Sequence

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.session import get_async_session
from backend.models.email_center import EmailMessage
from backend.models.email_feedback import EmailFeedback
from backend.routes.email_center import _require_email_admin
from backend.services.email_learning import EmailLearningService


router = APIRouter(prefix="/api/v1/email/ai/stats", tags=["Email AI Stats"])


async def _load_analyzed_messages(db: AsyncSession) -> List[EmailMessage]:
    result = await db.execute(
        select(EmailMessage)
        .where(EmailMessage.analysis_result.is_not(None))
        .order_by(EmailMessage.analyzed_at.desc().nullslast(), EmailMessage.id.desc())
    )
    return list(result.scalars().all())


async def _load_feedback_items(db: AsyncSession) -> List[EmailFeedback]:
    result = await db.execute(
        select(EmailFeedback).order_by(EmailFeedback.created_at.desc(), EmailFeedback.id.desc())
    )
    return list(result.scalars().all())


def _build_recommendations(
    metrics: Sequence[Any],
    decision_counts: Dict[str, int],
    sentiment_counts: Dict[str, int],
) -> List[str]:
    recommendations: List[str] = []

    weak_bots = [item.bot_key for item in metrics if item.feedback_count >= 3 and item.accuracy_rate < 0.6]
    if weak_bots:
        recommendations.append(
            f"Review routing rules or prompts for: {', '.join(sorted(weak_bots))}."
        )

    ai_count = decision_counts.get("ai", 0)
    rule_count = decision_counts.get("rule", 0)
    if ai_count > rule_count:
        recommendations.append("AI routing is dominant. Monitor confidence thresholds closely.")

    negative_share = sentiment_counts.get("negative", 0)
    positive_share = sentiment_counts.get("positive", 0)
    if negative_share > positive_share:
        recommendations.append("Negative sentiment is elevated. Prioritize escalation and response SLAs.")

    if not recommendations:
        recommendations.append("Routing performance looks stable. Keep collecting feedback for stronger learning signals.")

    return recommendations


@router.get("/bots")
async def get_bot_stats(
    db: AsyncSession = Depends(get_async_session),
    _user: Dict[str, Any] = Depends(_require_email_admin),
):
    service = EmailLearningService(db)
    metrics = await service.get_all_bot_learning_metrics()
    payload = [
        {
            "bot_key": item.bot_key,
            "feedback_count": item.feedback_count,
            "average_rating": item.average_rating,
            "accuracy_rate": item.accuracy_rate,
            "incorrect_rate": item.incorrect_rate,
            "average_routing_confidence": item.average_routing_confidence,
            "source_breakdown": item.source_breakdown,
        }
        for item in metrics
    ]
    return {
        "bots": payload,
        "summary": {
            "bot_count": len(payload),
            "total_feedback": sum(item["feedback_count"] for item in payload),
            "average_accuracy": round(
                (sum(item["accuracy_rate"] for item in payload) / len(payload)) if payload else 0.0,
                2,
            ),
        },
    }


@router.get("/trends")
async def get_sentiment_trends(
    db: AsyncSession = Depends(get_async_session),
    _user: Dict[str, Any] = Depends(_require_email_admin),
):
    messages = await _load_analyzed_messages(db)
    sentiment_counts = Counter()
    urgency_counts = Counter()
    category_counts = Counter()

    for message in messages:
        analysis = message.analysis_result if isinstance(message.analysis_result, dict) else {}
        sentiment = analysis.get("sentiment") or {}
        sentiment_counts[str(sentiment.get("label") or "unknown").lower()] += 1
        urgency_counts[str(sentiment.get("urgency") or "unknown").lower()] += 1
        category_counts[str(analysis.get("category") or "general").lower()] += 1

    total = sum(sentiment_counts.values())
    return {
        "sentiment": dict(sentiment_counts),
        "urgency": dict(urgency_counts),
        "categories": dict(category_counts),
        "summary": {
            "analyzed_messages": total,
            "dominant_sentiment": sentiment_counts.most_common(1)[0][0] if sentiment_counts else "unknown",
            "dominant_category": category_counts.most_common(1)[0][0] if category_counts else "general",
        },
    }


@router.get("/decisions")
async def get_decision_matrix(
    db: AsyncSession = Depends(get_async_session),
    _user: Dict[str, Any] = Depends(_require_email_admin),
):
    messages = await _load_analyzed_messages(db)
    feedback_items = await _load_feedback_items(db)
    learning_service = EmailLearningService(db)
    bot_metrics = await learning_service.get_all_bot_learning_metrics()

    decision_counts = Counter()
    confidence_buckets = {"high": 0, "medium": 0, "low": 0}

    for message in messages:
        analysis = message.analysis_result if isinstance(message.analysis_result, dict) else {}
        source = str(analysis.get("route_source") or "unknown").lower()
        decision_counts[source] += 1
        confidence = analysis.get("routing_confidence")
        try:
            value = float(confidence)
        except (TypeError, ValueError):
            value = 0.0
        if value >= 0.85:
            confidence_buckets["high"] += 1
        elif value >= 0.65:
            confidence_buckets["medium"] += 1
        else:
            confidence_buckets["low"] += 1

    feedback_by_source = Counter((item.routing_source or "unknown").lower() for item in feedback_items)
    correct_by_source = Counter(
        (item.routing_source or "unknown").lower() for item in feedback_items if item.was_correct
    )
    source_accuracy = {}
    for source, count in feedback_by_source.items():
        source_accuracy[source] = round(correct_by_source.get(source, 0) / count, 2) if count else 0.0

    sentiment_counts = Counter()
    for message in messages:
        analysis = message.analysis_result if isinstance(message.analysis_result, dict) else {}
        sentiment = analysis.get("sentiment") or {}
        sentiment_counts[str(sentiment.get("label") or "unknown").lower()] += 1

    return {
        "decision_counts": dict(decision_counts),
        "confidence_buckets": confidence_buckets,
        "feedback_by_source": dict(feedback_by_source),
        "source_accuracy": source_accuracy,
        "recommendations": _build_recommendations(bot_metrics, dict(decision_counts), dict(sentiment_counts)),
        "summary": {
            "routed_messages": sum(decision_counts.values()),
            "feedback_items": len(feedback_items),
        },
    }
