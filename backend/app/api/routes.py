"""API routes for LinkIntel AI with health diagnostics and structured error handling."""

import time
import uuid
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse

from ..config import settings
from ..schemas.request import LinkAnalysisRequest
from ..schemas.response import LinkAnalysisResponse
from ..schemas.benchmark import ProviderStatusResponse, BenchmarkRunRequest, BenchmarkRunResponse
from ..security.url_validator import validate_and_normalize_url, URLValidationError
from ..security.safe_fetcher import SafeFetchError
from ..security.dns_validator import SSRFSecurityError
from ..services.website_extractor import WebsiteExtractor
from ..services.analysis_service import AnalysisService, AnalysisServiceError
from ..services.cost_service import calculate_analysis_cost
from ..services.benchmark_service import benchmark_service
from ..utils.cache import analysis_cache
from ..utils.logging import log_event

router = APIRouter()
extractor = WebsiteExtractor()
analyzer = AnalysisService()


@router.get(
    "/health",
    summary="Liveness check",
    tags=["System"],
    response_model=dict,
)
async def health_check() -> dict:
    """Returns basic service reachability status."""
    return {"status": "ok"}


@router.get(
    "/health/ready",
    summary="Readiness check",
    tags=["System"],
    response_model=dict,
)
async def readiness_check() -> dict:
    """
    Returns deep backend readiness including provider configuration status.
    Never exposes API keys or private configuration values.
    """
    key_present = False
    if settings.llm_provider == "gemini":
        key_present = settings.is_gemini_configured
    elif settings.llm_provider == "openai":
        key_present = bool(settings.openai_api_key)
    elif settings.llm_provider == "anthropic":
        key_present = bool(settings.anthropic_api_key)
    elif settings.llm_provider == "mock":
        key_present = True

    return {
        "status": "ready" if key_present else "degraded",
        "provider": settings.llm_provider,
        "model": settings.llm_model,
        "provider_key_present": key_present,
        "search_provider": settings.search_provider,
        "search_provider_configured": settings.is_search_configured,
        "app_env": settings.app_env,
    }


@router.get(
    "/models/status",
    summary="List supported LLM providers and configuration status",
    tags=["Model Lab"],
    response_model=ProviderStatusResponse,
)
async def get_models_status():
    """Returns runtime credentials and pricing specifications for all supported LLM providers."""
    return benchmark_service.get_providers_status()


@router.post(
    "/benchmark/run",
    summary="Execute multi-model comparison benchmark",
    tags=["Model Lab"],
    response_model=BenchmarkRunResponse,
)
async def run_benchmark(request: BenchmarkRunRequest):
    """
    Executes a controlled benchmark comparing Gemini, OpenAI, and Anthropic
    on latency, token consumption, cost economics, and schema validity.
    """
    log_event("benchmark_requested", target_url=request.url, providers=request.providers)
    return await benchmark_service.run_benchmark(request)


@router.post(
    "/link-analysis",
    summary="Analyze public website",
    tags=["Analysis"],
    response_model=LinkAnalysisResponse,
    status_code=status.HTTP_200_OK,
)
async def analyze_link(request: LinkAnalysisRequest):
    """
    Analyzes a submitted business website and returns five structured dimensions of
    business intelligence, competitor comparisons, search queries, SEO, and audience profiles.
    """
    request_id = f"req-{uuid.uuid4().hex[:8]}"
    start_time = time.perf_counter()

    log_event("request_received", request_id=request_id, target_url=request.url)

    # 1. URL structural validation & normalization
    try:
        normalized_url, hostname, port = validate_and_normalize_url(request.url)
    except URLValidationError as e:
        log_event("validation_error", request_id=request_id, error=str(e))
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "success": False,
                "error": {
                    "code": "INVALID_URL",
                    "message": str(e),
                },
                "request_id": request_id,
            },
        )

    # 2. Cache Lookup (model-aware key)
    cache_key = f"{normalized_url}::{settings.llm_provider}::{settings.llm_model}"
    cached_response = analysis_cache.get(cache_key)
    if cached_response:
        log_event("cache_hit", request_id=request_id, normalized_url=normalized_url)
        return cached_response

    # 3. Safe Outbound Fetching & Extraction
    try:
        extraction = await extractor.extract(normalized_url)
        log_event(
            "extraction_complete",
            request_id=request_id,
            final_url=extraction.final_url,
            title=extraction.title,
            chars=len(extraction.main_content),
        )
    except (SSRFSecurityError, URLValidationError) as e:
        log_event("security_blocked", request_id=request_id, error=str(e))
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "success": False,
                "error": {
                    "code": "SECURITY_POLICY_VIOLATION",
                    "message": f"Security policy blocked request: {e}",
                },
                "request_id": request_id,
            },
        )
    except SafeFetchError as e:
        log_event("fetch_failed", request_id=request_id, error=str(e))
        return JSONResponse(
            status_code=status.HTTP_502_BAD_GATEWAY,
            content={
                "success": False,
                "error": {
                    "code": "FETCH_FAILED",
                    "message": f"Could not safely fetch website content: {e}",
                },
                "request_id": request_id,
            },
        )
    except Exception as e:
        log_event("unexpected_fetch_error", request_id=request_id, error=str(e))
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "error": {
                    "code": "INTERNAL_EXTRACTION_ERROR",
                    "message": "An error occurred while extracting the target website.",
                },
                "request_id": request_id,
            },
        )

    # 4. Intelligence Generation
    try:
        analysis_response, llm_result = await analyzer.analyze_website(extraction)
        total_latency = time.perf_counter() - start_time

        # Cost tracking
        cost_breakdown = calculate_analysis_cost(
            model_name=llm_result.model,
            input_tokens=llm_result.input_tokens,
            output_tokens=llm_result.output_tokens,
        )

        log_event(
            "analysis_complete",
            request_id=request_id,
            model=llm_result.model,
            in_tokens=llm_result.input_tokens,
            out_tokens=llm_result.output_tokens,
            cost_usd=cost_breakdown.total_cost_usd,
            latency_s=round(total_latency, 2),
        )

        # Cache successful analysis ONLY (never cache errors)
        analysis_cache.set(cache_key, analysis_response)

        return analysis_response

    except AnalysisServiceError as e:
        log_event("analysis_service_error", request_id=request_id, error_code=e.error_code, error=e.message)
        return JSONResponse(
            status_code=e.status_code,
            content={
                "success": False,
                "error": {
                    "code": e.error_code,
                    "message": e.message,
                },
                "request_id": request_id,
            },
        )
    except Exception as e:
        log_event("analysis_unhandled_failure", request_id=request_id, error=str(e))
        return JSONResponse(
            status_code=status.HTTP_502_BAD_GATEWAY,
            content={
                "success": False,
                "error": {
                    "code": "AI_SYNTHESIS_FAILED",
                    "message": f"Failed to generate website intelligence: {e}",
                },
                "request_id": request_id,
            },
        )
