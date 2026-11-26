
from fastapi import HTTPException
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.models.service import Service, ServiceStatus
from app.models.user import User
from app.schemas.services import ServiceCreate, ServiceUpdate


def create_service(
    db: Session,
    service_data: ServiceCreate,
    current_user: User
):
    new_service = Service(
        name=service_data.name.strip(),
        health_url=str(service_data.health_url),
        environment=service_data.environment,
        check_interval_seconds=service_data.check_interval_seconds,
        timeout_seconds=service_data.timeout_seconds,
        current_status=ServiceStatus.UNKNOWN,
        consecutive_failures=0,
        is_active=True,
        created_by_id=current_user.id
    )

    db.add(new_service)
    db.commit()
    db.refresh(new_service)

    return new_service


def get_services(
    db: Session,
    page: int = 1,
    page_size: int = 10,
    environment: str | None = None
):
    if page < 1 or page_size < 1 or page_size > 100:
        raise HTTPException(
            status_code=400,
            detail="Invalid pagination values"
        )

    query = select(Service).where(Service.is_active.is_(True))

    if environment:
        query = query.where(Service.environment == environment)

    total_query = select(func.count()).select_from(query.subquery())
    total = db.scalar(total_query) or 0

    services = db.scalars(
        query
        .order_by(Service.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()

    return {
        "items": services,
        "total": total,
        "page": page,
        "page_size": page_size
    }


def get_service_by_id(db: Session, service_id: int):
    service = db.get(Service, service_id)

    if not service or not service.is_active:
        raise HTTPException(
            status_code=404,
            detail="Service not found"
        )

    return service


def update_service(
    db: Session,
    service_id: int,
    service_data: ServiceUpdate
):
    service = get_service_by_id(db, service_id)

    updates = service_data.model_dump(exclude_unset=True)

    if not updates:
        raise HTTPException(
            status_code=400,
            detail="No update fields provided"
        )

    for field, value in updates.items():
        if value is None:
            raise HTTPException(
                status_code=400,
                detail=f"{field} cannot be null"
            )

        if field == "name":
            value = value.strip()

            if not value:
                raise HTTPException(
                    status_code=400,
                    detail="Name cannot be empty"
                )

        if field == "health_url":
            value = str(value)

        setattr(service, field, value)

    db.commit()
    db.refresh(service)

    return service


def deactivate_service(db: Session, service_id: int):
    service = get_service_by_id(db, service_id)

    # Soft deletion preserves service history for future analytics.
    service.is_active = False

    db.commit()
    db.refresh(service)

    return service
