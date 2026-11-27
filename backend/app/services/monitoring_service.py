
import ipaddress
import socket
import time

import httpx

from fastapi import HTTPException
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from app.models.service import Service, ServiceStatus
from app.models.health_check import HealthCheck


def validate_public_destination(url: str):
    """
    Development-stage SSRF preflight.
    Only public DNS destinations are allowed.
    Production monitoring needs DNS-pinned connections
    and network-level egress restrictions as well.
    """
    from urllib.parse import urlsplit

    parsed = urlsplit(url)

    if parsed.scheme != "https":
        raise ValueError("Only HTTPS health URLs are allowed")

    hostname = parsed.hostname

    if not hostname:
        raise ValueError("Invalid health URL")

    try:
        addresses = socket.getaddrinfo(
            hostname,
            parsed.port or 443,
            type=socket.SOCK_STREAM
        )
    except socket.gaierror as exc:
        raise ValueError("Health URL hostname could not be resolved") from exc

    if not addresses:
        raise ValueError("No destination addresses found")

    for address in addresses:
        ip = ipaddress.ip_address(address[4][0])

        if not ip.is_global:
            raise ValueError("Health URL must resolve to public IP addresses")


def run_health_check(db: Session, service_id: int):
    service = db.get(Service, service_id)

    if service is None or not service.is_active:
        raise HTTPException(
            status_code=404,
            detail="Active service not found"
        )

    status_code = None
    latency_ms = None
    error_message = None

    try:
        validate_public_destination(service.health_url)

        start_time = time.perf_counter()

        with httpx.Client(
            timeout=service.timeout_seconds,
            follow_redirects=False
        ) as client:
            response = client.get(service.health_url)

        latency_ms = round(
            (time.perf_counter() - start_time) * 1000,
            2
        )

        status_code = response.status_code

        if 200 <= status_code < 300:
            check_status = ServiceStatus.UP
        else:
            check_status = ServiceStatus.DOWN
            error_message = f"HTTP response: {status_code}"

    except (ValueError, httpx.HTTPError) as exc:
        check_status = ServiceStatus.DOWN
        error_message = str(exc)[:500]

    checked_at = datetime.now(timezone.utc)

    health_check = HealthCheck(
        service_id=service.id,
        status=check_status,
        status_code=status_code,
        latency_ms=latency_ms,
        error_message=error_message
    )

    db.add(health_check)

    service.current_status = check_status
    service.last_checked_at = health_check.checked_at

    if check_status == ServiceStatus.UP:
        service.consecutive_failures = 0
    else:
        service.consecutive_failures += 1

    db.commit()
    db.refresh(health_check)

    return health_check


def get_health_check_history(
    db: Session,
    service_id: int,
    page: int = 1,
    page_size: int = 10
):
    service = db.get(Service, service_id)

    if service is None:
        raise HTTPException(
            status_code=404,
            detail="Service not found"
        )

    if page < 1 or page_size < 1 or page_size > 100:
        raise HTTPException(
            status_code=400,
            detail="Invalid pagination values"
        )

    query = select(HealthCheck).where(
        HealthCheck.service_id == service_id
    )

    total = db.scalar(
        select(func.count()).select_from(
            query.subquery()
        )
    ) or 0

    records = db.scalars(
        query
        .order_by(HealthCheck.checked_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()

    return {
        "items": records,
        "total": total,
        "page": page,
        "page_size": page_size
    }
