# models.py  -- SQLAlchemy 2.0 models (ASCII-only)

from __future__ import annotations

from datetime import datetime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Text, DateTime, Float, func, ForeignKey


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


# === Task Management ===
class Task(Base):
    __tablename__ = "viz_tasks"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(Text, default="")
    priority: Mapped[int] = mapped_column(Integer, default=3)
    category: Mapped[str] = mapped_column(String(50), default="")
    expected_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="open")  # open|done
    created_at: Mapped[str] = mapped_column(String(32))
    updated_at: Mapped[str] = mapped_column(String(32))
    due_ts: Mapped[str | None] = mapped_column(String(32), nullable=True)


class TaskSession(Base):
    __tablename__ = "viz_sessions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    task_id: Mapped[int] = mapped_column(Integer, ForeignKey("viz_tasks.id", ondelete="CASCADE"))
    start_ts: Mapped[str] = mapped_column(String(32))
    end_ts: Mapped[str | None] = mapped_column(String(32), nullable=True)
    duration_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    note: Mapped[str] = mapped_column(Text, default="")


class TaskNote(Base):
    __tablename__ = "viz_notes"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    task_id: Mapped[int] = mapped_column(Integer, ForeignKey("viz_tasks.id", ondelete="CASCADE"))
    ts: Mapped[str] = mapped_column(String(32))
    text: Mapped[str] = mapped_column(Text)


class TaskEvent(Base):
    __tablename__ = "viz_events"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ts: Mapped[str] = mapped_column(String(32))
    event: Mapped[str] = mapped_column(String(64))
    message: Mapped[str] = mapped_column(Text, default="")
    meta_json: Mapped[str] = mapped_column(Text, default="{}")  # store JSON-serialized dict
