"""FastAPI endpoints and integration tests."""

import pytest
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient

from app.main import app
from app.api import routes
from app.services.analysis_service import MockProvider
from app.services.website_extractor import WebsiteExtraction

client = TestClient(app)


def test_health_check_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_health_ready_endpoint():
    response = client.get("/health/ready")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "provider" in data
    assert "provider_key_present" in data
    assert "search_provider_configured" in data


def test_openapi_docs_endpoint():
    response = client.get("/docs")
    assert response.status_code == 200
    assert "LinkIntel AI" in response.text


def test_link_analysis_rejects_empty_payload():
    response = client.post("/link-analysis", json={})
    assert response.status_code in (400, 422)


def test_link_analysis_rejects_invalid_url():
    response = client.post("/link-analysis", json={"url": "not-a-valid-url"})
    assert response.status_code in (400, 422)
    assert any(term in response.text.lower() for term in ["validation", "invalid", "supported", "protocols"])


def test_link_analysis_rejects_internal_ip():
    response = client.post("/link-analysis", json={"url": "http://127.0.0.1:4000"})
    assert response.status_code == 400
    assert "prohibited non-public network address" in response.text


def test_link_analysis_rejects_localhost():
    response = client.post("/link-analysis", json={"url": "http://localhost:3000"})
    assert response.status_code == 400
    assert "Prohibited target hostname" in response.text


def test_link_analysis_successful_flow():
    mock_extraction = WebsiteExtraction(
        requested_url="https://acme-cloud-solutions.com",
        final_url="https://acme-cloud-solutions.com",
        domain="acme-cloud-solutions.com",
        title="Acme Cloud Solutions — Scalable Systems",
        meta_description="Enterprise cloud architecture and engineering.",
        headings=[
            {"level": "h1", "text": "Cloud Solutions for Scale"},
            {"level": "h2", "text": "Infrastructure Consulting"},
            {"level": "h2", "text": "Kubernetes Architecture"},
        ],
        main_content="Acme Cloud Solutions provides enterprise cloud engineering and platform architecture.",
        internal_pages=[],
        canonical_url="https://acme-cloud-solutions.com",
        language="en",
        structured_data=[],
        open_graph={},
        meta_robots=None,
        extraction_warnings=[],
    )

    with patch("app.api.routes.extractor.extract", new_callable=AsyncMock) as mock_extract, \
         patch.object(routes.analyzer, "provider", MockProvider()):
        mock_extract.return_value = mock_extraction

        response = client.post("/link-analysis", json={"url": "https://acme-cloud-solutions.com"})

        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()

        assert data["success"] is True
        assert data["website"] == "https://acme-cloud-solutions.com"
        assert "brand" in data
        assert data["brand"]["name"]
        assert "analysis" in data

        # Check all 5 mandatory analytical sections
        analysis = data["analysis"]
        assert "competitor_analysis" in analysis
        assert "target_search_queries" in analysis
        assert len(analysis["target_search_queries"]) == 5
        assert "seo_improvements" in analysis
        assert "top_services" in analysis
        assert "target_audience" in analysis

        # Check metadata
        assert "metadata" in data
        assert data["metadata"]["report_id"]
        assert data["metadata"]["sample_data"] is False


def test_link_analysis_aborts_honestly_when_no_api_key():
    from app.utils.cache import analysis_cache
    analysis_cache.clear()

    mock_extraction = WebsiteExtraction(
        requested_url="https://no-key-test.example.com",
        final_url="https://no-key-test.example.com",
        domain="no-key-test.example.com",
        title="No Key Test",
        meta_description="Enterprise cloud architecture.",
        headings=[],
        main_content="No key test cloud engineering.",
        internal_pages=[],
        canonical_url="https://no-key-test.example.com",
        language="en",
        structured_data=[],
        open_graph={},
        meta_robots=None,
        extraction_warnings=[],
    )

    from app.providers.gemini import GeminiProvider
    unconfigured_provider = GeminiProvider(api_key=None)

    with patch("app.api.routes.extractor.extract", new_callable=AsyncMock) as mock_extract, \
         patch.object(routes.analyzer, "provider", unconfigured_provider):
        mock_extract.return_value = mock_extraction

        response = client.post("/link-analysis", json={"url": "https://no-key-test.example.com"})

        assert response.status_code == 503
        data = response.json()
        assert data["success"] is False
        assert data["error"]["code"] == "AI_PROVIDER_NOT_CONFIGURED"
