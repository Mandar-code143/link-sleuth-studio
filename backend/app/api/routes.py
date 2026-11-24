"""API routes for LinkIntel AI with health diagnostics, rate limiting, and structured error handling."""

import time
import uuid
import threading
from collections import defaultdict
from typing import Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from ..config import settings
from ..database import get_db, ReportRecord, BenchmarkRecord
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


def get_client_ip(request: Request) -> str:
    """
    Extracts client IP safely.
    Only trusts X-Forwarded-For if the direct peer is a configured trusted reverse proxy.
    """
    peer_ip = request.client.host if request.client else "127.0.0.1"
    trusted = settings.parsed_trusted_proxies
    # TestClient in pytest sets peer_ip to "testclient"
    is_trusted_peer = (
        peer_ip.lower() in trusted or
        peer_ip in ("127.0.0.1", "::1", "localhost", "testclient")
    )
    if is_trusted_peer:
        forwarded = request.headers.get("x-forwarded-for") or request.headers.get("X-Forwarded-For")
        if forwarded:
            candidate = forwarded.split(",")[0].strip()
            if candidate:
                return candidate
    return peer_ip


def get_workspace_id(request: Request) -> str:
    """Extracts isolated workspace identifier from header or query param."""
    header_val = request.headers.get("x-workspace-id") or request.headers.get("X-Workspace-Id")
    if header_val and header_val.strip():
        return header_val.strip()[:64]
    query_val = request.query_params.get("workspace_id")
    if query_val and query_val.strip():
        return query_val.strip()[:64]
    return "default"


class SimpleRateLimiter:
    """Sliding-window in-memory request throttler by client IP."""

    def __init__(self, max_requests: int = 60, window_seconds: float = 60.0):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._requests: Dict[str, List[float]] = defaultdict(list)
        self._lock = threading.Lock()

    def is_allowed(self, client_ip: str) -> bool:
        now = time.time()
        with self._lock:
            history = self._requests[client_ip]
            cutoff = now - self.window_seconds
            self._requests[client_ip] = [t for t in history if t > cutoff]
            if len(self._requests[client_ip]) >= self.max_requests:
                return False
            self._requests[client_ip].append(now)
            return True

    async def __call__(self, request: Request) -> None:
        client_ip = get_client_ip(request)
        if not self.is_allowed(client_ip):
            raise HTTPException(
                status_code=429,
                detail={
                    "error_code": "RATE_LIMIT_EXCEEDED",
                    "message": "Rate limit exceeded. Please wait before submitting additional requests.",
                },
            )


rate_limiter = SimpleRateLimiter(max_requests=60, window_seconds=60.0)


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
async def run_benchmark(
    request: BenchmarkRunRequest,
    http_req: Request,
    db: Session = Depends(get_db),
):
    """
    Executes a controlled benchmark comparing Gemini, OpenAI, and Anthropic
    on latency, token consumption, cost economics, and schema validity.
    """
    client_ip = get_client_ip(http_req)
    if not rate_limiter.is_allowed(client_ip):
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={
                "success": False,
                "detail": "Rate limit exceeded. Maximum 60 requests per minute.",
                "error": {
                    "code": "RATE_LIMIT_EXCEEDED",
                    "message": "Rate limit exceeded. Maximum 60 requests per minute.",
                },
                "request_id": f"req-{uuid.uuid4().hex[:8]}",
            },
        )

    log_event("benchmark_requested", target_url=request.url, providers=request.providers, mock=request.mock_mode)
    benchmark_result = await benchmark_service.run_benchmark(request)

    # Persist benchmark result with workspace isolation
    try:
        workspace_id = get_workspace_id(http_req)
        bmk_record = BenchmarkRecord(
            id=benchmark_result.benchmark_id,
            workspace_id=workspace_id,
            target_url=benchmark_result.target_url,
            benchmark_mode=benchmark_result.benchmark_mode,
            is_simulated=benchmark_result.is_simulated,
            winner_model=benchmark_result.recommended_winner or "",
            results_json=benchmark_result.model_dump_json(),
        )
        db.add(bmk_record)
        db.commit()
    except Exception as db_err:
        log_event("benchmark_persistence_error", error=str(db_err))
        db.rollback()

    return benchmark_result


@router.post(
    "/link-analysis",
    summary="Analyze public website",
    tags=["Analysis"],
    response_model=LinkAnalysisResponse,
    status_code=status.HTTP_200_OK,
)
async def analyze_link(
    request: LinkAnalysisRequest,
    http_req: Request,
    db: Session = Depends(get_db),
):
    """
    Analyzes a submitted business website and returns five structured dimensions of
    business intelligence, competitor comparisons, search queries, SEO, and audience profiles.
    """
    request_id = f"req-{uuid.uuid4().hex[:8]}"
    start_time = time.perf_counter()

    client_ip = get_client_ip(http_req)
    if not rate_limiter.is_allowed(client_ip):
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={
                "success": False,
                "detail": "Rate limit exceeded. Maximum 60 requests per minute.",
                "error": {
                    "code": "RATE_LIMIT_EXCEEDED",
                    "message": "Rate limit exceeded. Maximum 60 requests per minute.",
                },
                "request_id": request_id,
            },
        )

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
                "detail": str(e),
                "error": {
                    "code": "INVALID_URL",
                    "message": str(e),
                },
                "request_id": request_id,
            },
        )

    # 2. Cache Lookup (workspace-isolated & model-aware key)
    workspace_id = get_workspace_id(http_req)
    cache_key = f"{workspace_id}::{normalized_url}::{settings.llm_provider}::{settings.llm_model}"
    cached_response = analysis_cache.get(cache_key)
    if cached_response:
        log_event("cache_hit", request_id=request_id, workspace_id=workspace_id, normalized_url=normalized_url)
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
                "detail": f"Security policy blocked request: {e}",
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
                "detail": f"Could not safely fetch website content: {e}",
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
                "detail": "An error occurred while extracting the target website.",
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

        cost_info = calculate_analysis_cost(
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
            cost_usd=cost_info.total_cost_usd,
            latency_s=round(total_latency, 2),
        )

        # Cache successful analysis ONLY (never cache errors)
        analysis_cache.set(cache_key, analysis_response)

        # Persist to database with workspace isolation
        workspace_id = get_workspace_id(http_req)
        try:
            brand_name = ""
            category = ""
            summary = ""
            if analysis_response.analysis and analysis_response.analysis.business_summary:
                bs = analysis_response.analysis.business_summary
                brand_name = bs.brand_name or ""
                category = bs.industry_category or ""
                summary = bs.one_line_pitch or ""

            db_record = ReportRecord(
                id=request_id.replace("req-", "rep_"),
                workspace_id=workspace_id,
                url=normalized_url,
                brand_name=brand_name,
                category=category,
                summary=summary,
                report_json=analysis_response.model_dump_json(),
                model_used=llm_result.model,
                is_sample=bool(getattr(analysis_response.analysis.metadata, "sample_data", False)),
                tokens_used=llm_result.input_tokens + llm_result.output_tokens,
                cost_usd=cost_info.total_cost_usd,
            )
            db.add(db_record)
            db.commit()
        except Exception as db_err:
            log_event("report_persistence_error", request_id=request_id, error=str(db_err))
            db.rollback()

        return analysis_response

    except AnalysisServiceError as e:
        log_event("analysis_service_error", request_id=request_id, error_code=e.error_code, error=e.message)
        return JSONResponse(
            status_code=e.status_code,
            content={
                "success": False,
                "detail": e.message,
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
                "detail": f"Failed to generate website intelligence: {e}",
                "error": {
                    "code": "AI_SYNTHESIS_FAILED",
                    "message": f"Failed to generate website intelligence: {e}",
                },
                "request_id": request_id,
            },
        )


@router.get(
    "/reports",
    summary="List analysis reports for current workspace",
    tags=["Analysis"],
)
async def list_reports(
    http_req: Request,
    q: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    """Returns stored reports for the requested workspace with optional query search and pagination."""
    workspace_id = get_workspace_id(http_req)
    query = db.query(ReportRecord).filter(ReportRecord.workspace_id == workspace_id)
    if q and q.strip():
        search_pattern = f"%{q.strip()}%"
        query = query.filter(
            (ReportRecord.url.ilike(search_pattern))
            | (ReportRecord.brand_name.ilike(search_pattern))
            | (ReportRecord.category.ilike(search_pattern))
            | (ReportRecord.summary.ilike(search_pattern))
        )
    total = query.count()
    items = query.order_by(ReportRecord.created_at.desc()).offset(skip).limit(limit).all()
    return {
        "items": [r.to_dict() for r in items],
        "total": total,
        "workspace_id": workspace_id,
    }


@router.get(
    "/reports/{report_id}",
    summary="Get single analysis report by ID",
    tags=["Analysis"],
)
async def get_report_by_id(
    report_id: str,
    http_req: Request,
    db: Session = Depends(get_db),
):
    """Retrieves full analysis payload for a stored report within the active workspace."""
    workspace_id = get_workspace_id(http_req)
    record = (
        db.query(ReportRecord)
        .filter(ReportRecord.id == report_id, ReportRecord.workspace_id == workspace_id)
        .first()
    )
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Report '{report_id}' not found in workspace '{workspace_id}'.",
        )
    return record.get_full_report()


@router.delete(
    "/reports/{report_id}",
    summary="Delete analysis report by ID",
    tags=["Analysis"],
)
async def delete_report(
    report_id: str,
    http_req: Request,
    db: Session = Depends(get_db),
):
    """Permanently removes a saved report from the workspace archive."""
    workspace_id = get_workspace_id(http_req)
    record = (
        db.query(ReportRecord)
        .filter(ReportRecord.id == report_id, ReportRecord.workspace_id == workspace_id)
        .first()
    )
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Report '{report_id}' not found in workspace '{workspace_id}'.",
        )
    db.delete(record)
    db.commit()
    return {"status": "deleted", "id": report_id, "workspace_id": workspace_id}


@router.get(
    "/benchmarks",
    summary="List benchmark runs for current workspace",
    tags=["Model Lab"],
)
async def list_benchmarks(
    http_req: Request,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    """Lists historical multi-model evaluation runs conducted in the active workspace."""
    workspace_id = get_workspace_id(http_req)
    query = db.query(BenchmarkRecord).filter(BenchmarkRecord.workspace_id == workspace_id)
    total = query.count()
    items = query.order_by(BenchmarkRecord.created_at.desc()).offset(skip).limit(limit).all()
    return {
        "items": [r.to_dict() for r in items],
        "total": total,
        "workspace_id": workspace_id,
    }


@router.get(
    "/benchmarks/{benchmark_id}",
    summary="Get single benchmark run results by ID",
    tags=["Model Lab"],
)
async def get_benchmark_by_id(
    benchmark_id: str,
    http_req: Request,
    db: Session = Depends(get_db),
):
    """Returns detailed benchmark evaluation breakdown for a previous run."""
    workspace_id = get_workspace_id(http_req)
    record = (
        db.query(BenchmarkRecord)
        .filter(BenchmarkRecord.id == benchmark_id, BenchmarkRecord.workspace_id == workspace_id)
        .first()
    )
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Benchmark '{benchmark_id}' not found in workspace '{workspace_id}'.",
        )
    return record.get_full_results()
