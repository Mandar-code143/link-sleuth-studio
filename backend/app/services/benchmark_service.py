"""Multi-Model Research and Benchmarking Service for LinkIntel AI."""

import asyncio
import datetime
import logging
import time
import uuid
from typing import Dict, List, Optional, Tuple

from ..config import settings
from ..providers.base import BaseLLMProvider
from ..providers.gemini import GeminiProvider
from ..providers.openai import OpenAIProvider
from ..providers.anthropic import AnthropicProvider
from ..schemas.benchmark import (
    BenchmarkRunRequest,
    BenchmarkRunResponse,
    DimensionScores,
    ModelBenchmarkResult,
    ProviderStatusItem,
    ProviderStatusResponse,
)
from .analysis_service import LLMAnalysisPayload, MockProvider, SYSTEM_PROMPT
from .cost_service import PUBLISHED_PRICING, calculate_analysis_cost
from .website_extractor import WebsiteExtractor

logger = logging.getLogger("linkintel.benchmark")

PROVIDER_METADATA = {
    "gemini": {
        "name": "Google Gemini",
        "default_model": "gemini-2.5-flash",
        "context_window": "1,048,576 tokens",
        "structured_mode": "Native Pydantic Schema Mode",
        "pricing_source": "https://ai.google.dev/gemini-api/docs/pricing",
    },
    "openai": {
        "name": "OpenAI",
        "default_model": "gpt-4o-mini",
        "context_window": "128,000 tokens",
        "structured_mode": "JSON Object / Structured Outputs",
        "pricing_source": "https://developers.openai.com/api/docs/pricing",
    },
    "anthropic": {
        "name": "Anthropic Claude",
        "default_model": "claude-3-5-haiku-20241022",
        "context_window": "200,000 tokens",
        "structured_mode": "Messages API JSON Schema Enforcement",
        "pricing_source": "https://platform.claude.com/docs/en/about-claude/pricing",
    },
}

STANDARD_BENCHMARK_CONTENT = """Acme Cloud Solutions (acmecloud.example) is an enterprise cloud architecture and distributed systems engineering platform.
We provide turnkey Kubernetes cluster deployment, multi-cloud API gateways, automated infrastructure provisioning, and continuous SOC 2 compliance monitoring.
Our customers include high-growth B2B SaaS startups, mid-market fintech engineering teams, and enterprise digital organizations.
Key solutions include:
1. Managed Kubernetes Platform — Automated cluster lifecycle, zero-downtime rollouts, and multi-region failover.
2. Cloud API Gateway & SDKs — High-throughput REST and streaming gateways for developer microservices.
3. DevOps Compliance Guardrails — Continuous policy-as-code enforcement, secret scanning, and automated audit trails.
We help VP of Engineering and Lead Cloud Architects eliminate cloud tool sprawl, speed up developer release velocity by 10x, and control runaway cloud hosting spend.
"""


class BenchmarkService:
    """Manages provider status evaluation and multi-model benchmark runs."""

    def __init__(self):
        self.extractor = WebsiteExtractor()

    def get_provider_adapter(self, provider_id: str, mock_mode: bool = False) -> BaseLLMProvider:
        """Instantiates provider adapter with environment credentials or mock mode."""
        pid = provider_id.lower().strip()
        if mock_mode or pid == "mock":
            return MockProvider()
        elif pid == "openai":
            return OpenAIProvider(
                api_key=settings.openai_api_key,
                model_name=settings.llm_model if "gpt" in settings.llm_model else "gpt-4o-mini",
            )
        elif pid == "anthropic":
            return AnthropicProvider(
                api_key=settings.anthropic_api_key,
                model_name=settings.llm_model if "claude" in settings.llm_model else "claude-3-5-haiku-20241022",
            )
        else:
            return GeminiProvider(
                api_key=settings.gemini_api_key,
                model_name=settings.llm_model if "gemini" in settings.llm_model else "gemini-2.5-flash",
            )

    def is_provider_configured(self, provider_id: str, mock_mode: bool = False) -> bool:
        """Checks if provider has valid credentials in environment."""
        if mock_mode:
            return True
        pid = provider_id.lower().strip()
        if pid == "gemini":
            return settings.is_gemini_configured
        elif pid == "openai":
            return bool(settings.openai_api_key)
        elif pid == "anthropic":
            return bool(settings.anthropic_api_key)
        elif pid == "mock":
            return True
        return False

    def get_providers_status(self) -> ProviderStatusResponse:
        """Returns runtime configuration and pricing specs for all supported models."""
        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
        items = []

        for pid, meta in PROVIDER_METADATA.items():
            model_key = meta["default_model"]
            pricing = PUBLISHED_PRICING.get(model_key)
            configured = self.is_provider_configured(pid)

            items.append(
                ProviderStatusItem(
                    provider=pid,
                    name=meta["name"],
                    model=model_key,
                    configured=configured,
                    input_rate_per_million=pricing.input_rate_per_million if pricing else 0.0,
                    output_rate_per_million=pricing.output_rate_per_million if pricing else 0.0,
                    context_window=meta["context_window"],
                    pricing_source=meta["pricing_source"],
                    structured_output_mode=meta["structured_mode"],
                )
            )

        return ProviderStatusResponse(
            providers=items,
            default_provider="gemini",
            recommended_model="gemini-2.5-flash",
            timestamp=now_iso,
        )

    def _calculate_quality_score(
        self,
        payload_data,
        schema_valid: bool = True,
        latency_seconds: float = 0.0,
    ) -> Tuple[int, int, DimensionScores]:
        """
        Calculates analytical completeness and quality score purely decoupled from latency.
        Speed / latency is measured in its own metric and never inflates or penalizes analytical quality.
        """
        if not payload_data or not schema_valid:
            return 0, 0, DimensionScores()

        if isinstance(payload_data, dict):
            brand_name = payload_data.get("brand", {}).get("name") if isinstance(payload_data.get("brand"), dict) else None
            queries = payload_data.get("search_queries") or payload_data.get("target_search_queries") or []
            queries_len = len(queries)
            comps_data = payload_data.get("competitor_analysis")
            if isinstance(comps_data, dict):
                comps = comps_data.get("competitors", [])
            else:
                comps = payload_data.get("competitors", [])
            comps_len = len(comps)
            services = payload_data.get("top_services") or payload_data.get("services") or []
            services_len = len(services)
            aud_data = payload_data.get("target_audience", {})
            has_audience = bool(
                aud_data.get("profiles") or aud_data.get("primary_audience")
                if isinstance(aud_data, dict) else False
            )
            grounded = 20 if any(
                isinstance(c, dict) and c.get("evidence") in ("extracted", "verified") for c in comps
            ) else 15
        else:
            brand_name = payload_data.brand.name if payload_data.brand else None
            queries_len = len(payload_data.target_search_queries)
            comps = payload_data.competitor_analysis.competitors
            comps_len = len(comps)
            services_len = len(payload_data.top_services)
            has_audience = bool(payload_data.target_audience and payload_data.target_audience.profiles)
            grounded = 20 if any(c.evidence in ("extracted", "verified") for c in comps) else 10

        dim_brand = 100.0 if brand_name else 0.0
        dim_queries = min(100.0, (queries_len / 5.0) * 100.0)
        dim_comps = min(100.0, (comps_len / 3.0) * 100.0)
        dim_services = min(100.0, (services_len / 1.0) * 100.0)
        dim_audience = 100.0 if has_audience else 0.0

        completeness = int(
            (dim_brand * 0.2) +
            (dim_queries * 0.2) +
            (dim_comps * 0.2) +
            (dim_services * 0.2) +
            (dim_audience * 0.2)
        )
        quality_score = min(100, int(30 + (completeness * 0.5) + grounded))

        dim_scores = DimensionScores(
            competitors=round(dim_comps, 1),
            search_queries=round(dim_queries, 1),
            seo=100.0,
            services=round(dim_services, 1),
            target_audience=round(dim_audience, 1),
        )
        return completeness, quality_score, dim_scores

    async def _evaluate_single_provider(
        self,
        pid_clean: str,
        meta: dict,
        model_name: str,
        prompt: str,
        mock_mode: bool,
    ) -> ModelBenchmarkResult:
        """Evaluates a single provider concurrently and returns structured results."""
        configured = self.is_provider_configured(pid_clean, mock_mode=mock_mode)

        if not configured:
            return ModelBenchmarkResult(
                provider=pid_clean,
                model=model_name,
                name=meta["name"],
                configured=False,
                status="unconfigured",
                simulated=False,
                latency_seconds=0.0,
                latency_ms=0,
                input_tokens=None,
                output_tokens=None,
                total_tokens=None,
                estimated_cost_usd=None,
                cost_per_thousand_analyses_usd=None,
                schema_valid=False,
                completeness_score=0,
                quality_score=0,
                dimension_scores=DimensionScores(),
                error=f"API key for {meta['name']} is not configured in backend/.env.",
                error_message=f"API key for {meta['name']} is not configured in backend/.env.",
                error_code="AI_PROVIDER_NOT_CONFIGURED",
            )

        adapter = self.get_provider_adapter(pid_clean, mock_mode=mock_mode)
        start_time = time.perf_counter()

        try:
            # 20-second timeout per provider
            llm_result = await asyncio.wait_for(
                adapter.analyze(
                    system_prompt=SYSTEM_PROMPT,
                    user_prompt=prompt,
                    response_schema=LLMAnalysisPayload,
                ),
                timeout=20.0,
            )
            elapsed = round(time.perf_counter() - start_time, 3)
            elapsed_ms = int(elapsed * 1000)

            if llm_result.data:
                payload: LLMAnalysisPayload = llm_result.data
                cost_info = calculate_analysis_cost(
                    model_name=llm_result.model if not mock_mode else model_name,
                    input_tokens=llm_result.input_tokens,
                    output_tokens=llm_result.output_tokens,
                )

                completeness, quality_score, dim_scores = self._calculate_quality_score(
                    payload,
                    schema_valid=True,
                    latency_seconds=elapsed,
                )

                cost_per_thousand = (cost_info.total_cost_usd * 1000.0) if cost_info.total_cost_usd is not None else None

                return ModelBenchmarkResult(
                    provider=pid_clean,
                    model=model_name if mock_mode else llm_result.model,
                    name=meta["name"],
                    configured=True,
                    status="success",
                    simulated=mock_mode,
                    latency_seconds=elapsed,
                    latency_ms=elapsed_ms,
                    input_tokens=llm_result.input_tokens,
                    output_tokens=llm_result.output_tokens,
                    total_tokens=llm_result.total_tokens,
                    estimated_cost_usd=cost_info.total_cost_usd,
                    cost_per_thousand_analyses_usd=cost_per_thousand,
                    schema_valid=True,
                    completeness_score=completeness,
                    quality_score=quality_score,
                    brand_extracted=payload.brand.name,
                    extracted_brand=payload.brand.name,
                    competitors_count=len(payload.competitor_analysis.competitors),
                    services_count=len(payload.top_services),
                    queries_count=len(payload.target_search_queries),
                    dimension_scores=dim_scores,
                )
            else:
                return ModelBenchmarkResult(
                    provider=pid_clean,
                    model=model_name,
                    name=meta["name"],
                    configured=True,
                    status="failed",
                    simulated=mock_mode,
                    latency_seconds=elapsed,
                    latency_ms=elapsed_ms,
                    error=llm_result.error or "Provider execution failed to produce valid schema data.",
                    error_message=llm_result.error or "Provider execution failed to produce valid schema data.",
                    error_code=llm_result.error_code or "AI_PROVIDER_ERROR",
                )

        except asyncio.TimeoutError:
            return ModelBenchmarkResult(
                provider=pid_clean,
                model=model_name,
                name=meta["name"],
                configured=True,
                status="failed",
                simulated=mock_mode,
                latency_seconds=20.0,
                latency_ms=20000,
                error="Provider request timed out after 20.0 seconds.",
                error_message="Provider request timed out after 20.0 seconds.",
                error_code="AI_PROVIDER_TIMEOUT",
            )
        except Exception as e:
            elapsed = round(time.perf_counter() - start_time, 3)
            logger.error(f"Benchmark error for provider {pid_clean}: {e}")
            return ModelBenchmarkResult(
                provider=pid_clean,
                model=model_name,
                name=meta["name"],
                configured=True,
                status="failed",
                simulated=mock_mode,
                latency_seconds=elapsed,
                latency_ms=int(elapsed * 1000),
                error=str(e),
                error_message=str(e),
                error_code="AI_PROVIDER_ERROR",
            )

    async def run_benchmark(self, request: BenchmarkRunRequest) -> BenchmarkRunResponse:
        """
        Executes an identical, controlled website intelligence task across all selected providers.
        Supports synthetic benchmark dataset mode and live website benchmark mode with bounded concurrency.
        """
        benchmark_id = f"bmk-{uuid.uuid4().hex[:8]}"
        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
        mock_mode = bool(request.mock_mode)

        # Determine benchmark mode
        is_synthetic = (
            request.benchmark_mode == "synthetic" or
            not request.url or
            "acmecloud.example" in request.url or
            "example.com" in request.url
        )

        target_url = request.url or "https://acmecloud.example"
        target_domain = "acmecloud.example"
        page_title = "Acme Cloud Solutions — Enterprise Cloud Infrastructure & Kubernetes"
        meta_desc = "High-performance cloud architecture, automated Kubernetes deployment, and developer API tools for engineering teams."
        headings_summary = "H1: Enterprise Cloud Solutions for Scale\nH2: Kubernetes Architecture\nH2: Developer API Integrations\nH2: Security & SOC 2 Compliance"
        content = request.test_content or STANDARD_BENCHMARK_CONTENT
        extraction_note = ""

        # In live benchmark mode (and not mock mode), fetch the real target URL via SSRF-safe fetcher
        if not is_synthetic and not mock_mode:
            try:
                extraction = await self.extractor.extract(target_url)
                target_url = extraction.final_url
                target_domain = extraction.domain
                page_title = extraction.title or "Target Website"
                meta_desc = extraction.meta_description or "Business website"
                headings_summary = "\n".join([f"{h['level'].upper()}: {h['text']}" for h in extraction.headings[:15]])
                content = extraction.main_content[:6000]
                extraction_note = f"Evaluated using real extracted content from {target_domain}."
            except Exception as e:
                logger.error(f"Live benchmark extraction failed for '{target_url}': {e}. Live benchmarks require real website content and never fall back to synthetic data.")
                # Return explicit failed result for live benchmark without synthetic fallback
                failed_results = []
                for pid in request.providers:
                    pid_clean = pid.lower().strip()
                    meta = PROVIDER_METADATA.get(
                        pid_clean,
                        {"name": pid_clean.capitalize(), "default_model": f"{pid_clean}-model"},
                    )
                    failed_results.append(
                        ModelBenchmarkResult(
                            provider=pid_clean,
                            model=meta["default_model"],
                            name=meta["name"],
                            configured=self.is_provider_configured(pid_clean, mock_mode=False),
                            status="failed",
                            simulated=False,
                            latency_seconds=0.0,
                            latency_ms=0,
                            error=f"Live website content extraction failed: {e}. Live benchmarks require real website extraction and will never fall back to synthetic datasets.",
                            error_message=f"Live website content extraction failed: {e}. Live benchmarks require real website extraction and will never fall back to synthetic datasets.",
                            error_code="LIVE_EXTRACTION_FAILED",
                        )
                    )
                return BenchmarkRunResponse(
                    benchmark_id=benchmark_id,
                    timestamp=now_iso,
                    target_url=target_url,
                    benchmark_mode="live",
                    is_simulated=False,
                    results=failed_results,
                    summary=f"Live benchmark failed: Unable to extract content from '{target_url}' ({e}). Live benchmarks require real extracted content and never fall back to synthetic datasets.",
                    cheapest_model=None,
                    fastest_model=None,
                    highest_quality_model=None,
                    recommended_winner=None,
                    recommendation_rationale=f"Evaluation could not be performed because live website content extraction failed: {e}",
                )

        test_user_prompt = f"""Target Website: {target_url} (Domain: {target_domain})
Homepage Title: {page_title}
Meta Description: {meta_desc}
Language: en

Page Headings:
{headings_summary}

Extracted Content:
{content}
"""

        # Build concurrent tasks for all selected providers
        tasks = []
        for pid in request.providers:
            pid_clean = pid.lower().strip()
            meta = PROVIDER_METADATA.get(
                pid_clean,
                {"name": pid_clean.capitalize(), "default_model": f"{pid_clean}-model"},
            )
            model_name = meta["default_model"]
            tasks.append(
                self._evaluate_single_provider(
                    pid_clean=pid_clean,
                    meta=meta,
                    model_name=model_name,
                    prompt=test_user_prompt,
                    mock_mode=mock_mode,
                )
            )

        # Run concurrently with asyncio.gather
        results_or_exceptions = await asyncio.gather(*tasks, return_exceptions=True)
        results: List[ModelBenchmarkResult] = []

        for item in results_or_exceptions:
            if isinstance(item, ModelBenchmarkResult):
                results.append(item)
            elif isinstance(item, Exception):
                logger.error(f"Unhandled benchmark task exception: {item}")
                results.append(
                    ModelBenchmarkResult(
                        provider="unknown",
                        model="unknown",
                        name="Provider",
                        configured=False,
                        status="failed",
                        error=str(item),
                        error_message=str(item),
                        error_code="INTERNAL_BENCHMARK_ERROR",
                    )
                )

        # Determine independent winners and neutral recommendation among successful runs
        successful = [r for r in results if r.status == "success" and r.schema_valid]
        cheapest = None
        fastest = None
        highest_quality = None
        recommended_winner = None
        recommendation_rationale = None

        if successful:
            cheapest = min(
                (r for r in successful if r.estimated_cost_usd is not None),
                key=lambda x: x.estimated_cost_usd if x.estimated_cost_usd is not None else 999.0,
                default=None,
            )
            fastest = min(successful, key=lambda x: x.latency_seconds)
            highest_quality = max(successful, key=lambda x: x.quality_score)

            # Objective multi-criteria scoring methodology:
            # 1. Structural completeness (45% weight): measures adherence to the 5 mandatory analysis sections.
            # 2. Measured latency efficiency (30% weight): normalized response speed.
            # 3. Unit cost efficiency (25% weight): token economics based on published pricing.
            min_latency = min(r.latency_seconds for r in successful)
            max_latency = max(r.latency_seconds for r in successful)
            latency_spread = max(max_latency - min_latency, 0.2)

            costs = [r.estimated_cost_usd for r in successful if r.estimated_cost_usd is not None]
            min_cost = min(costs) if costs else 0.0
            max_cost = max(costs) if costs else 0.0
            cost_spread = max(max_cost - min_cost, 0.0001)

            scored_candidates = []
            for r in successful:
                # Completeness component (0 - 100)
                comp_score = float(r.completeness_score)

                # Latency component: fastest model gets 100, others scaled by delay
                lat_score = max(0.0, 100.0 * (1.0 - (r.latency_seconds - min_latency) / latency_spread))

                # Cost component: lowest cost model gets 100, others scaled
                if r.estimated_cost_usd is not None and costs:
                    cost_score = max(0.0, 100.0 * (1.0 - (r.estimated_cost_usd - min_cost) / cost_spread))
                else:
                    cost_score = 50.0

                composite_score = round((comp_score * 0.45) + (lat_score * 0.30) + (cost_score * 0.25), 1)
                scored_candidates.append({
                    "result": r,
                    "composite": composite_score,
                    "comp": comp_score,
                    "lat": lat_score,
                    "cost": cost_score,
                })

            # Sort by composite score desc; tie-breakers: lowest latency, then lowest cost
            scored_candidates.sort(
                key=lambda x: (
                    x["composite"],
                    -x["result"].latency_seconds,
                    -(x["result"].estimated_cost_usd or 999.0),
                ),
                reverse=True,
            )

            winner_item = scored_candidates[0]
            winner_res = winner_item["result"]
            recommended_winner = winner_res.model

            mode_context = "simulated benchmark" if mock_mode else ("synthetic dataset evaluation" if is_synthetic else "live website evaluation")
            cost_str = f"${winner_res.estimated_cost_usd:.6f}/run" if winner_res.estimated_cost_usd is not None else "N/A"
            recommendation_rationale = (
                f"{winner_res.model} ranked #1 in objective multi-criteria evaluation ({mode_context}) with a composite score of "
                f"{winner_item['composite']}/100. Measured metrics: Structural completeness {winner_res.completeness_score}%, "
                f"Latency {winner_res.latency_seconds:.2f}s, Estimated cost {cost_str}. "
                f"Methodology weighted: 45% structural completeness, 30% latency efficiency, 25% cost economics."
            )
            if mock_mode:
                recommendation_rationale += " Note: Results produced via deterministic simulation mode."
            elif is_synthetic:
                recommendation_rationale += " Note: Results produced using standard synthetic benchmark content."

        mode_label = "Synthetic benchmark dataset" if is_synthetic else "Live website extraction"
        if mock_mode:
            mode_label += " (Simulated mock mode)"

        summary = (
            f"Benchmark {benchmark_id} completed across {len(request.providers)} models ({mode_label}). "
            f"{len(successful)} successful, {len(results) - len(successful)} unconfigured or failed."
        )
        if extraction_note:
            summary += f" {extraction_note}"

        return BenchmarkRunResponse(
            benchmark_id=benchmark_id,
            timestamp=now_iso,
            target_url=target_url,
            benchmark_mode="synthetic" if is_synthetic else "live",
            is_simulated=mock_mode,
            results=results,
            summary=summary,
            cheapest_model=cheapest.model if cheapest else None,
            fastest_model=fastest.model if fastest else None,
            highest_quality_model=highest_quality.model if highest_quality else None,
            recommended_winner=recommended_winner,
            recommendation_rationale=recommendation_rationale,
        )


benchmark_service = BenchmarkService()
