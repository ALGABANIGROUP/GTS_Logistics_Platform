from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal

# Base schemas
class ShipperBase(BaseModel):
    name: str = Field(..., max_length=255)
    tax_id: Optional[str] = Field(None, max_length=50)
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None
    website: Optional[str] = Field(None, max_length=255)
    address_line1: Optional[str] = Field(None, max_length=255)
    address_line2: Optional[str] = Field(None, max_length=255)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=50)
    zip_code: Optional[str] = Field(None, max_length=20)
    country: str = "USA"
    contact_person: Optional[str] = Field(None, max_length=255)
    contact_phone: Optional[str] = Field(None, max_length=20)
    contact_email: Optional[EmailStr] = None
    industry_type: Optional[str] = Field(None, max_length=100)
    business_type: Optional[str] = Field(None, max_length=50)  # manufacturer, distributor, retailer, etc.
    annual_shipping_volume: Optional[int] = None  # Estimated annual loads
    credit_score: Optional[int] = None
    payment_terms: str = "net_30"
    rating: Optional[Decimal] = Field(None, ge=1.0, le=5.0)
    total_loads: int = 0
    on_time_pickup_rate: Optional[Decimal] = Field(None, ge=0.0, le=100.0)
    damage_claim_rate: Optional[Decimal] = Field(None, ge=0.0, le=100.0)
    is_active: bool = True
    is_verified: bool = False
    verification_date: Optional[datetime] = None
    preferred_carriers: Optional[List[str]] = None  # Array of preferred carrier IDs
    shipping_schedule: Optional[str] = None  # JSON string for shipping patterns
    special_requirements: Optional[str] = None
    notes: Optional[str] = None

# Create schema
class ShipperCreate(ShipperBase):
    pass

# Update schema
class ShipperUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    tax_id: Optional[str] = Field(None, max_length=50)
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None
    website: Optional[str] = Field(None, max_length=255)
    address_line1: Optional[str] = Field(None, max_length=255)
    address_line2: Optional[str] = Field(None, max_length=255)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=50)
    zip_code: Optional[str] = Field(None, max_length=20)
    country: Optional[str] = None
    contact_person: Optional[str] = Field(None, max_length=255)
    contact_phone: Optional[str] = Field(None, max_length=20)
    contact_email: Optional[EmailStr] = None
    industry_type: Optional[str] = Field(None, max_length=100)
    business_type: Optional[str] = Field(None, max_length=50)
    annual_shipping_volume: Optional[int] = None
    credit_score: Optional[int] = None
    payment_terms: Optional[str] = None
    rating: Optional[Decimal] = Field(None, ge=1.0, le=5.0)
    total_loads: Optional[int] = None
    on_time_pickup_rate: Optional[Decimal] = Field(None, ge=0.0, le=100.0)
    damage_claim_rate: Optional[Decimal] = Field(None, ge=0.0, le=100.0)
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None
    verification_date: Optional[datetime] = None
    preferred_carriers: Optional[List[str]] = None
    shipping_schedule: Optional[str] = None
    special_requirements: Optional[str] = None
    notes: Optional[str] = None

# Response schema
class ShipperResponse(ShipperBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# List response schema
class ShipperListResponse(BaseModel):
    shippers: List[ShipperResponse]
    total: int
    page: int
    per_page: int

# Verification schema
class ShipperVerification(BaseModel):
    tax_id: str = Field(..., max_length=50)

class ShipperVerificationResponse(BaseModel):
    is_valid: bool
    shipper_info: Optional[dict] = None
    message: str