"""Pydantic schemas for LinkIntel AI."""

from .request import LinkAnalysisRequest
from .response import (
    Brand,
    Competitor,
    SearchQuery,
    SeoSignal,
    ServiceInsight,
    AudienceProfile,
    CompetitorAnalysis,
    SeoImprovements,
    TargetAudience,
    AnalysisBundle,
    ReportMetadata,
    LinkAnalysisResponse,
)

__all__ = [
    "LinkAnalysisRequest",
    "Brand",
    "Competitor",
    "SearchQuery",
    "SeoSignal",
    "ServiceInsight",
    "AudienceProfile",
    "CompetitorAnalysis",
    "SeoImprovements",
    "TargetAudience",
    "AnalysisBundle",
    "ReportMetadata",
    "LinkAnalysisResponse",
]
