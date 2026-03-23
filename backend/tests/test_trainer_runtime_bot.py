from __future__ import annotations

import pytest

from backend.bots.trainer_bot import TrainerBotRuntime


@pytest.mark.asyncio
async def test_trainer_runtime_status_and_config():
    bot = TrainerBotRuntime()

    status = await bot.status()
    config = await bot.config()

    assert status["bot"] == "trainer_bot"
    assert status["ok"] is True
    assert config["name"] == "trainer_bot"
    assert "register_bot" in config["capabilities"]


@pytest.mark.asyncio
async def test_trainer_runtime_can_register_assess_and_plan():
    bot = TrainerBotRuntime()

    registered = await bot.register_bot("customer_service", "beginner", "1.0")
    assessment = await bot.assess_bot("customer_service")
    plan = await bot.create_training_plan("customer_service", "Improve support recovery quality.")

    assert registered["ok"] is True
    assert registered["profile"]["bot_key"] == "customer_service"
    assert assessment["ok"] is True
    assert assessment["assessment"]["bot_key"] == "customer_service"
    assert plan["ok"] is True
    assert plan["plan"]["bot_key"] == "customer_service"
