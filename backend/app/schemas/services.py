
from typing import Literal
from datetime import datetime
from app.core.url_validation import validate_health_url

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    HttpUrl,
    field_validator
)

from app.models.service import ServiceStatus


Environment = Literal[
    "DEVELOPMENT",
    "STAGING",
    "PRODUCTION"
]


class ServiceCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    health_url: HttpUrl
    environment: Environment

    check_interval_seconds: int = Field(
        default=60,
        ge=30,
        le=3600
    )

    timeout_seconds: int = Field(
        default=10,
        ge=1,
        le=60
    )

    @field_validator("health_url")
    @classmethod
    def check_health_url(cls, value):
        if value is not None:
            return validate_health_url(value)
        return value


class ServiceUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=100
    )

    health_url: HttpUrl | None = None
    environment: Environment | None = None

    check_interval_seconds: int | None = Field(
        default=None,
        ge=30,
        le=3600
    )

    timeout_seconds: int | None = Field(
        default=None,
        ge=1,
        le=60
    )

    @field_validator("health_url")
    @classmethod
    def check_health_url(cls, value):
        if value is not None:
            return validate_health_url(value)
        return value


class ServiceResponse(BaseModel):
    id: int
    name: str
    health_url: str
    environment: str
    check_interval_seconds: int
    timeout_seconds: int
    current_status: ServiceStatus
    consecutive_failures: int
    is_active: bool
    created_by_id: int
    last_checked_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ServiceListResponse(BaseModel):
    items: list[ServiceResponse]
    total: int
    page: int
    page_size: int
