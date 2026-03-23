from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple, Union
from datetime import datetime
import os

from fastapi import APIRouter, Depends, HTTPException
import httpx

# ---------- Optional DB path (preferred) ----------
try:
    from sqlalchemy.ext.asyncio import AsyncSession
    from backend.database.session import get_async_session as get_session  # type: ignore
    DB_AVAILABLE = True
except Exception:
    AsyncSession = object  # type: ignore
    def get_session():  # type: ignore
        raise RuntimeError("DB session unavailable")
    DB_AVAILABLE = False

# ---------- Provider registry (TruckerPath live/mock) ----------
try:
    from backend.integrations.loadboards.registry import get_provider  # type: ignore
except Exception:
    get_provider = None  # type: ignore

# ---------- Mock source as last resort ----------
try:
    from backend.integrations.loadboards.mock_truckerpath import get_mock_loads  # type: ignore
except Exception:
    def get_mock_loads() -> List[Dict[str, Any]]:
        return []

# ---------- Optional ShipmentCreate + service (DB path) ----------
try:
    from backend.schemas.shipment_schema import ShipmentCreate  # type: ignore
    from backend.services.shipment_service import create_shipment  # type: ignore
except Exception:
    ShipmentCreate = None  # type: ignore
    create_shipment = None  # type: ignore

# ---------- Optional WebSocket broadcast ----------
async def _noop_broadcast(*args, **kwargs) -> None:
    return None

broadcast_event = _noop_broadcast
try:
    from backend.routes.ws_routes import broadcast_event as _broadcast_event  # type: ignore
    broadcast_event = _broadcast_event
except Exception:
    pass

router = APIRouter(prefix="/ai/ops", tags=["AI Operations"])

# ---------- ENV / flags ----------
INTERNAL_BASE_URL = os.getenv("INTERNAL_BASE_URL", "http://localhost:8000")
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY") or ""
GOOGLE_MAPS_ENABLED = os.getenv("GOOGLE_MAPS_ENABLED", "0").lower() in ("1", "true", "yes", "on")
EXTERNAL_APIS_ENABLED = os.getenv("EXTERNAL_APIS_ENABLED", "0").lower() in ("1", "true", "yes", "on")

# ===========================
#           Helpers
# ===========================
async def _http_geocode(address: str) -> Tuple[Optional[float], Optional[float]]:
    if not address or not GOOGLE_MAPS_ENABLED or not EXTERNAL_APIS_ENABLED or not GOOGLE_MAPS_API_KEY:
        return None, None
    try:
        url = "https://maps.googleapis.com/maps/api/geocode/json"
        params = {"address": address, "key": GOOGLE_MAPS_API_KEY}
        async with httpx.AsyncClient(timeout=20) as client:
            r = await client.get(url, params=params)
            r.raise_for_status()
            data = r.json()
            if data.get("status") == "OK" and data.get("results"):
                loc = data["results"][0]["geometry"]["location"]
                return float(loc.get("lat")), float(loc.get("lng"))
    except Exception:
        pass
    return None, None

def _normalize_str(v: Any) -> str:
    return str(v or "").strip()

def _dedupe_key(load: Dict[str, Any]) -> Tuple[str, str, str, str]:
    origin = _normalize_str(
        load.get("origin") or load.get("pickup") or load.get("pickup_location") or load.get("pickup_city")
    )
    dest = _normalize_str(
        load.get("destination") or load.get("dropoff") or load.get("dropoff_location") or load.get("dropoff_city")
    )
    equip = _normalize_str(load.get("equipment_type") or load.get("equipment") or load.get("trailer_type"))
    date_ = _normalize_str(load.get("pickup_date") or load.get("date") or load.get("posted_at"))
    return origin.lower(), dest.lower(), equip.lower(), date_

def _to_float(v: Union[str, int, float, None]) -> Optional[float]:
    if v is None:
        return None
    if isinstance(v, (int, float)):
        return float(v)
    try:
        return float(str(v).replace(",", "").strip())
    except Exception:
        return None

async def _create_shipment_via_http(payload: Dict[str, Any]) -> Optional[int]:
    url = INTERNAL_BASE_URL.rstrip("/") + "/api/v1/shipments/shipments/"
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            r = await client.post(url, json=payload)
            if r.status_code // 100 == 2:
                data = r.json()
                return int(data.get("id") or data.get("shipment_id") or data.get("data", {}).get("id") or 0) or None
    except Exception:
        return None
    return None

def _build_shipment_payload(load: Dict[str, Any], lat: Optional[float], lng: Optional[float]) -> Dict[str, Any]:
    origin = _normalize_str(load.get("origin") or load.get("pickup") or load.get("pickup_location") or load.get("pickup_city"))
    dest = _normalize_str(load.get("destination") or load.get("dropoff") or load.get("dropoff_location") or load.get("dropoff_city"))
    equip = _normalize_str(load.get("equipment_type") or load.get("equipment") or load.get("trailer_type"))
    notes = _normalize_str(load.get("notes") or load.get("description"))
    weight = _normalize_str(load.get("weight"))
    length = _normalize_str(load.get("length"))
    price = _to_float(load.get("price") or load.get("rate") or load.get("rate_usd"))

    return {
        "user_id": 1,  # MVP: system user/admin
        "pickup_location": origin or "Unknown Pickup",
        "dropoff_location": dest or "Unknown Dropoff",
        "trailer_type": equip or None,
        "rate": price,
        "recurring_type": None,
        "days": None,
        "weight": weight or None,
        "length": length or None,
        "load_size": _normalize_str(load.get("load_size") or ""),
        "description": notes or None,
        "status": "Imported",
        "latitude": lat,
        "longitude": lng,
    }

async def _fetch_truckerpath_loads(limit: int) -> List[Dict[str, Any]]:
    loads: List[Dict[str, Any]] = []
    if get_provider is not None:
        try:
            ProviderClass = get_provider("truckerpath")
            provider = ProviderClass()
            res = await provider.list_loads(limit=limit)
            if isinstance(res, dict) and res.get("ok"):
                loads = list(res.get("loads") or [])
        except Exception:
            pass
    if not loads:
        loads = get_mock_loads()[:limit]
    return loads

# ===========================
#           Core
# ===========================
class AIOperationsManager:
    def __init__(self) -> None:
        self.last_checked: Optional[datetime] = None

    async def monitor_and_create(
        self,
        limit: int = 10,
        db: Optional[AsyncSession] = None,  # type: ignore
    ) -> Dict[str, Any]:
        loads = await _fetch_truckerpath_loads(limit=limit)
        if not loads:
            raise HTTPException(status_code=400, detail="No loads available")

        created_ids: List[int] = []
        skipped = 0
        errors: List[str] = []
        seen: set[Tuple[str, str, str, str]] = set()

        for load in loads:
            key = _dedupe_key(load)
            if key in seen:
                skipped += 1
                continue
            seen.add(key)

            lat, lng = await _http_geocode(
                _normalize_str(load.get("origin") or load.get("pickup") or load.get("pickup_location") or load.get("pickup_city"))
            )
            payload = _build_shipment_payload(load, lat, lng)

            created_id: Optional[int] = None
            if DB_AVAILABLE and ShipmentCreate is not None and create_shipment is not None and db is not None:
                try:
                    shipment_data = ShipmentCreate(**payload)  # type: ignore
                    obj = await create_shipment(db=db, shipment_data=shipment_data)  # type: ignore
                    created_id = int(getattr(obj, "id", 0) or 0) or None
                except Exception as e:
                    errors.append(f"DB create failed: {e}")

            if created_id is None:
                try:
                    created_id = await _create_shipment_via_http(payload)
                except Exception as e:
                    errors.append(f"HTTP create failed: {e}")

            if created_id is not None:
                created_ids.append(created_id)
                try:
                    await broadcast_event(
                        channel="events.ops.shipment_imported",
                        payload={"shipment_id": created_id, "pickup": payload.get("pickup_location"), "dropoff": payload.get("dropoff_location")},
                    )
                except Exception:
                    pass

        self.last_checked = datetime.utcnow()
        return {"ok": True, "created": created_ids, "skipped": skipped, "errors": errors}

    async def analyze_shipment_with_ai(self, shipment_id: int) -> Dict[str, Any]:
        # Stub AI analysis logic; replace with real integration as needed
        return {
            "ok": True,
            "shipment_id": shipment_id,
            "analysis": "AI review placeholder for shipment data.",
            "recommendations": [
                "Monitor ETA via tracker",
                "Prioritize load for expedited handling",
            ],
            "timestamp": datetime.utcnow().isoformat(),
        }

    async def generate_daily_report(self) -> Dict[str, Any]:
        now = datetime.utcnow().isoformat()
        return {
            "ok": True,
            "report": "Daily operations summary placeholder.",
            "shipments_processed": 0,
            "errors": [],
            "timestamp": now,
        }

    async def monitor_mock_truckerpath(self, limit: int = 10) -> Dict[str, Any]:
        loads = await _fetch_truckerpath_loads(limit=limit)
        if not loads:
            return {"ok": False, "message": "No mock loads available"}
        return {
            "ok": True,
            "timestamp": datetime.utcnow().isoformat(),
            "mock_loads": [load for load in loads[:limit]],
        }

@router.post("/run")
async def run_ops(limit: int = 10, db: Optional[AsyncSession] = Depends(get_session) if DB_AVAILABLE else None):
    mgr = AIOperationsManager()
    return await mgr.monitor_and_create(limit=limit, db=db)
