
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User, UserRole
from app.schemas.services import (
    ServiceCreate,
    ServiceUpdate,
    ServiceResponse,
    ServiceListResponse
)
from app.core.dependencies import (
    get_current_user,
    require_roles
)
from app.services.service_service import (
    create_service,
    get_services,
    get_service_by_id,
    update_service,
    deactivate_service
)


router = APIRouter(
    prefix="/services",
    tags=["Service Management"]
)


@router.post(
    "",
    response_model=ServiceResponse,
    status_code=status.HTTP_201_CREATED
)
def register_service(
    service_data: ServiceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(UserRole.ADMIN, UserRole.DEVELOPER)
    )
):
    return create_service(db, service_data, current_user)


@router.get(
    "",
    response_model=ServiceListResponse
)
def list_services(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    environment: str | None = Query(
        default=None,
        pattern="^(DEVELOPMENT|STAGING|PRODUCTION)$"
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_services(db, page, page_size, environment)


@router.get(
    "/{service_id}",
    response_model=ServiceResponse
)
def service_details(
    service_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_service_by_id(db, service_id)


@router.patch(
    "/{service_id}",
    response_model=ServiceResponse
)
def edit_service(
    service_id: int,
    service_data: ServiceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(UserRole.ADMIN, UserRole.DEVELOPER)
    )
):
    return update_service(db, service_id, service_data)


@router.delete(
    "/{service_id}",
    response_model=ServiceResponse
)
def remove_service(
    service_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(UserRole.ADMIN)
    )
):
    return deactivate_service(db, service_id)
