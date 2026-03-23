from __future__ import annotations

from pathlib import Path

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from backend.routes import training_center as training_center_module
from backend.training_center import TrainerBot


@pytest.fixture
def training_app(tmp_path: Path):
    app = FastAPI()
    training_center_module._trainer = TrainerBot(reports_dir=tmp_path / "reports", seed=13)
    app.include_router(training_center_module.router)
    return app


@pytest.fixture
async def training_client(training_app):
    transport = ASGITransport(app=training_app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client


@pytest.mark.asyncio
async def test_training_center_route_flow(training_client: AsyncClient):
    bots_response = await training_client.get("/api/v1/training-center/bots")
    assert bots_response.status_code == 200
    assert any(bot["id"] == "trainer_bot" for bot in bots_response.json()["bots"])

    register_response = await training_client.post(
        "/api/v1/training-center/bots/register",
        json={"bot_key": "customer_service", "level": "beginner", "version": "1.2"},
    )
    assert register_response.status_code == 200
    assert register_response.json()["profile"]["bot_key"] == "customer_service"

    assess_response = await training_client.post("/api/v1/training-center/assess", json={"bot_key": "customer_service"})
    assert assess_response.status_code == 200
    assert assess_response.json()["assessment"]["recommended_level"] in {
        "beginner",
        "intermediate",
        "advanced",
        "expert",
        "master",
    }

    plan_response = await training_client.post(
        "/api/v1/training-center/plans",
        json={"bot_key": "customer_service", "goal": "Improve service recovery quality."},
    )
    assert plan_response.status_code == 200
    plan_id = plan_response.json()["plan"]["plan_id"]

    filtered_courses = await training_client.get("/api/v1/training-center/courses", params={"specialization": "customer_service"})
    assert filtered_courses.status_code == 200
    assert filtered_courses.json()["courses"]
    assert all(course["specialization"] == "customer_service" for course in filtered_courses.json()["courses"])

    session_start_response = await training_client.post(
        "/api/v1/training-center/sessions/start",
        json={"plan_id": plan_id},
    )
    assert session_start_response.status_code == 200
    session_id = session_start_response.json()["session"]["session_id"]

    session_response = await training_client.get(f"/api/v1/training-center/sessions/{session_id}")
    assert session_response.status_code == 200
    assert session_response.json()["session"]["status"] == "completed"

    report_response = await training_client.get(f"/api/v1/training-center/reports/{session_id}")
    assert report_response.status_code == 200
    assert report_response.json()["report"]["session_id"] == session_id

    report_list_response = await training_client.get("/api/v1/training-center/reports", params={"bot_key": "customer_service"})
    assert report_list_response.status_code == 200
    assert report_list_response.json()["reports"]
    assert all(report["bot_key"] == "customer_service" for report in report_list_response.json()["reports"])

    stats_response = await training_client.get("/api/v1/training-center/stats")
    assert stats_response.status_code == 200
    assert stats_response.json()["stats"]["reports_generated"] >= 1
    assert stats_response.json()["stats"]["last_report_session_id"] == session_id
