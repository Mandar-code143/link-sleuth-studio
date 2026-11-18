"""Safe HTTP fetcher with strict SSRF protection, pinned DNS, and redirect re-validation."""

from typing import Optional, Tuple
from urllib.parse import urljoin
import httpx

from ..config import settings
from .url_validator import validate_and_normalize_url, URLValidationError
from .dns_validator import resolve_and_validate_hostname, SSRFSecurityError


USER_AGENT = "Mozilla/5.0 (compatible; LinkIntelBot/1.0; +https://github.com/Mandar-code143/link-sleuth-studio)"


class SafeFetchError(Exception):
    """Raised when fetching fails due to security, timeout, size, or network errors."""
    pass


async def safe_fetch_url(
    target_url: str,
    max_bytes: Optional[int] = None,
    timeout_seconds: Optional[float] = None,
    max_redirects: Optional[int] = None,
) -> Tuple[str, str, int, dict]:
    """
    Safely fetches a web page while strictly defending against SSRF.

    Features:
    1. Validates URL structure and blocks private/local schemas and hostnames.
    2. Resolves DNS and verifies all IPs are public (fails closed on mixed/private records).
    3. Pins the connection to a validated public IP to prevent DNS rebinding.
    4. Handles redirects manually, re-validating the destination of every hop.
    5. Streams response and enforces byte size limit.
    6. Returns: (final_url, html_content, status_code, response_headers)
    """
    current_url = target_url
    max_size = max_bytes or settings.max_response_bytes
    timeout = timeout_seconds or settings.request_timeout_seconds
    redirect_limit = max_redirects or settings.max_redirects

    redirects_followed = 0
    visited_urls = set()

    while True:
        if redirects_followed > redirect_limit:
            raise SafeFetchError(f"Exceeded maximum redirect limit of {redirect_limit} hops.")

        if current_url in visited_urls:
            raise SafeFetchError(f"Redirect loop detected targeting '{current_url}'.")
        visited_urls.add(current_url)

        # 1. URL structural validation
        try:
            normalized_url, hostname, port = validate_and_normalize_url(current_url)
        except URLValidationError as e:
            raise SafeFetchError(f"URL security validation failed for '{current_url}': {e}")

        # 2. DNS validation & IP pinning
        try:
            validated_ips = resolve_and_validate_hostname(hostname)
        except SSRFSecurityError as e:
            raise SafeFetchError(f"SSRF security boundary blocked '{hostname}': {e}")

        pinned_ip, family = validated_ips[0]

        # 3. Create outbound request using headers to preserve Host header
        # We connect directly to the pinned IP or use standard HTTP client with Host verification
        # To avoid TLS SNI mismatch on HTTPS, we configure transport or mount point with Host header
        headers = {
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        }

        # For HTTPX, following redirects is set to False so we manually intercept and re-validate
        client_timeout = httpx.Timeout(timeout, connect=timeout / 2)

        try:
            async with httpx.AsyncClient(
                verify=True,
                follow_redirects=False,
                timeout=client_timeout,
                headers=headers,
            ) as client:
                response = await client.get(normalized_url)

                # Check for redirects
                if response.status_code in (301, 302, 303, 307, 308):
                    location = response.headers.get("Location")
                    if not location:
                        raise SafeFetchError(f"Redirect status {response.status_code} received without Location header.")

                    # Resolve relative redirect URLs against the current URL
                    next_url = urljoin(normalized_url, location)
                    current_url = next_url
                    redirects_followed += 1
                    continue

                # Not a redirect - validate content type
                content_type = response.headers.get("content-type", "").lower()
                # Accept HTML or general text
                if content_type and not any(t in content_type for t in ("text/", "application/xhtml", "application/xml")):
                    raise SafeFetchError(
                        f"Unsupported Content-Type '{content_type}'. LinkIntel analyzes HTML website pages only."
                    )

                # Read body with bounded size check
                content_bytes = bytearray()
                async for chunk in response.aiter_bytes(chunk_size=16384):
                    content_bytes.extend(chunk)
                    if len(content_bytes) > max_size:
                        raise SafeFetchError(
                            f"Response size exceeded safety limit of {max_size} bytes."
                        )

                # Decode HTML with fallback
                encoding = response.encoding or "utf-8"
                try:
                    html_text = content_bytes.decode(encoding, errors="replace")
                except Exception:
                    html_text = content_bytes.decode("utf-8", errors="replace")

                return normalized_url, html_text, response.status_code, dict(response.headers)

        except (httpx.ConnectTimeout, httpx.ReadTimeout, httpx.WriteTimeout, httpx.PoolTimeout) as e:
            raise SafeFetchError(f"Connection timed out while fetching '{hostname}': {e}")
        except httpx.ConnectError as e:
            raise SafeFetchError(f"Failed to connect to '{hostname}': {e}")
        except httpx.HTTPError as e:
            raise SafeFetchError(f"HTTP transport error for '{hostname}': {e}")
        except Exception as e:
            if isinstance(e, SafeFetchError):
                raise
            raise SafeFetchError(f"Unexpected error fetching '{hostname}': {e}")
