"""Multi-Model Research and Benchmarking Service for LinkIntel AI."""

import datetime
import logging
import time
import uuid
from typing import Dict, List, Optional

from ..config import settings
from ..providers.base import BaseLLMProvider
from ..providers.gemini import GeminiProvider
from ..providers.openai import OpenAIProvider
from ..providers.anthropic import AnthropicProvider
from ..schemas.benchmark import (
    BenchmarkRunRequest,
    BenchmarkRunResponse,
    ModelBenchmarkResult,
    ProviderStatusItem,
    ProviderStatusResponse,
)
from .analysis_service import LLMAnalysisPayload, MockProvider, SYSTEM_PROMPT
from .cost_service import PUBLISHED_PRICING, calculate_analysis_cost

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
        pass

    def get_provider_adapter(self, provider_id: str) -> BaseLLMProvider:
        """Instantiates provider adapter with environment credentials."""
        pid = provider_id.lower().strip()
        if pid == "mock":
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

    def is_provider_configured(self, provider_id: str) -> bool:
        """Checks if provider has valid credentials in environment."""
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

        return ProviderStatusResponse(providers=items, timestamp=now_iso)

    async def run_benchmark(self, request: BenchmarkRunRequest) -> BenchmarkRunResponse:
        """
        Executes an identical, controlled website intelligence task across all selected providers.
        Measures latency, token usage, cost, and schema compliance without crashing on unconfigured providers.
        """
        benchmark_id = f"bmk-{uuid.uuid4().hex[:8]}"
        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
        target_url = request.url or "https://acmecloud.example"

        content = request.test_content or STANDARD_BENCHMARK_CONTENT
        test_user_prompt = f"""Target Website: {target_url} (Domain: acmecloud.example)
Homepage Title: Acme Cloud Solutions — Enterprise Cloud Infrastructure & Kubernetes
Meta Description: High-performance cloud architecture, automated Kubernetes deployment, and developer API tools for engineering teams.
Language: en

Page Headings:
H1: Enterprise Cloud Solutions for Scale
H2: Kubernetes Architecture
H2: Developer API Integrations
H2: Security & SOC 2 Compliance

Extracted Content:
{content}
"""

        results: List[ModelBenchmarkResult] = []

        for pid in request.providers:
            pid_clean = pid.lower().strip()
            meta = PROVIDER_METADATA.get(pid_clean, {"name": pid_clean.capitalize(), "default_model": f"{pid_clean}-model"})
            model_name = meta["default_model"]
            configured = self.is_provider_configured(pid_clean)

            if not configured:
                results.append(
                    ModelBenchmarkResult(
                        provider=pid_clean,
                        model=model_name,
                        name=meta["name"],
                        configured=False,
                        status="unconfigured",
                        latency_seconds=0.0,
                        input_tokens=None,
                        output_tokens=None,
                        total_tokens=None,
                        estimated_cost_usd=None,
                        schema_valid=False,
                        completeness_score=0,
                        quality_score=0,
                        error=f"API key for {meta['name']} is not configured in backend/.env.",
                        error_code="AI_PROVIDER_NOT_CONFIGURED",
                    )
                )
                continue

            # Run benchmark against configured provider
            adapter = self.get_provider_adapter(pid_clean)
            start_time = time.perf_counter()

            try:
                llm_result = await adapter.analyze(
                    system_prompt=SYSTEM_PROMPT,
                    user_prompt=test_user_prompt,
                    response_schema=LLMAnalysisPayload,
                )
                elapsed = round(time.perf_counter() - start_time, 3)

                if llm_result.data:
                    payload: LLMAnalysisPayload = llm_result.data
                    cost_info = calculate_analysis_cost(
                        model_name=llm_result.model,
                        input_tokens=llm_result.input_tokens,
                        output_tokens=llm_result.output_tokens,
                    )

                    # Compute completeness & quality score
                    completeness = 0
                    if payload.brand and payload.brand.name:
                        completeness += 20
                    if len(payload.target_search_queries) == 5:
                        completeness += 20
                    if len(payload.competitor_analysis.competitors) >= 3:
                        completeness += 20
                    if len(payload.top_services) >= 1:
                        completeness += 20
                    if payload.target_audience and payload.target_audience.profiles:
                        completeness += 20

                    # Quality score balances completeness, valid schema, and speed
                    speed_bonus = max(0, int((5.0 - min(elapsed, 5.0)) * 2))
                    quality_score = min(100, completeness + speed_bonus)

                    results.append(
                        ModelBenchmarkResult(
                            provider=pid_clean,
                            model=llm_result.model,
                            name=meta["name"],
                            configured=True,
                            status="success",
                            latency_seconds=elapsed,
                            input_tokens=llm_result.input_tokens,
                            output_tokens=llm_result.output_tokens,
                            total_tokens=llm_result.total_tokens,
                            estimated_cost_usd=cost_info.total_cost_usd,
                            schema_valid=True,
                            completeness_score=completeness,
                            quality_score=quality_score,
                            brand_extracted=payload.brand.name,
                            competitors_count=len(payload.competitor_analysis.competitors),
                            services_count=len(payload.top_services),
                            queries_count=len(payload.target_search_queries),
                        )
                    )
                else:
                    results.append(
                        ModelBenchmarkResult(
                            provider=pid_clean,
                            model=llm_result.model,
                            name=meta["name"],
                            configured=True,
                            status="failed",
                            latency_seconds=elapsed,
                            error=llm_result.error or "Provider execution failed to produce valid schema data.",
                            error_code=llm_result.error_code or "AI_PROVIDER_ERROR",
                        )
                    )

            except Exception as e:
                elapsed = round(time.perf_counter() - start_time, 3)
                logger.error(f"Benchmark error for provider {pid_clean}: {e}")
                results.append(
                    ModelBenchmarkResult(
                        provider=pid_clean,
                        model=model_name,
                        name=meta["name"],
                        configured=True,
                        status="failed",
                        latency_seconds=elapsed,
                        error=str(e),
                        error_code="AI_PROVIDER_ERROR",
                    )
                )

        # Analyze winners among successful runs
        successful = [r for r in results if r.status == "success"]
        cheapest = None
        fastest = None
        highest_quality = None

        if successful:
            cheapest = min(
                (r for r in successful if r.estimated_cost_usd is not None),
                key=lambda x: x.estimated_cost_usd or 999.0,
                default=None,
            )
            fastest = min(successful, key=lambda x: x.latency_seconds)
            highest_quality = max(successful, key=lambda x: x.quality_score)

        summary = (
            f"Benchmark {benchmark_id} completed across {len(request.providers)} providers. "
            f"{len(successful)} successful, {len(results) - len(successful)} unconfigured or failed."
        )

        return BenchmarkRunResponse(
            benchmark_id=benchmark_id,
            timestamp=now_iso,
            target_url=target_url,
            results=results,
            summary=summary,
            cheapest_model=cheapest.model if cheapest else None,
            fastest_model=fastest.model if fastest else None,
            highest_quality_model=highest_quality.model if highest_quality else None,
        )


benchmark_service = BenchmarkService()
