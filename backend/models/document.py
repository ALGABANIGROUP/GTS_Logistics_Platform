from __future__ import annotations

from datetime import datetime
from typing import Optional, TYPE_CHECKING

from sqlalchemy import Integer, String, DateTime, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.database.base import Base

if TYPE_CHECKING:
    from backend.models.user import User


class Document(Base):
    __tablename__: str = "documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    file_url: Mapped[str] = mapped_column(String(512), nullable=False)
    file_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    notify_before_days: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    owner_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    owner: Mapped["User"] = relationship(
        "User",
        # back_populates="documents",  # Disabled - User.documents is commented out
        lazy="select",
        passive_deletes=True,
    )

    def __repr__(self) -> str:
        return f"<Document id={self.id} title={self.title} owner_id={self.owner_id}>"

