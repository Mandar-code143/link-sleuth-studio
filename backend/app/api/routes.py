"""API routes for LinkIntel AI."""

import time
import uuid
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse

from ..schemas.request import LinkAnalysisRequest
from ..schemas.response import LinkAnalysisResponse
from ..security.url_validator import validate_and_normalize_url, URLValidationError
from ..security.safe_fetcher import SafeFetchError
from ..security.dns_validator import SSRFSecurityError
from ..services.website_extractor import WebsiteExtractor
from ..services.analysis_service import AnalysisService
from ..services.cost_service import calculate_analysis_cost
from ..utils.cache import analysis_cache
from ..utils.logging import log_event

router = APIRouter()
extractor = WebsiteExtractor()
analyzer = AnalysisService()


@router.get(
    "/health",
    summary="Health check",
    tags=["System"],
    response_model=dict,
)
async def health_check() -> dict:
    """Returns service availability status."""
    return {"status": "ok"}


@router.post(
    "/link-analysis",
    summary="Analyze public website",
    tags=["Analysis"],
    response_model=LinkAnalysisResponse,
    status_code=status.HTTP_200_OK,
)
async def analyze_link(request: LinkAnalysisRequest) -> LinkAnalysisResponse:
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
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid URL: {e}",
        )

    # 2. Cache Lookup
    cached_response = analysis_cache.get(normalized_url)
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
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Security policy blocked request: {e}",
        )
    except SafeFetchError as e:
        log_event("fetch_failed", request_id=request_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Could not safely fetch website content: {e}",
        )
    except Exception as e:
        log_event("unexpected_fetch_error", request_id=request_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal extraction error: {e}",
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

        # Cache successful analysis
        analysis_cache.set(normalized_url, analysis_response)

        return analysis_response

    except Exception as e:
        log_event("analysis_failed", request_id=request_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate website intelligence report: {e}",
        )
