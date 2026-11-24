"""Schemas for Multi-Model Research Lab, provider benchmarks, and cost comparisons."""

from typing import List, Optional
from pydantic import BaseModel, Field


class ProviderStatusItem(BaseModel):
    provider: str = Field(..., description="Provider identifier (gemini, openai, anthropic).")
    name: str = Field(..., description="Human-readable provider name.")
    model: str = Field(..., description="Model identifier used for analysis.")
    configured: bool = Field(..., description="Whether API credentials are set in environment.")
    input_rate_per_million: float = Field(..., description="Published price per 1M input tokens (USD).")
    output_rate_per_million: float = Field(..., description="Published price per 1M output tokens (USD).")
    context_window: str = Field(..., description="Context window capacity.")
    pricing_source: str = Field(..., description="Official documentation link for pricing.")
    structured_output_mode: str = Field(..., description="Mechanism used to enforce structured output.")


class ProviderStatusResponse(BaseModel):
    providers: List[ProviderStatusItem]
    timestamp: str


class BenchmarkRunRequest(BaseModel):
    url: Optional[str] = Field(default="https://example.com", description="Target website or test URL to benchmark.")
    test_content: Optional[str] = Field(default=None, description="Optional custom test content for prompt benchmarking.")
    providers: List[str] = Field(
        default_factory=lambda: ["gemini", "openai", "anthropic"],
        description="List of provider IDs to include in the benchmark.",
    )


class ModelBenchmarkResult(BaseModel):
    provider: str
    model: str
    name: str
    configured: bool
    status: str = Field(..., description="success, unconfigured, or failed")
    latency_seconds: float = 0.0
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None
    total_tokens: Optional[int] = None
    estimated_cost_usd: Optional[float] = None
    schema_valid: bool = False
    completeness_score: int = 0
    quality_score: int = 0
    brand_extracted: Optional[str] = None
    competitors_count: int = 0
    services_count: int = 0
    queries_count: int = 0
    error: Optional[str] = None
    error_code: Optional[str] = None


class BenchmarkRunResponse(BaseModel):
    benchmark_id: str
    timestamp: str
    target_url: str
    results: List[ModelBenchmarkResult]
    summary: str
    cheapest_model: Optional[str] = None
    fastest_model: Optional[str] = None
    highest_quality_model: Optional[str] = None
