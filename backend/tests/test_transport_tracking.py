from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.routes import transport_tracking_api as transport_module


class FakeQuery:
    def __init__(self, items):
        self.items = items
        self._id = None

    def filter(self, condition):
        right = getattr(condition, "right", None)
        self._id = getattr(right, "value", None)
        return self

    def first(self):
        return self.items.get(self._id)


class FakeDB:
    def __init__(self, shipments=None, trucks=None):
        self.shipments = shipments or {}
        self.trucks = trucks or {}

    def query(self, model):
        if model is transport_module.Shipment:
            return FakeQuery(self.shipments)
        if model is transport_module.TruckLocation:
            return FakeQuery(self.trucks)
        raise AssertionError(f"Unexpected model {model}")


class ShipmentRecord:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


class TruckRecord:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


def _build_client(fake_db):
    app = FastAPI()
    app.include_router(transport_module.router)
    app.dependency_overrides[transport_module.get_db] = lambda: fake_db
    return TestClient(app)


def test_track_shipment_returns_503_when_gps_missing():
    fake_db = FakeDB(
        shipments={
            1: ShipmentRecord(
                id=1,
                status="in_transit",
                origin_latitude=10.0,
                origin_longitude=20.0,
                destination_latitude=30.0,
                destination_longitude=40.0,
            )
        }
    )
    client = _build_client(fake_db)

    response = client.post("/api/v1/transport/shipments/1/track")
    assert response.status_code == 503
    assert "GPS telemetry is missing" in response.json()["detail"]


def test_track_shipment_uses_real_metrics_when_available():
    fake_db = FakeDB(
        shipments={
            1: ShipmentRecord(
                id=1,
                status="in_transit",
                current_latitude=11.0,
                current_longitude=22.0,
                origin_latitude=10.0,
                origin_longitude=20.0,
                destination_latitude=30.0,
                destination_longitude=40.0,
                distance_total_km=1000,
                distance_traveled_km=400,
                distance_remaining_km=600,
                progress_percentage=40,
                truck_id=99,
                driver_name="Driver One",
            )
        },
        trucks={99: TruckRecord(id=99, license_plate="ABC-123")},
    )
    client = _build_client(fake_db)

    response = client.post("/api/v1/transport/shipments/1/track")
    assert response.status_code == 200
    payload = response.json()
    assert payload["progress"] == 40
    assert payload["distance_remaining"] == 600
    assert payload["distance_total"] == 1000
    assert payload["vehicle_license"] == "ABC-123"
