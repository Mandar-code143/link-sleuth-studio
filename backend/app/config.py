"""Configuration settings for LinkIntel AI Backend."""

import os
from typing import List
from pydantic import Field

try:
    from pydantic_settings import BaseSettings, SettingsConfigDict
    
    class Settings(BaseSettings):
        model_config = SettingsConfigDict(
            env_file=".env",
            env_file_encoding="utf-8",
            extra="ignore",
        )

        app_env: str = Field(default="development", alias="APP_ENV")
        app_name: str = Field(default="LinkIntel AI", alias="APP_NAME")
        app_port: int = Field(default=4000, alias="APP_PORT")

        # LLM Provider settings: "gemini", "openai", "anthropic"
        llm_provider: str = Field(default="gemini", alias="LLM_PROVIDER")
        llm_model: str = Field(default="gemini-2.5-flash", alias="LLM_MODEL")

        # Provider API credentials
        gemini_api_key: str = Field(default="", alias="GEMINI_API_KEY")
        openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")
        anthropic_api_key: str = Field(default="", alias="ANTHROPIC_API_KEY")

        # Web search provider for live competitor research
        search_provider: str = Field(default="", alias="SEARCH_PROVIDER")
        search_api_key: str = Field(default="", alias="SEARCH_API_KEY")

        # CORS origins (comma-separated string in env)
        frontend_origins: str = Field(
            default="http://localhost:3000,http://localhost:5173,http://localhost:4173",
            alias="FRONTEND_ORIGINS",
        )

        # HTTP safe fetcher limits
        request_timeout_seconds: float = Field(default=20.0, alias="REQUEST_TIMEOUT_SECONDS")
        max_response_bytes: int = Field(default=5_000_000, alias="MAX_RESPONSE_BYTES")
        max_redirects: int = Field(default=3, alias="MAX_REDIRECTS")
        max_internal_pages: int = Field(default=4, alias="MAX_INTERNAL_PAGES")
        max_extracted_chars: int = Field(default=40_000, alias="MAX_EXTRACTED_CHARS")
        cache_ttl_seconds: int = Field(default=3600, alias="CACHE_TTL_SECONDS")

        @property
        def parsed_frontend_origins(self) -> List[str]:
            return [orig.strip() for orig in self.frontend_origins.split(",") if orig.strip()]

except ImportError:
    from pydantic import BaseModel
    
    class Settings(BaseModel):  # type: ignore
        app_env: str = os.getenv("APP_ENV", "development")
        app_name: str = os.getenv("APP_NAME", "LinkIntel AI")
        app_port: int = int(os.getenv("APP_PORT", "4000"))

        llm_provider: str = os.getenv("LLM_PROVIDER", "gemini")
        llm_model: str = os.getenv("LLM_MODEL", "gemini-2.5-flash")

        gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
        openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
        anthropic_api_key: str = os.getenv("ANTHROPIC_API_KEY", "")

        search_provider: str = os.getenv("SEARCH_PROVIDER", "")
        search_api_key: str = os.getenv("SEARCH_API_KEY", "")

        frontend_origins: str = os.getenv(
            "FRONTEND_ORIGINS",
            "http://localhost:3000,http://localhost:5173,http://localhost:4173",
        )

        request_timeout_seconds: float = float(os.getenv("REQUEST_TIMEOUT_SECONDS", "20.0"))
        max_response_bytes: int = int(os.getenv("MAX_RESPONSE_BYTES", "5000000"))
        max_redirects: int = int(os.getenv("MAX_REDIRECTS", "3"))
        max_internal_pages: int = int(os.getenv("MAX_INTERNAL_PAGES", "4"))
        max_extracted_chars: int = int(os.getenv("MAX_EXTRACTED_CHARS", "40000"))
        cache_ttl_seconds: int = int(os.getenv("CACHE_TTL_SECONDS", "3600"))

        @property
        def parsed_frontend_origins(self) -> List[str]:
            return [orig.strip() for orig in self.frontend_origins.split(",") if orig.strip()]


# Global configuration singleton
settings = Settings()
