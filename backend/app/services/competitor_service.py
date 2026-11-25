"""Competitor research and candidate discovery service with live search provider adapters."""

import logging
import re
from typing import List, Optional, Set
from urllib.parse import urlparse
import httpx
from bs4 import BeautifulSoup

from ..schemas.response import Competitor, Evidence

logger = logging.getLogger("linkintel.competitor")

# Known review aggregators, search engines, and social/news portals that should not be classified as competitors
AGGREGATOR_DOMAINS: Set[str] = {
    "wikipedia.org",
    "g2.com",
    "capterra.com",
    "trustradius.com",
    "trustpilot.com",
    "reddit.com",
    "quora.com",
    "medium.com",
    "linkedin.com",
    "twitter.com",
    "x.com",
    "facebook.com",
    "instagram.com",
    "youtube.com",
    "github.com",
    "crunchbase.com",
    "techcrunch.com",
    "forbes.com",
    "businessinsider.com",
    "bloomberg.com",
    "google.com",
    "bing.com",
    "duckduckgo.com",
    "yahoo.com",
    "amazon.com",
    "ebay.com",
    "pinterest.com",
    "glassdoor.com",
    "indeed.com",
    "stackoverflow.com",
    "tiktok.com",
    "techradar.com",
    "pcmag.com",
    "zdnet.com",
    "cnet.com",
    "softwareadvice.com",
    "getapp.com",
    "clutch.co",
    "upwork.com",
    "fiverr.com",
}


class CompetitorResearchService:
    """
    Handles live competitor discovery, search-provider integration,
    and rigorous evidence classification (extracted, inferred, verified).
    """

    def __init__(self, search_provider: str = "duckduckgo", api_key: str = ""):
        self.search_provider = (search_provider or "").lower().strip()
        self.api_key = (api_key or "").strip().strip("'\"")

    async def discover_competitors(
        self,
        brand_name: str,
        category: str,
        services: List[str],
        submitted_domain: str = "",
    ) -> List[Competitor]:
        """
        Queries an external search provider to find verified industry peers.
        Returns a list of evidence-backed Competitor instances with real source URLs.
        """
        clean_brand = brand_name.strip()
        clean_cat = category.strip()
        if not clean_brand and not clean_cat:
            return []

        search_query = f"{clean_brand} {clean_cat} top competitors alternatives"
        logger.info(f"Conducting competitor search for '{clean_brand}' using provider '{self.search_provider}'")

        try:
            if self.search_provider == "brave" and self.api_key:
                return await self._search_brave(search_query, clean_brand, submitted_domain, clean_cat)
            elif self.search_provider == "tavily" and self.api_key:
                return await self._search_tavily(search_query, clean_brand, submitted_domain, clean_cat)
            elif self.search_provider in ("duckduckgo", "ddg", ""):
                return await self._search_duckduckgo(search_query, clean_brand, submitted_domain, clean_cat)
        except Exception as e:
            logger.warning(f"Live competitor search failed ({self.search_provider}): {e}. Continuing with inferred analysis.")

        return []

    def _build_candidate(
        self,
        title: str,
        snippet: str,
        target_url: str,
        brand_name: str,
        category: str,
        submitted_domain: str,
        seen_domains: Set[str],
    ) -> Optional[Competitor]:
        """
        Validates, filters, and builds an attributable Competitor candidate.
        Returns None if the result is an aggregator, duplicate, self-reference, or irrelevant directory listicle.
        """
        if not target_url or not target_url.startswith("http"):
            return None

        parsed_url = urlparse(target_url)
        netloc = parsed_url.netloc.lower().replace("www.", "")

        if not netloc:
            return None

        # Check self-domain, seen domains, and known aggregator/portal networks
        sub_clean = submitted_domain.lower().replace("www.", "").strip()
        if sub_clean and (netloc == sub_clean or netloc.endswith(f".{sub_clean}")):
            return None

        if netloc in seen_domains:
            return None

        if any(agg in netloc for agg in AGGREGATOR_DOMAINS):
            return None

        # Check for generic blog post / listicle paths without distinct product identity
        lower_path = parsed_url.path.lower()
        if any(p in lower_path for p in ("/blog/", "/article/", "/news/", "/press/")) and any(
            t in title.lower() for t in ("top 10", "top 5", "alternatives to", "vs ", "best ")
        ):
            return None

        # Extract plausible company name from title or netloc
        clean_title = re.split(r" - | \| | : | — ", title)[0].strip()
        generic_prefixes = ("top ", "best ", "the best ", "10 best ", "alternatives to ", "compare ")
        if any(clean_title.lower().startswith(p) for p in generic_prefixes) or len(clean_title) > 40 or brand_name.lower() in clean_title.lower():
            comp_name = netloc.split(".")[0].capitalize()
        else:
            comp_name = clean_title or netloc.split(".")[0].capitalize()

        # Determine direct vs indirect competitor type
        clean_cat = (category or "").lower()
        snippet_lower = (snippet or "").lower()
        title_lower = (title or "").lower()

        is_direct = any(term in snippet_lower or term in title_lower for term in clean_cat.split() if len(term) > 3)
        comp_type = "direct" if is_direct else "indirect"
        evidence_provenance: Evidence = "verified" if is_direct else "inferred"
        confidence_score = 0.85 if is_direct else 0.65

        # Observed strengths & gaps derived contextually without invented factual metrics
        observed_strengths = []
        if "enterprise" in snippet_lower:
            observed_strengths.append("Enterprise positioning and deployment focus")
        if "open source" in snippet_lower or "open-source" in snippet_lower:
            observed_strengths.append("Open source or community-supported model")
        if "api" in snippet_lower or "developer" in snippet_lower:
            observed_strengths.append("Developer-facing API or SDK integration")
        if not observed_strengths:
            observed_strengths = [
                f"Active commercial web presence in the {category.strip() or 'industry'} category",
                "Attributable search discovery footprint",
            ]

        observed_gaps = [
            f"Detailed capability parity against {brand_name.strip()} requires live feature-by-feature evaluation"
        ]

        seen_domains.add(netloc)

        return Competitor(
            name=comp_name,
            website=f"https://{netloc}",
            category=f"{category.strip() or 'Industry'} competitor",
            description=snippet[:250].strip() if snippet else f"Attributable commercial peer operating in the {category.strip() or 'target'} market space.",
            strengths=observed_strengths,
            gaps=observed_gaps,
            positioning=f"{comp_type.capitalize()} market peer to {brand_name.strip()} operating under domain {netloc}.",
            opportunity=f"Differentiate {brand_name.strip()} through specialized features, superior developer experience, and transparent pricing.",
            evidence=evidence_provenance,
            source_urls=[target_url],
            confidence=confidence_score,
            competitor_type=comp_type,
        )

    async def _search_duckduckgo(
        self,
        query: str,
        brand_name: str,
        submitted_domain: str,
        category: str = "",
    ) -> List[Competitor]:
        """Searches DuckDuckGo HTML endpoint without requiring third-party API keys."""
        url = "https://html.duckduckgo.com/html/"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml",
        }
        data = {"q": query}

        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            res = await client.post(url, headers=headers, data=data)
            if res.status_code != 200:
                logger.warning(f"DuckDuckGo returned status {res.status_code}")
                return []

            soup = BeautifulSoup(res.text, "html.parser")
            candidates: List[Competitor] = []
            seen_domains = {submitted_domain.lower().replace("www.", "")}

            for result in soup.find_all("div", class_="result"):
                link_tag = result.find("a", class_="result__url")
                title_tag = result.find("a", class_="result__title")
                snippet_tag = result.find("a", class_="result__snippet")

                if not link_tag or not title_tag:
                    continue

                raw_href = link_tag.get("href", "").strip()
                if "uddg=" in raw_href:
                    import urllib.parse
                    parsed = urllib.parse.parse_qs(urllib.parse.urlparse(raw_href).query)
                    target_url = parsed.get("uddg", [raw_href])[0]
                else:
                    target_url = raw_href

                title = title_tag.get_text().strip()
                snippet = snippet_tag.get_text().strip() if snippet_tag else ""

                candidate = self._build_candidate(
                    title=title,
                    snippet=snippet,
                    target_url=target_url,
                    brand_name=brand_name,
                    category=category or brand_name,
                    submitted_domain=submitted_domain,
                    seen_domains=seen_domains,
                )
                if candidate:
                    candidates.append(candidate)
                    if len(candidates) >= 3:
                        break

            return candidates

    async def _search_brave(
        self,
        query: str,
        brand_name: str,
        submitted_domain: str,
        category: str = "",
    ) -> List[Competitor]:
        """Queries Brave Search API."""
        url = "https://api.search.brave.com/res/v1/web/search"
        headers = {"X-Subscription-Token": self.api_key, "Accept": "application/json"}
        params = {"q": query, "count": 10}

        async with httpx.AsyncClient(timeout=10.0) as client:
            res = await client.get(url, headers=headers, params=params)
            if res.status_code != 200:
                return []

            data = res.json()
            results = data.get("web", {}).get("results", [])
            candidates: List[Competitor] = []
            seen_domains = {submitted_domain.lower().replace("www.", "")}

            for item in results:
                target_url = item.get("url", "")
                title = item.get("title", "")
                snippet = item.get("description", "")

                candidate = self._build_candidate(
                    title=title,
                    snippet=snippet,
                    target_url=target_url,
                    brand_name=brand_name,
                    category=category or brand_name,
                    submitted_domain=submitted_domain,
                    seen_domains=seen_domains,
                )
                if candidate:
                    candidates.append(candidate)
                    if len(candidates) >= 3:
                        break

            return candidates

    async def _search_tavily(
        self,
        query: str,
        brand_name: str,
        submitted_domain: str,
        category: str = "",
    ) -> List[Competitor]:
        """Queries Tavily AI Search API."""
        url = "https://api.tavily.com/search"
        payload = {"api_key": self.api_key, "query": query, "max_results": 10}

        async with httpx.AsyncClient(timeout=10.0) as client:
            res = await client.post(url, json=payload)
            if res.status_code != 200:
                return []

            data = res.json()
            results = data.get("results", [])
            candidates: List[Competitor] = []
            seen_domains = {submitted_domain.lower().replace("www.", "")}

            for item in results:
                target_url = item.get("url", "")
                title = item.get("title", "")
                snippet = item.get("content", "")

                candidate = self._build_candidate(
                    title=title,
                    snippet=snippet,
                    target_url=target_url,
                    brand_name=brand_name,
                    category=category or brand_name,
                    submitted_domain=submitted_domain,
                    seen_domains=seen_domains,
                )
                if candidate:
                    candidates.append(candidate)
                    if len(candidates) >= 3:
                        break

            return candidates

    def classify_evidence(
        self,
        competitor: Competitor,
        on_page_text: str = "",
        verified_sources: Optional[Set[str]] = None,
    ) -> Evidence:
        """
        Accurately and strictly classifies competitor provenance:
        - 'extracted': explicitly mentioned on the submitted website HTML text
        - 'verified': corroborated via live web search with actual verified source URLs
        - 'inferred': reasoned hypothesis generated by LLM from site context (never fabricated as verified)
        """
        # Check if competitor is explicitly mentioned in the original website HTML text
        if on_page_text and competitor.name and len(competitor.name) > 2:
            pattern = rf"\b{re.escape(competitor.name)}\b"
            if re.search(pattern, on_page_text, re.IGNORECASE):
                return "extracted"

        # Check if competitor was confirmed by external search provider
        if verified_sources:
            comp_domain = urlparse(competitor.website or "").netloc.lower().replace("www.", "")
            comp_name = competitor.name.lower().strip()
            for src in verified_sources:
                src_clean = src.lower().replace("www.", "")
                if comp_domain and (comp_domain in src_clean or src_clean in comp_domain):
                    return "verified"
                if comp_name and comp_name in src_clean:
                    return "verified"

        # If competitor has confirmed source URLs from verified discovery
        if competitor.source_urls and any(u.startswith("http") for u in competitor.source_urls) and (competitor.confidence or 0) >= 0.8:
            return "verified"

        # All other claims without external verification are reasoned hypotheses
        return "inferred"
