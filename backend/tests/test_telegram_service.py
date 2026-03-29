from __future__ import annotations

from unittest.mock import Mock

from backend.services.telegram_service import TelegramService


def test_is_configured_true_with_token_only(monkeypatch):
    monkeypatch.setenv("TELEGRAM_ENABLED", "true")
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "token_123")
    monkeypatch.delenv("TELEGRAM_CHAT_ID", raising=False)

    service = TelegramService()

    assert service.is_configured() is True
    assert service.can_send_alerts() is False


def test_send_message_without_chat_id_returns_false(monkeypatch):
    monkeypatch.setenv("TELEGRAM_ENABLED", "true")
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "token_123")
    monkeypatch.delenv("TELEGRAM_CHAT_ID", raising=False)

    service = TelegramService()

    assert service.send_message("hello") is False


def test_test_connection_reports_valid_token_without_delivery_target(monkeypatch):
    monkeypatch.setenv("TELEGRAM_ENABLED", "true")
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "token_123")
    monkeypatch.delenv("TELEGRAM_CHAT_ID", raising=False)

    service = TelegramService()
    response = Mock()
    response.status_code = 200
    response.json.return_value = {"ok": True, "result": {"username": "gts_bot"}}

    monkeypatch.setattr("backend.services.telegram_service.requests.get", lambda *args, **kwargs: response)

    result = service.test_connection()

    assert result["success"] is True
    assert result["configured"] is True
    assert result["delivery_configured"] is False
    assert result["bot_username"] == "gts_bot"
