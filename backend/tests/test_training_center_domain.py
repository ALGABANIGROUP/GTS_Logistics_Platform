from __future__ import annotations

from pathlib import Path

import pytest

from backend.training_center import TrainerBot
from backend.training_center.integration.bot_connector import BotConnector


@pytest.mark.asyncio
async def test_bot_connector_resolves_aliases():
    connector = BotConnector()
    resolved = connector.get_bot("trainer")
    assert resolved is not None
    assert resolved["canonical_key"] == "trainer_bot"
    assert resolved["specialization"].value == "training"


@pytest.mark.asyncio
async def test_trainer_bot_creates_plan_and_session(tmp_path: Path):
    reports_dir = tmp_path / "reports"
    trainer = TrainerBot(reports_dir=reports_dir, seed=7)

    profile = await trainer.register_bot("security_manager_bot", level="intermediate")
    assert profile["bot_key"] == "security_manager_bot"

    assessment = await trainer.assess_bot_capabilities("security_manager_bot")
    assert assessment["overall_score"] > 0
    assert len(assessment["strengths"]) == 2
    assert len(assessment["weak_points"]) == 2

    plan = await trainer.create_training_plan("security_manager_bot")
    assert plan["specialization"] == "security"
    assert len(plan["courses"]) >= 1
    assert len(plan["milestones"]) == len(plan["courses"])

    result = await trainer.start_training_session(plan["plan_id"])
    assert result["session"]["status"] == "completed"
    assert result["report"]["grade"] in {"Excellent", "Very Good", "Good", "Pass", "Retraining Required"}
    assert reports_dir.joinpath(f"{result['session']['session_id']}.json").exists()


@pytest.mark.asyncio
async def test_course_and_scenario_selection_cover_expected_specialization(tmp_path: Path):
    trainer = TrainerBot(reports_dir=tmp_path / "reports", seed=11)
    await trainer.register_bot("operations_manager_bot", level="beginner")
    await trainer.assess_bot_capabilities("operations_manager_bot")
    plan = await trainer.create_training_plan("operations_manager_bot")

    assert all(course["specialization"] == "operations" for course in plan["courses"])

    scenarios = await trainer.scenario_generator.generate_scenarios(
        specialization="operations",
        level=trainer.bots_in_training["operations_manager_bot"].current_level,
        course_topics=plan["courses"][0]["topics"],
    )
    assert scenarios
    assert all(item["specialization"] == "operations" for item in scenarios)
