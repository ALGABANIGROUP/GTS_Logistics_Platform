from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import AsyncMock, Mock

import pytest

from backend.models.email_center import BotMailboxRule, EmailMessage, Mailbox
from backend.services.email_routing_engine import ActionType, ConditionOperator, EmailRoutingEngine


@pytest.fixture
def mock_db():
    db = AsyncMock()
    db.get = AsyncMock()
    db.execute = AsyncMock()
    db.commit = AsyncMock()
    return db


@pytest.fixture
def sample_mailbox():
    return Mailbox(
        id=1,
        email_address="routing@example.com",
        assigned_bot_key="customer_service",
    )


@pytest.fixture
def sample_message():
    return EmailMessage(
        id=1,
        mailbox_id=1,
        direction="inbound",
        subject="Invoice #123",
        body_preview="Please review the attached invoice and payment details.",
        from_addr="customer@example.com",
        to_addrs=["routing@example.com"],
        cc_addrs=[],
    )


@pytest.fixture
def sample_rules():
    return [
        BotMailboxRule(
            id=2,
            mailbox_id=1,
            bot_key="customer_service",
            condition_field="all",
            condition_operator=ConditionOperator.CONTAINS,
            condition_value=["help", "support"],
            action_type=ActionType.PROCESS,
            priority=2,
            is_active=True,
        ),
        BotMailboxRule(
            id=1,
            mailbox_id=1,
            bot_key="finance_bot",
            condition_field="all",
            condition_operator=ConditionOperator.CONTAINS,
            condition_value=["invoice", "payment"],
            condition_match_all=False,
            action_type=ActionType.PROCESS,
            priority=1,
            is_active=True,
        ),
    ]


def _mock_scalar_result(items):
    result = Mock()
    result.scalars.return_value.all.return_value = items
    return result


class FakeAnalyzer:
    def __init__(self, result):
        self.result = result

    async def analyze_message(self, message_id):
        return self.result


@pytest.mark.asyncio
async def test_route_message_with_matching_rule(mock_db, sample_mailbox, sample_message, sample_rules):
    mock_db.get.side_effect = [sample_message, sample_mailbox]
    mock_db.execute.return_value = _mock_scalar_result(sample_rules)

    engine = EmailRoutingEngine(mock_db)
    result = await engine.route_message(1)

    assert result["matched"] is True
    assert result["applied_rule_id"] == 1
    assert result["bot_key"] == "finance_bot"
    assert result["action_type"] == ActionType.PROCESS
    assert result["route_source"] == "rule"


@pytest.mark.asyncio
async def test_route_message_uses_default_mailbox_bot_when_no_rules(mock_db, sample_mailbox, sample_message):
    mock_db.get.side_effect = [sample_message, sample_mailbox]
    mock_db.execute.return_value = _mock_scalar_result([])

    engine = EmailRoutingEngine(mock_db)
    result = await engine.route_message(1)

    assert result["matched"] is True
    assert result["bot_key"] == "customer_service"
    assert result["applied_rule_id"] is None
    assert result["action_type"] == ActionType.PROCESS
    assert result["route_source"] == "mailbox_default"


@pytest.mark.asyncio
async def test_route_message_returns_unmatched_without_rules_or_default_bot(mock_db, sample_message):
    mailbox = Mailbox(id=1, email_address="routing@example.com", assigned_bot_key=None)
    mock_db.get.side_effect = [sample_message, mailbox]
    mock_db.execute.return_value = _mock_scalar_result([])

    engine = EmailRoutingEngine(mock_db)
    result = await engine.route_message(1)

    assert result["matched"] is False
    assert result["bot_key"] is None
    assert result["action_type"] is None
    assert result["route_source"] == "unmatched"


@pytest.mark.asyncio
async def test_route_message_respects_priority_even_if_mock_returns_unsorted_rules(
    mock_db, sample_mailbox, sample_message
):
    rules = [
        BotMailboxRule(
            id=99,
            mailbox_id=1,
            bot_key="low_priority",
            condition_field="all",
            condition_operator=ConditionOperator.CONTAINS,
            condition_value="invoice",
            action_type=ActionType.PROCESS,
            priority=10,
            is_active=True,
        ),
        BotMailboxRule(
            id=10,
            mailbox_id=1,
            bot_key="high_priority",
            condition_field="all",
            condition_operator=ConditionOperator.CONTAINS,
            condition_value="invoice",
            action_type=ActionType.PROCESS,
            priority=1,
            is_active=True,
        ),
    ]
    mock_db.get.side_effect = [sample_message, sample_mailbox]
    mock_db.execute.return_value = _mock_scalar_result(rules)

    engine = EmailRoutingEngine(mock_db)
    result = await engine.route_message(1)

    assert result["applied_rule_id"] == 10
    assert result["bot_key"] == "high_priority"


@pytest.mark.asyncio
async def test_apply_routing_to_message_updates_analysis_fields(mock_db, sample_mailbox, sample_message, sample_rules):
    sample_message.analysis_result = {
        "version": "1.0",
        "method": "fallback",
        "category": "billing",
        "keywords": ["invoice", "payment"],
        "confidence": 0.82,
    }
    mock_db.get.side_effect = [sample_message, sample_message, sample_mailbox, sample_message]
    mock_db.execute.return_value = _mock_scalar_result(sample_rules)

    engine = EmailRoutingEngine(mock_db)
    applied, bot_key = await engine.apply_routing_to_message(1)

    assert applied is True
    assert bot_key == "finance_bot"
    assert sample_message.applied_rule_id == 1
    assert sample_message.processed_by_bot == "finance_bot"
    assert sample_message.processed_at is not None
    assert sample_message.analyzed_at is not None
    assert sample_message.analysis_result["matched"] is True
    assert sample_message.analysis_result["route_source"] == "rule"
    mock_db.commit.assert_awaited()


@pytest.mark.asyncio
async def test_get_rules_for_mailbox_returns_serialized_rules(mock_db, sample_rules):
    sample_rules[0].created_at = datetime.now(timezone.utc)
    sample_rules[0].updated_at = datetime.now(timezone.utc)
    sample_rules[1].created_at = datetime.now(timezone.utc)
    sample_rules[1].updated_at = datetime.now(timezone.utc)
    mock_db.execute.return_value = _mock_scalar_result(sample_rules)

    engine = EmailRoutingEngine(mock_db)
    rules = await engine.get_rules_for_mailbox(1)

    assert len(rules) == 2
    assert rules[0]["id"] == 1
    assert rules[1]["id"] == 2
    assert rules[0]["condition_field"] == "all"


@pytest.mark.asyncio
async def test_route_message_uses_ai_selected_bot_when_confident_and_no_rule_match(
    mock_db, sample_mailbox, sample_message
):
    sample_message.analysis_result = {
        "version": "1.0",
        "method": "chatgpt",
        "category": "billing",
        "keywords": ["invoice", "payment", "overdue"],
        "confidence": 0.92,
        "sentiment": {"label": "negative", "score": 0.81, "urgency": "high"},
    }
    mock_db.get.side_effect = [sample_message, sample_mailbox]
    mock_db.execute.return_value = _mock_scalar_result([])

    engine = EmailRoutingEngine(mock_db)
    result = await engine.route_message(1)

    assert result["matched"] is True
    assert result["bot_key"] == "finance_bot"
    assert result["route_source"] == "ai"
    assert result["routing_confidence"] >= 0.75


@pytest.mark.asyncio
async def test_route_message_falls_back_to_default_bot_when_ai_confidence_is_low(
    mock_db, sample_mailbox, sample_message
):
    sample_message.analysis_result = {
        "version": "1.0",
        "method": "fallback",
        "category": "general",
        "keywords": ["hello"],
        "confidence": 0.4,
        "sentiment": {"label": "neutral", "score": 0.5, "urgency": "low"},
    }
    mock_db.get.side_effect = [sample_message, sample_mailbox]
    mock_db.execute.return_value = _mock_scalar_result([])

    engine = EmailRoutingEngine(mock_db)
    result = await engine.route_message(1)

    assert result["matched"] is True
    assert result["bot_key"] == "customer_service"
    assert result["route_source"] == "mailbox_default"


@pytest.mark.asyncio
async def test_apply_routing_to_message_runs_analyzer_when_analysis_is_missing(
    mock_db, sample_mailbox, sample_message
):
    mock_db.get.side_effect = [sample_message, sample_message, sample_mailbox, sample_message]
    mock_db.execute.return_value = _mock_scalar_result([])
    analyzer = FakeAnalyzer(
        {
            "version": "1.0",
            "method": "chatgpt",
            "category": "billing",
            "keywords": ["invoice", "payment"],
            "confidence": 0.9,
            "sentiment": {"label": "negative", "score": 0.8, "urgency": "high"},
        }
    )

    engine = EmailRoutingEngine(mock_db, analyzer=analyzer)
    applied, bot_key = await engine.apply_routing_to_message(1)

    assert applied is True
    assert bot_key == "finance_bot"
    assert sample_message.analysis_result["route_source"] == "ai"
