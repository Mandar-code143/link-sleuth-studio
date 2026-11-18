"""URL validation and normalization with strict security boundaries against SSRF."""

import ipaddress
import re
from urllib.parse import urlparse, urlunparse
from typing import Tuple


LOCAL_HOSTNAMES = {
    "localhost",
    "localhost.localdomain",
    "local",
    "broadcasthost",
    "loopback",
}

BLOCKED_TLD_SUFFIXES = (
    ".local",
    ".localhost",
    ".internal",
    ".lan",
    ".home",
    ".corp",
    ".test",
    ".example",
    ".invalid",
)


class URLValidationError(ValueError):
    """Raised when a URL fails security or structural validation."""
    pass


def validate_and_normalize_url(raw_url: str) -> Tuple[str, str, int]:
    """
    Validates a URL for safe public fetching.
    
    Returns:
        Tuple of (normalized_url, hostname, port)
    
    Raises:
        URLValidationError if URL is malformed, has invalid scheme, credentials,
        or targets a prohibited destination.
    """
    if not raw_url or not isinstance(raw_url, str):
        raise URLValidationError("URL must be a non-empty string.")

    cleaned = raw_url.strip()
    if len(cleaned) > 2048:
        raise URLValidationError("URL exceeds maximum permitted length of 2048 characters.")

    try:
        parsed = urlparse(cleaned)
    except Exception as e:
        raise URLValidationError(f"Invalid URL structure: {e}")

    scheme = (parsed.scheme or "").lower()
    if scheme not in ("http", "https"):
        raise URLValidationError(f"Prohibited URL scheme '{scheme}'. Only HTTP and HTTPS are permitted.")

    if parsed.username or parsed.password:
        raise URLValidationError("URLs containing embedded credentials (user:password@) are prohibited.")

    hostname = parsed.hostname
    if not hostname:
        raise URLValidationError("URL must include a valid hostname.")

    hostname_clean = hostname.lower().rstrip(".")

    # Reject local hostnames
    if hostname_clean in LOCAL_HOSTNAMES:
        raise URLValidationError(f"Prohibited target hostname '{hostname_clean}'. Internal addresses cannot be fetched.")

    # Reject local/internal TLDs
    if any(hostname_clean.endswith(suffix) for suffix in BLOCKED_TLD_SUFFIXES):
        raise URLValidationError(f"Prohibited private domain suffix in '{hostname_clean}'.")

    # Check if hostname is an IP literal
    is_ip = False
    ip_obj = None
    try:
        # Strip brackets if IPv6
        ip_str = hostname_clean.strip("[]")
        ip_obj = ipaddress.ip_address(ip_str)
        is_ip = True
    except ValueError:
        is_ip = False

    if is_ip and ip_obj:
        # Check against private / loopback IP address ranges
        if (
            ip_obj.is_loopback
            or ip_obj.is_private
            or ip_obj.is_link_local
            or ip_obj.is_multicast
            or ip_obj.is_unspecified
            or ip_obj.is_reserved
        ):
            raise URLValidationError(f"Direct IP target '{ip_obj}' is a prohibited non-public network address.")
        
        # Check for IPv4-mapped IPv6 (e.g. ::ffff:127.0.0.1)
        if isinstance(ip_obj, ipaddress.IPv6Address) and ip_obj.ipv4_mapped:
            mapped = ip_obj.ipv4_mapped
            if (
                mapped.is_loopback
                or mapped.is_private
                or mapped.is_link_local
                or mapped.is_multicast
                or mapped.is_unspecified
            ):
                raise URLValidationError(f"IPv4-mapped IPv6 target '{ip_obj}' resolves to prohibited address '{mapped}'.")
    else:
        # Not an IP literal, it's a domain name
        # Validate hostname syntax
        if not re.match(r"^[a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?(\.[a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?)*$", hostname_clean):
            # Check for IDN (punycode)
            try:
                hostname_clean = hostname_clean.encode("idna").decode("ascii")
            except Exception:
                raise URLValidationError(f"Malformed or invalid domain name '{hostname}'.")

    # Determine default port
    port = parsed.port or (443 if scheme == "https" else 80)
    if port not in (80, 443, 8080, 8443):
        # We permit standard web ports
        raise URLValidationError(f"Non-standard web port '{port}' is not permitted.")

    # Reconstruct clean normalized URL
    netloc = hostname_clean
    if parsed.port and parsed.port not in (80, 443):
        netloc = f"{netloc}:{parsed.port}"

    path = parsed.path or "/"
    normalized = urlunparse((scheme, netloc, path, parsed.params, parsed.query, ""))

    return normalized, hostname_clean, port
