"""Website extraction service using Trafilatura and BeautifulSoup with multi-page discovery."""

import json
import re
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set
from urllib.parse import urljoin, urlparse

from ..security.safe_fetcher import safe_fetch_url, SafeFetchError
from ..security.url_validator import validate_and_normalize_url
from .content_cleaner import clean_text_block, sanitize_for_prompt_context

# Try importing trafilatura and bs4 with graceful standard-library fallbacks
try:
    import trafilatura
except ImportError:
    trafilatura = None

try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None


@dataclass
class PageData:
    url: str
    title: Optional[str] = None
    meta_description: Optional[str] = None
    h1: List[str] = field(default_factory=list)
    h2: List[str] = field(default_factory=list)
    h3: List[str] = field(default_factory=list)
    main_text: str = ""
    canonical: Optional[str] = None
    language: Optional[str] = None
    viewport: Optional[str] = None
    open_graph: Dict[str, str] = field(default_factory=dict)
    twitter_cards: Dict[str, str] = field(default_factory=dict)
    schema_org: List[dict] = field(default_factory=list)
    meta_robots: Optional[str] = None
    internal_links: List[str] = field(default_factory=list)
    external_links: List[str] = field(default_factory=list)
    images_with_alt: List[Dict[str, str]] = field(default_factory=list)
    images_missing_alt_count: int = 0


@dataclass
class WebsiteExtraction:
    requested_url: str
    final_url: str
    domain: str
    title: Optional[str]
    meta_description: Optional[str]
    headings: List[Dict[str, str]]
    main_content: str
    internal_pages: List[PageData]
    canonical_url: Optional[str]
    language: Optional[str]
    structured_data: List[dict]
    open_graph: Dict[str, str]
    meta_robots: Optional[str]
    viewport: Optional[str] = None
    twitter_cards: Dict[str, str] = field(default_factory=dict)
    internal_links_count: int = 0
    images_total: int = 0
    images_missing_alt: int = 0
    extraction_warnings: List[str] = field(default_factory=list)


def parse_page_html(url: str, html: str) -> PageData:
    """Parses raw HTML and extracts key on-page metadata, headings, text, and structured data."""
    page = PageData(url=url)
    domain = urlparse(url).netloc.lower()

    if BeautifulSoup:
        # Use lxml parser if available, else html.parser
        try:
            soup = BeautifulSoup(html, "lxml")
        except Exception:
            soup = BeautifulSoup(html, "html.parser")

        # 1. Title tag
        title_tag = soup.find("title")
        if title_tag and title_tag.string:
            page.title = clean_text_block(title_tag.string)

        # 2. Meta tags
        for meta in soup.find_all("meta"):
            name = (meta.get("name") or "").lower()
            prop = (meta.get("property") or "").lower()
            content = meta.get("content") or ""

            if name == "description" and not page.meta_description:
                page.meta_description = clean_text_block(content)
            elif name == "robots":
                page.meta_robots = content.strip()
            elif name == "viewport":
                page.viewport = content.strip()
            elif prop.startswith("og:"):
                page.open_graph[prop] = content.strip()
            elif name.startswith("twitter:") or prop.startswith("twitter:"):
                page.twitter_cards[name or prop] = content.strip()

        # 3. Canonical URL
        link_canonical = soup.find("link", rel=lambda r: r and "canonical" in r.lower())
        if link_canonical and link_canonical.get("href"):
            page.canonical = urljoin(url, link_canonical["href"].strip())

        # 4. Language
        html_tag = soup.find("html")
        if html_tag and html_tag.get("lang"):
            page.language = html_tag["lang"].strip()

        # 5. Headings
        for h1 in soup.find_all("h1"):
            text = clean_text_block(h1.get_text())
            if text and text not in page.h1:
                page.h1.append(text)

        for h2 in soup.find_all("h2"):
            text = clean_text_block(h2.get_text())
            if text and text not in page.h2:
                page.h2.append(text)

        for h3 in soup.find_all("h3"):
            text = clean_text_block(h3.get_text())
            if text and text not in page.h3:
                page.h3.append(text)

        # 6. Links
        for a in soup.find_all("a", href=True):
            raw_href = a["href"].strip()
            if not raw_href or raw_href.startswith(("#", "javascript:", "mailto:", "tel:")):
                continue
            abs_url = urljoin(url, raw_href)
            link_domain = urlparse(abs_url).netloc.lower()
            if link_domain == domain:
                if abs_url not in page.internal_links:
                    page.internal_links.append(abs_url)
            else:
                if abs_url not in page.external_links:
                    page.external_links.append(abs_url)

        # 7. Images
        for img in soup.find_all("img"):
            alt = clean_text_block(img.get("alt") or "")
            src = img.get("src") or ""
            if not alt:
                page.images_missing_alt_count += 1
            if alt or src:
                page.images_with_alt.append({"src": urljoin(url, src), "alt": alt})

        # 8. Schema.org JSON-LD
        for script in soup.find_all("script", type="application/ld+json"):
            if script.string:
                try:
                    data = json.loads(script.string)
                    if isinstance(data, dict):
                        page.schema_org.append(data)
                    elif isinstance(data, list):
                        page.schema_org.extend([d for d in data if isinstance(d, dict)])
                except Exception:
                    pass

    else:
        # Regex fallback parser if BeautifulSoup is not installed
        title_match = re.search(r"<title[^>]*>(.*?)</title>", html, re.IGNORECASE | re.DOTALL)
        if title_match:
            page.title = clean_text_block(re.sub(r"<[^>]+>", "", title_match.group(1)))

        desc_match = re.search(r'<meta[^>]+name=[\'"]description[\'"][^>]+content=[\'"](.*?)[\'"]', html, re.IGNORECASE)
        if desc_match:
            page.meta_description = clean_text_block(desc_match.group(1))

        for h1_match in re.finditer(r"<h1[^>]*>(.*?)</h1>", html, re.IGNORECASE | re.DOTALL):
            t = clean_text_block(re.sub(r"<[^>]+>", "", h1_match.group(1)))
            if t and t not in page.h1:
                page.h1.append(t)

    # 9. Main content extraction via Trafilatura
    if trafilatura:
        extracted = trafilatura.extract(
            html,
            include_comments=False,
            include_tables=True,
            no_fallback=False,
            favor_precision=True,
        )
        if extracted:
            page.main_text = clean_text_block(extracted)

    # Fallback to plain text if trafilatura produced nothing or wasn't available
    if not page.main_text:
        text = re.sub(r"<(script|style|nav|footer)[^>]*>.*?</\1>", " ", html, flags=re.IGNORECASE | re.DOTALL)
        text = re.sub(r"<[^>]+>", " ", text)
        page.main_text = clean_text_block(text)

    return page


class WebsiteExtractor:
    """Orchestrates safe fetching of the homepage and selected key internal pages."""

    PRIORITY_KEYWORDS = ["about", "service", "product", "solution", "industry", "offer", "feature", "pricing"]

    async def extract(self, url: str, max_internal_pages: int = 3) -> WebsiteExtraction:
        warnings: List[str] = []

        # 1. Fetch homepage
        try:
            final_url, html, status_code, headers = await safe_fetch_url(url)
        except SafeFetchError as e:
            raise SafeFetchError(f"Failed to fetch website at '{url}': {e}")

        domain = urlparse(final_url).netloc.lower().replace("www.", "")
        homepage_data = parse_page_html(final_url, html)

        if not homepage_data.main_text or len(homepage_data.main_text) < 150:
            warnings.append(
                "Limited textual content found on homepage. The site may rely heavily on client-side JavaScript rendering or image-based messaging."
            )

        if homepage_data.meta_robots and "noindex" in homepage_data.meta_robots.lower():
            warnings.append("Page meta robots specifies 'noindex'; search indexing is disabled for this page.")

        # 2. Select priority internal pages (e.g. /about, /services)
        selected_internal_urls: List[str] = []
        for link in homepage_data.internal_links:
            if len(selected_internal_urls) >= max_internal_pages:
                break
            link_lower = link.lower()
            if any(keyword in link_lower for keyword in self.PRIORITY_KEYWORDS):
                if link != final_url and link not in selected_internal_urls:
                    selected_internal_urls.append(link)

        # 3. Fetch selected internal pages safely
        internal_pages: List[PageData] = []
        for sub_url in selected_internal_urls:
            try:
                sub_final_url, sub_html, sub_status, _ = await safe_fetch_url(sub_url)
                if sub_status == 200:
                    sub_page = parse_page_html(sub_final_url, sub_html)
                    internal_pages.append(sub_page)
            except SafeFetchError:
                # Internal subpage fetch failures should not fail the overall homepage analysis
                pass

        # 4. Aggregate structured headings
        headings: List[Dict[str, str]] = []
        for h1 in homepage_data.h1:
            headings.append({"level": "h1", "text": h1})
        for h2 in homepage_data.h2:
            headings.append({"level": "h2", "text": h2})
        for h3 in homepage_data.h3[:10]:
            headings.append({"level": "h3", "text": h3})

        # 5. Aggregate main content
        combined_texts = [f"=== Homepage ({final_url}) ===\n{homepage_data.main_text}"]
        for p in internal_pages:
            if p.main_text:
                combined_texts.append(f"\n=== Internal Page ({p.url}) ===\nTitle: {p.title or 'N/A'}\n{p.main_text}")

        full_content = "\n\n".join(combined_texts)
        sanitized_content = sanitize_for_prompt_context(full_content)

        return WebsiteExtraction(
            requested_url=url,
            final_url=final_url,
            domain=domain,
            title=homepage_data.title,
            meta_description=homepage_data.meta_description,
            headings=headings,
            main_content=sanitized_content,
            internal_pages=internal_pages,
            canonical_url=homepage_data.canonical,
            language=homepage_data.language,
            structured_data=homepage_data.schema_org,
            open_graph=homepage_data.open_graph,
            meta_robots=homepage_data.meta_robots,
            viewport=homepage_data.viewport,
            twitter_cards=homepage_data.twitter_cards,
            internal_links_count=len(homepage_data.internal_links),
            images_total=len(homepage_data.images_with_alt),
            images_missing_alt=homepage_data.images_missing_alt_count,
            extraction_warnings=warnings,
        )
