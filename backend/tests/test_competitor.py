"""Tests for competitor research, evidence classification, deduplication, and aggregator filtering."""

import pytest
from app.schemas.response import Competitor
from app.services.competitor_service import CompetitorResearchService, AGGREGATOR_DOMAINS


def test_competitor_candidate_rejection_aggregators():
    """Verify that known directory and review aggregator domains are strictly rejected."""
    service = CompetitorResearchService()
    seen = set()

    for agg in ["g2.com", "capterra.com", "trustpilot.com", "wikipedia.org", "reddit.com", "clutch.co"]:
        cand = service._build_candidate(
            title=f"Best Cloud Services on {agg}",
            snippet="Compare user reviews and ratings.",
            target_url=f"https://www.{agg}/categories/cloud",
            brand_name="Acme",
            category="Cloud Services",
            submitted_domain="acme.example",
            seen_domains=seen,
        )
        assert cand is None, f"Expected {agg} to be rejected as aggregator"


def test_competitor_candidate_rejection_self_and_duplicates():
    """Verify that the analyzed website domain and duplicate domains are rejected."""
    service = CompetitorResearchService()
    seen = {"peerone.com"}

    # Self-domain rejection
    self_cand = service._build_candidate(
        title="Acme Cloud Solutions",
        snippet="Acme enterprise cloud architecture.",
        target_url="https://acme.example/about",
        brand_name="Acme",
        category="Cloud",
        submitted_domain="acme.example",
        seen_domains=seen,
    )
    assert self_cand is None

    # Subdomain of self rejection
    sub_cand = service._build_candidate(
        title="Acme Docs",
        snippet="Acme developer documentation.",
        target_url="https://docs.acme.example",
        brand_name="Acme",
        category="Cloud",
        submitted_domain="acme.example",
        seen_domains=seen,
    )
    assert sub_cand is None

    # Duplicate domain rejection
    dup_cand = service._build_candidate(
        title="Peer One Cloud",
        snippet="Enterprise cloud hosting.",
        target_url="https://peerone.com/pricing",
        brand_name="Acme",
        category="Cloud",
        submitted_domain="acme.example",
        seen_domains=seen,
    )
    assert dup_cand is None


def test_competitor_candidate_rejection_listicles():
    """Verify that generic blog listicle articles without product identity are rejected."""
    service = CompetitorResearchService()
    seen = set()

    listicle_cand = service._build_candidate(
        title="Top 10 Best Alternatives to Acme in 2026",
        snippet="Here is our list of the top 10 alternatives to Acme.",
        target_url="https://techblog.example/blog/top-10-alternatives-to-acme",
        brand_name="Acme",
        category="Cloud Platform",
        submitted_domain="acme.example",
        seen_domains=seen,
    )
    assert listicle_cand is None


def test_verified_competitor_candidate_creation():
    """Verify that a legitimate commercial competitor is extracted and typed correctly."""
    service = CompetitorResearchService()
    seen = set()

    cand = service._build_candidate(
        title="ScaleCloud — Enterprise Distributed Kubernetes Platform",
        snippet="ScaleCloud provides automated enterprise Kubernetes deployment and developer API tools.",
        target_url="https://scalecloud.io",
        brand_name="Acme",
        category="Kubernetes Cloud Platform",
        submitted_domain="acme.example",
        seen_domains=seen,
    )
    assert cand is not None
    assert cand.name == "ScaleCloud"
    assert cand.website == "https://scalecloud.io"
    assert cand.evidence == "verified"
    assert cand.competitor_type == "direct"
    assert cand.source_urls == ["https://scalecloud.io"]
    assert cand.confidence == 0.85
    assert len(cand.strengths) >= 1
    assert "scalecloud.io" in seen


def test_classify_evidence_extracted_when_in_html():
    """Verify evidence is 'extracted' when explicitly mentioned in the submitted site HTML."""
    service = CompetitorResearchService()
    html_text = "Unlike LegacyHost and CloudPeer, our platform provisions in under 60 seconds."

    comp = Competitor(
        name="CloudPeer",
        website="https://cloudpeer.example",
        category="Cloud",
        description="Competitor",
        positioning="Positioning",
        opportunity="Opportunity",
        evidence="inferred",
    )
    evidence = service.classify_evidence(comp, on_page_text=html_text)
    assert evidence == "extracted"


def test_classify_evidence_inferred_when_unverified():
    """Verify evidence remains 'inferred' when neither on-page nor in verified external search results."""
    service = CompetitorResearchService()

    comp = Competitor(
        name="HypotheticalPeer",
        website="https://hypothetical.example",
        category="Cloud",
        description="Inferred peer",
        positioning="Positioning",
        opportunity="Opportunity",
        evidence="inferred",
        source_urls=[],
        confidence=None,
    )
    evidence = service.classify_evidence(
        comp,
        on_page_text="We are an independent software development agency.",
        verified_sources={"otherpeer.com"},
    )
    assert evidence == "inferred"


@pytest.mark.asyncio
async def test_search_failure_handled_transparently_without_fabrication():
    """Verify that search network failure returns an empty list without inventing fake companies."""
    # Use invalid host or dummy search provider that fails
    service = CompetitorResearchService(search_provider="invalid_provider")
    res = await service.discover_competitors(
        brand_name="Acme",
        category="Cloud",
        services=[],
        submitted_domain="acme.example",
    )
    # Must return empty list, NOT fabricated fake companies
    assert res == []
