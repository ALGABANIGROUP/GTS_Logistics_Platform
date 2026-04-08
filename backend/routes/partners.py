# backend/routes/partners.py
from fastapi import APIRouter, HTTPException, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging
import json
from pydantic import BaseModel, Field, EmailStr

from backend.database.session import get_db
from backend.security.auth import get_current_user
from backend.models.partner import LogisticsPartner  # We will create this model

router = APIRouter(prefix="/api/v1/partners", tags=["Partners"])
logger = logging.getLogger(__name__)


# ==================== Pydantic Models ====================
class PartnerCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    type: str = Field(..., description="carrier, shipper, broker, supplier, customer")
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    contact_person: Optional[str] = None
    mc_number: Optional[str] = None  # Motor Carrier number
    dot_number: Optional[str] = None  # DOT number
    tax_id: Optional[str] = None
    website: Optional[str] = None
    notes: Optional[str] = None
    status: str = Field(default="active", description="active, inactive, pending")
    rating: Optional[int] = Field(default=None, ge=1, le=5)
    tags: Optional[List[str]] = []


class PartnerUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    type: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    contact_person: Optional[str] = None
    mc_number: Optional[str] = None
    dot_number: Optional[str] = None
    tax_id: Optional[str] = None
    website: Optional[str] = None
    notes: Optional[str] = None
    status: Optional[str] = None
    rating: Optional[int] = Field(None, ge=1, le=5)
    tags: Optional[List[str]] = None


class PartnerResponse(BaseModel):
    id: int
    name: str
    type: str
    email: Optional[str]
    phone: Optional[str]
    address: Optional[str]
    contact_person: Optional[str]
    mc_number: Optional[str]
    dot_number: Optional[str]
    tax_id: Optional[str]
    website: Optional[str]
    notes: Optional[str]
    status: str
    rating: Optional[int]
    tags: List[str]
    created_at: str
    updated_at: Optional[str]
    user_count: int = 0
    shipment_count: int = 0
    total_spent: float = 0.0


# ==================== Mock Database (will be replaced with real database later) ====================
PARTNERS_DB = []
PARTNER_ID_COUNTER = 1

# Test data
MOCK_PARTNERS = [
    {
        "id": 1,
        "name": "Fast Freight Carriers",
        "type": "carrier",
        "email": "dispatch@fastfreight.com",
        "phone": "+1-800-555-0100",
        "address": "123 Transport Ave, Chicago, IL 60601",
        "contact_person": "John Smith",
        "mc_number": "MC-123456",
        "dot_number": "DOT-789012",
        "tax_id": "TX-987654",
        "website": "https://fastfreight.com",
        "notes": "Reliable carrier with 50+ trucks",
        "status": "active",
        "rating": 5,
        "tags": ["long_haul", "refrigerated"],
        "created_at": "2024-01-15T10:00:00",
        "updated_at": None,
        "user_count": 3,
        "shipment_count": 45,
        "total_spent": 125000.00
    },
    {
        "id": 2,
        "name": "Global Logistics Solutions",
        "type": "broker",
        "email": "info@globallogistics.com",
        "phone": "+1-800-555-0200",
        "address": "456 Broker Lane, Dallas, TX 75201",
        "contact_person": "Sarah Johnson",
        "mc_number": "MC-234567",
        "dot_number": "DOT-890123",
        "tax_id": "TX-876543",
        "website": "https://globallogistics.com",
        "notes": "Full-service logistics broker",
        "status": "active",
        "rating": 4,
        "tags": ["freight_forwarding", "customs"],
        "created_at": "2024-01-20T11:00:00",
        "updated_at": None,
        "user_count": 5,
        "shipment_count": 78,
        "total_spent": 234000.00
    },
    {
        "id": 3,
        "name": "Maple Load Canada",
        "type": "carrier",
        "email": "dispatch@mapleload.ca",
        "phone": "+1-800-555-0300",
        "address": "789 Maple Street, Toronto, ON M5V 2T6",
        "contact_person": "Mike Wilson",
        "mc_number": "MC-345678",
        "dot_number": "DOT-901234",
        "tax_id": "TX-765432",
        "website": "https://mapleload.ca",
        "notes": "Canadian cross-border specialist",
        "status": "active",
        "rating": 5,
        "tags": ["cross_border", "canada"],
        "created_at": "2024-02-01T09:00:00",
        "updated_at": None,
        "user_count": 2,
        "shipment_count": 32,
        "total_spent": 89000.00
    },
    {
        "id": 4,
        "name": "ABC Manufacturing",
        "type": "shipper",
        "email": "shipping@abcmfg.com",
        "phone": "+1-800-555-0400",
        "address": "101 Industrial Park, Detroit, MI 48201",
        "contact_person": "Robert Brown",
        "mc_number": None,
        "dot_number": None,
        "tax_id": "TX-654321",
        "website": "https://abcmfg.com",
        "notes": "Regular shipper of auto parts",
        "status": "active",
        "rating": 4,
        "tags": ["automotive", "just_in_time"],
        "created_at": "2024-02-15T14:00:00",
        "updated_at": None,
        "user_count": 1,
        "shipment_count": 28,
        "total_spent": 156000.00
    },
    {
        "id": 5,
        "name": "Premium Suppliers Inc",
        "type": "supplier",
        "email": "orders@premiumsuppliers.com",
        "phone": "+1-800-555-0500",
        "address": "202 Supply Chain Rd, Atlanta, GA 30301",
        "contact_person": "Lisa Davis",
        "mc_number": None,
        "dot_number": None,
        "tax_id": "TX-543210",
        "website": "https://premiumsuppliers.com",
        "notes": "Preferred supplier for packaging materials",
        "status": "inactive",
        "rating": 3,
        "tags": ["packaging", "supplies"],
        "created_at": "2024-03-01T08:00:00",
        "updated_at": "2024-03-20T16:00:00",
        "user_count": 0,
        "shipment_count": 12,
        "total_spent": 45000.00
    }
]

for partner in MOCK_PARTNERS:
    PARTNERS_DB.append(partner.copy())
    PARTNER_ID_COUNTER = max(PARTNER_ID_COUNTER, partner["id"] + 1)


# ==================== Helper Functions ====================
def get_partner_type_label(partner_type: str) -> str:
    types = {
        "carrier": "🚚 Carrier",
        "shipper": "📦 Shipper",
        "broker": "🤝 Broker",
        "supplier": "🏭 Supplier",
        "customer": "👥 Customer"
    }
    return types.get(partner_type, partner_type)


def get_partner_type_color(partner_type: str) -> str:
    colors = {
        "carrier": "#2196f3",
        "shipper": "#4caf50",
        "broker": "#ff9800",
        "supplier": "#9c27b0",
        "customer": "#00bcd4"
    }
    return colors.get(partner_type, "#757575")


def _actor_user_id(current_user: Dict[str, Any]) -> Optional[int]:
    try:
        return int(current_user.get("id") or current_user.get("sub") or 0) or None
    except Exception:
        return None


async def _resolve_actor_user_id(db: AsyncSession, current_user: Dict[str, Any]) -> Optional[int]:
    actor_id = _actor_user_id(current_user)
    if actor_id is not None:
        exists = await db.execute(text("SELECT id FROM users WHERE id = :id LIMIT 1"), {"id": actor_id})
        resolved = exists.scalar_one_or_none()
        if resolved is not None:
            return int(resolved)

    email = str(current_user.get("email") or "").strip().lower()
    if email:
        exists = await db.execute(
            text("SELECT id FROM users WHERE lower(email) = lower(:email) LIMIT 1"),
            {"email": email},
        )
        resolved = exists.scalar_one_or_none()
        if resolved is not None:
            return int(resolved)

    return None


async def _log_partner_audit(
    db: AsyncSession,
    *,
    request: Request,
    current_user: Dict[str, Any],
    action: str,
    partner_id: int,
    diff_json: Optional[Dict[str, Any]],
    severity: str = "info",
) -> None:
    try:
        actor_user_id = await _resolve_actor_user_id(db, current_user)
        await db.execute(
            text(
                """
                INSERT INTO audit_logs (
                    actor_user_id, action, target_type, target_id, diff_json, ip, severity
                ) VALUES (
                    :actor_user_id, :action, :target_type, :target_id, CAST(:diff_json AS jsonb), :ip, :severity
                )
                """
            ),
            {
                "actor_user_id": actor_user_id,
                "action": action,
                "target_type": "partner",
                "target_id": str(partner_id),
                "diff_json": json.dumps(diff_json or {}, default=str),
                "ip": request.client.host if request.client else None,
                "severity": severity,
            },
        )
        await db.commit()
    except Exception as exc:
        logger.warning("Partner audit logging failed for action=%s partner_id=%s: %s", action, partner_id, exc)


# ==================== API Endpoints ====================

@router.get("/", response_model=Dict[str, Any])
async def get_partners(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    partner_type: Optional[str] = None,
    status: Optional[str] = None,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get all partners with pagination and filtering
    """
    user_role = current_user.get("role", "").lower()

    # Copy data
    partners = PARTNERS_DB.copy()

    # Apply filters
    if search:
        search_lower = search.lower()
        partners = [
            p for p in partners
            if search_lower in p["name"].lower()
            or (p.get("email") and search_lower in p["email"].lower())
            or (p.get("mc_number") and search_lower in p["mc_number"].lower())
            or (p.get("phone") and search_lower in p["phone"].lower())
        ]

    if partner_type:
        partners = [p for p in partners if p["type"] == partner_type]

    if status:
        partners = [p for p in partners if p["status"] == status]

    # Sort by name
    partners.sort(key=lambda x: x["name"])

    # Pagination
    total = len(partners)
    start = (page - 1) * limit
    end = start + limit
    partners = partners[start:end]

    return {
        "partners": partners,
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": (total + limit - 1) // limit if total else 0
    }


@router.get("/{partner_id}", response_model=Dict[str, Any])
async def get_partner(
    partner_id: int,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get single partner by ID
    """
    partner = next((p for p in PARTNERS_DB if p["id"] == partner_id), None)

    if not partner:
        raise HTTPException(status_code=404, detail="Partner not found")

    return partner


@router.post("/", response_model=Dict[str, Any])
async def create_partner(
    partner: PartnerCreate,
    request: Request,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new partner
    """
    global PARTNER_ID_COUNTER

    user_role = current_user.get("role", "").lower()
    if user_role not in ["super_admin", "admin"]:
        raise HTTPException(status_code=403, detail="Admin access required")

    # Check if partner with same name exists
    existing = next((p for p in PARTNERS_DB if p["name"].lower() == partner.name.lower()), None)
    if existing:
        raise HTTPException(status_code=400, detail="Partner with this name already exists")

    new_partner = {
        "id": PARTNER_ID_COUNTER,
        "name": partner.name,
        "type": partner.type,
        "email": partner.email,
        "phone": partner.phone,
        "address": partner.address,
        "contact_person": partner.contact_person,
        "mc_number": partner.mc_number,
        "dot_number": partner.dot_number,
        "tax_id": partner.tax_id,
        "website": partner.website,
        "notes": partner.notes,
        "status": partner.status,
        "rating": partner.rating,
        "tags": partner.tags or [],
        "created_at": datetime.now().isoformat(),
        "updated_at": None,
        "user_count": 0,
        "shipment_count": 0,
        "total_spent": 0.0
    }

    PARTNERS_DB.append(new_partner)
    PARTNER_ID_COUNTER += 1

    logger.info(f"Partner created: {partner.name} by {current_user.get('email')}")
    await _log_partner_audit(
        db,
        request=request,
        current_user=current_user,
        action="partner_create",
        partner_id=int(new_partner["id"]),
        diff_json={
            "name": new_partner["name"],
            "type": new_partner["type"],
            "status": new_partner["status"],
        },
    )

    return new_partner


@router.patch("/{partner_id}", response_model=Dict[str, Any])
async def update_partner(
    partner_id: int,
    partner_update: PartnerUpdate,
    request: Request,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update a partner
    """
    user_role = current_user.get("role", "").lower()
    if user_role not in ["super_admin", "admin"]:
        raise HTTPException(status_code=403, detail="Admin access required")

    partner = next((p for p in PARTNERS_DB if p["id"] == partner_id), None)

    if not partner:
        raise HTTPException(status_code=404, detail="Partner not found")

    # Update fields
    original_partner = dict(partner)
    update_data = partner_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        if value is not None:
            partner[key] = value

    partner["updated_at"] = datetime.now().isoformat()

    logger.info(f"Partner updated: {partner['name']} by {current_user.get('email')}")
    await _log_partner_audit(
        db,
        request=request,
        current_user=current_user,
        action="partner_update",
        partner_id=partner_id,
        diff_json={
            "before": {
                "name": original_partner.get("name"),
                "type": original_partner.get("type"),
                "status": original_partner.get("status"),
            },
            "after": {
                "name": partner.get("name"),
                "type": partner.get("type"),
                "status": partner.get("status"),
            },
            "fields": sorted(update_data.keys()),
        },
    )

    return partner


@router.delete("/{partner_id}", response_model=Dict[str, Any])
async def delete_partner(
    partner_id: int,
    request: Request,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete a partner (soft delete - set status to inactive)
    """
    user_role = current_user.get("role", "").lower()
    if user_role not in ["super_admin", "admin"]:
        raise HTTPException(status_code=403, detail="Admin access required")

    partner = next((p for p in PARTNERS_DB if p["id"] == partner_id), None)

    if not partner:
        raise HTTPException(status_code=404, detail="Partner not found")

    # Soft delete - set status to inactive
    partner["status"] = "inactive"
    partner["updated_at"] = datetime.now().isoformat()

    logger.info(f"Partner deactivated: {partner['name']} by {current_user.get('email')}")
    await _log_partner_audit(
        db,
        request=request,
        current_user=current_user,
        action="partner_deactivate",
        partner_id=partner_id,
        diff_json={"name": partner.get("name"), "status": "inactive"},
        severity="warning",
    )

    return {"message": "Partner deactivated successfully", "partner_id": partner_id}


@router.delete("/{partner_id}/permanent")
async def permanent_delete_partner(
    partner_id: int,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Permanently delete a partner (admin only)
    """
    user_role = current_user.get("role", "").lower()
    if user_role != "super_admin":
        raise HTTPException(status_code=403, detail="Super admin access required")

    global PARTNERS_DB
    partner = next((p for p in PARTNERS_DB if p["id"] == partner_id), None)

    if not partner:
        raise HTTPException(status_code=404, detail="Partner not found")

    PARTNERS_DB = [p for p in PARTNERS_DB if p["id"] != partner_id]

    logger.info(f"Partner permanently deleted: {partner['name']} by {current_user.get('email')}")

    return {"message": "Partner permanently deleted", "partner_id": partner_id}


@router.get("/stats/summary")
async def get_partners_stats(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get partners statistics
    """
    total = len(PARTNERS_DB)
    active = len([p for p in PARTNERS_DB if p["status"] == "active"])
    inactive = total - active

    by_type = {}
    for partner in PARTNERS_DB:
        p_type = partner["type"]
        by_type[p_type] = by_type.get(p_type, 0) + 1

    return {
        "total": total,
        "active": active,
        "inactive": inactive,
        "by_type": by_type
    }


@router.get("/types/list")
async def get_partner_types():
    """
    Get list of available partner types
    """
    return {
        "types": [
            {"value": "carrier", "label": "🚚 Carrier"},
            {"value": "shipper", "label": "📦 Shipper"},
            {"value": "broker", "label": "🤝 Broker"},
            {"value": "supplier", "label": "🏭 Supplier"},
            {"value": "customer", "label": "👥 Customer"}
        ]
    }
