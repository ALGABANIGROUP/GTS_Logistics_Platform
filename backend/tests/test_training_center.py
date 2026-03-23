from __future__ import annotations

import pytest

from backend.training_center import TrainerBot


@pytest.mark.asyncio
async def test_training_center_demo_flow(tmp_path):
    trainer = TrainerBot(
        reports_dir=tmp_path / "reports",
        seed=7,
    )

    courses = await trainer.list_available_courses()
    assert any(course["id"] == "SEC-201" for course in courses)

    report = await trainer.train_bot("Security Manager v2.0", "SEC-201")
    assert report["bot_name"] == "Security Manager v2.0"
    assert report["course_id"] == "SEC-201"
    assert 0 <= report["final_score"] <= 100

    stats = await trainer.get_training_stats()
    assert stats["total_trained_bots"] == 1
    assert stats["last_training"]["session_id"] == report["session_id"]
