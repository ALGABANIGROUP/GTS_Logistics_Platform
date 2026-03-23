from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from backend.models.email_center import EmailMessage
from backend.models.email_feedback import EmailFeedback
from backend.routes import email_ai_stats as email_ai_stats_module


class FakeMetrics:
    def __init__(
        self,
        bot_key,
        feedback_count,
        average_rating,
        accuracy_rate,
        incorrect_rate,
        average_routing_confidence,
        source_breakdown,
    ):
        self.bot_key = bot_key
        self.feedback_count = feedback_count
        self.average_rating = average_rating
        self.accuracy_rate = accuracy_rate
        self.incorrect_rate = incorrect_rate
        self.average_routing_confidence = average_routing_confidence
        self.source_breakdown = source_breakdown


class FakeLearningService:
    def __init__(self, db):
        self.db = db

    async def get_all_bot_learning_metrics(self):
        return [
            FakeMetrics("finance_bot", 4, 4.5, 0.75, 0.25, 0.86, {"ai": 3, "rule": 1}),
            FakeMetrics("customer_service", 3, 2.67, 0.33, 0.67, 0.72, {"ai": 2, "mailbox_default": 1}),
        ]


@pytest.fixture
def stats_test_app(monkeypatch):
    app = FastAPI()
    app.include_router(email_ai_stats_module.router)
    current_user = {"id": 1, "role": "super_admin", "effective_role": "super_admin"}

    analyzed_messages = [
        EmailMessage(
            id=1,
            mailbox_id=1,
            direction="inbound",
            subject="Invoice issue",
            analysis_result={
                "category": "billing",
                "route_source": "ai",
                "routing_confidence": 0.91,
                "sentiment": {"label": "negative", "urgency": "high"},
            },
            analyzed_at=datetime.now(timezone.utc),
        ),
        EmailMessage(
            id=2,
            mailbox_id=1,
            direction="inbound",
            subject="Support request",
            analysis_result={
                "category": "support",
                "route_source": "rule",
                "routing_confidence": 0.74,
                "sentiment": {"label": "neutral", "urgency": "medium"},
            },
            analyzed_at=datetime.now(timezone.utc),
        ),
        EmailMessage(
            id=3,
            mailbox_id=1,
            direction="inbound",
            subject="General follow-up",
            analysis_result={
                "category": "general",
                "route_source": "mailbox_default",
                "routing_confidence": 0.55,
                "sentiment": {"label": "positive", "urgency": "low"},
            },
            analyzed_at=datetime.now(timezone.utc),
        ),
    ]
    feedback_items = [
        EmailFeedback(
            id=1,
            message_id=1,
            bot_key="finance_bot",
            rating=5,
            was_correct=True,
            routing_source="ai",
            routing_confidence=0.91,
            created_at=datetime.now(timezone.utc),
        ),
        EmailFeedback(
            id=2,
            message_id=2,
            bot_key="customer_service",
            rating=2,
            was_correct=False,
            routing_source="rule",
            routing_confidence=0.74,
            created_at=datetime.now(timezone.utc),
        ),
    ]

    async def fake_current_user():
        return current_user

    async def fake_db():
        yield object()

    async def fake_load_messages(_db):
        return analyzed_messages

    async def fake_load_feedback(_db):
        return feedback_items

    monkeypatch.setattr(email_ai_stats_module, "EmailLearningService", FakeLearningService)
    monkeypatch.setattr(email_ai_stats_module, "_load_analyzed_messages", fake_load_messages)
    monkeypatch.setattr(email_ai_stats_module, "_load_feedback_items", fake_load_feedback)
    app.dependency_overrides[email_ai_stats_module._require_email_admin] = fake_current_user
    app.dependency_overrides[email_ai_stats_module.get_async_session] = fake_db
    return app


@pytest.fixture
async def stats_client(stats_test_app):
    transport = ASGITransport(app=stats_test_app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client


@pytest.mark.asyncio
async def test_get_bot_stats_returns_learning_summary(stats_client):
    response = await stats_client.get("/api/v1/email/ai/stats/bots")

    assert response.status_code == 200
    payload = response.json()
    assert payload["summary"]["bot_count"] == 2
    assert payload["bots"][0]["bot_key"] == "finance_bot"


@pytest.mark.asyncio
async def test_get_sentiment_trends_returns_aggregated_counts(stats_client):
    response = await stats_client.get("/api/v1/email/ai/stats/trends")

    assert response.status_code == 200
    payload = response.json()
    assert payload["sentiment"] == {"negative": 1, "neutral": 1, "positive": 1}
    assert payload["summary"]["dominant_category"] in {"billing", "support", "general"}


@pytest.mark.asyncio
async def test_get_decision_matrix_returns_counts_and_recommendations(stats_client):
    response = await stats_client.get("/api/v1/email/ai/stats/decisions")

    assert response.status_code == 200
    payload = response.json()
    assert payload["decision_counts"] == {"ai": 1, "rule": 1, "mailbox_default": 1}
    assert payload["confidence_buckets"] == {"high": 1, "medium": 1, "low": 1}
    assert payload["feedback_by_source"] == {"ai": 1, "rule": 1}
    assert isinstance(payload["recommendations"], list)
    assert payload["summary"]["routed_messages"] == 3
