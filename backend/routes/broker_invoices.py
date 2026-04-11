"""
Freight Broker Invoice and Commission Management Routes
Handles invoice generation, commission calculation, and profit tracking
"""

from datetime import datetime, date, timedelta
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.session import get_async_session
from models.broker_commission import (
    EnhancedInvoice, BrokerCommission, CommissionTier, InvoiceType
)

router = APIRouter(prefix="/api/v1/broker", tags=["Freight Broker"])


# ==================== Pydantic Schemas ====================

class CommissionTierCreate(BaseModel):
    name: str
    shipment_type: str
    commission_percentage: float = Field(..., gt=0, le=100)
    minimum_commission: float = Field(default=0.0, ge=0)
    maximum_commission: Optional[float] = None
    is_active: bool = True


class CommissionTierOut(CommissionTierCreate):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]
    
    model_config = {"from_attributes": True}


class CommissionCalculationRequest(BaseModel):
    shipment_id: int
    shipment_number: str
    client_invoice_amount: float = Field(..., gt=0)
    carrier_cost: float = Field(..., gt=0)
    commission_tier_id: Optional[int] = None
    custom_commission_percentage: Optional[float] = Field(None, ge=0, le=100)


class BrokerCommissionOut(BaseModel):
    id: int
    shipment_id: int
    shipment_number: str
    client_invoice_amount: float
    carrier_cost: float
    commission_percentage: float
    commission_amount: float
    gross_profit: float
    net_profit: float
    profit_margin_percentage: float
    status: str
    shipment_date: Optional[datetime]
    delivery_date: Optional[datetime]
    commission_payment_date: Optional[datetime]
    created_at: datetime
    notes: Optional[str]
    
    model_config = {"from_attributes": True}


class EnhancedInvoiceCreate(BaseModel):
    number: str
    invoice_type: str  # "client", "carrier", "commission"
    shipment_id: Optional[int] = None
    shipment_number: Optional[str] = None
    from_party: Optional[str] = None
    to_party: Optional[str] = None
    amount_usd: float = Field(..., gt=0)
    commission_percentage: Optional[float] = None
    commission_amount: Optional[float] = None
    carrier_cost: Optional[float] = None
    notes: Optional[str] = None
    due_date: Optional[date] = None


class EnhancedInvoiceOut(EnhancedInvoiceCreate):
    id: int
    date: datetime
    profit_margin: Optional[float]
    profit_margin_percentage: Optional[float]
    status: str
    payment_date: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]
    
    model_config = {"from_attributes": True}


# ==================== Commission Tier Management ====================

@router.post("/commission-tiers", response_model=CommissionTierOut)
async def create_commission_tier(
    payload: CommissionTierCreate,
    db: AsyncSession = Depends(get_async_session),
) -> CommissionTierOut:
    """Create a new commission tier for shipment types"""
    tier = CommissionTier(**payload.model_dump())
    db.add(tier)
    await db.commit()
    await db.refresh(tier)
    return CommissionTierOut.model_validate(tier)


@router.get("/commission-tiers", response_model=List[CommissionTierOut])
async def list_commission_tiers(
    shipment_type: Optional[str] = None,
    db: AsyncSession = Depends(get_async_session),
) -> List[CommissionTierOut]:
    """List all commission tiers, optionally filtered by shipment type"""
    query = select(CommissionTier).where(CommissionTier.is_active == True)
    if shipment_type:
        query = query.where(CommissionTier.shipment_type == shipment_type)
    result = await db.execute(query)
    tiers = result.scalars().all()
    return [CommissionTierOut.model_validate(t) for t in tiers]


# ==================== Commission Calculation ====================

@router.post("/calculate-commission", response_model=BrokerCommissionOut)
async def calculate_commission(
    payload: CommissionCalculationRequest,
    db: AsyncSession = Depends(get_async_session),
) -> BrokerCommissionOut:
    """Calculate and create broker commission for a shipment"""
    
    # Validate amounts
    if payload.carrier_cost >= payload.client_invoice_amount:
        raise HTTPException(
            status_code=400,
            detail="Carrier cost cannot be >= client invoice amount"
        )
    
    # Determine commission percentage
    commission_percentage = payload.custom_commission_percentage or 5.0
    
    if payload.commission_tier_id and not payload.custom_commission_percentage:
        result = await db.execute(
            select(CommissionTier).where(CommissionTier.id == payload.commission_tier_id)
        )
        tier = result.scalars().first()
        if tier:
            commission_percentage = tier.commission_percentage
    
    # Calculate amounts
    gross_profit = payload.client_invoice_amount - payload.carrier_cost
    commission_amount = gross_profit * (commission_percentage / 100)
    net_profit = gross_profit - commission_amount
    profit_margin_percentage = (gross_profit / payload.client_invoice_amount) * 100
    
    # Check for maximum commission
    if payload.commission_tier_id and not payload.custom_commission_percentage:
        result = await db.execute(
            select(CommissionTier).where(CommissionTier.id == payload.commission_tier_id)
        )
        tier = result.scalars().first()
        if tier and tier.maximum_commission and commission_amount > tier.maximum_commission:
            commission_amount = tier.maximum_commission
            net_profit = gross_profit - commission_amount
    
    # Create commission record
    commission = BrokerCommission(
        shipment_id=payload.shipment_id,
        shipment_number=payload.shipment_number,
        client_invoice_amount=payload.client_invoice_amount,
        carrier_cost=payload.carrier_cost,
        commission_tier_id=payload.commission_tier_id,
        commission_percentage=commission_percentage,
        commission_amount=commission_amount,
        gross_profit=gross_profit,
        net_profit=net_profit,
        profit_margin_percentage=profit_margin_percentage,
        status="calculated",
    )
    
    db.add(commission)
    await db.commit()
    await db.refresh(commission)
    
    return BrokerCommissionOut.model_validate(commission)


@router.get("/commissions", response_model=List[BrokerCommissionOut])
async def list_commissions(
    status: Optional[str] = None,
    shipment_id: Optional[int] = None,
    db: AsyncSession = Depends(get_async_session),
) -> List[BrokerCommissionOut]:
    """List all broker commissions with optional filters"""
    query = select(BrokerCommission)
    
    if status:
        query = query.where(BrokerCommission.status == status)
    if shipment_id:
        query = query.where(BrokerCommission.shipment_id == shipment_id)
    
    result = await db.execute(query.order_by(BrokerCommission.created_at.desc()))
    commissions = result.scalars().all()
    return [BrokerCommissionOut.model_validate(c) for c in commissions]


@router.get("/commissions/{commission_id}", response_model=BrokerCommissionOut)
async def get_commission(
    commission_id: int,
    db: AsyncSession = Depends(get_async_session),
) -> BrokerCommissionOut:
    """Get specific commission details"""
    result = await db.execute(
        select(BrokerCommission).where(BrokerCommission.id == commission_id)
    )
    commission = result.scalars().first()
    if not commission:
        raise HTTPException(status_code=404, detail="Commission not found")
    return BrokerCommissionOut.model_validate(commission)


# ==================== Enhanced Invoice Management ====================

@router.post("/invoices", response_model=EnhancedInvoiceOut)
async def create_enhanced_invoice(
    payload: EnhancedInvoiceCreate,
    db: AsyncSession = Depends(get_async_session),
) -> EnhancedInvoiceOut:
    """Create a new broker invoice"""
    
    # Calculate profit if amounts provided
    profit_margin = None
    profit_margin_percentage = None
    
    if payload.carrier_cost and payload.invoice_type != "carrier":
        profit_margin = payload.amount_usd - payload.carrier_cost
        if payload.amount_usd > 0:
            profit_margin_percentage = (profit_margin / payload.amount_usd) * 100
    
    invoice = EnhancedInvoice(
        number=payload.number,
        invoice_type=payload.invoice_type,
        shipment_id=payload.shipment_id,
        shipment_number=payload.shipment_number,
        from_party=payload.from_party,
        to_party=payload.to_party,
        amount_usd=payload.amount_usd,
        commission_percentage=payload.commission_percentage,
        commission_amount=payload.commission_amount,
        carrier_cost=payload.carrier_cost,
        profit_margin=profit_margin,
        profit_margin_percentage=profit_margin_percentage,
        notes=payload.notes,
        due_date=payload.due_date,
    )
    
    db.add(invoice)
    await db.commit()
    await db.refresh(invoice)
    
    return EnhancedInvoiceOut.model_validate(invoice)


@router.get("/invoices", response_model=List[EnhancedInvoiceOut])
async def list_enhanced_invoices(
    invoice_type: Optional[str] = None,
    status: Optional[str] = None,
    shipment_id: Optional[int] = None,
    db: AsyncSession = Depends(get_async_session),
) -> List[EnhancedInvoiceOut]:
    """List broker invoices with optional filters"""
    query = select(EnhancedInvoice)
    
    if invoice_type:
        query = query.where(EnhancedInvoice.invoice_type == invoice_type)
    if status:
        query = query.where(EnhancedInvoice.status == status)
    if shipment_id:
        query = query.where(EnhancedInvoice.shipment_id == shipment_id)
    
    result = await db.execute(query.order_by(EnhancedInvoice.created_at.desc()))
    invoices = result.scalars().all()
    return [EnhancedInvoiceOut.model_validate(inv) for inv in invoices]


@router.patch("/invoices/{invoice_id}", response_model=EnhancedInvoiceOut)
async def update_invoice_status(
    invoice_id: int,
    status: str,
    payment_date: Optional[date] = None,
    db: AsyncSession = Depends(get_async_session),
) -> EnhancedInvoiceOut:
    """Update invoice status and payment info"""
    result = await db.execute(
        select(EnhancedInvoice).where(EnhancedInvoice.id == invoice_id)
    )
    invoice = result.scalars().first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    invoice.status = status
    if payment_date:
        invoice.payment_date = datetime.combine(payment_date, datetime.min.time())
    
    invoice.updated_at = datetime.utcnow()
    db.add(invoice)
    await db.commit()
    await db.refresh(invoice)
    
    return EnhancedInvoiceOut.model_validate(invoice)


# ==================== Broker Analytics & Reports ====================

class CommissionReport(BaseModel):
    total_commissions: float
    total_invoices: int
    average_commission_percentage: float
    total_gross_profit: float
    total_net_profit: float
    average_profit_margin: float
    paid_commissions: float
    pending_commissions: float
    
    model_config = ConfigDict(from_attributes=True)


@router.get("/reports/commission-summary", response_model=CommissionReport)
async def get_commission_summary(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: AsyncSession = Depends(get_async_session),
) -> CommissionReport:
    """Get commission summary report for date range"""
    
    query = select(BrokerCommission)
    
    if start_date:
        query = query.where(BrokerCommission.created_at >= datetime.combine(start_date, datetime.min.time()))
    if end_date:
        query = query.where(BrokerCommission.created_at <= datetime.combine(end_date, datetime.max.time()))
    
    result = await db.execute(query)
    commissions = result.scalars().all()
    
    if not commissions:
        return CommissionReport(
            total_commissions=0, total_invoices=0, average_commission_percentage=0,
            total_gross_profit=0, total_net_profit=0, average_profit_margin=0,
            paid_commissions=0, pending_commissions=0
        )
    
    total_commissions = sum(c.commission_amount for c in commissions)
    total_gross_profit = sum(c.gross_profit for c in commissions)
    total_net_profit = sum(c.net_profit for c in commissions)
    average_commission_percentage = sum(c.commission_percentage for c in commissions) / len(commissions)
    average_profit_margin = sum(c.profit_margin_percentage for c in commissions) / len(commissions)
    
    paid = sum(c.commission_amount for c in commissions if c.status == "paid")
    pending = sum(c.commission_amount for c in commissions if c.status in ["calculated", "approved"])
    
    return CommissionReport(
        total_commissions=total_commissions,
        total_invoices=len(commissions),
        average_commission_percentage=average_commission_percentage,
        total_gross_profit=total_gross_profit,
        total_net_profit=total_net_profit,
        average_profit_margin=average_profit_margin,
        paid_commissions=paid,
        pending_commissions=pending,
    )


@router.get("/reports/profit-breakdown")
async def get_profit_breakdown(
    shipment_type: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: AsyncSession = Depends(get_async_session),
):
    """Get profit breakdown by shipment statistics"""
    
    query = select(BrokerCommission)
    
    if start_date:
        query = query.where(BrokerCommission.created_at >= datetime.combine(start_date, datetime.min.time()))
    if end_date:
        query = query.where(BrokerCommission.created_at <= datetime.combine(end_date, datetime.max.time()))
    
    result = await db.execute(query)
    commissions = result.scalars().all()
    
    return {
        "summary": {
            "total_shipments": len(commissions),
            "total_revenue": sum(c.client_invoice_amount for c in commissions),
            "total_costs": sum(c.carrier_cost for c in commissions),
            "total_gross_profit": sum(c.gross_profit for c in commissions),
            "total_commissions": sum(c.commission_amount for c in commissions),
            "total_net_profit": sum(c.net_profit for c in commissions),
        },
        "statistics": {
            "avg_revenue_per_shipment": sum(c.client_invoice_amount for c in commissions) / len(commissions) if commissions else 0,
            "avg_profit_margin": sum(c.profit_margin_percentage for c in commissions) / len(commissions) if commissions else 0,
            "avg_commission_percentage": sum(c.commission_percentage for c in commissions) / len(commissions) if commissions else 0,
        }
    }
