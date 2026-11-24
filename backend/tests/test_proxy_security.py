"""Tests for CIDR proxy validation, client IP extraction, and sanitized API error responses."""

from unittest.mock import patch
import pytest
from starlette.requests import Request
from fastapi.testclient import TestClient

from app.api.routes import is_trusted_proxy_ip, get_client_ip
from app.security.dns_validator import SSRFSecurityError
from app.config import settings
from app.main import create_app

TRUSTED_RENDER_PROXIES = [
    "127.0.0.1",
    "::1",
    "localhost",
    "10.0.0.0/8",
    "172.16.0.0/12",
    "192.168.0.0/16",
]


class MockClient:
    def __init__(self, host: str):
        self.host = host


def make_mock_request(peer_host: str, headers: dict = None) -> Request:
    scope = {
        "type": "http",
        "client": (peer_host, 12345),
        "headers": [(k.lower().encode("latin-1"), v.encode("latin-1")) for k, v in (headers or {}).items()],
    }
    return Request(scope)


def test_is_trusted_proxy_ip_loopback():
    assert is_trusted_proxy_ip("127.0.0.1", TRUSTED_RENDER_PROXIES) is True
    assert is_trusted_proxy_ip("::1", TRUSTED_RENDER_PROXIES) is True
    assert is_trusted_proxy_ip("localhost", TRUSTED_RENDER_PROXIES) is True
    assert is_trusted_proxy_ip("testclient", TRUSTED_RENDER_PROXIES) is True


def test_is_trusted_proxy_ip_cidr_ranges():
    # 10.0.0.0/8
    assert is_trusted_proxy_ip("10.0.4.15", TRUSTED_RENDER_PROXIES) is True
    assert is_trusted_proxy_ip("10.255.255.254", TRUSTED_RENDER_PROXIES) is True
    # 172.16.0.0/12
    assert is_trusted_proxy_ip("172.16.0.1", TRUSTED_RENDER_PROXIES) is True
    assert is_trusted_proxy_ip("172.31.255.255", TRUSTED_RENDER_PROXIES) is True
    # 192.168.0.0/16
    assert is_trusted_proxy_ip("192.168.1.100", TRUSTED_RENDER_PROXIES) is True


def test_is_trusted_proxy_ip_rejects_untrusted_public_ips():
    assert is_trusted_proxy_ip("203.0.113.195", TRUSTED_RENDER_PROXIES) is False
    assert is_trusted_proxy_ip("8.8.8.8", TRUSTED_RENDER_PROXIES) is False
    assert is_trusted_proxy_ip("172.32.0.1", TRUSTED_RENDER_PROXIES) is False  # Outside 172.16.0.0/12


def test_is_trusted_proxy_ip_handles_malformed():
    assert is_trusted_proxy_ip("", TRUSTED_RENDER_PROXIES) is False
    assert is_trusted_proxy_ip("invalid_ip", TRUSTED_RENDER_PROXIES) is False
    assert is_trusted_proxy_ip("10.0.0.1; rm -rf", TRUSTED_RENDER_PROXIES) is False


def test_get_client_ip_honors_forwarded_from_trusted_peer(monkeypatch):
    monkeypatch.setattr(settings, "trusted_proxies", ",".join(TRUSTED_RENDER_PROXIES))
    req = make_mock_request(
        peer_host="10.244.0.1",
        headers={"x-forwarded-for": "198.51.100.22, 10.244.0.1"},
    )
    client_ip = get_client_ip(req)
    assert client_ip == "198.51.100.22"


def test_get_client_ip_ignores_spoofed_forwarded_from_untrusted_peer(monkeypatch):
    monkeypatch.setattr(settings, "trusted_proxies", ",".join(TRUSTED_RENDER_PROXIES))
    # Direct peer is untrusted public address
    req = make_mock_request(
        peer_host="203.0.113.5",
        headers={"x-forwarded-for": "1.1.1.1"},
    )
    client_ip = get_client_ip(req)
    # Must reject spoofed header and return the untrusted peer's actual IP
    assert client_ip == "203.0.113.5"


def test_get_client_ip_rejects_malformed_forwarded_candidate(monkeypatch):
    monkeypatch.setattr(settings, "trusted_proxies", ",".join(TRUSTED_RENDER_PROXIES))
    req = make_mock_request(
        peer_host="10.0.0.1",
        headers={"x-forwarded-for": "malformed_ip_injection"},
    )
    client_ip = get_client_ip(req)
    assert client_ip == "10.0.0.1"


def test_error_response_sanitization_on_security_violation():
    app = create_app()
    client = TestClient(app)

    # 1. URL validation error
    response_url = client.post("/link-analysis", json={"url": "http://169.254.169.254/latest/meta-data"})
    assert response_url.status_code == 400
    data_url = response_url.json()
    assert data_url["success"] is False
    assert data_url["error"]["code"] == "INVALID_URL"
    assert "Traceback" not in data_url["detail"]

    # 2. SSRF Security Violation
    with patch("app.api.routes.extractor.extract", side_effect=SSRFSecurityError("Internal network blocked")):
        response_ssrf = client.post("/link-analysis", json={"url": "https://internal.company.com"})
        assert response_ssrf.status_code == 400
        data_ssrf = response_ssrf.json()
        assert data_ssrf["success"] is False
        assert data_ssrf["error"]["code"] == "SECURITY_POLICY_VIOLATION"
        assert "Internal network blocked" not in data_ssrf["detail"]
        assert "SSRFSecurityError" not in data_ssrf["detail"]
        assert "request_id" in data_ssrf
