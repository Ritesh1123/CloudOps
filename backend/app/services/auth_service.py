
from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status

from app.models.user import User, UserRole
from app.schemas.auth import UserRegister
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token
)


def register_user(
    db: Session,
    user_data: UserRegister
) -> User:

    email = str(user_data.email).lower()

    # Check whether email already exists
    existing_user = db.scalar(
        select(User).where(User.email == email)
    )

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )

    # Hash password
    hashed_password = hash_password(
        user_data.password
    )

    # Create user
    new_user = User(
        name=user_data.name.strip(),
        email=email,
        password_hash=hashed_password,
        role=UserRole.VIEWER,
        is_active=True
    )

    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )

    return new_user


def authenticate_user(
    db: Session,
    email: str,
    password: str
) -> tuple[User, str]:

    normalized_email = email.lower()

    # Find user
    user = db.scalar(
        select(User).where(
            User.email == normalized_email
        )
    )

    # Generic error prevents revealing whether an email exists
    if not user or not verify_password(
        password,
        user.password_hash
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive"
        )

    # Generate JWT
    access_token = create_access_token(
        data={
            "sub": str(user.id)
        }
    )

    return user, access_token
