
from collections.abc import Callable

from fastapi import Depends, HTTPException, status
from fastapi.security import (
    HTTPBearer,
    HTTPAuthorizationCredentials
)

from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User, UserRole
from app.core.security import decode_access_token


# Extract Bearer token from Authorization header
bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(
        bearer_scheme
    ),
    db: Session = Depends(get_db)
) -> User:

    # Check whether token exists
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"}
        )

    token = credentials.credentials

    # Decode JWT
    try:
        payload = decode_access_token(token)

        user_id = int(payload["sub"])

    except (ValueError, KeyError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # Fetch user from database
    user = db.get(User, user_id)

    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
            headers={"WWW-Authenticate": "Bearer"}
        )

    return user


def require_roles(
    *allowed_roles: UserRole
) -> Callable:

    def role_checker(
        current_user: User = Depends(get_current_user)
    ) -> User:

        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this resource"
            )

        return current_user

    return role_checker
