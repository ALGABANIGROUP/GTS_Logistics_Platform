from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from backend.models.email_center import EmailMessage
from backend.services.chatgpt_service import ChatServiceUnavailableError
from backend.services.email_ai_analyzer import EmailAIAnalyzer


@pytest.fixture
def mock_db():
    db = AsyncMock()
    db.get = AsyncMock()
    db.commit = AsyncMock()
    return db


@pytest.fixture
def sample_message():
    return EmailMessage(
        id=10,
        mailbox_id=4,
        direction="inbound",
        from_addr="billing@example.com",
        to_addrs=["ops@example.com"],
        cc_addrs=[],
        subject="Urgent overdue invoice INV-2026-001",
        body_preview=(
            "Please review overdue payment of $5,000 by 2026-03-15. "
            "This delay is unacceptable and needs action immediately."
        ),
    )


class FakeChatService:
    def __init__(self, configured: bool = True, response: str = "", raises: Exception | None = None):
        self._configured = configured
        self._response = response
        self._raises = raises

    def is_configured(self) -> bool:
        return self._configured

    async def chat(self, **kwargs):
        if self._raises:
            raise self._raises
        return {"response": self._response}


@pytest.mark.asyncio
async def test_analyze_message_uses_chatgpt_when_configured(mock_db, sample_message):
    mock_db.get.return_value = sample_message
    service = FakeChatService(
        configured=True,
        response=(
            '{"version":"1.0","method":"chatgpt","keywords":["invoice","payment"],'
            '"sentiment":{"label":"negative","score":0.82,"urgency":"high"},'
            '"category":"billing","language":"en","summary":"Customer requests invoice action.",'
            '"confidence":0.91,"entities":{"invoice_numbers":["INV-2026-001"],"amounts":[5000],"dates":["2026-03-15"]}}'
        ),
    )

    analyzer = EmailAIAnalyzer(mock_db, service)
    result = await analyzer.analyze_message(10)

    assert result["method"] == "chatgpt"
    assert result["category"] == "billing"
    assert result["sentiment"]["urgency"] == "high"
    assert result["entities"]["invoice_numbers"] == ["INV-2026-001"]
    assert sample_message.analysis_result == result
    assert sample_message.analyzed_at is not None
    mock_db.commit.assert_awaited()


@pytest.mark.asyncio
async def test_analyze_message_falls_back_when_ai_not_configured(mock_db, sample_message):
    mock_db.get.return_value = sample_message
    analyzer = EmailAIAnalyzer(mock_db, FakeChatService(configured=False))

    result = await analyzer.analyze_message(10)

    assert result["method"] == "fallback"
    assert result["category"] == "billing"
    assert "invoice" in result["keywords"]
    assert result["sentiment"]["label"] == "negative"
    assert result["sentiment"]["urgency"] == "high"
    assert result["entities"]["amounts"] == [5000]
    assert result["entities"]["dates"] == ["2026-03-15"]


@pytest.mark.asyncio
async def test_analyze_message_falls_back_when_ai_provider_is_unavailable(mock_db, sample_message):
    mock_db.get.return_value = sample_message
    analyzer = EmailAIAnalyzer(
        mock_db,
        FakeChatService(
            configured=True,
            raises=ChatServiceUnavailableError("provider unavailable"),
        ),
    )

    result = await analyzer.analyze_message(10)

    assert result["method"] == "fallback"
    assert result["summary"].startswith("Email from billing@example.com")


@pytest.mark.asyncio
async def test_analyze_message_raises_for_missing_message(mock_db):
    mock_db.get.return_value = None
    analyzer = EmailAIAnalyzer(mock_db, FakeChatService(configured=False))

    with pytest.raises(ValueError, match="Message 99 not found"):
        await analyzer.analyze_message(99)


def test_detect_language_returns_arabic_for_arabic_text(mock_db):
    message = EmailMessage(
        id=1,
        mailbox_id=1,
        direction="inbound",
        subject="\u0637\u0644\u0628 \u0639\u0627\u062c\u0644",
        body_preview=(
            "\u064a\u0631\u062c\u0649 \u0645\u0631\u0627\u062c\u0639\u0629 "
            "\u0627\u0644\u0641\u0627\u062a\u0648\u0631\u0629 "
            "\u0627\u0644\u0645\u062a\u0623\u062e\u0631\u0629 "
            "\u0627\u0644\u064a\u0648\u0645"
        ),
        from_addr="test@example.com",
    )
    analyzer = EmailAIAnalyzer(mock_db, FakeChatService(configured=False))

    assert analyzer._detect_language(message) == "ar"


def test_extract_entities_handles_invoice_amounts_and_dates(mock_db, sample_message):
    analyzer = EmailAIAnalyzer(mock_db, FakeChatService(configured=False))

    entities = analyzer._extract_entities(sample_message)

    assert entities["invoice_numbers"] == ["INV-2026-001"]
    assert entities["amounts"] == [5000]
    assert entities["dates"] == ["2026-03-15"]
