"""Content cleaning and prompt injection sanitization for untrusted website content."""

import re
from typing import Optional


# HTML tags that generally contain non-content boilerplate or executable code
REMOVABLE_TAGS = [
    "script",
    "style",
    "noscript",
    "iframe",
    "svg",
    "canvas",
    "nav",
    "footer",
    "form",
    "input",
    "button",
    "header",
]

# Patterns often seen in prompt injection attempts from scraped text
PROMPT_INJECTION_PATTERNS = [
    r"(?i)ignore\s+(all\s+)?(previous|prior|above)\s+instructions",
    r"(?i)you\s+are\s+now\s+in\s+developer\s+mode",
    r"(?i)system\s+prompt\s*:",
    r"(?i)print\s+(the\s+)?api\s+key",
    r"(?i)reveal\s+(the\s+)?environment\s+variables",
]


def clean_text_block(text: str) -> str:
    """Normalizes whitespace and removes control characters."""
    if not text:
        return ""
    # Remove control characters except standard whitespace
    cleaned = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]", " ", text)
    # Collapse multiple blank lines and spaces
    cleaned = re.sub(r"[ \t]+", " ", cleaned)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip()


def sanitize_for_prompt_context(text: str, max_chars: int = 40_000) -> str:
    """
    Sanitizes untrusted scraped content before embedding it into LLM context.

    1. Neutralizes known prompt injection override directives by wrapping in quotation.
    2. Enforces maximum character bounds.
    3. Returns sanitized text block safely bounded.
    """
    if not text:
        return ""

    sanitized = clean_text_block(text)

    # Flag and neutralize any explicit attempt to break prompt instructions
    for pattern in PROMPT_INJECTION_PATTERNS:
        sanitized = re.sub(pattern, "[Scraped text contains prompt override attempt - neutralized]", sanitized)

    # Enforce upper character limit
    if len(sanitized) > max_chars:
        sanitized = sanitized[:max_chars] + "\n... [Content truncated due to context limit]"

    return sanitized


def format_untrusted_context(content: str, source_url: str) -> str:
    """
    Wraps scraped content inside a distinct XML-like perimeter to instruct the LLM
    that the contained text is untrusted data and not system instructions.
    """
    return (
        f'<untrusted_scraped_website_content url="{source_url}">\n'
        f'{content}\n'
        f'</untrusted_scraped_website_content>'
    )
