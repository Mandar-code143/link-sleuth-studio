"""LLM token pricing calculations and cost optimization service."""

from dataclasses import dataclass
from typing import Dict, Optional


@dataclass(frozen=True)
class ModelPricing:
    provider: str
    model: str
    input_rate_per_million: float
    output_rate_per_million: float
    effective_date: str
    pricing_source: str
    verification_date: str = "November 2026"
    currency: str = "USD"


# Authoritative, documented provider pricing verified for November 2026
PUBLISHED_PRICING: Dict[str, ModelPricing] = {
    # Google Gemini (Standard Pay-as-you-go <=128k prompt context)
    "gemini-2.5-flash": ModelPricing(
        provider="gemini",
        model="gemini-2.5-flash",
        input_rate_per_million=0.30,
        output_rate_per_million=2.50,
        effective_date="2026-11-20",
        pricing_source="https://ai.google.dev/gemini-api/docs/pricing",
        verification_date="November 2026",
    ),
    "gemini-1.5-flash": ModelPricing(
        provider="gemini",
        model="gemini-1.5-flash",
        input_rate_per_million=0.075,
        output_rate_per_million=0.30,
        effective_date="2024-05-14",
        pricing_source="https://ai.google.dev/gemini-api/docs/pricing",
        verification_date="November 2026",
    ),
    "gemini-1.5-pro": ModelPricing(
        provider="gemini",
        model="gemini-1.5-pro",
        input_rate_per_million=1.25,
        output_rate_per_million=5.00,
        effective_date="2024-05-14",
        pricing_source="https://ai.google.dev/gemini-api/docs/pricing",
        verification_date="November 2026",
    ),
    # OpenAI (Standard API pricing)
    "gpt-4o-mini": ModelPricing(
        provider="openai",
        model="gpt-4o-mini",
        input_rate_per_million=0.15,
        output_rate_per_million=0.60,
        effective_date="2024-07-18",
        pricing_source="https://developers.openai.com/api/docs/pricing",
        verification_date="November 2026",
    ),
    "gpt-4o": ModelPricing(
        provider="openai",
        model="gpt-4o",
        input_rate_per_million=2.50,
        output_rate_per_million=10.00,
        effective_date="2024-08-01",
        pricing_source="https://developers.openai.com/api/docs/pricing",
        verification_date="November 2026",
    ),
    # Anthropic Claude
    "claude-3-5-haiku-20241022": ModelPricing(
        provider="anthropic",
        model="claude-3-5-haiku-20241022",
        input_rate_per_million=0.80,
        output_rate_per_million=4.00,
        effective_date="2024-10-22",
        pricing_source="https://platform.claude.com/docs/en/about-claude/pricing",
        verification_date="November 2026",
    ),
    "claude-3-5-sonnet-20241022": ModelPricing(
        provider="anthropic",
        model="claude-3-5-sonnet-20241022",
        input_rate_per_million=3.00,
        output_rate_per_million=15.00,
        effective_date="2024-10-22",
        pricing_source="https://platform.claude.com/docs/en/about-claude/pricing",
        verification_date="November 2026",
    ),
}


@dataclass
class CostBreakdown:
    provider: str
    model: str
    input_tokens: Optional[int]
    output_tokens: Optional[int]
    input_cost_usd: Optional[float]
    output_cost_usd: Optional[float]
    total_cost_usd: Optional[float]
    is_measured: bool
    pricing_source: Optional[str]
    pricing_verification_date: str = "November 2026"


def calculate_analysis_cost(
    model_name: str,
    input_tokens: Optional[int],
    output_tokens: Optional[int],
) -> CostBreakdown:
    """
    Calculates cost for an analysis run based on measured tokens and published rates.
    Explicitly distinguishes measured vs unavailable metrics.
    """
    # Normalize model key
    lookup_key = model_name.lower().strip()
    pricing = PUBLISHED_PRICING.get(lookup_key)
    if not pricing:
        for k, v in PUBLISHED_PRICING.items():
            if k in lookup_key:
                pricing = v
                break

    if not pricing or input_tokens is None or output_tokens is None:
        return CostBreakdown(
            provider=pricing.provider if pricing else "unknown",
            model=model_name,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            input_cost_usd=None,
            output_cost_usd=None,
            total_cost_usd=None,
            is_measured=False,
            pricing_source=pricing.pricing_source if pricing else None,
            pricing_verification_date="November 2026",
        )

    in_cost = (input_tokens / 1_000_000) * pricing.input_rate_per_million
    out_cost = (output_tokens / 1_000_000) * pricing.output_rate_per_million
    total = in_cost + out_cost

    return CostBreakdown(
        provider=pricing.provider,
        model=pricing.model,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        input_cost_usd=round(in_cost, 6),
        output_cost_usd=round(out_cost, 6),
        total_cost_usd=round(total, 6),
        is_measured=True,
        pricing_source=pricing.pricing_source,
        pricing_verification_date=pricing.verification_date,
    )
