import asyncio

from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.routes.safety_api import router
from backend.safety.main import AISafetyManagerBot


def test_dashboard_reflects_driver_risk_signals() -> None:
    bot = AISafetyManagerBot()

    asyncio.run(
        bot.monitor_driver(
            driver_id=42,
            hours_driven=10,
            speeding_events=4,
            hard_braking=2,
            rapid_acceleration=2,
            rest_hours=4,
            heart_rate=122,
        )
    )
    dashboard = asyncio.run(bot.get_safety_dashboard())

    assert dashboard["safety_score"] < 100
    assert dashboard["risk_level"] in {"MEDIUM", "HIGH", "CRITICAL"}
    assert dashboard["quick_stats"]["high_risk_drivers"] >= 1


def test_process_message_dispatches_context_action() -> None:
    bot = AISafetyManagerBot()

    response = asyncio.run(
        bot.process_message(
            "monitor this driver",
            {
                "action": "monitor_driver",
                "driver_id": 7,
                "hours_driven": 9,
                "speeding_events": 3,
                "hard_braking": 1,
                "rapid_acceleration": 1,
                "rest_hours": 5,
            },
        )
    )

    assert response["driver_id"] == 7
    assert response["risk_level"] in {"MEDIUM", "HIGH", "CRITICAL"}


def test_safety_routes_expose_live_manager_endpoints() -> None:
    app = FastAPI()
    app.include_router(router)
    client = TestClient(app)

    report = client.post(
        "/api/v1/safety/incidents/report",
        json={
            "incident_type": "vehicle_accident",
            "severity": "moderate",
            "description": "Rear-end collision near yard entrance",
            "location": "Dubai Yard Gate 2",
            "reporter": "ops@gts.example",
        },
    )
    assert report.status_code == 200
    assert report.json()["success"] is True

    dashboard = client.get("/api/v1/safety/dashboard")
    assert dashboard.status_code == 200
    dashboard_json = dashboard.json()
    assert "safety_score" in dashboard_json
    assert "active_alerts" in dashboard_json

    monitor = client.post(
        "/api/v1/safety/drivers/monitor",
        json={
            "driver_id": 9,
            "hours_driven": 8,
            "speeding_events": 2,
            "hard_braking": 1,
            "rapid_acceleration": 0,
            "rest_hours": 6,
        },
    )
    assert monitor.status_code == 200
    assert monitor.json()["driver_id"] == 9
