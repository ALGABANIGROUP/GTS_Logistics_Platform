from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.email_center import EmailMessage
from backend.models.email_feedback import EmailFeedback


@dataclass
class BotLearningMetrics:
    bot_key: str
    feedback_count: int
    average_rating: float
    accuracy_rate: float
    incorrect_rate: float
    average_routing_confidence: float
    source_breakdown: Dict[str, int]


class EmailLearningService:
    """Persist email routing feedback and derive lightweight learning metrics."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def submit_feedback(
        self,
        *,
        message_id: int,
        rating: int,
        was_correct: bool,
        user_comment: Optional[str] = None,
        created_by: Optional[int] = None,
        bot_key: Optional[str] = None,
    ) -> EmailFeedback:
        if rating < 1 or rating > 5:
            raise ValueError("Rating must be between 1 and 5")

        message = await self.db.get(EmailMessage, message_id)
        if not message:
            raise ValueError(f"Message {message_id} not found")

        analysis = message.analysis_result if isinstance(message.analysis_result, dict) else {}
        feedback = EmailFeedback(
            message_id=message_id,
            bot_key=bot_key or message.processed_by_bot or message.assigned_bot,
            rating=rating,
            was_correct=was_correct,
            user_comment=user_comment,
            routing_source=analysis.get("route_source"),
            routing_confidence=self._normalize_confidence(analysis.get("routing_confidence")),
            created_by=created_by,
        )
        self.db.add(feedback)
        await self.db.commit()
        await self.db.refresh(feedback)
        return feedback

    async def get_bot_learning_metrics(self, bot_key: str) -> BotLearningMetrics:
        feedback_items = await self._load_feedback(bot_key=bot_key)
        return self._build_metrics(bot_key, feedback_items)

    async def get_all_bot_learning_metrics(self) -> List[BotLearningMetrics]:
        feedback_items = await self._load_feedback()
        grouped: Dict[str, List[EmailFeedback]] = {}
        for item in feedback_items:
            key = item.bot_key or "unassigned"
            grouped.setdefault(key, []).append(item)
        return [self._build_metrics(bot_key, items) for bot_key, items in sorted(grouped.items())]

    async def get_confidence_adjustment(self, bot_key: str) -> float:
        metrics = await self.get_bot_learning_metrics(bot_key)
        if metrics.feedback_count < 3:
            return 0.0

        adjustment = 0.0
        adjustment += (metrics.accuracy_rate - 0.5) * 0.2
        adjustment += ((metrics.average_rating / 5.0) - 0.5) * 0.1
        return round(max(-0.15, min(adjustment, 0.15)), 2)

    async def _load_feedback(self, bot_key: Optional[str] = None) -> List[EmailFeedback]:
        stmt = select(EmailFeedback).order_by(EmailFeedback.created_at.desc(), EmailFeedback.id.desc())
        if bot_key:
            stmt = stmt.where(EmailFeedback.bot_key == bot_key)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    def _build_metrics(self, bot_key: str, feedback_items: List[EmailFeedback]) -> BotLearningMetrics:
        if not feedback_items:
            return BotLearningMetrics(
                bot_key=bot_key,
                feedback_count=0,
                average_rating=0.0,
                accuracy_rate=0.0,
                incorrect_rate=0.0,
                average_routing_confidence=0.0,
                source_breakdown={},
            )

        feedback_count = len(feedback_items)
        rating_sum = sum(item.rating for item in feedback_items)
        correct_count = sum(1 for item in feedback_items if item.was_correct)
        confidence_values = [item.routing_confidence for item in feedback_items if item.routing_confidence is not None]

        source_breakdown: Dict[str, int] = {}
        for item in feedback_items:
            source = item.routing_source or "unknown"
            source_breakdown[source] = source_breakdown.get(source, 0) + 1

        average_rating = round(rating_sum / feedback_count, 2)
        accuracy_rate = round(correct_count / feedback_count, 2)
        average_routing_confidence = round(
            (sum(confidence_values) / len(confidence_values)) if confidence_values else 0.0,
            2,
        )

        return BotLearningMetrics(
            bot_key=bot_key,
            feedback_count=feedback_count,
            average_rating=average_rating,
            accuracy_rate=accuracy_rate,
            incorrect_rate=round(1 - accuracy_rate, 2),
            average_routing_confidence=average_routing_confidence,
            source_breakdown=source_breakdown,
        )

    def _normalize_confidence(self, value: Any) -> Optional[float]:
        try:
            return round(max(0.0, min(float(value), 1.0)), 2)
        except (TypeError, ValueError):
            return None
