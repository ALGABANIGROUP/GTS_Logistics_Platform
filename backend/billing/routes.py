from __future__ import annotations

from datetime import datetime
import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, Header, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.billing.models import Subscription, SubscriptionAddon
from backend.billing.service import (
    get_plan_by_code,
    get_plans_for_country,
    get_pricing_catalog,
    save_pricing_catalog,
)
from backend.database.config import get_db_async
from backend.security.auth import get_current_user, require_roles
from backend.auth.rbac_middleware import require_permission
from backend.security.entitlements import resolve_entitlements, resolve_region, resolve_user_from_claims
from backend.services.plan_invoice_service import PlanInvoiceService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/billing", tags=["Billing"])
admin_router = APIRouter(
    prefix="/api/v1/admin/billing",
    tags=["Billing Admin"],
    dependencies=[Depends(require_roles(["admin", "super_admin", "owner"]))],
)


class SubscriptionSelectPayload(BaseModel):
    plan_code: str = Field(..., min_length=1)
    country: Optional[str] = None


class SubscriptionAssignPayload(BaseModel):
    plan_code: str = Field(..., min_length=1)
    country: Optional[str] = None
    user_id: Optional[int] = None
    email: Optional[str] = None
    status: Optional[str] = "active"
    addons: Optional[List[str]] = None


class PricingCatalogUpdatePayload(BaseModel):
    country: Optional[str] = None
    plans: List[Dict[str, Any]] = Field(default_factory=list)
    addons: List[Dict[str, Any]] = Field(default_factory=list)
    vehicle_pricing: List[Dict[str, Any]] = Field(default_factory=list)
    user_pricing: List[Dict[str, Any]] = Field(default_factory=list)
    bot_pricing: List[Dict[str, Any]] = Field(default_factory=list)
    bot_bundle: Optional[Dict[str, Any]] = None
    extra_services: Dict[str, List[Dict[str, Any]]] = Field(default_factory=dict)
    transaction_fees: Dict[str, Any] = Field(default_factory=dict)


async def _get_user_or_404(db: AsyncSession, claims: Dict[str, Any]):
    user = await resolve_user_from_claims(db, claims)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


async def _get_latest_subscription(db: AsyncSession, user_id: int) -> Optional[Subscription]:
    stmt = select(Subscription).where(Subscription.user_id == user_id).order_by(Subscription.created_at.desc())
    result = await db.execute(stmt)
    return result.scalars().first()


def _resolve_plan_code(plan: Any, fallback: str) -> str:
    for key in ("code", "key", "plan_code", "id"):
        value = getattr(plan, key, None)
        if value:
            return str(value).upper()
    return str(fallback or "UNKNOWN").upper()


def _resolve_plan_amount(plan: Any) -> float:
    for key in ("price_amount", "price_monthly", "price"):
        value = getattr(plan, key, None)
        if value is not None:
            try:
                return float(value)
            except Exception:
                continue
    return 0.0


async def _create_subscription_cycle_invoice(
    db: AsyncSession,
    *,
    user_id: int,
    plan: Any,
    fallback_plan_code: str,
) -> Dict[str, Any]:
    plan_code = _resolve_plan_code(plan, fallback_plan_code)
    amount = _resolve_plan_amount(plan)
    plan_invoice_service = PlanInvoiceService(db)
    invoice = await plan_invoice_service.ensure_subscription_cycle_invoice(
        user_id=int(user_id),
        plan_code=plan_code,
        amount_usd=amount,
        status="pending",
    )
    return {
        "invoice_id": invoice.id,
        "invoice_number": invoice.number,
        "plan_code": invoice.plan_code or plan_code,
        "amount_usd": float(invoice.amount_usd),
        "status": invoice.status,
        "date": str(invoice.date),
    }


@router.get("/plans")
async def list_plans(
    db: AsyncSession = Depends(get_db_async),
    country: Optional[str] = None,
) -> Dict[str, Any]:
    catalog = get_pricing_catalog(country)
    return catalog


@admin_router.get("/catalog")
async def get_admin_catalog(country: Optional[str] = None) -> Dict[str, Any]:
    return get_pricing_catalog(country)


@admin_router.put("/catalog")
async def update_admin_catalog(payload: PricingCatalogUpdatePayload) -> Dict[str, Any]:
    saved = save_pricing_catalog(
        payload.country,
        {
            "plans": payload.plans,
            "addons": payload.addons,
            "vehicle_pricing": payload.vehicle_pricing,
            "user_pricing": payload.user_pricing,
            "bot_pricing": payload.bot_pricing,
            "bot_bundle": payload.bot_bundle,
            "extra_services": payload.extra_services,
            "transaction_fees": payload.transaction_fees,
        },
    )
    return {"success": True, "catalog": saved}


@router.get("/subscription/me")
async def get_my_subscription(
    db: AsyncSession = Depends(get_db_async),
    claims: Dict[str, Any] = Depends(get_current_user),
    x_gts_country: Optional[str] = Header(None, alias="X-GTS-COUNTRY"),
    _=Depends(require_permission("billing.read")),
) -> Dict[str, Any]:
    user = await _get_user_or_404(db, claims)
    region = resolve_region(header_country=x_gts_country, user_country=user.country, override=None)
    resolved = await resolve_entitlements(db, user, region=region)

    subscription = await _get_latest_subscription(db, user.id)
    addons = []
    if subscription and subscription.addons:
        addons = [
            {"code": addon.addon_code, "enabled": addon.enabled}
            for addon in subscription.addons
        ]

    return {
        "plan_code": resolved.get("plan_code"),
        "subscription_status": resolved.get("subscription_status"),
        "entitlements": resolved.get("entitlements"),
        "enabled_modules": resolved.get("enabled_modules"),
        "addons": addons,
    }


@router.post("/subscription/select", status_code=status.HTTP_201_CREATED)
async def select_subscription(
    payload: SubscriptionSelectPayload,
    db: AsyncSession = Depends(get_db_async),
    claims: Dict[str, Any] = Depends(get_current_user),
    x_gts_country: Optional[str] = Header(None, alias="X-GTS-COUNTRY"),
    _=Depends(require_permission("billing.pay")),
) -> Dict[str, Any]:
    user = await _get_user_or_404(db, claims)
    region = resolve_region(header_country=x_gts_country, user_country=user.country, override=payload.country)

    plan = await get_plan_by_code(db, plan_code=payload.plan_code, country=region)
    if plan is None:
        raise HTTPException(status_code=404, detail="Plan not found")

    active = await db.scalar(
        select(Subscription).where(Subscription.user_id == user.id, Subscription.status == "active")
    )
    if active is not None:
        raise HTTPException(status_code=409, detail="Active subscription already exists")

    pending = await db.scalar(
        select(Subscription).where(Subscription.user_id == user.id, Subscription.status != "active")
    )
    if pending is None:
        pending = Subscription(
            user_id=user.id,
            plan_id=plan.id,
            status="pending",
            source="self_service",
            start_at=None,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db.add(pending)
    else:
        pending.plan_id = plan.id
        pending.status = "pending"
        pending.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(pending)

    return {
        "subscription_id": pending.id,
        "status": pending.status,
        "plan_code": plan.code,
    }


@admin_router.post("/subscriptions/assign")
async def assign_subscription(
    payload: SubscriptionAssignPayload,
    db: AsyncSession = Depends(get_db_async),
    _=Depends(require_permission("billing.assign")),
) -> Dict[str, Any]:
    if not payload.user_id and not payload.email:
        raise HTTPException(status_code=400, detail="user_id or email is required")

    claims: Dict[str, Any] = {}
    if payload.user_id:
        claims["user_id"] = payload.user_id
    if payload.email:
        claims["email"] = payload.email

    user = await _get_user_or_404(db, claims)
    plan = await get_plan_by_code(db, plan_code=payload.plan_code, country=payload.country)
    if plan is None:
        raise HTTPException(status_code=404, detail="Plan not found")

    subscription = await db.scalar(select(Subscription).where(Subscription.user_id == user.id))
    if subscription is None:
        subscription = Subscription(
            user_id=user.id,
            plan_id=plan.id,
            status=payload.status or "active",
            source="admin",
            start_at=datetime.utcnow(),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db.add(subscription)
    else:
        subscription.plan_id = plan.id
        subscription.status = payload.status or "active"
        subscription.updated_at = datetime.utcnow()

    await db.flush()

    addons_applied = []
    if payload.addons:
        for addon_code in payload.addons:
            addon = await db.scalar(
                select(SubscriptionAddon).where(
                    SubscriptionAddon.subscription_id == subscription.id,
                    SubscriptionAddon.addon_code == addon_code,
                )
            )
            if addon is None:
                addon = SubscriptionAddon(
                    subscription_id=subscription.id,
                    addon_code=addon_code,
                    enabled=True,
                )
                db.add(addon)
            else:
                addon.enabled = True
            addons_applied.append(addon_code)

    await db.commit()
    await db.refresh(subscription)

    cycle_invoice: Optional[Dict[str, Any]] = None
    if (subscription.status or "").lower() == "active":
        try:
            cycle_invoice = await _create_subscription_cycle_invoice(
                db,
                user_id=user.id,
                plan=plan,
                fallback_plan_code=payload.plan_code,
            )
        except Exception as exc:
            logger.exception(
                "Failed to create cycle invoice during subscription assignment",
                extra={
                    "user_id": user.id,
                    "subscription_id": subscription.id,
                    "plan_code": _resolve_plan_code(plan, payload.plan_code),
                },
            )
            cycle_invoice = None

    return {
        "subscription_id": subscription.id,
        "status": subscription.status,
        "plan_code": _resolve_plan_code(plan, payload.plan_code),
        "addons": addons_applied,
        "cycle_invoice": cycle_invoice,
    }


@admin_router.post("/subscriptions/process-cycle-invoices")
async def process_cycle_invoices(
    db: AsyncSession = Depends(get_db_async),
    _=Depends(require_permission("billing.assign")),
) -> Dict[str, Any]:
    stmt = select(Subscription).where(Subscription.status == "active")
    rows = (await db.execute(stmt)).scalars().all()

    created: List[Dict[str, Any]] = []
    skipped = 0
    for subscription in rows:
        if not subscription.user_id:
            skipped += 1
            continue

        plan = subscription.plan
        if plan is None:
            skipped += 1
            continue

        try:
            cycle_invoice = await _create_subscription_cycle_invoice(
                db,
                user_id=subscription.user_id,
                plan=plan,
                fallback_plan_code=str(subscription.plan_id),
            )
            created.append({
                "subscription_id": subscription.id,
                "user_id": subscription.user_id,
                **cycle_invoice,
            })
        except Exception as exc:
            logger.exception(
                "Failed to process cycle invoice",
                extra={
                    "subscription_id": subscription.id,
                    "user_id": subscription.user_id,
                    "plan_id": subscription.plan_id,
                },
            )
            skipped += 1

    return {
        "processed": len(rows),
        "created_or_existing": len(created),
        "skipped": skipped,
        "items": created,
    }


router.include_router(admin_router)

__all__ = ["router"]
