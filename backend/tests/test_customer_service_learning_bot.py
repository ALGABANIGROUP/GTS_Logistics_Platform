from __future__ import annotations

import pytest

from backend.ai.customer_service import CustomerServiceLearningBot
from backend.services.ai_customer_service import AICustomerService


def test_ai_customer_service_detects_language_and_negotiation() -> None:
    service = AICustomerService()

    result = service.generate_reply("Bonjour, le prix est trop élevé. Avez-vous une remise ?")

    assert result["language"] == "fr"
    assert result["intent"] == "negotiation"
    assert result["negotiation_offer"]["discount_percent"] > 0
    assert "remise" in result["reply"].lower()


@pytest.mark.asyncio
async def test_learning_bot_escalates_and_creates_ticket() -> None:
    bot = CustomerServiceLearningBot()
    bot.start_conversation(
        user_id="42",
        conversation_id="conv_test_1",
        metadata={"customer_name": "Test Customer", "channel": "whatsapp", "email": "test@example.com"},
    )

    response = await bot.process_message(
        message="I cannot access the portal and this is urgent.",
        user_id="42",
        conversation_id="conv_test_1",
    )

    assert response["needs_human"] is True
    assert response["ticket"] is not None
    assert len(bot.tickets) == 1

    conversations = bot.list_conversations()
    assert conversations[0]["status"] == "escalated"
    assert conversations[0]["customerName"] == "Test Customer"
    assert conversations[0]["channel"] == "whatsapp"


@pytest.mark.asyncio
async def test_learning_bot_keeps_normal_conversation_without_ticket() -> None:
    bot = CustomerServiceLearningBot()

    response = await bot.process_message(
        message="Hello, can you track shipment GTS-100 for me?",
        user_id="7",
        conversation_id="conv_test_2",
    )

    assert response["needs_human"] is False
    assert response["intent"] == "shipment"
    assert bot.get_stats()["pending_tickets"] == 0
