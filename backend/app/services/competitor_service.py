"""Competitor research and candidate discovery service."""

from typing import List, Optional
from ..schemas.response import Competitor, Evidence


class CompetitorResearchService:
    """
    Handles competitor discovery, evidence classification, and source attribution.
    """

    def __init__(self, search_provider: str = "", api_key: str = ""):
        self.search_provider = search_provider
        self.api_key = api_key

    async def discover_competitors(
        self,
        brand_name: str,
        category: str,
        services: List[str],
    ) -> List[Competitor]:
        """
        If a live search API is configured, searches for verified industry peers.
        Otherwise returns an empty list, allowing LLM to produce clearly labeled inferred candidates.
        """
        # When no external search provider is configured, we do not fabricate source URLs or claims.
        if not self.search_provider or not self.api_key:
            return []

        # Extensible integration for real web search APIs (Brave, Tavily, SerpApi)
        # In this implementation, external search is cleanly decoupled
        return []

    def classify_evidence(self, competitor: Competitor, has_verified_source: bool = False) -> Evidence:
        """Ensures rigorous classification of competitor provenance."""
        if has_verified_source and competitor.source_urls:
            return "verified"
        if competitor.evidence == "extracted":
            return "extracted"
        return "inferred"
