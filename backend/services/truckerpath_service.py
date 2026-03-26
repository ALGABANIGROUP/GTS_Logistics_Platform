# backend/services/truckerpath_service.py
from __future__ import annotations

import logging
import inspect
from typing import Any, Dict, Optional, Iterable, Tuple, List

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

# Outbound provider (handles HTTP + env; has pull_loads + optional others)
from backend.integrations.loadboards.truckerpath import TruckerPathProvider

logger = logging.getLogger("truckerpath.service")

# Initialize once; provider reads integration env.
_provider = TruckerPathProvider()

# Try to import your Shipment model from common locations
Shipment = None  # type: ignore
for _path in (
    "backend.models.shipment",        # e.g., class Shipment in shipment.py
    "backend.models.models",          # e.g., class Shipment in models.py
):
    try:
        mod = __import__(_path, fromlist=["Shipment"])
        Shipment = getattr(mod, "Shipment")
        break
    except Exception as e:
        logger.debug("Shipment not in %s: %s", _path, e)


class TruckerPathService:
    """
    Unified service for TruckerPath:
    - Outbound: delegates to TruckerPathProvider when available.
    - Inbound: maps webhook events to DB updates on your Shipment model.
    """

    # ---------------------- Safe outbound helpers ----------------------

    @staticmethod
    async def _call_provider(method_name: str, *args: Any, **kwargs: Any) -> Any:
        """Call a provider method if it exists; otherwise return a disabled result."""
        if not getattr(_provider, "auth", ""):
            return {
                "ok": False,
                "error": "truckerpath_not_configured",
                "message": "Set TRUCKERPATH_API_TOKEN to enable TruckerPath integration.",
            }
        fn = getattr(_provider, method_name, None)
        if callable(fn):
            res = fn(*args, **kwargs)
            if inspect.isawaitable(res):
                return await res
            return res
        return {
            "ok": False,
            "error": "provider_method_unavailable",
            "method": method_name,
            "message": f"TruckerPath provider does not implement '{method_name}'.",
        }

    # ---------------------- Outbound (public API) ----------------------

    @staticmethod
    async def ping() -> Dict[str, Any]:
        if not getattr(_provider, "auth", ""):
            return {"ok": False, "provider": getattr(_provider, "name", "truckerpath"), "configured": False}
        return {"ok": True, "provider": getattr(_provider, "name", "truckerpath")}

    @staticmethod
    async def create_company(payload: Dict[str, Any]) -> Dict[str, Any]:
        return await TruckerPathService._call_provider("create_company", payload)

    @staticmethod
    async def post_load(payload: Dict[str, Any]) -> Dict[str, Any]:
        return await TruckerPathService._call_provider("post_load", payload)

    @staticmethod
    async def register_webhook(payload: Dict[str, Any]) -> Dict[str, Any]:
        # If provider exposes register_webhook(url) signature, adapt payload automatically
        return await TruckerPathService._call_provider("register_webhook", payload)

    @staticmethod
    async def register_webhook_add(payload: Dict[str, Any]) -> Dict[str, Any]:
        return await TruckerPathService._call_provider("register_webhook_add", payload)

    @staticmethod
    async def tracking_create(payload: Dict[str, Any]) -> Dict[str, Any]:
        return await TruckerPathService._call_provider("tracking_create", payload)

    @staticmethod
    async def push_tracking_points(payload: Dict[str, Any]) -> Dict[str, Any]:
        return await TruckerPathService._call_provider("push_tracking_points", payload)

    @staticmethod
    async def list_loads(limit: int = 10, **filters: Any) -> Dict[str, Any]:
        """
        Returns normalized shape:
        { "loads": [...], "total": int, "source": "mock"|"live"|... }
        """
        res = await TruckerPathService._call_provider("list_loads", limit=limit, **filters)
        if isinstance(res, dict) and not res.get("ok", True) and "loads" not in res:
            return {
                "loads": [],
                "total": 0,
                "source": "disabled",
                "error": res.get("error"),
                "message": res.get("message"),
            }
        if isinstance(res, dict) and "loads" in res:
            loads = res["loads"] or []
            if limit:
                loads = loads[:limit]
            res["loads"] = loads
            res.setdefault("total", len(loads))
            return res

        if isinstance(res, list):
            return {"loads": res[:limit], "total": min(len(res), limit)}

        return {"loads": [], "total": 0, "source": "disabled"}

    # ---------------------- Inbound (webhook -> DB) ----------------------

    # Map provider statuses to internal statuses. Adjust to your domain as needed.
    STATUS_MAP: Dict[str, str] = {
        "posted": "posted",
        "booked": "booked",
        "in_transit": "on_the_way",
        "in-transit": "on_the_way",
        "picked_up": "on_the_way",
        "delivered": "completed",
        "completed": "completed",
        "cancelled": "cancelled",
        "canceled": "cancelled",
        "failed": "failed",
    }

    @staticmethod
    async def _first_match(
        db: AsyncSession,
        *conds: Any,
    ) -> Optional[Any]:
        """
        Return first Shipment matching any cond in order.
        """
        if Shipment is None:
            return None
        for cond in conds:
            if not cond:
                continue
            q = await db.execute(select(Shipment).where(cond).limit(1))
            obj = q.scalars().first()
            if obj:
                return obj
        return None

    @staticmethod
    async def find_shipment(
        db: AsyncSession,
        *,
        load_id: Optional[str] = None,
        shipment_id: Optional[str] = None,
        reference_id: Optional[str] = None,
        extra_ref: Optional[str] = None,
    ) -> Optional[Any]:
        """
        Try multiple keys in sequence to locate a Shipment.
        Adapt conditions to match your schema names.
        """
        if Shipment is None:
            return None

        conds: List[Any] = []
        if reference_id:
            try:
                conds.append(Shipment.reference_id == reference_id)  # type: ignore[attr-defined]
            except Exception:
                pass
        if load_id:
            try:
                conds.append(Shipment.external_load_id == load_id)  # type: ignore[attr-defined]
            except Exception:
                pass
        if shipment_id:
            try:
                conds.append(Shipment.external_shipment_id == shipment_id)  # type: ignore[attr-defined]
            except Exception:
                pass
        if extra_ref:
            # Optional alternative reference (BOL/PRO/etc.) if you store it
            for attr in ("bol_number", "pro_number", "customer_ref", "tp_reference"):
                try:
                    conds.append(getattr(Shipment, attr) == extra_ref)  # type: ignore[attr-defined]
                except Exception:
                    continue

        return await TruckerPathService._first_match(db, *conds)

    # ---------------- Mapping helpers ----------------

    @staticmethod
    def _extract_ids(data: Dict[str, Any]) -> Tuple[Optional[str], Optional[str], Optional[str], Optional[str]]:
        """
        Extract likely identifiers from provider payload.
        Returns: (load_id, shipment_id, reference_id, extra_ref)
        """
        load_id = str(data.get("load_id") or data.get("loadId") or "") or None
        shipment_id = str(data.get("shipment_id") or data.get("shipmentId") or "") or None
        reference_id = str(data.get("reference_id") or data.get("referenceId") or "") or None
        extra_ref = str(
            data.get("bol") or data.get("bol_number") or data.get("pro") or data.get("pro_number") or ""
        ) or None
        return load_id, shipment_id, reference_id, extra_ref

    @staticmethod
    def _map_status(provider_status: Optional[str], current_status: Optional[str]) -> Optional[str]:
        if not provider_status:
            return None
        key = provider_status.replace(" ", "_").lower()
        return TruckerPathService.STATUS_MAP.get(key, current_status)

    @staticmethod
    def _extract_last_point(data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Try to read latest tracking point from payload.
        Accepts either a list under 'points'/'locations' or direct lat/lng on root.
        """
        # List of points
        points = data.get("points") or data.get("locations")
        if isinstance(points, list) and points:
            return points[-1]
        # Single point
        if "lat" in data and "lng" in data:
            return {"lat": data.get("lat"), "lng": data.get("lng")}
        return None

    # ---------------- Apply updates ----------------

    @staticmethod
    async def apply_tracking_update(db: AsyncSession, shipment: Any, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update current_lat/current_lng (or latitude/longitude) from tracking payload.
        """
        last_point = TruckerPathService._extract_last_point(data)
        if not last_point:
            return {"applied": False, "reason": "no_point"}

        try:
            lat_val = last_point.get("lat")
            lng_val = last_point.get("lng")
            if lat_val is None or lng_val is None:
                return {"applied": False, "reason": "invalid_point"}
            lat = float(lat_val)
            lng = float(lng_val)
        except Exception:
            return {"applied": False, "reason": "invalid_point"}

        values: Dict[str, Any] = {}
        # Adjust field names if your schema differs
        for name, val in (("current_lat", lat), ("current_lng", lng)):
            try:
                getattr(shipment, name)  # check attribute exists
                values[name] = val
            except Exception:
                # Try alternative common names
                alt = "latitude" if "lat" in name else "longitude"
                try:
                    getattr(shipment, alt)
                    values[alt] = val
                except Exception:
                    continue

        if not values:
            return {"applied": False, "reason": "no_fields"}

        await db.execute(update(Shipment).where(Shipment.id == shipment.id).values(**values))  # type: ignore
        await db.commit()
        return {"applied": True, "values": values}

    @staticmethod
    async def apply_status_update(db: AsyncSession, shipment: Any, provider_status: Optional[str]) -> Dict[str, Any]:
        """
        Map provider status to internal status and persist.
        """
        new_status = TruckerPathService._map_status(provider_status, getattr(shipment, "status", None))
        if not new_status or new_status == getattr(shipment, "status", None):
            return {"applied": False, "reason": "no_change"}

        await db.execute(
            update(Shipment).where(Shipment.id == shipment.id).values(status=new_status)  # type: ignore
        )
        await db.commit()
        return {"applied": True, "values": {"status": new_status}}

    # ---------------- Entry point ----------------

    @staticmethod
    async def handle_webhook(db: AsyncSession, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generic handler for TruckerPath webhook events.
        Expected minimal shape:
          {
            "event": "tracking.update" | "load.status" | "load.booked" | ...,
            "data": { ... }
          }
        """
        event = (payload.get("event") or payload.get("type") or "").strip()
        data = payload.get("data") or {}

        load_id, shipment_id, reference_id, extra_ref = TruckerPathService._extract_ids(data)

        # Locate shipment record
        shipment = await TruckerPathService.find_shipment(
            db,
            load_id=load_id,
            shipment_id=shipment_id,
            reference_id=reference_id,
            extra_ref=extra_ref,
        )
        if not shipment:
            logger.info(
                "Webhook received but shipment not found. ids=%s",
                (load_id, shipment_id, reference_id, extra_ref),
            )
            return {
                "ok": True,
                "matched": False,
                "event": event,
                "ids": {
                    "load_id": load_id,
                    "shipment_id": shipment_id,
                    "reference_id": reference_id,
                    "extra_ref": extra_ref,
                },
            }

        applied: Dict[str, Any] = {}

        # Apply event-specific updates
        ev = event.lower().replace(" ", "_")
        try:
            if ev in {"tracking.update", "tracking_update"}:
                res = await TruckerPathService.apply_tracking_update(db, shipment, data)
                applied["tracking"] = res

            if ev in {"load.status", "load_status"}:
                provider_status = str(data.get("status") or "")
                res = await TruckerPathService.apply_status_update(db, shipment, provider_status)
                applied["status"] = res

            if ev in {"load.booked", "booked"}:
                res = await TruckerPathService.apply_status_update(db, shipment, "booked")
                applied["booked"] = res

        except Exception as e:  # keep webhook resilient
            logger.exception("Failed to apply webhook update: %s", e)
            return {"ok": True, "matched": True, "event": event, "error": str(e)}

        return {"ok": True, "matched": True, "event": event, "applied": applied}

    # ---------------- Optional helpers (outbound) ----------------

    @staticmethod
    def build_post_load_payload_from_internal(shipment: Any) -> Dict[str, Any]:
        """
        Convert your internal shipment object into TruckerPath post-load payload shape.
        Adjust the mappings to your model fields.
        """
        # Example assumptions; rename to your fields:
        pickup = getattr(shipment, "pickup", None)  # object with city/state/lat/lng/date
        dropoff = getattr(shipment, "dropoff", None)

        return {
            "company_id": getattr(shipment, "company_mc", None) or "",
            "contact_info": {
                "contact_email": getattr(shipment, "contact_email", "ops@example.com"),
                "contact_first_name": getattr(shipment, "contact_first_name", "Ops"),
                "contact_last_name": getattr(shipment, "contact_last_name", "Team"),
                "contact_phone_number": getattr(shipment, "contact_phone", "+10000000000"),
                "contact_phone_ext": "",
            },
            "shipment_info": {
                "equipment": [getattr(shipment, "equipment_type", "Dry Van")],
                "load_size": "FULL",
                "description": getattr(shipment, "description", "") or "",
                "shipment_weight": int(getattr(shipment, "weight_lbs", 0) or 0),
                "shipment_dimensions": {},
                "requirements": getattr(shipment, "requirements", "") or "",
                "stop_list": [
                    {
                        "type": "PICKUP",
                        "state": getattr(pickup, "state", None),
                        "city": getattr(pickup, "city", None),
                        "address": getattr(pickup, "address", None),
                        "lat": getattr(pickup, "lat", None),
                        "lng": getattr(pickup, "lng", None),
                        "date_local": getattr(pickup, "date_local", None),
                    },
                    {
                        "type": "DROPOFF",
                        "state": getattr(dropoff, "state", None),
                        "city": getattr(dropoff, "city", None),
                        "address": getattr(dropoff, "address", None),
                        "lat": getattr(dropoff, "lat", None),
                        "lng": getattr(dropoff, "lng", None),
                        "date_local": getattr(dropoff, "date_local", None),
                    },
                ],
            },
        }
