"""Response schemas for LinkIntel AI matching the TypeScript contract in src/lib/linkintel.ts."""

from typing import List, Literal, Optional
from pydantic import BaseModel, Field

Evidence = Literal["extracted", "inferred", "verified"]
SeoSignalStatus = Literal["present", "missing", "potential_issue", "not_inspected"]


class Brand(BaseModel):
    name: str = Field(..., description="Identified brand or business name.")
    category: str = Field(..., description="Primary business or industry category.")
    summary: str = Field(..., description="Concise executive summary of the brand.")


class Competitor(BaseModel):
    name: str = Field(..., description="Name of the competing brand.")
    website: str = Field(..., description="Website URL or domain of the competitor.")
    category: str = Field(..., description="Competitor's market category.")
    description: str = Field(..., description="Overview of the competitor's offering.")
    strengths: List[str] = Field(default_factory=list, description="Observed competitive strengths.")
    gaps: List[str] = Field(default_factory=list, description="Observed weaknesses or missing offerings.")
    positioning: str = Field(..., description="Market positioning summary.")
    opportunity: str = Field(..., description="Strategic opportunity for our brand.")
    evidence: Evidence = Field(default="inferred", description="Provenance of this competitor entry.")
    source_urls: List[str] = Field(default_factory=list, description="Attributable external source links.")
    confidence: Optional[float] = Field(default=None, description="Confidence score if assessed.")


class SearchQuery(BaseModel):
    query: str = Field(..., description="Search query phrase.")
    platforms: List[str] = Field(..., description="Target search or social platforms (Google, LinkedIn, etc.).")
    intent: str = Field(..., description="Search intent: Informational, Commercial, Transactional, etc.")
    relevance: str = Field(..., description="Why this query is commercially relevant.")
    audience: str = Field(..., description="Target audience segment searching for this query.")


class SeoSignal(BaseModel):
    name: str = Field(..., description="Name of the technical signal (e.g. Title tag, Meta description).")
    value: Optional[str] = Field(default=None, description="Extracted value or state.")
    status: SeoSignalStatus = Field(..., description="Signal status: present, missing, potential_issue, not_inspected.")
    note: str = Field(..., description="Diagnostic observation note.")


class ServiceInsight(BaseModel):
    name: str = Field(..., description="Name of the offered service or product.")
    description: str = Field(..., description="Description of the service.")
    target_industry: str = Field(..., description="Target industry vertical.")
    target_customer: str = Field(..., description="Ideal customer persona.")
    benefit: str = Field(..., description="Primary customer value proposition or benefit.")
    evidence: Evidence = Field(default="extracted", description="Provenance: extracted from page or inferred.")
    source: Optional[str] = Field(default=None, description="Source page URL where evidence was found.")


class AudienceProfile(BaseModel):
    name: str = Field(..., description="Persona title (e.g. The Early-Stage Founder).")
    business_type: str = Field(..., description="Customer business profile.")
    needs: List[str] = Field(default_factory=list, description="Identified core needs.")
    challenges: List[str] = Field(default_factory=list, description="Identified pain points.")
    services: List[str] = Field(default_factory=list, description="Relevant services addressing their needs.")
    opportunity: str = Field(..., description="Recommended marketing angle or strategic opportunity.")
    evidence: Evidence = Field(default="inferred", description="Evidence classification.")


class CompetitorAnalysis(BaseModel):
    overview: str = Field(..., description="Market framing and competitive landscape overview.")
    competitors: List[Competitor] = Field(default_factory=list, description="List of competitors.")
    strengths: List[str] = Field(default_factory=list, description="Submitted brand's core strengths.")
    weaknesses: List[str] = Field(default_factory=list, description="Observed brand weaknesses or gaps.")
    advantages: List[str] = Field(default_factory=list, description="Key brand competitive advantages.")
    opportunities: List[str] = Field(default_factory=list, description="Market positioning opportunities.")
    evidence: List[str] = Field(default_factory=list, description="Evidence source URLs.")


class SeoImprovements(BaseModel):
    primary_keyword: str = Field(..., description="Target primary keyword.")
    secondary_keywords: List[str] = Field(default_factory=list, description="Supporting secondary keywords.")
    long_tail_keywords: List[str] = Field(default_factory=list, description="Long-tail keyword phrases.")
    business_keywords: List[str] = Field(default_factory=list, description="Core business keywords.")
    current_title: Optional[str] = Field(default=None, description="Actual page title from extraction.")
    recommended_title: str = Field(..., description="AI-recommended SEO-optimized title tag.")
    title_reason: str = Field(..., description="Rationale for title recommendation.")
    current_meta_description: Optional[str] = Field(default=None, description="Extracted meta description.")
    recommended_meta_description: str = Field(..., description="AI-recommended meta description.")
    business_summary: str = Field(..., description="Concise business summary for meta copy.")
    supporting_content: List[str] = Field(default_factory=list, description="Content ideas to build topical authority.")
    technical_findings: List[SeoSignal] = Field(default_factory=list, description="Extracted technical SEO observations.")
    search_volume_note: str = Field(
        default="No verified search-volume data available; recommendations are strategy-led.",
        description="Search volume disclaimer.",
    )


class TargetAudience(BaseModel):
    primary_audience: str = Field(..., description="Primary customer demographic / role.")
    secondary_audience: List[str] = Field(default_factory=list, description="Secondary customer segments.")
    industry_segments: List[str] = Field(default_factory=list, description="Target industry sectors.")
    business_types: List[str] = Field(default_factory=list, description="Target business types (e.g. B2B, Startups).")
    profiles: List[AudienceProfile] = Field(default_factory=list, description="Structured customer personas.")
    geographic_focus: List[str] = Field(default_factory=list, description="Geographic presence or target regions.")
    needs: List[str] = Field(default_factory=list, description="Aggregate customer needs.")
    challenges: List[str] = Field(default_factory=list, description="Aggregate customer pain points.")
    interests: List[str] = Field(default_factory=list, description="Relevant professional topics and interests.")
    marketing_segments: List[str] = Field(default_factory=list, description="High-priority marketing segments.")


class AnalysisBundle(BaseModel):
    competitor_analysis: CompetitorAnalysis
    target_search_queries: List[SearchQuery]
    seo_improvements: SeoImprovements
    top_services: List[ServiceInsight]
    target_audience: TargetAudience


class CostBreakdown(BaseModel):
    provider: str = Field(..., description="LLM provider name.")
    model: str = Field(..., description="LLM model identifier.")
    input_tokens: Optional[int] = Field(default=None, description="Count of input tokens processed.")
    output_tokens: Optional[int] = Field(default=None, description="Count of output tokens generated.")
    total_tokens: Optional[int] = Field(default=None, description="Total tokens consumed.")
    input_cost_usd: Optional[float] = Field(default=None, description="Calculated input cost in USD.")
    output_cost_usd: Optional[float] = Field(default=None, description="Calculated output cost in USD.")
    total_estimated_cost_usd: Optional[float] = Field(default=None, description="Total estimated cost in USD.")
    pricing_source: str = Field(
        default="https://ai.google.dev/gemini-api/docs/pricing",
        description="Official published pricing documentation URL.",
    )
    pricing_verification_date: str = Field(
        default="November 2026",
        description="Date when published pricing was verified.",
    )


class ReportMetadata(BaseModel):
    report_id: str = Field(..., description="Unique analysis report identifier.")
    analyzed_at: str = Field(..., description="ISO 8601 timestamp of analysis execution.")
    page_title: Optional[str] = Field(default=None, description="Scraped page title.")
    canonical_url: Optional[str] = Field(default=None, description="Scraped canonical URL.")
    extraction_warnings: List[str] = Field(default_factory=list, description="Warnings encountered during extraction.")
    sample_data: bool = Field(default=False, description="Flag indicating if this is an illustrative sample.")
    model: Optional[str] = Field(default=None, description="Identifier of the LLM model that generated the report.")
    cost_breakdown: Optional[CostBreakdown] = Field(default=None, description="Microdollar token cost metrics.")


class LinkAnalysisResponse(BaseModel):
    success: bool = Field(default=True, description="Indicates successful analysis.")
    website: str = Field(..., description="Analyzed website URL.")
    brand: Brand = Field(..., description="Identified brand overview.")
    analysis: AnalysisBundle = Field(..., description="Five structured intelligence sections.")
    metadata: ReportMetadata = Field(..., description="Report generation metadata.")
