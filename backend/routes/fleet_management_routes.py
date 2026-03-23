from __future__ import annotations

import asyncio
import json
from datetime import date, datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, EmailStr
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.config import get_db_async
from backend.security.auth import get_password_hash, require_roles

router = APIRouter(
    prefix="/api/v1/fleet",
    tags=["Fleet Management"],
    dependencies=[Depends(require_roles(["admin", "owner", "super_admin"]))],
)

_schema_ready = False
_schema_lock = asyncio.Lock()

DRIVER_STATUS = {
    "available": "Available",
    "busy": "Busy",
    "rest": "On Rest",
    "leave": "On Leave",
    "inactive": "Inactive",
}

VEHICLE_STATUS = {
    "available": "Available",
    "occupied": "Occupied",
    "maintenance": "Maintenance",
    "broken": "Broken",
    "inactive": "Inactive",
}

VEHICLE_TYPES = {
    "small_truck": "Small Truck",
    "medium_truck": "Medium Truck",
    "large_truck": "Large Truck",
    "refrigerated": "Refrigerated",
    "light_transport": "Light Transport",
}

INCIDENT_TYPES = {
    "accident": "Traffic Accident",
    "breakdown": "Mechanical Breakdown",
    "injury": "Injury",
    "theft": "Theft",
    "other": "Other",
}

INCIDENT_SEVERITY = {
    "low": "Low",
    "medium": "Medium",
    "high": "High",
    "critical": "Critical",
}

INCIDENT_STATUS = {
    "open": "Open",
    "investigating": "Investigating",
    "closed": "Closed",
}

SCHEMA_SQL = [
    """
    CREATE TABLE IF NOT EXISTS fleet_driver_profiles (
        user_id INTEGER PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
        driver_code VARCHAR(50) UNIQUE NOT NULL,
        license_number VARCHAR(50),
        license_expiry DATE,
        hire_date DATE,
        status VARCHAR(20) NOT NULL DEFAULT 'available',
        rating NUMERIC(3,2) NOT NULL DEFAULT 5.0,
        total_trips INTEGER NOT NULL DEFAULT 0,
        safety_score NUMERIC(5,2) NOT NULL DEFAULT 100.0,
        violations_count INTEGER NOT NULL DEFAULT 0,
        notes TEXT,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS fleet_vehicles (
        id SERIAL PRIMARY KEY,
        vehicle_code VARCHAR(50) UNIQUE NOT NULL,
        plate_number VARCHAR(20) UNIQUE NOT NULL,
        type VARCHAR(40) NOT NULL,
        capacity_kg NUMERIC(10,2),
        year INTEGER,
        status VARCHAR(20) NOT NULL DEFAULT 'available',
        current_driver_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
        last_maintenance DATE,
        next_maintenance DATE,
        current_km INTEGER NOT NULL DEFAULT 0,
        fuel_type VARCHAR(50),
        insurance_expiry DATE,
        notes TEXT,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS fleet_driver_vehicle_assignments (
        id SERIAL PRIMARY KEY,
        driver_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        vehicle_id INTEGER NOT NULL REFERENCES fleet_vehicles(id) ON DELETE CASCADE,
        assigned_date DATE NOT NULL DEFAULT CURRENT_DATE,
        unassigned_date DATE,
        is_active BOOLEAN NOT NULL DEFAULT TRUE,
        notes TEXT,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    )
    """,
    """
    CREATE UNIQUE INDEX IF NOT EXISTS uq_fleet_active_driver_assignment
    ON fleet_driver_vehicle_assignments (driver_id)
    WHERE is_active = TRUE
    """,
    """
    CREATE UNIQUE INDEX IF NOT EXISTS uq_fleet_active_vehicle_assignment
    ON fleet_driver_vehicle_assignments (vehicle_id)
    WHERE is_active = TRUE
    """,
    """
    CREATE TABLE IF NOT EXISTS fleet_incidents (
        id SERIAL PRIMARY KEY,
        incident_number VARCHAR(50) UNIQUE NOT NULL,
        incident_date TIMESTAMPTZ NOT NULL,
        incident_type VARCHAR(30) NOT NULL,
        driver_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
        vehicle_id INTEGER REFERENCES fleet_vehicles(id) ON DELETE SET NULL,
        location TEXT,
        description TEXT,
        severity VARCHAR(20) NOT NULL DEFAULT 'medium',
        actions_taken TEXT,
        status VARCHAR(20) NOT NULL DEFAULT 'open',
        police_report VARCHAR(500),
        insurance_claim VARCHAR(200),
        images JSONB NOT NULL DEFAULT '[]'::jsonb,
        created_by VARCHAR(100),
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        resolved_at TIMESTAMPTZ
    )
    """,
]


class DriverCreate(BaseModel):
    email: EmailStr
    full_name: str
    phone_number: Optional[str] = None
    password: Optional[str] = None
    company: Optional[str] = None
    country: Optional[str] = None
    license_number: Optional[str] = None
    license_expiry: Optional[str] = None
    hire_date: Optional[str] = None
    status: Optional[str] = "available"
    rating: Optional[float] = 5.0
    total_trips: Optional[int] = 0
    safety_score: Optional[float] = 100.0
    violations_count: Optional[int] = 0
    notes: Optional[str] = None


class DriverUpdate(BaseModel):
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[EmailStr] = None
    company: Optional[str] = None
    country: Optional[str] = None
    license_number: Optional[str] = None
    license_expiry: Optional[str] = None
    hire_date: Optional[str] = None
    status: Optional[str] = None
    rating: Optional[float] = None
    total_trips: Optional[int] = None
    safety_score: Optional[float] = None
    violations_count: Optional[int] = None
    is_active: Optional[bool] = None
    notes: Optional[str] = None
    password: Optional[str] = None


class VehicleCreate(BaseModel):
    plate_number: str
    type: str
    capacity_kg: Optional[float] = None
    year: Optional[int] = None
    status: Optional[str] = "available"
    last_maintenance: Optional[str] = None
    next_maintenance: Optional[str] = None
    current_km: Optional[int] = 0
    fuel_type: Optional[str] = None
    insurance_expiry: Optional[str] = None
    notes: Optional[str] = None


class VehicleUpdate(BaseModel):
    plate_number: Optional[str] = None
    type: Optional[str] = None
    capacity_kg: Optional[float] = None
    year: Optional[int] = None
    status: Optional[str] = None
    last_maintenance: Optional[str] = None
    next_maintenance: Optional[str] = None
    current_km: Optional[int] = None
    fuel_type: Optional[str] = None
    insurance_expiry: Optional[str] = None
    notes: Optional[str] = None


class AssignmentCreate(BaseModel):
    driver_id: int
    vehicle_id: int
    notes: Optional[str] = None


class IncidentCreate(BaseModel):
    incident_date: str
    incident_type: str
    driver_id: Optional[int] = None
    vehicle_id: Optional[int] = None
    location: Optional[str] = None
    description: Optional[str] = None
    severity: Optional[str] = "medium"
    actions_taken: Optional[str] = None
    status: Optional[str] = "open"
    police_report: Optional[str] = None
    insurance_claim: Optional[str] = None
    images: Optional[List[str]] = None
    created_by: Optional[str] = None


class IncidentUpdate(BaseModel):
    incident_date: Optional[str] = None
    incident_type: Optional[str] = None
    driver_id: Optional[int] = None
    vehicle_id: Optional[int] = None
    location: Optional[str] = None
    description: Optional[str] = None
    severity: Optional[str] = None
    actions_taken: Optional[str] = None
    status: Optional[str] = None
    police_report: Optional[str] = None
    insurance_claim: Optional[str] = None
    images: Optional[List[str]] = None


def _parse_date(value: Optional[str]) -> Optional[date]:
    if not value:
        return None
    return date.fromisoformat(str(value)[:10])


def _parse_datetime(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    return datetime.fromisoformat(str(value).replace("Z", "+00:00"))


def _mapping_rows(result) -> List[Dict[str, Any]]:
    return [dict(row) for row in result.mappings().all()]


def _mapping_one(result) -> Optional[Dict[str, Any]]:
    row = result.mappings().first()
    return dict(row) if row else None


async def _ensure_schema(db: AsyncSession) -> None:
    global _schema_ready
    if _schema_ready:
        return
    async with _schema_lock:
        if _schema_ready:
            return
        for statement in SCHEMA_SQL:
            await db.execute(text(statement))
        await db.commit()
        _schema_ready = True


def _driver_projection() -> str:
    return """
        SELECT
            u.id,
            COALESCE(p.driver_code, 'DRV' || LPAD(u.id::text, 4, '0')) AS driver_code,
            u.full_name,
            u.email,
            u.phone_number,
            u.company,
            u.country,
            u.is_active,
            p.license_number,
            p.license_expiry,
            p.hire_date,
            COALESCE(p.status, CASE WHEN u.is_active THEN 'available' ELSE 'inactive' END) AS status,
            COALESCE(p.rating, 5.0) AS rating,
            COALESCE(p.total_trips, 0) AS total_trips,
            COALESCE(p.safety_score, 100.0) AS safety_score,
            COALESCE(p.violations_count, 0) AS violations_count,
            p.notes,
            u.created_at
        FROM users u
        LEFT JOIN fleet_driver_profiles p ON p.user_id = u.id
        WHERE LOWER(COALESCE(u.role, '')) = 'driver'
          AND COALESCE(u.is_deleted, FALSE) = FALSE
    """


async def _ensure_driver_profile(db: AsyncSession, driver_id: int) -> None:
    existing = await db.execute(
        text("SELECT 1 FROM fleet_driver_profiles WHERE user_id = :driver_id"),
        {"driver_id": driver_id},
    )
    if existing.scalar_one_or_none():
        return
    await db.execute(
        text(
            """
            INSERT INTO fleet_driver_profiles (
                user_id, driver_code, status, rating, total_trips, safety_score, violations_count
            )
            VALUES (
                :driver_id,
                'DRV' || LPAD(:driver_id::text, 4, '0'),
                'available',
                5.0,
                0,
                100.0,
                0
            )
            """
        ),
        {"driver_id": driver_id},
    )


@router.get("/config")
async def get_fleet_config(db: AsyncSession = Depends(get_db_async)) -> Dict[str, Any]:
    await _ensure_schema(db)
    return {
        "driver_status": DRIVER_STATUS,
        "vehicle_status": VEHICLE_STATUS,
        "vehicle_types": VEHICLE_TYPES,
        "incident_types": INCIDENT_TYPES,
        "incident_severity": INCIDENT_SEVERITY,
        "incident_status": INCIDENT_STATUS,
    }


@router.get("/dashboard")
async def get_dashboard(db: AsyncSession = Depends(get_db_async)) -> Dict[str, Any]:
    await _ensure_schema(db)
    summary: Dict[str, int] = {}

    total_drivers = await db.execute(
        text(
            """
            SELECT COUNT(*)
            FROM users
            WHERE LOWER(COALESCE(role, '')) = 'driver'
              AND COALESCE(is_deleted, FALSE) = FALSE
            """
        )
    )
    summary["total_drivers"] = int(total_drivers.scalar_one() or 0)

    available_drivers = await db.execute(
        text(
            """
            SELECT COUNT(*)
            FROM fleet_driver_profiles p
            JOIN users u ON u.id = p.user_id
            WHERE LOWER(COALESCE(u.role, '')) = 'driver'
              AND COALESCE(u.is_deleted, FALSE) = FALSE
              AND COALESCE(u.is_active, TRUE) = TRUE
              AND p.status = 'available'
            """
        )
    )
    summary["available_drivers"] = int(available_drivers.scalar_one() or 0)

    total_vehicles = await db.execute(text("SELECT COUNT(*) FROM fleet_vehicles WHERE status <> 'inactive'"))
    summary["total_vehicles"] = int(total_vehicles.scalar_one() or 0)

    available_vehicles = await db.execute(text("SELECT COUNT(*) FROM fleet_vehicles WHERE status = 'available'"))
    summary["available_vehicles"] = int(available_vehicles.scalar_one() or 0)

    maintenance_due = await db.execute(text("SELECT COUNT(*) FROM fleet_vehicles WHERE status = 'maintenance'"))
    summary["maintenance_due"] = int(maintenance_due.scalar_one() or 0)

    total_incidents = await db.execute(text("SELECT COUNT(*) FROM fleet_incidents"))
    summary["total_incidents"] = int(total_incidents.scalar_one() or 0)

    this_month = await db.execute(
        text(
            """
            SELECT COUNT(*)
            FROM fleet_incidents
            WHERE DATE_TRUNC('month', incident_date) = DATE_TRUNC('month', NOW())
            """
        )
    )
    summary["incidents_this_month"] = int(this_month.scalar_one() or 0)

    this_week = await db.execute(
        text(
            """
            SELECT COUNT(*)
            FROM fleet_incidents
            WHERE DATE_TRUNC('week', incident_date) = DATE_TRUNC('week', NOW())
            """
        )
    )
    summary["incidents_this_week"] = int(this_week.scalar_one() or 0)

    today = await db.execute(text("SELECT COUNT(*) FROM fleet_incidents WHERE incident_date::date = CURRENT_DATE"))
    summary["incidents_today"] = int(today.scalar_one() or 0)

    open_incidents = await db.execute(
        text("SELECT COUNT(*) FROM fleet_incidents WHERE status IN ('open', 'investigating')")
    )
    summary["open_incidents"] = int(open_incidents.scalar_one() or 0)

    recent_incidents = await db.execute(
        text(
            """
            SELECT
                i.id,
                i.incident_number,
                i.incident_date,
                i.incident_type,
                i.severity,
                i.status,
                d.full_name AS driver_name,
                v.plate_number
            FROM fleet_incidents i
            LEFT JOIN users d ON d.id = i.driver_id
            LEFT JOIN fleet_vehicles v ON v.id = i.vehicle_id
            ORDER BY i.incident_date DESC
            LIMIT 5
            """
        )
    )

    maintenance_alerts = await db.execute(
        text(
            """
            SELECT id, vehicle_code, plate_number, next_maintenance, status
            FROM fleet_vehicles
            WHERE next_maintenance IS NOT NULL
              AND next_maintenance <= CURRENT_DATE + INTERVAL '30 days'
              AND status <> 'inactive'
            ORDER BY next_maintenance ASC
            LIMIT 6
            """
        )
    )

    return {
        "summary": summary,
        "recent_incidents": _mapping_rows(recent_incidents),
        "maintenance_alerts": _mapping_rows(maintenance_alerts),
    }


@router.get("/drivers")
async def list_drivers(
    search: Optional[str] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status"),
    db: AsyncSession = Depends(get_db_async),
) -> Dict[str, Any]:
    await _ensure_schema(db)
    query = _driver_projection()
    params: Dict[str, Any] = {}

    if search:
        query += """
            AND (
                u.full_name ILIKE :search
                OR u.email ILIKE :search
                OR COALESCE(p.driver_code, '') ILIKE :search
                OR COALESCE(u.phone_number, '') ILIKE :search
            )
        """
        params["search"] = f"%{search.strip()}%"

    if status_filter:
        query += " AND COALESCE(p.status, CASE WHEN u.is_active THEN 'available' ELSE 'inactive' END) = :status"
        params["status"] = status_filter

    query += " ORDER BY u.created_at DESC"
    result = await db.execute(text(query), params)
    return {"ok": True, "drivers": _mapping_rows(result)}


@router.post("/drivers", status_code=status.HTTP_201_CREATED)
async def create_driver(payload: DriverCreate, db: AsyncSession = Depends(get_db_async)) -> Dict[str, Any]:
    await _ensure_schema(db)

    email = payload.email.strip().lower()
    exists = await db.execute(
        text(
            """
            SELECT id
            FROM users
            WHERE LOWER(email) = :email
              AND COALESCE(is_deleted, FALSE) = FALSE
            """
        ),
        {"email": email},
    )
    if exists.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Driver email already exists")

    created = await db.execute(
        text(
            """
            INSERT INTO users (
                email, full_name, phone_number, hashed_password, company, country,
                role, is_active, created_at, updated_at
            )
            VALUES (
                :email, :full_name, :phone_number, :hashed_password, :company, :country,
                'driver', TRUE, NOW(), NOW()
            )
            RETURNING id
            """
        ),
        {
            "email": email,
            "full_name": payload.full_name.strip(),
            "phone_number": payload.phone_number,
            "hashed_password": get_password_hash(payload.password) if payload.password else None,
            "company": payload.company,
            "country": payload.country,
        },
    )
    driver_id = int(created.scalar_one())

    await db.execute(
        text(
            """
            INSERT INTO fleet_driver_profiles (
                user_id, driver_code, license_number, license_expiry, hire_date,
                status, rating, total_trips, safety_score, violations_count, notes, created_at, updated_at
            )
            VALUES (
                :user_id,
                'DRV' || LPAD(:user_id::text, 4, '0'),
                :license_number,
                :license_expiry,
                :hire_date,
                :status,
                :rating,
                :total_trips,
                :safety_score,
                :violations_count,
                :notes,
                NOW(),
                NOW()
            )
            """
        ),
        {
            "user_id": driver_id,
            "license_number": payload.license_number,
            "license_expiry": _parse_date(payload.license_expiry),
            "hire_date": _parse_date(payload.hire_date) or date.today(),
            "status": payload.status or "available",
            "rating": payload.rating or 5.0,
            "total_trips": payload.total_trips or 0,
            "safety_score": payload.safety_score or 100.0,
            "violations_count": payload.violations_count or 0,
            "notes": payload.notes,
        },
    )
    await db.commit()
    return {"ok": True, "driver_id": driver_id}


@router.patch("/drivers/{driver_id}")
async def update_driver(
    driver_id: int,
    payload: DriverUpdate,
    db: AsyncSession = Depends(get_db_async),
) -> Dict[str, Any]:
    await _ensure_schema(db)
    await _ensure_driver_profile(db, driver_id)

    user_exists = await db.execute(
        text(
            """
            SELECT id
            FROM users
            WHERE id = :driver_id
              AND LOWER(COALESCE(role, '')) = 'driver'
              AND COALESCE(is_deleted, FALSE) = FALSE
            """
        ),
        {"driver_id": driver_id},
    )
    if not user_exists.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Driver not found")

    user_fields: List[str] = []
    user_params: Dict[str, Any] = {"driver_id": driver_id}
    profile_fields: List[str] = []
    profile_params: Dict[str, Any] = {"driver_id": driver_id}

    for field in ["full_name", "phone_number", "company", "country", "is_active"]:
        value = getattr(payload, field)
        if value is not None:
            user_fields.append(f"{field} = :{field}")
            user_params[field] = value

    if payload.email is not None:
        user_fields.append("email = :email")
        user_params["email"] = payload.email.strip().lower()

    if payload.password:
        user_fields.append("hashed_password = :hashed_password")
        user_params["hashed_password"] = get_password_hash(payload.password)

    profile_mapping = {
        "license_number": payload.license_number,
        "status": payload.status,
        "rating": payload.rating,
        "total_trips": payload.total_trips,
        "safety_score": payload.safety_score,
        "violations_count": payload.violations_count,
        "notes": payload.notes,
    }
    for field, value in profile_mapping.items():
        if value is not None:
            profile_fields.append(f"{field} = :{field}")
            profile_params[field] = value

    if payload.license_expiry is not None:
        profile_fields.append("license_expiry = :license_expiry")
        profile_params["license_expiry"] = _parse_date(payload.license_expiry)
    if payload.hire_date is not None:
        profile_fields.append("hire_date = :hire_date")
        profile_params["hire_date"] = _parse_date(payload.hire_date)

    if user_fields:
        user_fields.append("updated_at = NOW()")
        await db.execute(
            text(f"UPDATE users SET {', '.join(user_fields)} WHERE id = :driver_id"),
            user_params,
        )
    if profile_fields:
        profile_fields.append("updated_at = NOW()")
        await db.execute(
            text(f"UPDATE fleet_driver_profiles SET {', '.join(profile_fields)} WHERE user_id = :driver_id"),
            profile_params,
        )

    await db.commit()
    return {"ok": True}


@router.delete("/drivers/{driver_id}")
async def delete_driver(driver_id: int, db: AsyncSession = Depends(get_db_async)) -> Dict[str, Any]:
    await _ensure_schema(db)
    await db.execute(
        text(
            """
            UPDATE users
            SET is_active = FALSE, is_deleted = TRUE, deleted_at = NOW(), updated_at = NOW()
            WHERE id = :driver_id AND LOWER(COALESCE(role, '')) = 'driver'
            """
        ),
        {"driver_id": driver_id},
    )
    await db.execute(
        text(
            """
            UPDATE fleet_driver_profiles
            SET status = 'inactive', updated_at = NOW()
            WHERE user_id = :driver_id
            """
        ),
        {"driver_id": driver_id},
    )
    await db.execute(
        text(
            """
            UPDATE fleet_driver_vehicle_assignments
            SET is_active = FALSE, unassigned_date = CURRENT_DATE
            WHERE driver_id = :driver_id AND is_active = TRUE
            """
        ),
        {"driver_id": driver_id},
    )
    await db.execute(
        text(
            """
            UPDATE fleet_vehicles
            SET current_driver_id = NULL,
                status = CASE WHEN status = 'occupied' THEN 'available' ELSE status END,
                updated_at = NOW()
            WHERE current_driver_id = :driver_id
            """
        ),
        {"driver_id": driver_id},
    )
    await db.commit()
    return {"ok": True}


@router.get("/vehicles")
async def list_vehicles(
    search: Optional[str] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status"),
    db: AsyncSession = Depends(get_db_async),
) -> Dict[str, Any]:
    await _ensure_schema(db)
    query = """
        SELECT
            v.*,
            u.full_name AS driver_name,
            p.driver_code
        FROM fleet_vehicles v
        LEFT JOIN users u ON u.id = v.current_driver_id
        LEFT JOIN fleet_driver_profiles p ON p.user_id = u.id
        WHERE 1 = 1
    """
    params: Dict[str, Any] = {}
    if search:
        query += """
            AND (
                v.plate_number ILIKE :search
                OR v.vehicle_code ILIKE :search
                OR COALESCE(u.full_name, '') ILIKE :search
            )
        """
        params["search"] = f"%{search.strip()}%"
    if status_filter:
        query += " AND v.status = :status"
        params["status"] = status_filter
    query += " ORDER BY v.created_at DESC"
    result = await db.execute(text(query), params)
    return {"ok": True, "vehicles": _mapping_rows(result)}


@router.post("/vehicles", status_code=status.HTTP_201_CREATED)
async def create_vehicle(payload: VehicleCreate, db: AsyncSession = Depends(get_db_async)) -> Dict[str, Any]:
    await _ensure_schema(db)
    created = await db.execute(
        text(
            """
            INSERT INTO fleet_vehicles (
                vehicle_code, plate_number, type, capacity_kg, year, status,
                last_maintenance, next_maintenance, current_km, fuel_type,
                insurance_expiry, notes, created_at, updated_at
            )
            VALUES (
                'VEH' || TO_CHAR(NOW(), 'YYMMDDHH24MISSMS'),
                :plate_number,
                :type,
                :capacity_kg,
                :year,
                :status,
                :last_maintenance,
                :next_maintenance,
                :current_km,
                :fuel_type,
                :insurance_expiry,
                :notes,
                NOW(),
                NOW()
            )
            RETURNING id, vehicle_code
            """
        ),
        {
            "plate_number": payload.plate_number.strip().upper(),
            "type": payload.type,
            "capacity_kg": payload.capacity_kg,
            "year": payload.year,
            "status": payload.status or "available",
            "last_maintenance": _parse_date(payload.last_maintenance),
            "next_maintenance": _parse_date(payload.next_maintenance),
            "current_km": payload.current_km or 0,
            "fuel_type": payload.fuel_type,
            "insurance_expiry": _parse_date(payload.insurance_expiry),
            "notes": payload.notes,
        },
    )
    row = created.mappings().one()
    await db.commit()
    return {"ok": True, "vehicle": dict(row)}


@router.patch("/vehicles/{vehicle_id}")
async def update_vehicle(
    vehicle_id: int,
    payload: VehicleUpdate,
    db: AsyncSession = Depends(get_db_async),
) -> Dict[str, Any]:
    await _ensure_schema(db)
    fields: List[str] = []
    params: Dict[str, Any] = {"vehicle_id": vehicle_id}

    for field in ["type", "capacity_kg", "year", "status", "current_km", "fuel_type", "notes"]:
        value = getattr(payload, field)
        if value is not None:
            fields.append(f"{field} = :{field}")
            params[field] = value

    if payload.plate_number is not None:
        fields.append("plate_number = :plate_number")
        params["plate_number"] = payload.plate_number.strip().upper()
    if payload.last_maintenance is not None:
        fields.append("last_maintenance = :last_maintenance")
        params["last_maintenance"] = _parse_date(payload.last_maintenance)
    if payload.next_maintenance is not None:
        fields.append("next_maintenance = :next_maintenance")
        params["next_maintenance"] = _parse_date(payload.next_maintenance)
    if payload.insurance_expiry is not None:
        fields.append("insurance_expiry = :insurance_expiry")
        params["insurance_expiry"] = _parse_date(payload.insurance_expiry)

    if not fields:
        raise HTTPException(status_code=400, detail="No vehicle fields provided")

    fields.append("updated_at = NOW()")
    await db.execute(
        text(f"UPDATE fleet_vehicles SET {', '.join(fields)} WHERE id = :vehicle_id"),
        params,
    )
    await db.commit()
    return {"ok": True}


@router.delete("/vehicles/{vehicle_id}")
async def delete_vehicle(vehicle_id: int, db: AsyncSession = Depends(get_db_async)) -> Dict[str, Any]:
    await _ensure_schema(db)
    await db.execute(
        text(
            """
            UPDATE fleet_driver_vehicle_assignments
            SET is_active = FALSE, unassigned_date = CURRENT_DATE
            WHERE vehicle_id = :vehicle_id AND is_active = TRUE
            """
        ),
        {"vehicle_id": vehicle_id},
    )
    await db.execute(
        text(
            """
            UPDATE fleet_vehicles
            SET current_driver_id = NULL, status = 'inactive', updated_at = NOW()
            WHERE id = :vehicle_id
            """
        ),
        {"vehicle_id": vehicle_id},
    )
    await db.commit()
    return {"ok": True}


@router.get("/assignments")
async def list_assignments(db: AsyncSession = Depends(get_db_async)) -> Dict[str, Any]:
    await _ensure_schema(db)
    result = await db.execute(
        text(
            """
            SELECT
                a.id,
                a.driver_id,
                a.vehicle_id,
                a.assigned_date,
                a.notes,
                d.full_name AS driver_name,
                p.driver_code,
                v.plate_number,
                v.vehicle_code,
                v.type AS vehicle_type
            FROM fleet_driver_vehicle_assignments a
            JOIN users d ON d.id = a.driver_id
            LEFT JOIN fleet_driver_profiles p ON p.user_id = d.id
            JOIN fleet_vehicles v ON v.id = a.vehicle_id
            WHERE a.is_active = TRUE
            ORDER BY a.assigned_date DESC, a.id DESC
            """
        )
    )
    return {"ok": True, "assignments": _mapping_rows(result)}


@router.post("/assignments")
async def create_assignment(payload: AssignmentCreate, db: AsyncSession = Depends(get_db_async)) -> Dict[str, Any]:
    await _ensure_schema(db)
    await _ensure_driver_profile(db, payload.driver_id)

    driver = await db.execute(
        text(
            """
            SELECT id
            FROM users
            WHERE id = :driver_id
              AND LOWER(COALESCE(role, '')) = 'driver'
              AND COALESCE(is_deleted, FALSE) = FALSE
              AND COALESCE(is_active, TRUE) = TRUE
            """
        ),
        {"driver_id": payload.driver_id},
    )
    if not driver.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Driver not found")

    vehicle = await db.execute(
        text("SELECT id FROM fleet_vehicles WHERE id = :vehicle_id AND status <> 'inactive'"),
        {"vehicle_id": payload.vehicle_id},
    )
    if not vehicle.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Vehicle not found")

    previous_driver_vehicle = await db.execute(
        text(
            """
            SELECT vehicle_id
            FROM fleet_driver_vehicle_assignments
            WHERE driver_id = :driver_id AND is_active = TRUE
            """
        ),
        {"driver_id": payload.driver_id},
    )
    current_driver_assignment = previous_driver_vehicle.scalar_one_or_none()

    previous_vehicle_driver = await db.execute(
        text(
            """
            SELECT driver_id
            FROM fleet_driver_vehicle_assignments
            WHERE vehicle_id = :vehicle_id AND is_active = TRUE
            """
        ),
        {"vehicle_id": payload.vehicle_id},
    )
    current_vehicle_assignment = previous_vehicle_driver.scalar_one_or_none()

    await db.execute(
        text(
            """
            UPDATE fleet_driver_vehicle_assignments
            SET is_active = FALSE, unassigned_date = CURRENT_DATE
            WHERE (driver_id = :driver_id OR vehicle_id = :vehicle_id) AND is_active = TRUE
            """
        ),
        {"driver_id": payload.driver_id, "vehicle_id": payload.vehicle_id},
    )

    if current_driver_assignment:
        await db.execute(
            text(
                """
                UPDATE fleet_vehicles
                SET current_driver_id = NULL,
                    status = CASE WHEN status = 'occupied' THEN 'available' ELSE status END,
                    updated_at = NOW()
                WHERE id = :vehicle_id
                """
            ),
            {"vehicle_id": current_driver_assignment},
        )

    if current_vehicle_assignment:
        await db.execute(
            text(
                """
                UPDATE fleet_driver_profiles
                SET status = 'available', updated_at = NOW()
                WHERE user_id = :driver_id
                """
            ),
            {"driver_id": current_vehicle_assignment},
        )

    await db.execute(
        text(
            """
            INSERT INTO fleet_driver_vehicle_assignments (
                driver_id, vehicle_id, assigned_date, is_active, notes, created_at
            )
            VALUES (:driver_id, :vehicle_id, CURRENT_DATE, TRUE, :notes, NOW())
            """
        ),
        {
            "driver_id": payload.driver_id,
            "vehicle_id": payload.vehicle_id,
            "notes": payload.notes,
        },
    )
    await db.execute(
        text(
            """
            UPDATE fleet_driver_profiles
            SET status = 'busy', updated_at = NOW()
            WHERE user_id = :driver_id
            """
        ),
        {"driver_id": payload.driver_id},
    )
    await db.execute(
        text(
            """
            UPDATE fleet_vehicles
            SET current_driver_id = :driver_id, status = 'occupied', updated_at = NOW()
            WHERE id = :vehicle_id
            """
        ),
        {"driver_id": payload.driver_id, "vehicle_id": payload.vehicle_id},
    )
    await db.commit()
    return {"ok": True}


@router.post("/assignments/{driver_id}/unassign")
async def unassign_driver(driver_id: int, db: AsyncSession = Depends(get_db_async)) -> Dict[str, Any]:
    await _ensure_schema(db)
    vehicle_result = await db.execute(
        text(
            """
            SELECT vehicle_id
            FROM fleet_driver_vehicle_assignments
            WHERE driver_id = :driver_id AND is_active = TRUE
            """
        ),
        {"driver_id": driver_id},
    )
    vehicle_id = vehicle_result.scalar_one_or_none()

    await db.execute(
        text(
            """
            UPDATE fleet_driver_vehicle_assignments
            SET is_active = FALSE, unassigned_date = CURRENT_DATE
            WHERE driver_id = :driver_id AND is_active = TRUE
            """
        ),
        {"driver_id": driver_id},
    )
    await db.execute(
        text(
            """
            UPDATE fleet_driver_profiles
            SET status = 'available', updated_at = NOW()
            WHERE user_id = :driver_id
            """
        ),
        {"driver_id": driver_id},
    )
    if vehicle_id:
        await db.execute(
            text(
                """
                UPDATE fleet_vehicles
                SET current_driver_id = NULL,
                    status = CASE WHEN status = 'occupied' THEN 'available' ELSE status END,
                    updated_at = NOW()
                WHERE id = :vehicle_id
                """
            ),
            {"vehicle_id": vehicle_id},
        )
    await db.commit()
    return {"ok": True}


@router.get("/incidents")
async def list_incidents(
    status_filter: Optional[str] = Query(None, alias="status"),
    severity_filter: Optional[str] = Query(None, alias="severity"),
    db: AsyncSession = Depends(get_db_async),
) -> Dict[str, Any]:
    await _ensure_schema(db)
    query = """
        SELECT
            i.*,
            d.full_name AS driver_name,
            p.driver_code,
            v.plate_number,
            v.vehicle_code,
            v.type AS vehicle_type
        FROM fleet_incidents i
        LEFT JOIN users d ON d.id = i.driver_id
        LEFT JOIN fleet_driver_profiles p ON p.user_id = d.id
        LEFT JOIN fleet_vehicles v ON v.id = i.vehicle_id
        WHERE 1 = 1
    """
    params: Dict[str, Any] = {}
    if status_filter:
        query += " AND i.status = :status"
        params["status"] = status_filter
    if severity_filter:
        query += " AND i.severity = :severity"
        params["severity"] = severity_filter
    query += " ORDER BY i.incident_date DESC, i.id DESC"
    result = await db.execute(text(query), params)
    return {"ok": True, "incidents": _mapping_rows(result)}


@router.get("/incidents/{incident_id}")
async def get_incident(incident_id: int, db: AsyncSession = Depends(get_db_async)) -> Dict[str, Any]:
    await _ensure_schema(db)
    result = await db.execute(
        text(
            """
            SELECT
                i.*,
                d.full_name AS driver_name,
                p.driver_code,
                v.plate_number,
                v.vehicle_code,
                v.type AS vehicle_type
            FROM fleet_incidents i
            LEFT JOIN users d ON d.id = i.driver_id
            LEFT JOIN fleet_driver_profiles p ON p.user_id = d.id
            LEFT JOIN fleet_vehicles v ON v.id = i.vehicle_id
            WHERE i.id = :incident_id
            """
        ),
        {"incident_id": incident_id},
    )
    incident = _mapping_one(result)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return {"ok": True, "incident": incident}


@router.post("/incidents", status_code=status.HTTP_201_CREATED)
async def create_incident(payload: IncidentCreate, db: AsyncSession = Depends(get_db_async)) -> Dict[str, Any]:
    await _ensure_schema(db)
    created = await db.execute(
        text(
            """
            INSERT INTO fleet_incidents (
                incident_number, incident_date, incident_type, driver_id, vehicle_id,
                location, description, severity, actions_taken, status,
                police_report, insurance_claim, images, created_by, created_at
            )
            VALUES (
                'INC-' || TO_CHAR(NOW(), 'YYYY') || '-' || TO_CHAR(NOW(), 'MMDDHH24MISSMS'),
                :incident_date,
                :incident_type,
                :driver_id,
                :vehicle_id,
                :location,
                :description,
                :severity,
                :actions_taken,
                :status,
                :police_report,
                :insurance_claim,
                CAST(:images AS JSONB),
                :created_by,
                NOW()
            )
            RETURNING id, incident_number
            """
        ),
        {
            "incident_date": _parse_datetime(payload.incident_date) or datetime.utcnow(),
            "incident_type": payload.incident_type,
            "driver_id": payload.driver_id,
            "vehicle_id": payload.vehicle_id,
            "location": payload.location,
            "description": payload.description,
            "severity": payload.severity or "medium",
            "actions_taken": payload.actions_taken,
            "status": payload.status or "open",
            "police_report": payload.police_report,
            "insurance_claim": payload.insurance_claim,
            "images": json.dumps(payload.images or []),
            "created_by": payload.created_by or "admin",
        },
    )
    row = created.mappings().one()
    await db.commit()
    return {"ok": True, "incident": dict(row)}


@router.patch("/incidents/{incident_id}")
async def update_incident(
    incident_id: int,
    payload: IncidentUpdate,
    db: AsyncSession = Depends(get_db_async),
) -> Dict[str, Any]:
    await _ensure_schema(db)
    fields: List[str] = []
    params: Dict[str, Any] = {"incident_id": incident_id}

    simple_fields = {
        "incident_type": payload.incident_type,
        "driver_id": payload.driver_id,
        "vehicle_id": payload.vehicle_id,
        "location": payload.location,
        "description": payload.description,
        "severity": payload.severity,
        "actions_taken": payload.actions_taken,
        "status": payload.status,
        "police_report": payload.police_report,
        "insurance_claim": payload.insurance_claim,
    }
    for field, value in simple_fields.items():
        if value is not None:
            fields.append(f"{field} = :{field}")
            params[field] = value

    if payload.incident_date is not None:
        fields.append("incident_date = :incident_date")
        params["incident_date"] = _parse_datetime(payload.incident_date)

    if payload.images is not None:
        fields.append("images = CAST(:images AS JSONB)")
        params["images"] = json.dumps(payload.images)

    if payload.status == "closed":
        fields.append("resolved_at = NOW()")
    elif payload.status in {"open", "investigating"}:
        fields.append("resolved_at = NULL")

    if not fields:
        raise HTTPException(status_code=400, detail="No incident fields provided")

    await db.execute(
        text(f"UPDATE fleet_incidents SET {', '.join(fields)} WHERE id = :incident_id"),
        params,
    )
    await db.commit()
    return {"ok": True}


@router.delete("/incidents/{incident_id}")
async def delete_incident(incident_id: int, db: AsyncSession = Depends(get_db_async)) -> Dict[str, Any]:
    await _ensure_schema(db)
    await db.execute(text("DELETE FROM fleet_incidents WHERE id = :incident_id"), {"incident_id": incident_id})
    await db.commit()
    return {"ok": True}
