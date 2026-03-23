from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import AsyncMock, Mock

import pytest

from backend.models.email_center import EmailMessage
from backend.models.email_feedback import EmailFeedback
from backend.services.email_learning import EmailLearningService


@pytest.fixture
def mock_db():
    db = AsyncMock()
    db.get = AsyncMock()
    db.execute = AsyncMock()
    db.add = Mock()
    db.commit = AsyncMock()
    db.refresh = AsyncMock()
    return db


@pytest.fixture
def sample_message():
    message = EmailMessage(
        id=15,
        mailbox_id=3,
        direction="inbound",
        subject="Invoice follow-up",
        body_preview="Please check invoice INV-2026-100",
        from_addr="customer@example.com",
        to_addrs=["ops@example.com"],
    )
    message.processed_by_bot = "finance_bot"
    message.analysis_result = {
        "route_source": "ai",
        "routing_confidence": 0.87,
    }
    return message


def _mock_scalar_result(items):
    result = Mock()
    result.scalars.return_value.all.return_value = items
    return result


@pytest.mark.asyncio
async def test_submit_feedback_persists_snapshot_fields(mock_db, sample_message):
    mock_db.get.return_value = sample_message

    async def _refresh(feedback):
        feedback.id = 1

    mock_db.refresh.side_effect = _refresh
    service = EmailLearningService(mock_db)

    feedback = await service.submit_feedback(
        message_id=15,
        rating=5,
        was_correct=True,
        user_comment="Correct routing",
        created_by=22,
    )

    added_feedback = mock_db.add.call_args.args[0]
    assert isinstance(added_feedback, EmailFeedback)
    assert added_feedback.bot_key == "finance_bot"
    assert added_feedback.routing_source == "ai"
    assert added_feedback.routing_confidence == 0.87
    assert feedback.id == 1
    mock_db.commit.assert_awaited()
    mock_db.refresh.assert_awaited()


@pytest.mark.asyncio
async def test_submit_feedback_rejects_invalid_rating(mock_db, sample_message):
    mock_db.get.return_value = sample_message
    service = EmailLearningService(mock_db)

    with pytest.raises(ValueError, match="Rating must be between 1 and 5"):
        await service.submit_feedback(message_id=15, rating=6, was_correct=True)


@pytest.mark.asyncio
async def test_get_bot_learning_metrics_computes_accuracy_and_rating(mock_db):
    items = [
        EmailFeedback(
            id=1,
            message_id=11,
            bot_key="finance_bot",
            rating=5,
            was_correct=True,
            routing_source="ai",
            routing_confidence=0.9,
            created_at=datetime.now(timezone.utc),
        ),
        EmailFeedback(
            id=2,
            message_id=12,
            bot_key="finance_bot",
            rating=3,
            was_correct=False,
            routing_source="rule",
            routing_confidence=0.7,
            created_at=datetime.now(timezone.utc),
        ),
        EmailFeedback(
            id=3,
            message_id=13,
            bot_key="finance_bot",
            rating=4,
            was_correct=True,
            routing_source="ai",
            routing_confidence=0.8,
            created_at=datetime.now(timezone.utc),
        ),
    ]
    mock_db.execute.return_value = _mock_scalar_result(items)
    service = EmailLearningService(mock_db)

    metrics = await service.get_bot_learning_metrics("finance_bot")

    assert metrics.bot_key == "finance_bot"
    assert metrics.feedback_count == 3
    assert metrics.average_rating == 4.0
    assert metrics.accuracy_rate == 0.67
    assert metrics.incorrect_rate == 0.33
    assert metrics.average_routing_confidence == 0.8
    assert metrics.source_breakdown == {"ai": 2, "rule": 1}


@pytest.mark.asyncio
async def test_get_confidence_adjustment_rewards_consistently_good_feedback(mock_db):
    items = [
        EmailFeedback(message_id=1, bot_key="finance_bot", rating=5, was_correct=True, routing_confidence=0.9),
        EmailFeedback(message_id=2, bot_key="finance_bot", rating=5, was_correct=True, routing_confidence=0.8),
        EmailFeedback(message_id=3, bot_key="finance_bot", rating=4, was_correct=True, routing_confidence=0.85),
        EmailFeedback(message_id=4, bot_key="finance_bot", rating=5, was_correct=True, routing_confidence=0.88),
    ]
    mock_db.execute.return_value = _mock_scalar_result(items)
    service = EmailLearningService(mock_db)

    adjustment = await service.get_confidence_adjustment("finance_bot")

    assert adjustment > 0


@pytest.mark.asyncio
async def test_get_confidence_adjustment_penalizes_poor_feedback(mock_db):
    items = [
        EmailFeedback(message_id=1, bot_key="customer_service", rating=1, was_correct=False, routing_confidence=0.9),
        EmailFeedback(message_id=2, bot_key="customer_service", rating=2, was_correct=False, routing_confidence=0.8),
        EmailFeedback(message_id=3, bot_key="customer_service", rating=2, was_correct=False, routing_confidence=0.85),
        EmailFeedback(message_id=4, bot_key="customer_service", rating=3, was_correct=True, routing_confidence=0.75),
    ]
    mock_db.execute.return_value = _mock_scalar_result(items)
    service = EmailLearningService(mock_db)

    adjustment = await service.get_confidence_adjustment("customer_service")

    assert adjustment < 0
