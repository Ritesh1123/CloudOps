
from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.models.incident import (
    Incident,
    IncidentStatus,
    IncidentSeverity
)
from app.models.incident_comment import IncidentComment
from app.models.incident_history import IncidentHistory
from app.models.service import Service
from app.models.user import User, UserRole

from app.schemas.incidents import IncidentCreate


def get_incident_or_404(db: Session, incident_id: int):
    incident = db.get(Incident, incident_id)

    if not incident:
        raise HTTPException(
            status_code=404,
            detail="Incident not found"
        )

    return incident


def create_incident(
    db: Session,
    data: IncidentCreate,
    current_user: User
):
    service = db.get(Service, data.service_id)

    if not service or not service.is_active:
        raise HTTPException(
            status_code=404,
            detail="Active service not found"
        )

    incident = Incident(
        service_id=data.service_id,
        title=data.title.strip(),
        description=data.description.strip(),
        severity=data.severity,
        status=IncidentStatus.OPEN,
        created_by_id=current_user.id
    )

    db.add(incident)
    db.flush()

    history = IncidentHistory(
        incident_id=incident.id,
        user_id=current_user.id,
        old_status=None,
        new_status=IncidentStatus.OPEN.value
    )

    db.add(history)
    db.commit()
    db.refresh(incident)

    return incident


def list_incidents(
    db: Session,
    page: int = 1,
    page_size: int = 10,
    status_filter: IncidentStatus | None = None,
    severity_filter: IncidentSeverity | None = None
):
    if page < 1 or page_size < 1 or page_size > 100:
        raise HTTPException(
            status_code=400,
            detail="Invalid pagination values"
        )

    query = select(Incident)

    if status_filter:
        query = query.where(Incident.status == status_filter)

    if severity_filter:
        query = query.where(Incident.severity == severity_filter)

    total = db.scalar(
        select(func.count()).select_from(query.subquery())
    ) or 0

    incidents = db.scalars(
        query
        .order_by(Incident.opened_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()

    return {
        "items": incidents,
        "total": total,
        "page": page,
        "page_size": page_size
    }


def get_incident(db: Session, incident_id: int):
    return get_incident_or_404(db, incident_id)


def assign_incident(
    db: Session,
    incident_id: int,
    assigned_to_id: int
):
    incident = get_incident_or_404(db, incident_id)

    if incident.status == IncidentStatus.RESOLVED:
        raise HTTPException(
            status_code=400,
            detail="Cannot assign a resolved incident"
        )

    assignee = db.get(User, assigned_to_id)

    if (
        not assignee
        or not assignee.is_active
        or assignee.role not in (UserRole.ADMIN, UserRole.DEVELOPER)
    ):
        raise HTTPException(
            status_code=400,
            detail="Assignee must be an active Admin or Developer"
        )

    incident.assigned_to_id = assigned_to_id

    db.commit()
    db.refresh(incident)

    return incident


def update_incident_status(
    db: Session,
    incident_id: int,
    new_status: IncidentStatus,
    current_user: User
):
    incident = get_incident_or_404(db, incident_id)

    allowed_transitions = {
        IncidentStatus.OPEN: {
            IncidentStatus.ACKNOWLEDGED
        },
        IncidentStatus.ACKNOWLEDGED: {
            IncidentStatus.IN_PROGRESS
        },
        IncidentStatus.IN_PROGRESS: {
            IncidentStatus.RESOLVED
        }
    }

    if new_status not in allowed_transitions.get(incident.status, set()):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status transition: {incident.status.value} to {new_status.value}"
        )

    old_status = incident.status
    incident.status = new_status

    if new_status == IncidentStatus.RESOLVED:
        incident.resolved_at = datetime.now(timezone.utc)

    history = IncidentHistory(
        incident_id=incident.id,
        user_id=current_user.id,
        old_status=old_status.value,
        new_status=new_status.value
    )

    db.add(history)
    db.commit()
    db.refresh(incident)

    return incident


def add_incident_comment(
    db: Session,
    incident_id: int,
    comment_text: str,
    current_user: User
):
    incident = get_incident_or_404(db, incident_id)

    comment_text = comment_text.strip()

    if not comment_text:
        raise HTTPException(
            status_code=400,
            detail="Comment cannot be empty"
        )

    comment = IncidentComment(
        incident_id=incident.id,
        user_id=current_user.id,
        comment=comment_text
    )

    db.add(comment)
    db.commit()
    db.refresh(comment)

    return comment


def get_incident_comments(
    db: Session,
    incident_id: int
):
    get_incident_or_404(db, incident_id)

    return db.scalars(
        select(IncidentComment)
        .where(IncidentComment.incident_id == incident_id)
        .order_by(IncidentComment.created_at.asc())
    ).all()


def get_incident_history(
    db: Session,
    incident_id: int
):
    get_incident_or_404(db, incident_id)

    return db.scalars(
        select(IncidentHistory)
        .where(IncidentHistory.incident_id == incident_id)
        .order_by(IncidentHistory.changed_at.asc())
    ).all()
