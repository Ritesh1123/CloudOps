
from datetime import datetime
from sqlalchemy import Float

from sqlalchemy import (
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    Integer,
    String,
    func
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.service import ServiceStatus


class HealthCheck(Base):
    __tablename__ = "health_checks"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    service_id: Mapped[int] = mapped_column(
        ForeignKey("services.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    status: Mapped[ServiceStatus] = mapped_column(
        SQLEnum(ServiceStatus, name="health_check_status"),
        nullable=False
    )

    status_code: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )

    latency_ms: Mapped[float | None] = mapped_column(
    Float,
    nullable=True
    )

    error_message: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True
    )

    checked_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
