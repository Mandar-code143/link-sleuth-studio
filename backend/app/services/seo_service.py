"""Technical SEO signal extraction and evaluation service."""

from typing import List
from ..schemas.response import SeoSignal
from .website_extractor import WebsiteExtraction, PageData


def inspect_technical_seo(extraction: WebsiteExtraction) -> List[SeoSignal]:
    """
    Analyzes extracted technical signals from the website HTML and generates
    objective diagnostic status items for the SEO report section.
    """
    signals: List[SeoSignal] = []

    # 1. Title Tag
    title = extraction.title
    if not title:
        signals.append(
            SeoSignal(
                name="Title tag",
                value=None,
                status="missing",
                note="No <title> tag was found in the page markup. Search engines will generate an automated title.",
            )
        )
    elif len(title) > 65:
        signals.append(
            SeoSignal(
                name="Title tag",
                value=f"{title[:50]}... ({len(title)} chars)",
                status="potential_issue",
                note=f"Title length ({len(title)} chars) exceeds standard search preview truncation threshold (~60 chars).",
            )
        )
    elif len(title) < 20:
        signals.append(
            SeoSignal(
                name="Title tag",
                value=title,
                status="potential_issue",
                note="Title is unusually brief and may lack primary brand or category keywords.",
            )
        )
    else:
        signals.append(
            SeoSignal(
                name="Title tag",
                value=title,
                status="present",
                note=f"Title tag is present and well-proportioned ({len(title)} characters).",
            )
        )

    # 2. Meta Description
    desc = extraction.meta_description
    if not desc:
        signals.append(
            SeoSignal(
                name="Meta description",
                value=None,
                status="missing",
                note="No meta description was defined. Search snippets will fall back to body excerpt.",
            )
        )
    elif len(desc) > 165:
        signals.append(
            SeoSignal(
                name="Meta description",
                value=f"{desc[:60]}... ({len(desc)} chars)",
                status="potential_issue",
                note=f"Meta description ({len(desc)} chars) exceeds typical desktop snippet display (~155-160 chars).",
            )
        )
    elif len(desc) < 50:
        signals.append(
            SeoSignal(
                name="Meta description",
                value=desc,
                status="potential_issue",
                note="Meta description is very short and could provide more context for search click-through.",
            )
        )
    else:
        signals.append(
            SeoSignal(
                name="Meta description",
                value=desc,
                status="present",
                note=f"Meta description is present ({len(desc)} characters).",
            )
        )

    # 3. H1 Heading structure
    h1_list = [h["text"] for h in extraction.headings if h["level"] == "h1"]
    if not h1_list:
        signals.append(
            SeoSignal(
                name="H1 heading",
                value=None,
                status="missing",
                note="No <h1> heading was located on the homepage. An H1 helps clarify page topic hierarchy.",
            )
        )
    elif len(h1_list) > 1:
        signals.append(
            SeoSignal(
                name="H1 heading",
                value=f"Found {len(h1_list)} H1 tags",
                status="potential_issue",
                note=f"Multiple H1 tags ({len(h1_list)}) were detected. Modern SEO recommends a single prominent H1.",
            )
        )
    else:
        signals.append(
            SeoSignal(
                name="H1 heading",
                value=h1_list[0],
                status="present",
                note="Single top-level H1 heading present.",
            )
        )

    # 4. Canonical URL
    canonical = extraction.canonical_url
    if canonical:
        signals.append(
            SeoSignal(
                name="Canonical URL",
                value=canonical,
                status="present",
                note="Canonical tag is specified, preventing duplicate content ambiguity across protocols or subdomains.",
            )
        )
    else:
        signals.append(
            SeoSignal(
                name="Canonical URL",
                value=None,
                status="missing",
                note="No rel='canonical' tag found on the homepage.",
            )
        )

    # 5. Open Graph Metadata
    og = extraction.open_graph
    if og and "og:title" in og:
        has_image = "og:image" in og
        signals.append(
            SeoSignal(
                name="Open Graph",
                value=f"{len(og)} properties (Image: {'yes' if has_image else 'missing'})",
                status="present" if has_image else "potential_issue",
                note="Open Graph tags present for rich social and search sharing previews.",
            )
        )
    else:
        signals.append(
            SeoSignal(
                name="Open Graph",
                value=None,
                status="missing",
                note="No Open Graph tags detected. Shared links will lack structured preview cards.",
            )
        )

    # 6. Schema.org Structured Data
    schemas = extraction.structured_data
    if schemas:
        types = [s.get("@type", "Schema") for s in schemas if isinstance(s, dict)]
        signals.append(
            SeoSignal(
                name="Structured data",
                value=", ".join(types[:3]),
                status="present",
                note=f"Found {len(schemas)} JSON-LD structured data block(s).",
            )
        )
    else:
        signals.append(
            SeoSignal(
                name="Structured data",
                value=None,
                status="missing",
                note="No Schema.org JSON-LD found for business or organization entity disambiguation.",
            )
        )

    # 7. Language attribute
    lang = extraction.language
    if lang:
        signals.append(
            SeoSignal(
                name="Page language",
                value=lang,
                status="present",
                note=f"HTML lang attribute explicitly configured ('{lang}').",
            )
        )
    else:
        signals.append(
            SeoSignal(
                name="Page language",
                value=None,
                status="potential_issue",
                note="HTML tag is missing the lang attribute for internationalization & screen readers.",
            )
        )

    # 8. HTTPS Protocol & Transport Security
    is_https = extraction.final_url.lower().startswith("https://")
    if is_https:
        signals.append(
            SeoSignal(
                name="HTTPS security",
                value="Enabled (HTTPS)",
                status="present",
                note="Website is served securely over TLS/HTTPS, satisfying modern security standards and ranking signals.",
            )
        )
    else:
        signals.append(
            SeoSignal(
                name="HTTPS security",
                value="Insecure (HTTP)",
                status="potential_issue",
                note="Website is served over unencrypted HTTP. Search engines penalize insecure sites and browsers display warnings.",
            )
        )

    # 9. Robots Directives
    robots = extraction.meta_robots
    if robots:
        has_noindex = "noindex" in robots.lower()
        signals.append(
            SeoSignal(
                name="Robots directives",
                value=robots,
                status="potential_issue" if has_noindex else "present",
                note="Disallows indexing (noindex detected)!" if has_noindex else "Explicit robots crawling directives defined.",
            )
        )
    else:
        signals.append(
            SeoSignal(
                name="Robots directives",
                value="Default (index, follow)",
                status="present",
                note="No blocking meta robots tags detected; search engines will index and follow links by default.",
            )
        )

    return signals
