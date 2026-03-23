from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class TransportType(str, Enum):
    ROAD = "road"
    AIR = "air"
    SEA = "sea"
    RAIL = "rail"
    MULTIMODAL = "multimodal"


class SafetyStandardLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Country(BaseModel):
    code: str
    name: str
    region: str
    continent: str


class TransportLaw(BaseModel):
    id: str
    country_code: str
    country_name: str
    title: str
    description: str
    transport_type: TransportType
    year: int
    safety_standards: SafetyStandardLevel
    last_updated: datetime = Field(default_factory=datetime.now)
    next_update_due: datetime
    document_url: Optional[str] = None
    tags: list[str] = Field(default_factory=list)

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "USA-2023-RD",
                "country_code": "US",
                "country_name": "United States",
                "title": "Federal Motor Carrier Safety Regulations",
                "description": "Comprehensive regulations governing commercial motor vehicle safety",
                "transport_type": "road",
                "year": 2023,
                "safety_standards": "high",
                "tags": ["compliance", "fmcsa", "safety", "commercial"],
            }
        }
    }


class LawUpdateRequest(BaseModel):
    law_id: str
    update_reason: str
    new_content: Optional[str] = None
    document_url: Optional[str] = None
    update_date: datetime = Field(default_factory=datetime.now)
