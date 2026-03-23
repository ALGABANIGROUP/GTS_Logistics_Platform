# backend/routes/ai_operations_api.py
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
import os
import httpx

# ✅ provide the legacy name `get_session` from the async dependency
from backend.database.session import get_async_session as get_session
from backend.integrations.loadboards.mock_truckerpath import get_mock_loads
from backend.schemas.shipment_schema import ShipmentCreate
from backend.services.shipment_service import create_shipment

# Load .env if available (safe no-op if missing)
try:
    from dotenv import load_dotenv  # type: ignore
    load_dotenv()
except Exception:
    pass

GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY") or ""
GOOGLE_MAPS_ENABLED = os.getenv("GOOGLE_MAPS_ENABLED", "0").lower() in ("1", "true", "yes", "on")
EXTERNAL_APIS_ENABLED = os.getenv("EXTERNAL_APIS_ENABLED", "0").lower() in ("1", "true", "yes", "on")

router = APIRouter()


async def get_coordinates(address: str):
    """
    Resolve an address to (lat, lng).
    Returns (None, None) immediately if Google Maps is disabled or key missing.
    """
    if not address or not GOOGLE_MAPS_ENABLED or not EXTERNAL_APIS_ENABLED or not GOOGLE_MAPS_API_KEY:
        return None, None

    try:
        url = "https://maps.googleapis.com/maps/api/geocode/json"
        params = {"address": address, "key": GOOGLE_MAPS_API_KEY}
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, params=params, timeout=20)
            resp.raise_for_status()
            data = resp.json()
            if data.get("status") == "OK" and data.get("results"):
                loc = data["results"][0]["geometry"]["location"]
                return loc.get("lat"), loc.get("lng")
    except Exception as e:
        print(f"[geocoding] Error for '{address}': {e}")
    return None, None


class AIOperationsManager:
    def __init__(self) -> None:
        self.last_checked: datetime | None = None

    async def monitor_mock_truckerpath(self, db: AsyncSession):
        """
        Pull mock loads, optionally geocode origins, and create shipments.
        """
        loads = get_mock_loads()
        created = []

        for load in loads:
            origin = str(load.get("origin", "") or "")
            destination = str(load.get("destination", "") or "")
            equipment = str(load.get("equipment_type", "") or "")
            notes = str(load.get("notes", "") or "")
            weight = str(load.get("weight", "0") or "0")
            length = str(load.get("length", "0") or "0")
            price = float(load.get("price", 0) or 0)

            lat, lng = await get_coordinates(origin)

            shipment_data = ShipmentCreate(
                user_id=1,
                pickup_location=origin,
                dropoff_location=destination,
                trailer_type=equipment,
                rate=price,
                recurring_type=None,
                days=None,
                weight=weight,
                length=length,
                load_size=str(load.get("load_size", "") or ""),
                description=notes,
                status="Imported",
                latitude=lat,
                longitude=lng,
            )

            await create_shipment(db=db, shipment_data=shipment_data)
            created.append(shipment_data)

        self.last_checked = datetime.utcnow()
        return {
            "new_shipments": len(created),
            "timestamp": self.last_checked,
        }


@router.post("/ai/ops/load-import/trigger")
async def trigger_load_import(session: AsyncSession = Depends(get_session)):
    """
    Triggers a mock import from TruckerPath into the shipments table.
    """
    manager = AIOperationsManager()
    result = await manager.monitor_mock_truckerpath(db=session)
    return {"status": "ok", **result}

