from __future__ import annotations

from backend.services.dispatch_service import DispatchService


def test_coordinate_from_label_is_deterministic() -> None:
    first = DispatchService._coordinate_from_label("Toronto Hub")
    second = DispatchService._coordinate_from_label("Toronto Hub")
    third = DispatchService._coordinate_from_label("Montreal Yard")

    assert first == second
    assert first != third


def test_haversine_and_duration_are_positive() -> None:
    service = DispatchService(db=None)
    distance = service._haversine_km((43.65, -79.38), (45.50, -73.56))
    duration = service._estimate_duration_minutes(distance, "normal")

    assert distance > 0
    assert duration > 0


def test_maintenance_recommendation_thresholds() -> None:
    assert DispatchService._maintenance_recommendation(20) == "No immediate maintenance action required."
    assert DispatchService._maintenance_recommendation(50) == "Schedule a preventive check during the next idle window."
    assert DispatchService._maintenance_recommendation(80) == "Inspect the assigned vehicle before the next dispatch cycle."
