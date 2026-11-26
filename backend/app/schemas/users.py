
from pydantic import BaseModel, Field

from app.schemas.auth import UserResponse
from app.models.user import UserRole


class UserUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=100
    )


class UserRoleUpdate(BaseModel):
    role: UserRole


class UserListResponse(BaseModel):
    items: list[UserResponse]
    total: int
    page: int
    page_size: int
