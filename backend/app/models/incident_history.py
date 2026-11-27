
from datetime import datetime

from sqlalchemy import (
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    Integer,
    func
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.incident import IncidentStatus
from sqlalchemy import String


class IncidentHistory(Base):
    __tablename__ = "incident_history"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    incident_id: Mapped[int] = mapped_column(
        ForeignKey("incidents.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False
    )

    old_status: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True
    )

    new_status: Mapped[str] = mapped_column(
        String(30),
        nullable=False
    )

    changed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
