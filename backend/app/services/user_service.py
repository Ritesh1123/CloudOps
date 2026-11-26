
from fastapi import HTTPException
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.models.user import User, UserRole
from app.schemas.users import UserUpdate


def get_users(db: Session, page: int = 1, page_size: int = 10):
    if page < 1 or page_size < 1 or page_size > 100:
        raise HTTPException(
            status_code=400,
            detail="Invalid pagination values"
        )

    total = db.scalar(
        select(func.count()).select_from(User)
    ) or 0

    users = db.scalars(
        select(User)
        .order_by(User.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()

    return {
        "items": users,
        "total": total,
        "page": page,
        "page_size": page_size
    }


def get_user_by_id(db: Session, user_id: int):
    user = db.get(User, user_id)

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return user


def update_user(
    db: Session,
    user_id: int,
    user_data: UserUpdate
):
    user = get_user_by_id(db, user_id)

    if "name" not in user_data.model_fields_set:
        raise HTTPException(
            status_code=400,
            detail="No update fields provided"
        )

    if user_data.name is None:
        raise HTTPException(
            status_code=400,
            detail="Name cannot be null"
        )

    user.name = user_data.name.strip()

    if not user.name:
        raise HTTPException(
            status_code=400,
            detail="Name cannot be empty"
        )

    db.commit()
    db.refresh(user)

    return user


def update_user_role(
    db: Session,
    user_id: int,
    new_role: UserRole,
    current_admin: User
):
    user = get_user_by_id(db, user_id)

    # Prevent an admin from accidentally removing their own admin access.
    if user.id == current_admin.id:
        raise HTTPException(
            status_code=400,
            detail="You cannot change your own role"
        )

    user.role = new_role
    db.commit()
    db.refresh(user)

    return user


def deactivate_user(
    db: Session,
    user_id: int,
    current_admin: User
):
    user = get_user_by_id(db, user_id)

    if user.id == current_admin.id:
        raise HTTPException(
            status_code=400,
            detail="You cannot deactivate your own account"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=400,
            detail="User is already inactive"
        )

    # Do not allow the last active admin to be deactivated.
    if user.role == UserRole.ADMIN:
        active_admins = db.scalar(
            select(func.count())
            .select_from(User)
            .where(
                User.role == UserRole.ADMIN,
                User.is_active.is_(True)
            )
        ) or 0

        if active_admins <= 1:
            raise HTTPException(
                status_code=400,
                detail="Cannot deactivate the last active admin"
            )

    user.is_active = False
    db.commit()
    db.refresh(user)

    return user
