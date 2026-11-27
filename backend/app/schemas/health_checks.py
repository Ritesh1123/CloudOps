
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.service import ServiceStatus


class HealthCheckResponse(BaseModel):
    id: int
    service_id: int
    status: ServiceStatus
    status_code: int | None
    latency_ms: float | None
    error_message: str | None
    checked_at: datetime

    model_config = ConfigDict(from_attributes=True)


class HealthCheckListResponse(BaseModel):
    items: list[HealthCheckResponse]
    total: int
    page: int
    page_size: int
