"""Request schemas for LinkIntel AI."""

from pydantic import BaseModel, Field, field_validator
from urllib.parse import urlparse


class LinkAnalysisRequest(BaseModel):
    url: str = Field(
        ...,
        description="Public website URL to analyze (must use http or https scheme).",
        examples=["https://example.com"],
    )

    @field_validator("url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("URL cannot be empty.")
        
        parsed = urlparse(v)
        if parsed.scheme.lower() not in ("http", "https"):
            raise ValueError("Only http and https protocols are supported.")
        
        if not parsed.hostname:
            raise ValueError("URL must include a valid hostname (e.g. example.com).")
        
        if "." not in parsed.hostname and parsed.hostname != "localhost":
            raise ValueError("URL must contain a valid domain name with an extension.")

        return v
