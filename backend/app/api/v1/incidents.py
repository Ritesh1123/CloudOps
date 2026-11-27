
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User, UserRole
from app.models.incident import IncidentStatus, IncidentSeverity

from app.core.dependencies import (
    get_current_user,
    require_roles
)

from app.schemas.incidents import (
    IncidentCreate,
    IncidentAssign,
    IncidentStatusUpdate,
    IncidentCommentCreate,
    IncidentResponse,
    IncidentListResponse,
    IncidentCommentResponse,
    IncidentHistoryResponse
)

from app.services.incident_service import (
    create_incident,
    list_incidents,
    get_incident,
    assign_incident,
    update_incident_status,
    add_incident_comment,
    get_incident_comments,
    get_incident_history
)


router = APIRouter(
    prefix="/incidents",
    tags=["Incident Management"]
)


@router.post(
    "",
    response_model=IncidentResponse,
    status_code=status.HTTP_201_CREATED
)
def create_new_incident(
    data: IncidentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(UserRole.ADMIN, UserRole.DEVELOPER)
    )
):
    return create_incident(db, data, current_user)


@router.get(
    "",
    response_model=IncidentListResponse
)
def get_all_incidents(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    incident_status: IncidentStatus | None = Query(default=None, alias="status"),
    severity: IncidentSeverity | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return list_incidents(
        db,
        page,
        page_size,
        incident_status,
        severity
    )


@router.get(
    "/{incident_id}",
    response_model=IncidentResponse
)
def get_incident_details(
    incident_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_incident(db, incident_id)


@router.patch(
    "/{incident_id}/assign",
    response_model=IncidentResponse
)
def assign_incident_to_user(
    incident_id: int,
    data: IncidentAssign,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(UserRole.ADMIN, UserRole.DEVELOPER)
    )
):
    return assign_incident(
        db,
        incident_id,
        data.assigned_to_id
    )


@router.patch(
    "/{incident_id}/status",
    response_model=IncidentResponse
)
def change_incident_status(
    incident_id: int,
    data: IncidentStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(UserRole.ADMIN, UserRole.DEVELOPER)
    )
):
    return update_incident_status(
        db,
        incident_id,
        data.status,
        current_user
    )


@router.post(
    "/{incident_id}/comments",
    response_model=IncidentCommentResponse,
    status_code=status.HTTP_201_CREATED
)
def create_incident_comment(
    incident_id: int,
    data: IncidentCommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return add_incident_comment(
        db,
        incident_id,
        data.comment,
        current_user
    )


@router.get(
    "/{incident_id}/comments",
    response_model=list[IncidentCommentResponse]
)
def list_incident_comments(
    incident_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_incident_comments(db, incident_id)


@router.get(
    "/{incident_id}/history",
    response_model=list[IncidentHistoryResponse]
)
def list_incident_history(
    incident_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_incident_history(db, incident_id)
