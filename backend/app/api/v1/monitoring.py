
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User, UserRole
from app.core.dependencies import (
    get_current_user,
    require_roles
)

from app.schemas.health_checks import (
    HealthCheckResponse,
    HealthCheckListResponse
)

from app.services.monitoring_service import (
    run_health_check,
    get_health_check_history
)


router = APIRouter(
    prefix="/services",
    tags=["Service Monitoring"]
)


@router.post(
    "/{service_id}/check",
    response_model=HealthCheckResponse,
    status_code=status.HTTP_201_CREATED
)
def trigger_health_check(
    service_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(UserRole.ADMIN, UserRole.DEVELOPER)
    )
):
    return run_health_check(db, service_id)


@router.get(
    "/{service_id}/checks",
    response_model=HealthCheckListResponse
)
def list_health_checks(
    service_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_health_check_history(
        db,
        service_id,
        page,
        page_size
    )
