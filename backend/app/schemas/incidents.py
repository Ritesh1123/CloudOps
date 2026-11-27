
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.incident import IncidentSeverity, IncidentStatus


class IncidentCreate(BaseModel):
    service_id: int = Field(gt=0)
    title: str = Field(min_length=3, max_length=200)
    description: str = Field(min_length=5)
    severity: IncidentSeverity = IncidentSeverity.MEDIUM


class IncidentAssign(BaseModel):
    assigned_to_id: int = Field(gt=0)


class IncidentStatusUpdate(BaseModel):
    status: IncidentStatus


class IncidentCommentCreate(BaseModel):
    comment: str = Field(min_length=1, max_length=5000)


class IncidentResponse(BaseModel):
    id: int
    service_id: int
    title: str
    description: str
    severity: IncidentSeverity
    status: IncidentStatus
    assigned_to_id: int | None
    created_by_id: int
    opened_at: datetime
    resolved_at: datetime | None
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class IncidentListResponse(BaseModel):
    items: list[IncidentResponse]
    total: int
    page: int
    page_size: int


class IncidentCommentResponse(BaseModel):
    id: int
    incident_id: int
    user_id: int
    comment: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class IncidentHistoryResponse(BaseModel):
    id: int
    incident_id: int
    user_id: int
    old_status: str | None
    new_status: str
    changed_at: datetime

    model_config = ConfigDict(from_attributes=True)
