from sqlalchemy import Column, Integer, String, Date, Text, Float, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.database.config import Base
import enum

class CampaignStatus(str, enum.Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class CampaignType(str, enum.Enum):
    PROMOTION = "promotion"
    LOYALTY = "loyalty"
    SEASONAL = "seasonal"
    BRAND_AWARENESS = "brand_awareness"
    LEAD_GENERATION = "lead_generation"

class Campaign(Base):
    __tablename__ = "campaigns"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    type = Column(Enum(CampaignType), nullable=False)
    target_audience = Column(String(255))
    budget = Column(Float, default=0.0)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date)
    status = Column(Enum(CampaignStatus), default=CampaignStatus.DRAFT)
    created_by = Column(String(100))
    created_at = Column(Date, default=func.current_date())
    updated_at = Column(Date, default=func.current_date(), onupdate=func.current_date())

    # Relationships
    # campaigns_targets = relationship("CampaignTarget", back_populates="campaign")