
from datetime import datetime, timedelta, timezone

from jose import jwt, JWTError
from pwdlib import PasswordHash

from app.core.config import settings


# Argon2 password hashing
password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    """
    Convert plain-text password into a secure Argon2 hash.
    """

    return password_hash.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str
) -> bool:
    """
    Verify plain-text password against stored hash.
    """

    return password_hash.verify(
        plain_password,
        hashed_password
    )


def create_access_token(data: dict) -> str:
    """
    Generate a signed JWT access token.
    """

    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    to_encode.update({
        "exp": expire
    })

    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )

    return encoded_jwt


def decode_access_token(token: str) -> dict:
    """
    Decode and validate JWT token.
    Raises ValueError if token is invalid or expired.
    """

    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )

        user_id = payload.get("sub")

        if not isinstance(user_id, str) or not user_id:
            raise ValueError("Invalid token subject")

        return payload

    except JWTError as exc:
        raise ValueError("Invalid or expired token") from exc
