from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.config import get_db_async

router = APIRouter(prefix="/api/v1/map", tags=["Map Entities"])

CITY_COORDINATES = {
    "toronto": [43.6532, -79.3832],
    "montreal": [45.5017, -73.5673],
    "vancouver": [49.2827, -123.1207],
    "calgary": [51.0447, -114.0719],
    "edmonton": [53.5461, -113.4938],
    "winnipeg": [49.8951, -97.1384],
    "halifax": [44.6488, -63.5752],
    "new_york": [40.7128, -74.0060],
    "chicago": [41.8781, -87.6298],
    "atlanta": [33.7490, -84.3880],
    "dallas": [32.7767, -96.7970],
    "phoenix": [33.4484, -112.0740],
    "los_angeles": [34.0522, -118.2437],
    "san_francisco": [37.7749, -122.4194],
    "houston": [29.7604, -95.3698],
    "philadelphia": [39.9526, -75.1652],
    "boston": [42.3601, -71.0589],
    "dubai": [25.2048, 55.2708],
    "abu_dhabi": [24.4539, 54.3773],
    "riyadh": [24.7136, 46.6753],
}


def _normalize_key(value: Any) -> str:
    return (
        str(value or "")
        .strip()
        .lower()
        .replace(",", " ")
        .replace("-", " ")
        .replace("/", " ")
        .replace(".", " ")
    )


def _coords_from_text(*values: Any) -> tuple[float | None, float | None]:
    for value in values:
        text_value = _normalize_key(value)
        if not text_value:
            continue
        for chunk in text_value.split():
            if chunk in CITY_COORDINATES:
                coords = CITY_COORDINATES[chunk]
                return float(coords[0]), float(coords[1])
        normalized = "_".join(part for part in text_value.split() if part)
        if normalized in CITY_COORDINATES:
            coords = CITY_COORDINATES[normalized]
            return float(coords[0]), float(coords[1])
    return None, None


def _to_float(value: Any) -> float | None:
    try:
        if value is None or value == "":
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _safe_count(value: Any) -> int:
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0


async def _read_rows(session: AsyncSession, sql: str) -> list[Any]:
    try:
        result = await session.execute(text(sql))
        return list(result.mappings().all())
    except Exception:
        return []


def _format_admin_tenant(row: Any) -> dict[str, Any]:
    lat, lng = _coords_from_text(row.get("company_name"), row.get("domain"), row.get("tenant_id"))
    return {
        "id": row.get("tenant_id"),
        "name": row.get("company_name") or row.get("tenant_id"),
        "type": "tenant",
        "location": {
            "lat": lat,
            "lng": lng,
            "city": None,
            "state": None,
            "country": None,
            "address": row.get("domain"),
        },
        "contact": {
            "phone": row.get("contact_phone"),
            "email": row.get("contact_email"),
            "website": row.get("domain"),
        },
        "stats": {
            "drivers": _safe_count(row.get("users_count")),
            "vehicles": 0,
            "active_shipments": 0,
        },
        "status": row.get("status") or "active",
    }


def _format_core_tenant(row: Any) -> dict[str, Any]:
    lat, lng = _coords_from_text(row.get("name"), row.get("subdomain"), row.get("id"))
    return {
        "id": row.get("id"),
        "name": row.get("name") or row.get("id"),
        "type": "tenant",
        "location": {
            "lat": lat,
            "lng": lng,
            "city": None,
            "state": None,
            "country": None,
            "address": row.get("subdomain"),
        },
        "contact": {
            "phone": None,
            "email": row.get("owner_email"),
            "website": row.get("subdomain"),
        },
        "stats": {
            "drivers": 0,
            "vehicles": 0,
            "active_shipments": 0,
        },
        "status": row.get("status") or "active",
    }


def _format_user_entity(row: Any, entity_type: str) -> dict[str, Any]:
    lat, lng = _coords_from_text(row.get("city"), row.get("company"), row.get("country"))
    base = {
        "id": row.get("id"),
        "name": row.get("full_name") or row.get("company") or row.get("email") or f"{entity_type.title()} {row.get('id')}",
        "type": entity_type,
        "location": {
            "lat": lat,
            "lng": lng,
            "city": row.get("city"),
            "state": None,
            "country": row.get("country"),
            "address": row.get("company"),
        },
        "contact": {
            "phone": row.get("phone_number"),
            "email": row.get("email"),
            "website": None,
        },
        "status": "active" if row.get("is_active") else "inactive",
    }
    if entity_type == "driver":
        base["stats"] = {
            "completed_trips": 0,
            "rating": None,
            "experience": None,
        }
    else:
        base["stats"] = {
            "loads_posted": 0,
            "active_loads": 0,
        }
        base["rating"] = None
    return base


def _format_carrier(row: Any) -> dict[str, Any]:
    lat, lng = _coords_from_text(row.get("name"))
    return {
        "id": row.get("id"),
        "name": row.get("name"),
        "type": "carrier",
        "location": {
            "lat": lat,
            "lng": lng,
            "city": None,
            "state": None,
            "country": None,
            "address": None,
        },
        "contact": {
            "phone": row.get("phone"),
            "email": row.get("email"),
            "website": None,
        },
        "stats": {
            "fleet_size": 0,
            "available_trucks": 0,
            "active_shipments": 0,
        },
        "rating": None,
        "status": "active" if row.get("is_active") else "inactive",
    }


def _format_shipment(row: Any) -> dict[str, Any]:
    pickup_lat, pickup_lng = _coords_from_text(row.get("pickup_location"))
    dropoff_lat, dropoff_lng = _coords_from_text(row.get("dropoff_location"))
    current_lat = _to_float(row.get("latitude"))
    current_lng = _to_float(row.get("longitude"))
    return {
        "id": row.get("id"),
        "reference": row.get("reference") or row.get("id"),
        "type": "shipment",
        "origin": {
            "lat": pickup_lat,
            "lng": pickup_lng,
            "city": row.get("pickup_location"),
            "state": None,
            "country": None,
            "address": row.get("pickup_location"),
        },
        "destination": {
            "lat": dropoff_lat,
            "lng": dropoff_lng,
            "city": row.get("dropoff_location"),
            "state": None,
            "country": None,
            "address": row.get("dropoff_location"),
        },
        "current_location": {
            "lat": current_lat,
            "lng": current_lng,
            "description": row.get("description"),
            "updated_at": row.get("updated_at"),
            "speed": None,
        },
        "cargo": {
            "type": row.get("trailer_type"),
            "weight": row.get("weight"),
            "dimensions": row.get("load_size"),
        },
        "driver_id": row.get("user_id"),
        "carrier_id": None,
        "broker_id": None,
        "status": row.get("status"),
        "eta": None,
        "progress": None,
    }


async def _collect_entities(session: AsyncSession) -> dict[str, list[dict[str, Any]]]:
    admin_tenants_rows = await _read_rows(
        session,
        """
        SELECT tenant_id, company_name, domain, status, users_count, contact_email, contact_phone
        FROM admin_tenants
        ORDER BY company_name NULLS LAST, tenant_id
        """,
    )
    tenants_rows = await _read_rows(
        session,
        """
        SELECT id, name, subdomain, owner_email, status
        FROM tenants
        ORDER BY name NULLS LAST, id
        """,
    )
    drivers_rows = await _read_rows(
        session,
        """
        SELECT id, full_name, email, phone_number, company, city, country, is_active
        FROM users
        WHERE lower(role) = 'driver' AND COALESCE(is_deleted, FALSE) = FALSE
        ORDER BY created_at DESC NULLS LAST, id DESC
        LIMIT 200
        """,
    )
    brokers_rows = await _read_rows(
        session,
        """
        SELECT id, full_name, email, phone_number, company, city, country, is_active
        FROM users
        WHERE lower(role) IN ('broker', 'freight_broker', 'dispatcher', 'manager')
          AND COALESCE(is_deleted, FALSE) = FALSE
        ORDER BY created_at DESC NULLS LAST, id DESC
        LIMIT 200
        """,
    )
    carriers_rows = await _read_rows(
        session,
        """
        SELECT id, name, phone, email, is_active
        FROM carriers
        ORDER BY id DESC
        LIMIT 200
        """,
    )
    shipments_rows = await _read_rows(
        session,
        """
        SELECT
            id,
            id::text AS reference,
            pickup_location,
            dropoff_location,
            description,
            trailer_type,
            weight,
            load_size,
            latitude,
            longitude,
            status,
            user_id,
            updated_at
        FROM shipments
        ORDER BY created_at DESC NULLS LAST, id DESC
        LIMIT 200
        """,
    )

    tenants: list[dict[str, Any]] = []
    seen_tenants: set[str] = set()
    for row in admin_tenants_rows:
        item = _format_admin_tenant(row)
        if item["id"] in seen_tenants:
            continue
        seen_tenants.add(str(item["id"]))
        tenants.append(item)
    for row in tenants_rows:
        item = _format_core_tenant(row)
        if item["id"] in seen_tenants:
            continue
        seen_tenants.add(str(item["id"]))
        tenants.append(item)

    brokers = [_format_user_entity(row, "broker") for row in brokers_rows]
    carriers = [_format_carrier(row) for row in carriers_rows]
    drivers = [_format_user_entity(row, "driver") for row in drivers_rows]
    shipments = [_format_shipment(row) for row in shipments_rows]

    return {
        "tenants": [item for item in tenants if item["location"]["lat"] and item["location"]["lng"]],
        "brokers": [item for item in brokers if item["location"]["lat"] and item["location"]["lng"]],
        "carriers": [item for item in carriers if item["location"]["lat"] and item["location"]["lng"]],
        "drivers": [item for item in drivers if item["location"]["lat"] and item["location"]["lng"]],
        "shipments": shipments,
    }


@router.get("/entities")
async def get_all_map_entities(db: AsyncSession = Depends(get_db_async)) -> dict[str, Any]:
    return await _collect_entities(db)


@router.get("/tenants")
async def get_map_tenants(db: AsyncSession = Depends(get_db_async)) -> dict[str, Any]:
    return {"tenants": (await _collect_entities(db))["tenants"]}


@router.get("/brokers")
async def get_map_brokers(db: AsyncSession = Depends(get_db_async)) -> dict[str, Any]:
    return {"brokers": (await _collect_entities(db))["brokers"]}


@router.get("/carriers")
async def get_map_carriers(db: AsyncSession = Depends(get_db_async)) -> dict[str, Any]:
    return {"carriers": (await _collect_entities(db))["carriers"]}


@router.get("/drivers")
async def get_map_drivers(db: AsyncSession = Depends(get_db_async)) -> dict[str, Any]:
    return {"drivers": (await _collect_entities(db))["drivers"]}


@router.get("/shipments")
async def get_map_shipments(db: AsyncSession = Depends(get_db_async)) -> dict[str, Any]:
    return {"shipments": (await _collect_entities(db))["shipments"]}
