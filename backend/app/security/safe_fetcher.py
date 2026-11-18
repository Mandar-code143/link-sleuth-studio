"""Safe HTTP fetcher with true connection-level DNS pinning, streaming byte bounding, and redirect re-validation."""

import asyncio
from typing import Optional, Tuple
from urllib.parse import urljoin
import httpcore
import httpx

from ..config import settings
from .url_validator import validate_and_normalize_url, URLValidationError
from .dns_validator import resolve_and_validate_hostname, SSRFSecurityError


USER_AGENT = "Mozilla/5.0 (compatible; LinkIntelBot/1.0; +https://github.com/Mandar-code143/link-sleuth-studio)"


class SafeFetchError(Exception):
    """Raised when fetching fails due to security, timeout, size, or network errors."""
    pass


class PinnedAsyncNetworkBackend(httpcore.AsyncNetworkBackend):
    """
    Custom network backend for httpcore that routes outbound TCP connections
    directly to a pre-validated public IP address while preserving the original
    hostname for HTTP Host headers and TLS Server Name Indication (SNI).
    """

    def __init__(self, target_hostname: str, pinned_ip: str):
        self._target_hostname = target_hostname.lower()
        self._pinned_ip = pinned_ip
        self._backend = httpcore._backends.auto.AutoBackend()

    async def connect_tcp(
        self,
        host: str,
        port: int,
        timeout: Optional[float] = None,
        local_address: Optional[str] = None,
        socket_options = None,
    ) -> httpcore.AsyncNetworkStream:
        # Route socket explicitly to the validated pinned IP
        return await self._backend.connect_tcp(
            host=self._pinned_ip,
            port=port,
            timeout=timeout,
            local_address=local_address,
            socket_options=socket_options,
        )

    async def connect_unix_socket(self, *args, **kwargs):
        raise SafeFetchError("Unix domain socket connection is prohibited.")

    async def sleep(self, seconds: float) -> None:
        await self._backend.sleep(seconds)


class PinnedAsyncHTTPTransport(httpx.AsyncHTTPTransport):
    """
    Hardened HTTPX transport enforcing connection-level DNS pinning.
    Guarantees no secondary, uncontrolled DNS resolution occurs during the TCP handshake.
    """

    def __init__(self, pinned_ip: str, target_hostname: str, **kwargs):
        super().__init__(**kwargs)
        backend = PinnedAsyncNetworkBackend(
            target_hostname=target_hostname,
            pinned_ip=pinned_ip,
        )
        self._pool = httpcore.AsyncConnectionPool(
            ssl_context=self._pool._ssl_context,
            max_connections=1,
            max_keepalive_connections=0,
            network_backend=backend,
            retries=0,
        )


async def safe_fetch_url(
    target_url: str,
    max_bytes: Optional[int] = None,
    timeout_seconds: Optional[float] = None,
    max_redirects: Optional[int] = None,
) -> Tuple[str, str, int, dict]:
    """
    Safely fetches a web page while strictly defending against SSRF.

    Security Guarantees:
    1. Validates URL scheme (strictly http/https) and rejects credentials or private TLDs.
    2. Resolves DNS asynchronously and validates all returned IPs against prohibited ranges (fails closed).
    3. Pins the TCP connection directly to the pre-validated IP via PinnedAsyncHTTPTransport.
    4. Follows redirects manually, strictly re-validating each hop's scheme, hostname, and DNS.
    5. Detects circular redirect loops and enforces hop bounds.
    6. Streams bytes with chunk-by-chunk accumulation, enforcing the maximum size limit before buffering.
    7. Validates Content-Type to reject binary payloads or zip bombs.

    Returns:
        Tuple of (final_url, html_text, status_code, response_headers)
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

        # 1. URL structural and scheme validation
        try:
            normalized_url, hostname, port = validate_and_normalize_url(current_url)
        except URLValidationError as e:
            raise SafeFetchError(f"URL security validation failed for '{current_url}': {e}")

        # 2. DNS resolution and strict IP range check (fails closed on mixed records)
        try:
            validated_ips = await asyncio.to_thread(resolve_and_validate_hostname, hostname)
        except SSRFSecurityError as e:
            raise SafeFetchError(f"SSRF security boundary blocked '{hostname}': {e}")

        pinned_ip, _ = validated_ips[0]

        # 3. Connection-level pinned transport
        transport = PinnedAsyncHTTPTransport(pinned_ip=pinned_ip, target_hostname=hostname)

        headers = {
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        }

        client_timeout = httpx.Timeout(timeout, connect=min(timeout / 2, 5.0))

        try:
            async with httpx.AsyncClient(
                transport=transport,
                verify=True,
                follow_redirects=False,
                timeout=client_timeout,
                headers=headers,
            ) as client:
                async with client.stream("GET", normalized_url) as response:
                    # Check for redirects (manual hop interception)
                    if response.status_code in (301, 302, 303, 307, 308):
                        location = response.headers.get("Location")
                        if not location:
                            raise SafeFetchError(
                                f"Redirect status {response.status_code} received without Location header."
                            )

                        # Resolve relative redirect URLs against the current URL
                        next_url = urljoin(normalized_url, location)
                        current_url = next_url
                        redirects_followed += 1
                        continue

                    # Check Content-Length before downloading full body
                    cl_header = response.headers.get("content-length")
                    if cl_header:
                        try:
                            content_len = int(cl_header)
                            if content_len > max_size:
                                raise SafeFetchError(
                                    f"Response Content-Length {content_len} bytes exceeds safety limit of {max_size} bytes."
                                )
                        except ValueError:
                            pass

                    # Content-Type validation
                    content_type = response.headers.get("content-type", "").lower()
                    if content_type and not any(
                        t in content_type for t in ("text/", "application/xhtml", "application/xml", "application/json")
                    ):
                        raise SafeFetchError(
                            f"Unsupported Content-Type '{content_type}'. LinkIntel analyzes HTML website pages only."
                        )

                    # Stream body with strict chunk-by-chunk byte accumulation
                    content_bytes = bytearray()
                    async for chunk in response.aiter_bytes(chunk_size=16384):
                        content_bytes.extend(chunk)
                        if len(content_bytes) > max_size:
                            raise SafeFetchError(
                                f"Response size exceeded safety limit of {max_size} bytes."
                            )

                    # Status code evaluation
                    if response.status_code >= 400:
                        raise SafeFetchError(
                            f"HTTP {response.status_code} returned by '{hostname}'. Cannot analyze error page."
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
            raise SafeFetchError(f"Failed to connect to '{hostname}' at pinned IP {pinned_ip}: {e}")
        except httpx.HTTPError as e:
            raise SafeFetchError(f"HTTP transport error for '{hostname}': {e}")
        except Exception as e:
            if isinstance(e, SafeFetchError):
                raise
            raise SafeFetchError(f"Unexpected error fetching '{hostname}': {e}")
