
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User, UserRole
from app.schemas.auth import UserResponse
from app.schemas.users import (
    UserUpdate,
    UserRoleUpdate,
    UserListResponse
)
from app.core.dependencies import (
    get_current_user,
    require_roles
)
from app.services.user_service import (
    get_users,
    get_user_by_id,
    update_user,
    update_user_role,
    deactivate_user
)


router = APIRouter(prefix="/users", tags=["User Management"])


@router.get("", response_model=UserListResponse)
def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_admin: User = Depends(
        require_roles(UserRole.ADMIN)
    )
):
    return get_users(db, page, page_size)


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(
        require_roles(UserRole.ADMIN)
    )
):
    return get_user_by_id(db, user_id)


@router.patch("/{user_id}", response_model=UserResponse)
def edit_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(
        require_roles(UserRole.ADMIN)
    )
):
    return update_user(db, user_id, user_data)


@router.patch("/{user_id}/role", response_model=UserResponse)
def change_user_role(
    user_id: int,
    role_data: UserRoleUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(
        require_roles(UserRole.ADMIN)
    )
):
    return update_user_role(
        db,
        user_id,
        role_data.role,
        current_admin
    )


@router.patch("/{user_id}/deactivate", response_model=UserResponse)
def deactivate_user_account(
    user_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(
        require_roles(UserRole.ADMIN)
    )
):
    return deactivate_user(db, user_id, current_admin)
