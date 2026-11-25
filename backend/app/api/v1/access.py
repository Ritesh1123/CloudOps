
from fastapi import APIRouter, Depends

from app.models.user import User, UserRole
from app.core.dependencies import (
    get_current_user,
    require_roles
)


router = APIRouter(
    prefix="/access",
    tags=["Authorization"]
)


@router.get("/authenticated")
def authenticated_access(
    current_user: User = Depends(get_current_user)
):

    return {
        "message": "You are authenticated",
        "user": current_user.email,
        "role": current_user.role.value
    }


@router.get("/admin-only")
def admin_only(
    current_user: User = Depends(
        require_roles(UserRole.ADMIN)
    )
):

    return {
        "message": "Welcome Admin",
        "user": current_user.email
    }


@router.get("/developer-access")
def developer_access(
    current_user: User = Depends(
        require_roles(
            UserRole.ADMIN,
            UserRole.DEVELOPER
        )
    )
):

    return {
        "message": "Welcome Developer",
        "user": current_user.email,
        "role": current_user.role.value
    }


@router.get("/viewer-access")
def viewer_access(
    current_user: User = Depends(
        require_roles(
            UserRole.ADMIN,
            UserRole.DEVELOPER,
            UserRole.VIEWER
        )
    )
):

    return {
        "message": "You can view CloudOps resources",
        "user": current_user.email,
        "role": current_user.role.value
    }
