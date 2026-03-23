# models.py  -- SQLAlchemy 2.0 models (ASCII-only)

from __future__ import annotations

from datetime import datetime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Text, DateTime, Float, func


class Base(DeclarativeBase):
    pass


# === Social performance logs ===
class PerformanceLog(Base):
    __tablename__ = "performance_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_name: Mapped[str] = mapped_column(String(200))
    platform: Mapped[str] = mapped_column(String(50))

    likes: Mapped[int] = mapped_column(Integer, default=0)
    comments: Mapped[int] = mapped_column(Integer, default=0)
    shares: Mapped[int] = mapped_column(Integer, default=0)
    views: Mapped[int] = mapped_column(Integer, default=0)

    engagement_score: Mapped[float] = mapped_column(Float, default=0.0)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        server_default=func.now(),
    )


# === Publish logs ===
class PublishLog(Base):
    __tablename__ = "publish_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_name: Mapped[str] = mapped_column(String(200))
    platform: Mapped[str] = mapped_column(String(50))
    status: Mapped[str] = mapped_column(String(40), default="posted")
    preview_link: Mapped[str] = mapped_column(String(500), default="")
    note: Mapped[str] = mapped_column(String(500), default="")

    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        server_default=func.now(),
    )


# === The VIZION: generic events stream (file change, task ops, etc.) ===
class VizionEvent(Base):
    __tablename__ = "vizion_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    event: Mapped[str] = mapped_column(String(100))          # e.g. "file.change"
    message: Mapped[str] = mapped_column(String(500), default="")
    meta: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON string

timestamp: Mapped[datetime] = mapped_column(
    DateTime(timezone=False),
    server_default=func.now(),
)
