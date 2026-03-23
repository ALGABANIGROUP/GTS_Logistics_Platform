from __future__ import annotations

from typing import Optional, List, Tuple, cast
from uuid import UUID
from datetime import datetime

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from backend.models.partner import Partner, PartnerRevenue
from backend.schemas.partner import (
    ServiceTypeLiteral,
    PartnerRevenueSummaryResponse,
    PartnerRevenueSummaryItem,
)


async def calculate_and_store_partner_revenue(
    db: AsyncSession,
    *,
    partner_id: UUID,
    client_id: Optional[UUID],
    order_id: UUID,
    service_type: ServiceTypeLiteral,
    net_profit_amount: float,
    currency_code: str = "USD",
    gross_amount: Optional[float] = None,
) -> PartnerRevenue:
    """
    Create a PartnerRevenue row for a completed order and update partner aggregates.
    """
    if net_profit_amount <= 0:
        raise ValueError("net_profit_amount must be positive")

    partner: Partner | None = await db.scalar(
        select(Partner).where(Partner.id == partner_id)
    )
    if partner is None:
        raise ValueError("Partner not found")

    # Resolve share percent from partner defaults
    if service_type == "b2b":
        share_percent = float(
            cast(float, partner.default_b2b_share or 0.0)  # type: ignore[arg-type]
        )
    elif service_type == "b2c":
        share_percent = float(
            cast(float, partner.default_b2c_share or 0.0)  # type: ignore[arg-type]
        )
    else:
        share_percent = float(
            cast(float, partner.default_marketplace_share or 0.0)  # type: ignore[arg-type]
        )

    partner_amount = net_profit_amount * (share_percent / 100.0)
    gts_amount = net_profit_amount - partner_amount

    if gross_amount is None:
        gross_amount = net_profit_amount

    # determine period (year/month)
    now = datetime.utcnow()
    period_year = now.year
    period_month = now.month

    revenue_row = PartnerRevenue(
        partner_id=partner_id,
        client_id=client_id,
        order_id=order_id,
        service_type=service_type,
        currency_code=currency_code,
        gross_amount=gross_amount,
        net_profit_amount=net_profit_amount,
        partner_share_percent=share_percent,
        partner_amount=partner_amount,
        gts_amount=gts_amount,
        status="pending",
        period_year=period_year,
        period_month=period_month,
    )
    db.add(revenue_row)

    # update partner aggregates (runtime-safe, but Pylance needs ignore)
    partner.revenue_total = (partner.revenue_total or 0) + net_profit_amount  # type: ignore[assignment]
    partner.revenue_pending = (partner.revenue_pending or 0) + partner_amount  # type: ignore[assignment]

    await db.flush()
    await db.refresh(revenue_row)

    return revenue_row


async def get_partner_revenue_summary(
    db: AsyncSession,
    *,
    partner_id: UUID,
    period_year: Optional[int] = None,
    period_month: Optional[int] = None,
) -> PartnerRevenueSummaryResponse:
    """
    Aggregate revenue for a partner, optionally filtered by year/month.
    """
    conditions = [PartnerRevenue.partner_id == partner_id]

    if period_year is not None:
        conditions.append(PartnerRevenue.period_year == period_year)
    if period_month is not None:
        conditions.append(PartnerRevenue.period_month == period_month)

    stmt = (
        select(
            PartnerRevenue.service_type,
            PartnerRevenue.period_year,
            PartnerRevenue.period_month,
            func.sum(PartnerRevenue.net_profit_amount),
            func.sum(PartnerRevenue.partner_amount),
            func.sum(PartnerRevenue.gts_amount),
            func.count(PartnerRevenue.id),
        )
        .where(*conditions)
        .group_by(
            PartnerRevenue.service_type,
            PartnerRevenue.period_year,
            PartnerRevenue.period_month,
        )
        .order_by(
            PartnerRevenue.period_year.desc(),
            PartnerRevenue.period_month.desc(),
            PartnerRevenue.service_type,
        )
    )

    result = await db.execute(stmt)
    rows: List[Tuple[str, int, int, float, float, float, int]] = result.all()  # type: ignore[assignment]

    items: List[PartnerRevenueSummaryItem] = []
    total_partner_amount = 0.0
    total_gts_amount = 0.0
    total_orders = 0

    for (
        service_type,
        year,
        month,
        total_net_profit,
        total_partner,
        total_gts,
        count_orders,
    ) in rows:
        item = PartnerRevenueSummaryItem(
            service_type=service_type,  # type: ignore[arg-type]
            period_year=year,
            period_month=month,
            total_net_profit=float(total_net_profit or 0),
            total_partner_amount=float(total_partner or 0),
            total_gts_amount=float(total_gts or 0),
            orders_count=int(count_orders or 0),
        )
        items.append(item)
        total_partner_amount += item.total_partner_amount
        total_gts_amount += item.total_gts_amount
        total_orders += item.orders_count

    return PartnerRevenueSummaryResponse(
        partner_id=partner_id,
        items=items,
        total_partner_amount=total_partner_amount,
        total_gts_amount=total_gts_amount,
        total_orders=total_orders,
    )

