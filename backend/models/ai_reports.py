from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from .base import Base

class AIReport(Base):
    __tablename__ = "ai_reports"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    summary = Column(Text, nullable=True)
    content = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
