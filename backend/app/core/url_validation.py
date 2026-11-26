
import ipaddress

from urllib.parse import urlsplit
from pydantic import HttpUrl


def validate_health_url(url: HttpUrl) -> HttpUrl:
    parsed = urlsplit(str(url))
    hostname = (parsed.hostname or "").lower()

    blocked_hosts = {
        "localhost",
        "metadata.google.internal",
    }

    if hostname in blocked_hosts:
        raise ValueError("This health-check URL is not allowed")

    if hostname.endswith((".local", ".internal")):
        raise ValueError("Internal hostnames are not allowed")

    try:
        ip = ipaddress.ip_address(hostname)
    except ValueError:
        ip = None

    if ip is not None and (
        ip.is_private
        or ip.is_loopback
        or ip.is_link_local
        or ip.is_reserved
        or ip.is_multicast
        or ip.is_unspecified
    ):
        raise ValueError(
            "Private or reserved IP addresses are not allowed"
        )
        # A hostname rather than an IP address is acceptable here.
        # DNS resolution and IP validation must happen again
        # immediately before the monitoring worker makes a request.

    return url
