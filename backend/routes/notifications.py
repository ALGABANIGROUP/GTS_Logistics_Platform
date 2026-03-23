from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from backend.database.session import Base

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    message = Column(String, nullable=False)
    status = Column(String, default="unread") 
    created_at = Column(DateTime(timezone=True), server_default=func.now())

