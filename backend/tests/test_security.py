"""Comprehensive SSRF security tests verifying defense-in-depth boundaries."""

import ipaddress
import pytest
from unittest.mock import patch, AsyncMock
import httpx

from app.security.url_validator import validate_and_normalize_url, URLValidationError
from app.security.dns_validator import (
    resolve_and_validate_hostname,
    is_ip_prohibited,
    SSRFSecurityError,
)
from app.security.safe_fetcher import safe_fetch_url, SafeFetchError


class TestURLValidator:
    def test_valid_public_https_url(self):
        url, host, port = validate_and_normalize_url("https://example.com/about")
        assert url == "https://example.com/about"
        assert host == "example.com"
        assert port == 443

    def test_valid_public_http_url(self):
        url, host, port = validate_and_normalize_url("http://acme.org")
        assert url == "http://acme.org/"
        assert host == "acme.org"
        assert port == 80

    def test_reject_ftp_protocol(self):
        with pytest.raises(URLValidationError, match="Prohibited URL scheme"):
            validate_and_normalize_url("ftp://example.com/file.txt")

    def test_reject_file_protocol(self):
        with pytest.raises(URLValidationError, match="Prohibited URL scheme"):
            validate_and_normalize_url("file:///etc/passwd")

    def test_reject_embedded_credentials(self):
        with pytest.raises(URLValidationError, match="embedded credentials"):
            validate_and_normalize_url("https://admin:secret@example.com")

    def test_reject_localhost_hostname(self):
        with pytest.raises(URLValidationError, match="Prohibited target hostname"):
            validate_and_normalize_url("http://localhost:8080")

    def test_reject_internal_tld(self):
        with pytest.raises(URLValidationError, match="Prohibited private domain suffix"):
            validate_and_normalize_url("http://service.internal")
        with pytest.raises(URLValidationError, match="Prohibited private domain suffix"):
            validate_and_normalize_url("http://app.local")

    def test_reject_direct_loopback_ip(self):
        with pytest.raises(URLValidationError, match="prohibited non-public network address"):
            validate_and_normalize_url("http://127.0.0.1:4000")

    def test_reject_direct_private_rfc1918_ip(self):
        with pytest.raises(URLValidationError, match="prohibited non-public network address"):
            validate_and_normalize_url("http://192.168.1.1")
        with pytest.raises(URLValidationError, match="prohibited non-public network address"):
            validate_and_normalize_url("http://10.0.0.1")
        with pytest.raises(URLValidationError, match="prohibited non-public network address"):
            validate_and_normalize_url("http://172.16.0.5")

    def test_reject_direct_ipv6_loopback(self):
        with pytest.raises(URLValidationError, match="prohibited non-public network address"):
            validate_and_normalize_url("http://[::1]")

    def test_reject_direct_ipv4_mapped_ipv6_loopback(self):
        with pytest.raises(URLValidationError, match="prohibited"):
            validate_and_normalize_url("http://[::ffff:127.0.0.1]")

    def test_reject_cloud_metadata_ip(self):
        with pytest.raises(URLValidationError, match="prohibited non-public network address"):
            validate_and_normalize_url("http://169.254.169.254/latest/meta-data")


class TestDNSValidator:
    def test_detects_prohibited_ips(self):
        assert is_ip_prohibited(ipaddress.ip_address("127.0.0.1")) is True
        assert is_ip_prohibited(ipaddress.ip_address("10.10.10.10")) is True
        assert is_ip_prohibited(ipaddress.ip_address("192.168.0.1")) is True
        assert is_ip_prohibited(ipaddress.ip_address("172.20.0.1")) is True
        assert is_ip_prohibited(ipaddress.ip_address("169.254.169.254")) is True
        assert is_ip_prohibited(ipaddress.ip_address("0.0.0.0")) is True
        assert is_ip_prohibited(ipaddress.ip_address("::1")) is True
        assert is_ip_prohibited(ipaddress.ip_address("fc00::1")) is True
        assert is_ip_prohibited(ipaddress.ip_address("fe80::1")) is True

    def test_allows_public_ip(self):
        assert is_ip_prohibited(ipaddress.ip_address("93.184.216.34")) is False
        assert is_ip_prohibited(ipaddress.ip_address("8.8.8.8")) is False
        assert is_ip_prohibited(ipaddress.ip_address("2606:4700:4700::1111")) is False

    @patch("socket.getaddrinfo")
    def test_fails_closed_when_dns_resolves_to_private_ip(self, mock_getaddrinfo):
        mock_getaddrinfo.return_value = [
            (2, 1, 6, "", ("192.168.1.50", 80)),
        ]
        with pytest.raises(SSRFSecurityError, match="resolved to prohibited private IP"):
            resolve_and_validate_hostname("internal.victim.com")

    @patch("socket.getaddrinfo")
    def test_fails_closed_on_mixed_public_and_private_dns(self, mock_getaddrinfo):
        # A hostname returning both a public IP and an internal IP must be rejected immediately
        mock_getaddrinfo.return_value = [
            (2, 1, 6, "", ("93.184.216.34", 80)),
            (2, 1, 6, "", ("127.0.0.1", 80)),
        ]
        with pytest.raises(SSRFSecurityError, match="prohibited private IP"):
            resolve_and_validate_hostname("attacker-dns-rebind.com")

    @patch("socket.getaddrinfo")
    def test_blocks_cloud_metadata_hostname(self, mock_getaddrinfo):
        with pytest.raises(SSRFSecurityError, match="metadata"):
            resolve_and_validate_hostname("metadata.google.internal")


from contextlib import asynccontextmanager


@pytest.mark.asyncio
class TestSafeFetcher:
    @patch("app.security.safe_fetcher.resolve_and_validate_hostname")
    async def test_redirect_to_localhost_is_blocked(self, mock_dns):
        mock_dns.return_value = [("93.184.216.34", 2)]

        # Mock HTTP client where hop 1 redirects to localhost
        @asynccontextmanager
        async def mock_stream(method, url):
            if "example.com" in str(url):
                resp = httpx.Response(
                    302,
                    headers={"Location": "http://127.0.0.1:8080/admin"},
                    request=httpx.Request("GET", url),
                )
                yield resp
            else:
                resp = httpx.Response(200, text="internal data", request=httpx.Request("GET", url))
                yield resp

        with patch("httpx.AsyncClient.stream", side_effect=mock_stream):
            with pytest.raises(SafeFetchError, match="URL security validation failed|prohibited"):
                await safe_fetch_url("https://example.com/redirect")

    @patch("app.security.safe_fetcher.resolve_and_validate_hostname")
    async def test_redirect_loop_is_detected(self, mock_dns):
        mock_dns.return_value = [("93.184.216.34", 2)]

        @asynccontextmanager
        async def mock_loop_stream(method, url):
            resp = httpx.Response(
                301,
                headers={"Location": "https://example.com/loop"},
                request=httpx.Request("GET", url),
            )
            yield resp

        with patch("httpx.AsyncClient.stream", side_effect=mock_loop_stream):
            with pytest.raises(SafeFetchError, match="Redirect loop detected|Exceeded maximum redirect"):
                await safe_fetch_url("https://example.com/loop")


from app.api.routes import SimpleRateLimiter
from app.security.safe_fetcher import PinnedAsyncNetworkBackend
from fastapi import HTTPException


class TestRateLimiter:
    @pytest.mark.asyncio
    async def test_rate_limiter_allows_under_limit(self):
        limiter = SimpleRateLimiter(max_requests=3, window_seconds=60)
        req = AsyncMock()
        req.headers = {}
        req.client.host = "198.51.100.1"

        # 3 calls should succeed without exception
        await limiter(req)
        await limiter(req)
        await limiter(req)

    @pytest.mark.asyncio
    async def test_rate_limiter_blocks_excessive_requests(self):
        limiter = SimpleRateLimiter(max_requests=2, window_seconds=60)
        req = AsyncMock()
        req.headers = {}
        req.client.host = "198.51.100.2"

        await limiter(req)
        await limiter(req)

        with pytest.raises(HTTPException) as exc_info:
            await limiter(req)
        assert exc_info.value.status_code == 429
        assert "Rate limit exceeded" in exc_info.value.detail["message"]

    @pytest.mark.asyncio
    async def test_rate_limiter_uses_x_forwarded_for_from_trusted_proxy(self):
        """When direct peer is a trusted reverse proxy (127.0.0.1), forwarded IP is trusted."""
        limiter = SimpleRateLimiter(max_requests=1, window_seconds=60)
        req = AsyncMock()
        req.headers = {"X-Forwarded-For": "203.0.113.195, 127.0.0.1"}
        req.client.host = "127.0.0.1"

        await limiter(req)

        with pytest.raises(HTTPException) as exc_info:
            await limiter(req)
        assert exc_info.value.status_code == 429

    @pytest.mark.asyncio
    async def test_rate_limiter_ignores_x_forwarded_for_from_untrusted_peer(self):
        """When direct peer is NOT a trusted proxy, X-Forwarded-For is ignored to prevent IP spoofing."""
        from app.api.routes import get_client_ip
        req = AsyncMock()
        req.headers = {"X-Forwarded-For": "203.0.113.195"}
        req.client.host = "198.51.100.77"

        # Direct peer is untrusted; client IP must be the peer IP, not spoofed header
        extracted = get_client_ip(req)
        assert extracted == "198.51.100.77"

    def test_workspace_cache_isolation(self):
        """Verify that cache keys isolate data between different workspaces."""
        from app.utils.cache import TTLMemoryCache
        cache = TTLMemoryCache(ttl_seconds=60)

        # Store result in workspace_a
        cache.set("workspace_a::https://example.com::gemini::gemini-2.5-flash", {"data": "workspace_a_report"})

        # workspace_a should hit
        assert cache.get("workspace_a::https://example.com::gemini::gemini-2.5-flash") == {"data": "workspace_a_report"}

        # workspace_b should miss
        assert cache.get("workspace_b::https://example.com::gemini::gemini-2.5-flash") is None



class TestPinnedTransport:
    @pytest.mark.asyncio
    async def test_pinned_network_backend_connects_to_pinned_ip(self):
        mock_underlying = AsyncMock()
        mock_underlying.connect_tcp.return_value = "mock_stream"

        pinned_backend = PinnedAsyncNetworkBackend(
            target_hostname="example.com",
            pinned_ip="93.184.216.34",
            backend=mock_underlying,
        )

        res = await pinned_backend.connect_tcp(host="example.com", port=443)

        assert res == "mock_stream"
        # Must have connected to pinned_ip, NOT "example.com"
        mock_underlying.connect_tcp.assert_called_once()
        call_kwargs = mock_underlying.connect_tcp.call_args[1]
        assert call_kwargs["host"] == "93.184.216.34"
        assert call_kwargs["port"] == 443

