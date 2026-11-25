
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import (
    UserRegister,
    UserLogin,
    UserResponse,
    TokenResponse
)
from app.core.dependencies import get_current_user
from app.services.auth_service import (
    register_user,
    authenticate_user
)


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
def register(
    user_data: UserRegister,
    db: Session = Depends(get_db)
):

    user = register_user(
        db,
        user_data
    )

    return user


@router.post(
    "/login",
    response_model=TokenResponse
)
def login(
    login_data: UserLogin,
    db: Session = Depends(get_db)
):

    user, access_token = authenticate_user(
        db,
        str(login_data.email),
        login_data.password
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer"
    )


@router.get(
    "/me",
    response_model=UserResponse
)
def get_my_profile(
    current_user: User = Depends(get_current_user)
):

    return current_user


@router.post("/logout")
def logout(
    current_user: User = Depends(get_current_user)
):

    return {
        "message": "Logout successful. Please discard your access token."
    }
