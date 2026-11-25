"""Tests for LinkIntel analysis models, schema contracts, and cost calculation."""

import pytest
from app.schemas.response import (
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
from app.services.cost_service import calculate_analysis_cost, PUBLISHED_PRICING


def test_link_analysis_response_schema_validation():
    # Build complete report object conforming to the TypeScript contract
    brand = Brand(
        name="Northstar Studio",
        category="Brand Strategy & Design",
        summary="Independent studio helping early-stage teams build thoughtful digital experiences.",
    )

    competitor = Competitor(
        name="DesignCraft Consultancy",
        website="https://designcraft.example",
        category="Digital Agency",
        description="High-end design agency focusing on enterprise clients.",
        strengths=["Strong portfolio", "Global presence"],
        gaps=["Higher cost tier", "Less agile engagement model"],
        positioning="Enterprise brand agency",
        opportunity="Position with founder-led agility and transparent milestone pricing.",
        evidence="inferred",
        source_urls=[],
        confidence=None,
    )

    queries = [
        SearchQuery(
            query=f"query {i}",
            platforms=["Google", "LinkedIn"],
            intent="Commercial",
            relevance="High relevance.",
            audience="Startup founders",
        )
        for i in range(1, 6)
    ]

    seo = SeoImprovements(
        primary_keyword="startup brand strategy",
        secondary_keywords=["digital design studio", "brand positioning workshop"],
        long_tail_keywords=["early stage startup brand design agency"],
        business_keywords=["branding", "web design"],
        current_title="Northstar Studio",
        recommended_title="Startup Brand Strategy & Design | Northstar Studio",
        title_reason="States value proposition before brand name.",
        current_meta_description="Northstar Studio website.",
        recommended_meta_description="Clarify your positioning and build exceptional digital experiences.",
        business_summary="Brand strategy and design.",
        supporting_content=["Case study: fintech brand launch"],
        technical_findings=[
            SeoSignal(name="Title tag", value="Northstar Studio", status="present", note="Present"),
        ],
        search_volume_note="No verified search-volume data available.",
    )

    services = [
        ServiceInsight(
            name="Brand Strategy",
            description="Core positioning workshop.",
            target_industry="Technology",
            target_customer="Founders",
            benefit="Clear differentiation in competitive markets.",
            evidence="extracted",
            source="https://northstarstudio.example/services",
        )
    ]

    audience = TargetAudience(
        primary_audience="Founders of early-stage tech businesses",
        secondary_audience=["In-house marketing leads"],
        industry_segments=["SaaS", "Fintech"],
        business_types=["Startups", "Scaleups"],
        profiles=[
            AudienceProfile(
                name="The Early-Stage Founder",
                business_type="Seed-stage Startup",
                needs=["Clear messaging", "Investor-ready brand"],
                challenges=["Limited bandwidth", "Market noise"],
                services=["Brand Strategy"],
                opportunity="Lead with rapid discovery sprint.",
                evidence="inferred",
            )
        ],
        geographic_focus=["North America", "Remote-first"],
        needs=["Clear positioning"],
        challenges=["Brand confusion"],
        interests=["Product growth"],
        marketing_segments=["Pre-Series A Founders"],
    )

    bundle = AnalysisBundle(
        competitor_analysis=CompetitorAnalysis(
            overview="Landscape assessment.",
            competitors=[competitor],
            strengths=["Focused service scope"],
            weaknesses=["Smaller team size"],
            advantages=["Personalized founder access"],
            opportunities=["Specialization in early-stage tech"],
            evidence=["https://northstarstudio.example"],
        ),
        target_search_queries=queries,
        seo_improvements=seo,
        top_services=services,
        target_audience=audience,
    )

    metadata = ReportMetadata(
        report_id="rpt-test-12345",
        analyzed_at="2026-11-18T12:00:00Z",
        page_title="Northstar Studio",
        canonical_url="https://northstarstudio.example",
        extraction_warnings=[],
        sample_data=False,
        model="gemini (gemini-2.5-flash)",
    )

    response = LinkAnalysisResponse(
        success=True,
        website="https://northstarstudio.example",
        brand=brand,
        analysis=bundle,
        metadata=metadata,
    )

    assert response.success is True
    assert len(response.analysis.target_search_queries) == 5
    assert response.analysis.competitor_analysis.competitors[0].evidence in ("extracted", "inferred", "verified")
    assert response.metadata.sample_data is False


def test_cost_service_calculation():
    # Gemini 2.5 Flash: $0.30 / 1M input, $2.50 / 1M output (November 2026 verified)
    cost_gemini = calculate_analysis_cost(
        model_name="gemini-2.5-flash",
        input_tokens=10_000,
        output_tokens=2_000,
    )
    assert cost_gemini.is_measured is True
    # (10000 / 1M * 0.30) = 0.0030, (2000 / 1M * 2.50) = 0.0050 -> total = 0.0080
    assert cost_gemini.total_cost_usd == pytest.approx(0.0080, rel=1e-3)

    # OpenAI GPT-4o-mini: $0.15 / 1M input, $0.60 / 1M output
    cost_openai = calculate_analysis_cost(
        model_name="gpt-4o-mini",
        input_tokens=10_000,
        output_tokens=2_000,
    )
    assert cost_openai.is_measured is True
    # (10000 / 1M * 0.15) = 0.0015, (2000 / 1M * 0.60) = 0.0012 -> total = 0.0027
    assert cost_openai.total_cost_usd == pytest.approx(0.0027, rel=1e-3)

    # Unmeasured tokens return is_measured=False
    cost_unmeasured = calculate_analysis_cost("gemini-2.5-flash", None, None)
    assert cost_unmeasured.is_measured is False
    assert cost_unmeasured.total_cost_usd is None


def test_search_queries_five_platforms_coverage():
    from app.services.analysis_service import AnalysisService

    service = AnalysisService()
    # Test normalization when model returns only 1 query
    raw_queries = [
        SearchQuery(
            query="test query 1",
            platforms=["Google"],
            intent="Commercial",
            relevance="Relevant",
            audience="Founders",
        )
    ]
    normalized = service.normalize_search_queries(
        queries=raw_queries,
        brand_name="Test Brand",
        category="Tech Solutions",
    )
    # Must enforce exactly 5 queries
    assert len(normalized) == 5
    # Must collectively cover all 5 required platforms
    all_platforms = set()
    for q in normalized:
        all_platforms.update(p.lower() for p in q.platforms)
    for expected in ["google", "linkedin", "x", "instagram", "facebook"]:
        assert any(expected in p for p in all_platforms)


def test_report_metadata_cost_breakdown_schema():
    from app.schemas.response import CostBreakdown

    cb = CostBreakdown(
        provider="gemini",
        model="gemini-2.5-flash",
        input_tokens=1500,
        output_tokens=850,
        total_tokens=2350,
        input_cost_usd=0.000225,
        output_cost_usd=0.000510,
        total_estimated_cost_usd=0.000735,
        pricing_source="https://ai.google.dev/gemini-api/docs/pricing",
        pricing_verification_date="November 2026",
    )
    metadata = ReportMetadata(
        report_id="rpt-cost-test",
        analyzed_at="2026-11-24T12:00:00Z",
        model="gemini-2.5-flash",
        cost_breakdown=cb,
    )
    assert metadata.cost_breakdown is not None
    assert metadata.cost_breakdown.total_tokens == 2350
    assert metadata.cost_breakdown.total_estimated_cost_usd == pytest.approx(0.000735)
    assert metadata.cost_breakdown.pricing_verification_date == "November 2026"

