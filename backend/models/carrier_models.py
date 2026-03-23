from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal

# Base schemas
class CarrierBase(BaseModel):
    name: str = Field(..., max_length=255)
    mc_number: Optional[str] = Field(None, max_length=50)
    dot_number: Optional[str] = Field(None, max_length=50)
    scac_code: Optional[str] = Field(None, max_length=10)
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
    insurance_provider: Optional[str] = Field(None, max_length=255)
    insurance_policy_number: Optional[str] = Field(None, max_length=100)
    insurance_expiry_date: Optional[datetime] = None
    bonding_company: Optional[str] = Field(None, max_length=255)
    bonding_amount: Optional[Decimal] = None
    bonding_expiry_date: Optional[datetime] = None
    carrier_type: str = "common"  # common, owner_operator, fleet
    equipment_types: Optional[List[str]] = None
    operating_areas: Optional[List[str]] = None
    preferred_lanes: Optional[List[str]] = None
    credit_score: Optional[int] = None
    payment_terms: str = "net_30"
    rating: Optional[Decimal] = Field(None, ge=1.0, le=5.0)
    total_loads: int = 0
    on_time_delivery_rate: Optional[Decimal] = Field(None, ge=0.0, le=100.0)
    incident_rate: Optional[Decimal] = Field(None, ge=0.0, le=100.0)
    is_active: bool = True
    is_verified: bool = False
    verification_date: Optional[datetime] = None
    notes: Optional[str] = None

# Create schema
class CarrierCreate(CarrierBase):
    pass

# Update schema
class CarrierUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    mc_number: Optional[str] = Field(None, max_length=50)
    dot_number: Optional[str] = Field(None, max_length=50)
    scac_code: Optional[str] = Field(None, max_length=10)
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
    insurance_provider: Optional[str] = Field(None, max_length=255)
    insurance_policy_number: Optional[str] = Field(None, max_length=100)
    insurance_expiry_date: Optional[datetime] = None
    bonding_company: Optional[str] = Field(None, max_length=255)
    bonding_amount: Optional[Decimal] = None
    bonding_expiry_date: Optional[datetime] = None
    carrier_type: Optional[str] = None
    equipment_types: Optional[List[str]] = None
    operating_areas: Optional[List[str]] = None
    preferred_lanes: Optional[List[str]] = None
    credit_score: Optional[int] = None
    payment_terms: Optional[str] = None
    rating: Optional[Decimal] = Field(None, ge=1.0, le=5.0)
    total_loads: Optional[int] = None
    on_time_delivery_rate: Optional[Decimal] = Field(None, ge=0.0, le=100.0)
    incident_rate: Optional[Decimal] = Field(None, ge=0.0, le=100.0)
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None
    verification_date: Optional[datetime] = None
    notes: Optional[str] = None

# Response schema
class CarrierResponse(CarrierBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# List response schema
class CarrierListResponse(BaseModel):
    carriers: List[CarrierResponse]
    total: int
    page: int
    per_page: int

# Verification schema
class CarrierVerification(BaseModel):
    mc_number: str = Field(..., max_length=50)

class CarrierVerificationResponse(BaseModel):
    is_valid: bool
    carrier_info: Optional[dict] = None
    message: str