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


@pytest.mark.asyncio
async def test_benchmark_mock_mode_simulation():
    """Verify mock_mode=True returns deterministic simulation for all 3 models without calling live APIs."""
    service = BenchmarkService()
    req = BenchmarkRunRequest(
        url="https://acmecloud.example",
        providers=["gemini", "openai", "anthropic"],
        mock_mode=True,
    )
    res = await service.run_benchmark(req)

    assert res.is_simulated is True
    assert len(res.results) == 3
    assert res.recommended_winner is not None
    assert res.cheapest_model is not None
    assert res.fastest_model is not None
    assert res.highest_quality_model is not None

    for item in res.results:
        assert item.status == "success"
        assert item.simulated is True
        assert item.schema_valid is True
        assert item.completeness_score >= 80
        assert item.quality_score >= 80
        assert item.dimension_scores.competitors > 0
        assert item.dimension_scores.search_queries > 0
        assert item.dimension_scores.seo > 0
        assert item.dimension_scores.services > 0
        assert item.dimension_scores.target_audience > 0


def test_benchmark_quality_score_decoupled_from_latency():
    """Verify quality score is purely analytical and does NOT reward or penalize latency."""
    service = BenchmarkService()
    bundle = {
        "brand": {"name": "Acme", "category": "Cloud Platform", "summary": "Enterprise cloud services."},
        "competitors": [{"name": f"Comp{i}"} for i in range(3)],
        "search_queries": [{"query": f"q{i}", "platforms": ["Google"]} for i in range(5)],
        "seo_improvements": {"primary_keyword": "cloud", "recommended_title": "Title"},
        "services": [{"name": f"Service {i}"} for i in range(3)],
        "target_audience": {"primary_audience": "Enterprise Engineers"},
    }

    # Calculate quality score with low latency
    comp_fast, score_fast, dim_fast = service._calculate_quality_score(bundle, schema_valid=True, latency_seconds=0.2)
    # Calculate quality score with high latency
    comp_slow, score_slow, dim_slow = service._calculate_quality_score(bundle, schema_valid=True, latency_seconds=15.0)

    # Must be strictly identical: latency must NOT influence analytical quality
    assert score_fast == score_slow
    assert dim_fast.competitors == dim_slow.competitors
    assert dim_fast.seo == dim_slow.seo
    assert dim_fast.services == dim_slow.services


def test_benchmark_endpoint_mock_mode_via_api():
    """Verify POST /benchmark/run accepts mock_mode=true and returns 200 with simulated results."""
    response = client.post(
        "/benchmark/run",
        json={
            "url": "https://acmecloud.example",
            "mock_mode": True,
            "benchmark_mode": "synthetic",
            "providers": ["gemini", "openai", "anthropic"],
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["is_simulated"] is True
    assert len(data["results"]) == 3
    for r in data["results"]:
        assert r["simulated"] is True
        assert r["status"] == "success"


@pytest.mark.asyncio
async def test_live_benchmark_extraction_failure_never_falls_back_to_synthetic():
    """
    Regression test: Live benchmark extraction failure must return an explicit failed result.
    It must NEVER silently fall back to STANDARD_BENCHMARK_CONTENT or report synthetic success.
    """
    service = BenchmarkService()
    # Mock extractor.extract to simulate a network or scraping failure
    with patch.object(service.extractor, "extract", side_effect=RuntimeError("DNS resolution failed for test host")):
        req = BenchmarkRunRequest(
            url="https://unreachable-live-site.test",
            benchmark_mode="live",
            mock_mode=False,
            providers=["gemini", "openai"],
        )
        res = await service.run_benchmark(req)

        assert res.benchmark_mode == "live"
        assert res.is_simulated is False
        assert "Live benchmark failed" in res.summary
        assert res.recommended_winner is None
        assert len(res.results) == 2
        for r in res.results:
            assert r.status == "failed"
            assert r.error_code == "LIVE_EXTRACTION_FAILED"
            assert "never fall back to synthetic" in r.error.lower()


@pytest.mark.asyncio
async def test_neutral_model_recommendation_logic():
    """
    Verify recommendation methodology is neutral, multi-criteria (completeness, latency, cost),
    and does not pre-select any specific provider by default.
    """
    service = BenchmarkService()
    req = BenchmarkRunRequest(
        url="https://acmecloud.example",
        mock_mode=True,
        benchmark_mode="synthetic",
        providers=["gemini", "openai", "anthropic"],
    )
    res = await service.run_benchmark(req)

    assert res.recommended_winner is not None
    assert "composite score of" in res.recommendation_rationale
    assert "45% structural completeness, 30% latency efficiency, 25% cost economics" in res.recommendation_rationale
    assert "simulated benchmark" in res.recommendation_rationale or "simulation mode" in res.recommendation_rationale


