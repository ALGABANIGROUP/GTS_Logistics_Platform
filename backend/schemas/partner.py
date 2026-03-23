from __future__ import annotations

from datetime import datetime, date
from typing import List, Optional, Literal

from pydantic import BaseModel, EmailStr, Field
from uuid import UUID


PartnerStatusLiteral = Literal["pending", "active", "suspended", "closed"]
ServiceTypeLiteral = Literal["b2b", "b2c", "marketplace"]
PayoutStatusLiteral = Literal[
    "requested",
    "under_review",
    "approved",
    "paid",
    "rejected",
]


# ---------------------------------------------------------------------------
# Partner base models
# ---------------------------------------------------------------------------


class PartnerBase(BaseModel):
    code: str = Field(..., max_length=32)
    name: str = Field(..., max_length=255)
    partner_type: Literal["individual", "company", "agency"]
    email: EmailStr
    phone: Optional[str] = None
    address_text: Optional[str] = None

    default_b2b_share: float = 60.0
    default_b2c_share: float = 70.0
    default_marketplace_share: float = 80.0

    status: PartnerStatusLiteral = "pending"


class PartnerCreate(PartnerBase):
    pass


class PartnerUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    partner_type: Optional[Literal["individual", "company", "agency"]] = None
    phone: Optional[str] = None
    address_text: Optional[str] = None

    default_b2b_share: Optional[float] = None
    default_b2c_share: Optional[float] = None
    default_marketplace_share: Optional[float] = None

    bank_account_name: Optional[str] = None
    bank_account_iban: Optional[str] = None
    bank_account_swift: Optional[str] = None

    status: Optional[PartnerStatusLiteral] = None


class PartnerStatusUpdate(BaseModel):
    status: PartnerStatusLiteral


class PartnerRead(BaseModel):
    id: UUID
    code: str
    name: str
    partner_type: str
    email: EmailStr
    phone: Optional[str]
    address_text: Optional[str]

    default_b2b_share: float
    default_b2c_share: float
    default_marketplace_share: float

    revenue_total: float
    revenue_pending: float
    revenue_paid: float

    status: PartnerStatusLiteral
    joined_at: datetime
    last_login_at: Optional[datetime]

    class Config:
        orm_mode = True


class PartnerListResponse(BaseModel):
    items: List[PartnerRead]
    total: int


# ---------------------------------------------------------------------------
# Partner client models
# ---------------------------------------------------------------------------


class PartnerClientRead(BaseModel):
    id: UUID
    client_id: UUID
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    is_active: bool
    relationship_started_at: datetime
    relationship_channel: str
    total_orders: int = 0
    total_revenue: float = 0.0

    class Config:
        orm_mode = True


class PartnerClientListResponse(BaseModel):
    items: List[PartnerClientRead]
    total: int


# ---------------------------------------------------------------------------
# Partner revenue models
# ---------------------------------------------------------------------------


class PartnerRevenueRow(BaseModel):
    id: UUID
    order_id: UUID
    client_id: Optional[UUID]
    service_type: ServiceTypeLiteral
    currency_code: str
    gross_amount: float
    net_profit_amount: float
    partner_share_percent: float
    partner_amount: float
    gts_amount: float
    status: str
    period_year: int
    period_month: int
    created_at: datetime

    class Config:
        orm_mode = True


class PartnerRevenueListResponse(BaseModel):
    items: List[PartnerRevenueRow]
    total: int


class PartnerRevenueSummaryItem(BaseModel):
    service_type: ServiceTypeLiteral
    period_year: int
    period_month: int
    total_net_profit: float
    total_partner_amount: float
    total_gts_amount: float
    orders_count: int


class PartnerRevenueSummaryResponse(BaseModel):
    partner_id: UUID
    items: List[PartnerRevenueSummaryItem]
    total_partner_amount: float
    total_gts_amount: float
    total_orders: int


# ---------------------------------------------------------------------------
# Partner payout models
# ---------------------------------------------------------------------------


class PartnerPayoutRead(BaseModel):
    id: UUID
    currency_code: str
    total_amount: float
    fees_amount: float
    net_amount: float
    period_start_date: date
    period_end_date: date
    status: PayoutStatusLiteral
    requested_at: datetime
    approved_at: Optional[datetime]
    paid_at: Optional[datetime]
    payment_reference: Optional[str]

    class Config:
        orm_mode = True


class PartnerPayoutListResponse(BaseModel):
    items: List[PartnerPayoutRead]
    total: int


class PartnerPayoutCreate(BaseModel):
    period_start_date: date
    period_end_date: date
    currency_code: str = "USD"


# ---------------------------------------------------------------------------
# Partner dashboard models
# ---------------------------------------------------------------------------


class PartnerDashboardSummary(BaseModel):
    partner_id: UUID
    total_clients: int
    total_orders: int
    total_revenue: float
    total_pending_payout: float
    last_month_revenue: float
    last_payout_date: Optional[datetime]


# ---------------------------------------------------------------------------
# Agreement models
# ---------------------------------------------------------------------------


class PartnerAgreementCurrentResponse(BaseModel):
    agreement_version: str
    agreement_body: str
    agreement_text_hash: str


class PartnerAgreementSignRequest(BaseModel):
    agreement_version: str
    signature_name: str
    checkbox_revenue: bool
    checkbox_confidentiality: bool
    checkbox_misuse: bool


class PartnerAgreementSignResponse(BaseModel):
    partner_id: UUID
    agreement_version: str
    signed_at: datetime
    ip_address: Optional[str]
    signature_name: str
