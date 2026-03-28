from __future__ import annotations

import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import backend.bots as bots_pkg
from backend import main
from backend.routes import ai_bots_routes


class _DummyBot:
    name = "general_manager"

    async def status(self) -> dict:
        return {"status": "ok"}


class _DummyBotOS:
    def __init__(self) -> None:
        self.started = False

    async def start(self) -> None:
        self.started = True


@pytest.mark.asyncio
async def test_start_bot_os_initializes_app_state(monkeypatch: pytest.MonkeyPatch) -> None:
    dummy_registry = main._AIRegistry()
    dummy_registry.register(_DummyBot())
    dummy_bot_os = _DummyBotOS()

    async def fake_session_factory():
        yield None

    def fake_init_bot_os(**kwargs):
        assert kwargs["bot_names_provider"]() == ["general_manager"]
        assert kwargs["bot_getter"].__self__ is dummy_registry
        assert kwargs["bot_getter"].__func__ is dummy_registry.get.__func__
        assert kwargs["session_factory"] is fake_session_factory
        return dummy_bot_os

    monkeypatch.setattr(main, "ai_registry", dummy_registry)
    monkeypatch.setattr(main, "_get_session", fake_session_factory)
    monkeypatch.setattr(bots_pkg, "init_bot_os", fake_init_bot_os)

    if hasattr(main.app.state, "bot_os"):
        delattr(main.app.state, "bot_os")

    await main._start_bot_os()

    assert dummy_bot_os.started is True
    assert main.app.state.bot_os is dummy_bot_os


@pytest.mark.asyncio
async def test_list_bots_uses_imported_capabilities(monkeypatch: pytest.MonkeyPatch) -> None:
    dummy_bot = _DummyBot()

    class _Registry:
        def list(self) -> dict:
            return {"general_manager": "DummyBot"}

        def get(self, name: str):
            assert name == "general_manager"
            return dummy_bot

    monkeypatch.setattr(ai_bots_routes, "_registry", lambda: _Registry())
    monkeypatch.setattr(ai_bots_routes, "_has_backend", lambda _bot_key: False)
    monkeypatch.setattr(
        ai_bots_routes.bot_access_policy,
        "can_see_bot",
        lambda *_args, **_kwargs: {"allowed": True},
    )
    monkeypatch.setattr(
        ai_bots_routes.bot_access_policy,
        "can_run_bot",
        lambda *_args, **_kwargs: {"allowed": True},
    )

    result = await ai_bots_routes.list_bots(current_user={"role": "admin", "features": []})

    assert result["count"] == 1
    assert result["bots"][0]["bot_key"] == "general_manager"
    assert result["bots"][0]["display_name"] == ai_bots_routes.BOT_CAPABILITIES["general_manager"]["name"]


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__]))
