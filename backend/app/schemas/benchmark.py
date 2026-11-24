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
    default_provider: str = "gemini"
    recommended_model: str = "gemini-2.5-flash"
    timestamp: str


class BenchmarkRunRequest(BaseModel):
    url: Optional[str] = Field(default="https://acmecloud.example", description="Target website or test URL to benchmark.")
    test_content: Optional[str] = Field(default=None, description="Optional custom test content for prompt benchmarking.")
    providers: List[str] = Field(
        default_factory=lambda: ["gemini", "openai", "anthropic"],
        description="List of provider IDs to include in the benchmark.",
    )
    mock_mode: bool = Field(default=False, description="Run in deterministic mock/simulation mode without consuming live API tokens.")
    benchmark_mode: str = Field(default="synthetic", description="'synthetic' (standard dataset) or 'live' (crawls submitted url).")


class DimensionScores(BaseModel):
    competitors: float = 0.0
    search_queries: float = 0.0
    seo: float = 0.0
    services: float = 0.0
    target_audience: float = 0.0


class ModelBenchmarkResult(BaseModel):
    provider: str
    model: str
    name: str
    configured: bool
    status: str = Field(..., description="success, unconfigured, or failed")
    simulated: bool = Field(default=False, description="True if generated via mock/simulation mode.")
    latency_seconds: float = 0.0
    latency_ms: int = 0
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None
    total_tokens: Optional[int] = None
    estimated_cost_usd: Optional[float] = None
    cost_per_thousand_analyses_usd: Optional[float] = None
    schema_valid: bool = False
    completeness_score: int = 0
    quality_score: int = 0
    brand_extracted: Optional[str] = None
    extracted_brand: Optional[str] = None
    competitors_count: int = 0
    services_count: int = 0
    queries_count: int = 0
    dimension_scores: DimensionScores = Field(default_factory=DimensionScores)
    error: Optional[str] = None
    error_message: Optional[str] = None
    error_code: Optional[str] = None


class BenchmarkRunResponse(BaseModel):
    benchmark_id: str
    timestamp: str
    target_url: str
    benchmark_mode: str = Field(default="synthetic", description="'synthetic' or 'live'")
    is_simulated: bool = Field(default=False, description="Indicates if run used simulation/mock mode.")
    results: List[ModelBenchmarkResult]
    summary: str
    cheapest_model: Optional[str] = None
    fastest_model: Optional[str] = None
    highest_quality_model: Optional[str] = None
    recommended_winner: Optional[str] = None
    recommendation_rationale: Optional[str] = None

