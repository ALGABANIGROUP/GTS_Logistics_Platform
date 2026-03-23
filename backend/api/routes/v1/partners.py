from __future__ import annotations

from typing import List, Optional, Sequence, cast, Tuple
from uuid import UUID
from datetime import datetime

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    Request,
    status,
)
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_db_async  # type: ignore[attr-defined]
from backend.models.partner import (
    Partner,
    PartnerClient,
    PartnerRevenue,
    PartnerPayout,
)
from backend.models.user import User
from backend.schemas.partner import (
    PartnerCreate,
    PartnerUpdate,
    PartnerStatusUpdate,
    PartnerRead,
    PartnerListResponse,
    PartnerDashboardSummary,
    PartnerClientListResponse,
    PartnerClientRead,
    PartnerRevenueListResponse,
    PartnerRevenueRow,
    PartnerRevenueSummaryResponse,
    PartnerPayoutListResponse,
    PartnerPayoutCreate,
    PartnerPayoutRead,
    PartnerAgreementCurrentResponse,
    PartnerAgreementSignRequest,
    PartnerAgreementSignResponse,
)
from backend.services.partner_revenue import get_partner_revenue_summary
from backend.services.partner_agreement import (
    get_current_agreement,
    sign_agreement,
)

# adjust this import name if your auth dependency is named differently
from backend.security.auth import get_current_user  # type: ignore[import]


admin_router = APIRouter(prefix="/api/v1/partners", tags=["partners-admin"])
partner_router = APIRouter(prefix="/api/v1/partner", tags=["partners"])


# ---------------------------------------------------------------------------
# Auth helpers (local wrappers to avoid undefined imports)
# ---------------------------------------------------------------------------


def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    # if you have an "is_active" field, you can check it here.
    # for now we just return the user object.
    return current_user


def get_current_admin_user(
    current_user: User = Depends(get_current_active_user),
) -> User:
    role = getattr(current_user, "role", None)
    if role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required.",
        )
    return current_user


async def _get_partner_or_404(db: AsyncSession, partner_id: UUID) -> Partner:
    partner = await db.scalar(select(Partner).where(Partner.id == partner_id))
    if not partner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Partner not found.",
        )
    return partner


async def get_current_partner_user(
    db: AsyncSession = Depends(get_db_async),
    current_user: User = Depends(get_current_active_user),
) -> tuple[User, Partner]:
    partner_id = getattr(current_user, "partner_id", None)
    if not partner_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not linked to a partner.",
        )

    partner = await db.scalar(select(Partner).where(Partner.id == partner_id))
    if not partner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Linked partner not found.",
        )

    return current_user, partner


# ---------------------------------------------------------------------------
# Admin endpoints
# ---------------------------------------------------------------------------


@admin_router.get("", response_model=PartnerListResponse)
async def list_partners(
    db: AsyncSession = Depends(get_db_async),
    current_admin: User = Depends(get_current_admin_user),
    page: Optional[int] = Query(None, ge=1),
    page_size: Optional[int] = Query(None, ge=1, le=100),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
) -> PartnerListResponse:
    if page is not None:
        limit = page_size or limit
        skip = (page - 1) * limit

    stmt = select(Partner)
    conditions = []

    if status:
        conditions.append(Partner.status == status)

    if search:
        pattern = f"%{search}%"
        conditions.append(
            (Partner.name.ilike(pattern))
            | (Partner.email.ilike(pattern))
            | (Partner.code.ilike(pattern))
        )

    if conditions:
        stmt = stmt.where(*conditions)

    total_stmt = stmt.with_only_columns(func.count(Partner.id)).order_by(None)
    total_result = await db.execute(total_stmt)
    total = int(total_result.scalar_one() or 0)

    stmt = stmt.order_by(Partner.joined_at.desc()).offset(skip).limit(limit)
    result = await db.execute(stmt)
    partners_seq: Sequence[Partner] = result.scalars().all()
    partners: List[Partner] = list(partners_seq)

    return PartnerListResponse(
        items=cast(List[PartnerRead], partners),
        total=total,
    )


@admin_router.post(
    "",
    response_model=PartnerRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_partner(
    payload: PartnerCreate,
    db: AsyncSession = Depends(get_db_async),
    current_admin: User = Depends(get_current_admin_user),
) -> Partner:
    existing = await db.scalar(
        select(Partner).where(
            (Partner.code == payload.code) | (Partner.email == payload.email)
        )
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Partner with the same code or email already exists.",
        )

    partner = Partner(
        code=payload.code,
        name=payload.name,
        partner_type=payload.partner_type,
        email=payload.email,
        phone=payload.phone,
        address_text=payload.address_text,
        default_b2b_share=payload.default_b2b_share,
        default_b2c_share=payload.default_b2c_share,
        default_marketplace_share=payload.default_marketplace_share,
        status=payload.status,  # type: ignore[assignment]
        created_by_user_id=current_admin.id,
    )
    db.add(partner)
    await db.flush()
    await db.refresh(partner)
    return partner


@admin_router.get("/{partner_id}", response_model=PartnerRead)
async def get_partner(
    partner_id: UUID,
    db: AsyncSession = Depends(get_db_async),
    current_admin: User = Depends(get_current_admin_user),
) -> Partner:
    partner = await _get_partner_or_404(db, partner_id)
    return partner


@admin_router.patch("/{partner_id}", response_model=PartnerRead)
async def update_partner(
    partner_id: UUID,
    payload: PartnerUpdate,
    db: AsyncSession = Depends(get_db_async),
    current_admin: User = Depends(get_current_admin_user),
) -> Partner:
    partner = await _get_partner_or_404(db, partner_id)

    update_data = payload.dict(exclude_unset=True)
    for field_name, value in update_data.items():
        setattr(partner, field_name, value)

    await db.flush()
    await db.refresh(partner)
    return partner


@admin_router.patch("/{partner_id}/status", response_model=PartnerRead)
async def update_partner_status(
    partner_id: UUID,
    payload: PartnerStatusUpdate,
    db: AsyncSession = Depends(get_db_async),
    current_admin: User = Depends(get_current_admin_user),
) -> Partner:
    partner = await _get_partner_or_404(db, partner_id)
    partner.status = payload.status  # type: ignore[assignment]
    await db.flush()
    await db.refresh(partner)
    return partner


@admin_router.get(
    "/{partner_id}/revenue/summary",
    response_model=PartnerRevenueSummaryResponse,
)
async def get_partner_revenue_summary_admin(
    partner_id: UUID,
    db: AsyncSession = Depends(get_db_async),
    current_admin: User = Depends(get_current_admin_user),
    period_year: Optional[int] = Query(None, ge=2000, le=2100),
    period_month: Optional[int] = Query(None, ge=1, le=12),
) -> PartnerRevenueSummaryResponse:
    return await get_partner_revenue_summary(
        db,
        partner_id=partner_id,
        period_year=period_year,
        period_month=period_month,
    )


@admin_router.get(
    "/{partner_id}/payouts",
    response_model=PartnerPayoutListResponse,
)
async def list_partner_payouts_admin(
    partner_id: UUID,
    db: AsyncSession = Depends(get_db_async),
    current_admin: User = Depends(get_current_admin_user),
    page: Optional[int] = Query(None, ge=1),
    page_size: Optional[int] = Query(None, ge=1, le=100),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
) -> PartnerPayoutListResponse:
    await _get_partner_or_404(db, partner_id)
    if page is not None:
        limit = page_size or limit
        skip = (page - 1) * limit

    stmt = (
        select(PartnerPayout)
        .where(PartnerPayout.partner_id == partner_id)
        .order_by(PartnerPayout.requested_at.desc())
    )

    total_stmt = stmt.with_only_columns(func.count(PartnerPayout.id)).order_by(None)
    total_result = await db.execute(total_stmt)
    total = int(total_result.scalar_one() or 0)

    stmt = stmt.offset(skip).limit(limit)
    result = await db.execute(stmt)
    payouts_seq: Sequence[PartnerPayout] = result.scalars().all()
    payouts: List[PartnerPayout] = list(payouts_seq)

    return PartnerPayoutListResponse(
        items=cast(List[PartnerPayoutRead], payouts),
        total=total,
    )


# ---------------------------------------------------------------------------
# Partner self endpoints
# ---------------------------------------------------------------------------


@partner_router.get("/me", response_model=PartnerRead)
async def get_my_partner_profile(
    db: AsyncSession = Depends(get_db_async),
    user_and_partner: tuple[User, Partner] = Depends(get_current_partner_user),
) -> Partner:
    _, partner = user_and_partner
    return partner


@partner_router.get("/me/dashboard", response_model=PartnerDashboardSummary)
async def get_my_partner_dashboard(
    db: AsyncSession = Depends(get_db_async),
    user_and_partner: tuple[User, Partner] = Depends(get_current_partner_user),
) -> PartnerDashboardSummary:
    _, partner = user_and_partner

    # total clients
    total_clients_stmt = select(func.count(PartnerClient.id)).where(
        PartnerClient.partner_id == partner.id
    )
    total_clients_result = await db.execute(total_clients_stmt)
    total_clients = int(total_clients_result.scalar_one() or 0)

    # total orders / total revenue
    revenue_stmt = select(
        func.count(PartnerRevenue.id),
        func.coalesce(func.sum(PartnerRevenue.partner_amount), 0),
    ).where(PartnerRevenue.partner_id == partner.id)

    revenue_result = await db.execute(revenue_stmt)
    total_orders_raw, total_revenue_raw = revenue_result.one()
    total_orders = int(total_orders_raw or 0)
    total_revenue = float(total_revenue_raw or 0)

    # pending payout
    pending_stmt = select(
        func.coalesce(func.sum(PartnerRevenue.partner_amount), 0)
    ).where(
        PartnerRevenue.partner_id == partner.id,
        PartnerRevenue.status == "pending",
    )
    pending_result = await db.execute(pending_stmt)
    total_pending = float(pending_result.scalar_one() or 0)

    # last month revenue
    now = datetime.utcnow()
    last_month_year = now.year
    last_month = now.month - 1
    if last_month == 0:
        last_month = 12
        last_month_year -= 1

    last_month_stmt = select(
        func.coalesce(func.sum(PartnerRevenue.partner_amount), 0)
    ).where(
        PartnerRevenue.partner_id == partner.id,
        PartnerRevenue.period_year == last_month_year,
        PartnerRevenue.period_month == last_month,
    )
    last_month_result = await db.execute(last_month_stmt)
    last_month_revenue = float(last_month_result.scalar_one() or 0)

    # last payout date
    last_payout_stmt = (
        select(PartnerPayout.paid_at)
        .where(
            PartnerPayout.partner_id == partner.id,
            PartnerPayout.status == "paid",
            PartnerPayout.paid_at.is_not(None),
        )
        .order_by(PartnerPayout.paid_at.desc())
        .limit(1)
    )
    last_payout_result = await db.execute(last_payout_stmt)
    last_payout_date = last_payout_result.scalar_one_or_none()

    return PartnerDashboardSummary(
        partner_id=partner.id,
        total_clients=total_clients,
        total_orders=total_orders,
        total_revenue=total_revenue,
        total_pending_payout=total_pending,
        last_month_revenue=last_month_revenue,
        last_payout_date=last_payout_date,
    )


@partner_router.get("/me/clients", response_model=PartnerClientListResponse)
async def list_my_clients(
    db: AsyncSession = Depends(get_db_async),
    user_and_partner: tuple[User, Partner] = Depends(get_current_partner_user),
    page: Optional[int] = Query(None, ge=1),
    page_size: Optional[int] = Query(None, ge=1, le=100),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
) -> PartnerClientListResponse:
    _, partner = user_and_partner
    if page is not None:
        limit = page_size or limit
        skip = (page - 1) * limit

    stmt = (
        select(PartnerClient)
        .where(PartnerClient.partner_id == partner.id)
        .order_by(PartnerClient.relationship_started_at.desc())
    )

    total_stmt = stmt.with_only_columns(func.count(PartnerClient.id)).order_by(None)
    total_result = await db.execute(total_stmt)
    total = int(total_result.scalar_one() or 0)

    stmt = stmt.offset(skip).limit(limit)
    result = await db.execute(stmt)
    clients_seq: Sequence[PartnerClient] = result.scalars().all()
    clients: List[PartnerClient] = list(clients_seq)

    return PartnerClientListResponse(
        items=cast(List[PartnerClientRead], clients),
        total=total,
    )


@partner_router.get("/me/revenue", response_model=PartnerRevenueListResponse)
async def list_my_revenue_rows(
    db: AsyncSession = Depends(get_db_async),
    user_and_partner: tuple[User, Partner] = Depends(get_current_partner_user),
    page: Optional[int] = Query(None, ge=1),
    page_size: Optional[int] = Query(None, ge=1, le=100),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    service_type: Optional[str] = Query(None),
) -> PartnerRevenueListResponse:
    _, partner = user_and_partner
    if page is not None:
        limit = page_size or limit
        skip = (page - 1) * limit

    stmt = select(PartnerRevenue).where(PartnerRevenue.partner_id == partner.id)

    if service_type:
        stmt = stmt.where(PartnerRevenue.service_type == service_type)

    total_stmt = stmt.with_only_columns(func.count(PartnerRevenue.id)).order_by(None)
    total_result = await db.execute(total_stmt)
    total = int(total_result.scalar_one() or 0)

    stmt = stmt.order_by(PartnerRevenue.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(stmt)
    rows: List[PartnerRevenue] = list(result.scalars().all())

    return PartnerRevenueListResponse(
        items=cast(List[PartnerRevenueRow], rows),
        total=total,
    )


@partner_router.get("/me/orders", response_model=PartnerRevenueListResponse)
async def list_my_orders(
    db: AsyncSession = Depends(get_db_async),
    user_and_partner: tuple[User, Partner] = Depends(get_current_partner_user),
    page: Optional[int] = Query(None, ge=1),
    page_size: Optional[int] = Query(None, ge=1, le=100),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None),
) -> PartnerRevenueListResponse:
    _, partner = user_and_partner
    if page is not None:
        limit = page_size or limit
        skip = (page - 1) * limit

    stmt = select(PartnerRevenue).where(PartnerRevenue.partner_id == partner.id)
    if status:
        stmt = stmt.where(PartnerRevenue.status == status)

    total_stmt = stmt.with_only_columns(func.count(PartnerRevenue.id)).order_by(None)
    total_result = await db.execute(total_stmt)
    total = int(total_result.scalar_one() or 0)

    stmt = stmt.order_by(PartnerRevenue.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(stmt)
    rows: List[PartnerRevenue] = list(result.scalars().all())

    return PartnerRevenueListResponse(
        items=cast(List[PartnerRevenueRow], rows),
        total=total,
    )


@partner_router.get("/me/payouts", response_model=PartnerPayoutListResponse)
async def list_my_payouts(
    db: AsyncSession = Depends(get_db_async),
    user_and_partner: tuple[User, Partner] = Depends(get_current_partner_user),
    page: Optional[int] = Query(None, ge=1),
    page_size: Optional[int] = Query(None, ge=1, le=100),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
) -> PartnerPayoutListResponse:
    _, partner = user_and_partner
    if page is not None:
        limit = page_size or limit
        skip = (page - 1) * limit

    stmt = (
        select(PartnerPayout)
        .where(PartnerPayout.partner_id == partner.id)
        .order_by(PartnerPayout.requested_at.desc())
    )

    total_stmt = stmt.with_only_columns(func.count(PartnerPayout.id)).order_by(None)
    total_result = await db.execute(total_stmt)
    total = int(total_result.scalar_one() or 0)

    stmt = stmt.offset(skip).limit(limit)
    result = await db.execute(stmt)
    payouts_seq: Sequence[PartnerPayout] = result.scalars().all()
    payouts: List[PartnerPayout] = list(payouts_seq)

    return PartnerPayoutListResponse(
        items=cast(List[PartnerPayoutRead], payouts),
        total=total,
    )


@partner_router.post(
    "/me/payouts",
    response_model=PartnerPayoutRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_payout_request(
    payload: PartnerPayoutCreate,
    db: AsyncSession = Depends(get_db_async),
    user_and_partner: tuple[User, Partner] = Depends(get_current_partner_user),
) -> PartnerPayout:
    _, partner = user_and_partner

    payout = PartnerPayout(
        partner_id=cast(UUID, partner.id),
        currency_code=payload.currency_code,
        total_amount=0,
        fees_amount=0,
        net_amount=0,
        period_start_date=payload.period_start_date,
        period_end_date=payload.period_end_date,
        status="requested",
    )
    db.add(payout)
    await db.flush()
    await db.refresh(payout)
    return payout


# ---------------------------------------------------------------------------
# Agreement endpoints
# ---------------------------------------------------------------------------


@partner_router.get(
    "/agreement/current",
    response_model=PartnerAgreementCurrentResponse,
)
async def get_partner_agreement_current(
    current_user: User = Depends(get_current_active_user),
) -> PartnerAgreementCurrentResponse:
    return await get_current_agreement()


@partner_router.post(
    "/agreement/sign",
    response_model=PartnerAgreementSignResponse,
)
async def sign_partner_agreement(
    request: Request,
    payload: PartnerAgreementSignRequest,
    db: AsyncSession = Depends(get_db_async),
    user_and_partner: tuple[User, Partner] = Depends(get_current_partner_user),
) -> PartnerAgreementSignResponse:
    _, partner = user_and_partner

    client_host = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    return await sign_agreement(
        db,
        partner_id=partner.id,  # type: ignore[arg-type]
        request=payload,
        ip_address=client_host,
        user_agent=user_agent,
    )

