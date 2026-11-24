"""Tests for Multi-Model Research Lab, provider status, and benchmarking endpoints."""

import pytest
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient

from app.main import app
from app.services.benchmark_service import BenchmarkService, ModelBenchmarkResult
from app.schemas.benchmark import BenchmarkRunRequest

client = TestClient(app)


def test_models_status_endpoint():
    """Verify /models/status returns all 3 supported providers with pricing specs."""
    response = client.get("/models/status")
    assert response.status_code == 200
    data = response.json()
    assert "providers" in data
    assert len(data["providers"]) == 3

    provider_ids = [p["provider"] for p in data["providers"]]
    assert "gemini" in provider_ids
    assert "openai" in provider_ids
    assert "anthropic" in provider_ids

    for p in data["providers"]:
        assert "model" in p
        assert "configured" in p
        assert "input_rate_per_million" in p
        assert "output_rate_per_million" in p
        assert "structured_output_mode" in p


def test_benchmark_run_reports_unconfigured_gracefully():
    """Verify benchmark run reports unconfigured status without crashing when API keys are missing."""
    response = client.post(
        "/benchmark/run",
        json={
            "url": "https://acmecloud.example",
            "providers": ["gemini", "openai", "anthropic"],
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "benchmark_id" in data
    assert "results" in data
    assert len(data["results"]) == 3

    for res in data["results"]:
        assert res["status"] in ("success", "unconfigured", "failed")
        if not res["configured"]:
            assert res["status"] == "unconfigured"
            assert "not configured" in res["error"].lower()


@pytest.mark.asyncio
async def test_benchmark_run_with_mock_provider():
    """Verify benchmark execution correctly scores valid structured responses."""
    service = BenchmarkService()
    req = BenchmarkRunRequest(url="https://acmecloud.example", providers=["mock"])
    res = await service.run_benchmark(req)

    assert res.benchmark_id
    assert len(res.results) == 1
    mock_res = res.results[0]
    assert mock_res.status == "success"
    assert mock_res.schema_valid is True
    assert mock_res.completeness_score == 100
    assert mock_res.quality_score >= 90
    assert mock_res.queries_count == 5
    assert mock_res.competitors_count >= 3
