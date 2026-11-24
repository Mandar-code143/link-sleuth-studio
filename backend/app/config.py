"""Configuration settings for LinkIntel AI Backend with hardened environment resolution."""

import os
import sys
from pathlib import Path
from typing import List, Optional

try:
    from pydantic import Field, field_validator
    from pydantic_settings import BaseSettings, SettingsConfigDict
except ImportError as e:
    sys.stderr.write(
        "\nCRITICAL ERROR: 'pydantic' and 'pydantic-settings' are mandatory backend dependencies.\n"
        "Ensure you are running with the project virtual environment:\n"
        "  .\\backend\\.venv\\Scripts\\python.exe -m pip install -r backend/requirements.txt\n\n"
    )
    raise SystemExit(1) from e


# Resolve directories relative to this file
CONFIG_FILE_PATH = Path(__file__).resolve()
BACKEND_DIR = CONFIG_FILE_PATH.parents[1]
ROOT_DIR = BACKEND_DIR.parent

BACKEND_ENV_FILE = BACKEND_DIR / ".env"
ROOT_ENV_FILE = ROOT_DIR / ".env"

# Candidate env files in priority order (latter overrides earlier in pydantic-settings tuple)
_env_files = []
if ROOT_ENV_FILE.is_file():
    _env_files.append(str(ROOT_ENV_FILE))
if BACKEND_ENV_FILE.is_file():
    _env_files.append(str(BACKEND_ENV_FILE))

# Fallback default if no .env exists on disk yet
ACTIVE_ENV_FILES = tuple(_env_files) if _env_files else (str(BACKEND_ENV_FILE),)


class Settings(BaseSettings):
    """LinkIntel AI runtime application configuration."""

    model_config = SettingsConfigDict(
        env_file=ACTIVE_ENV_FILES,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_env: str = Field(default="development", alias="APP_ENV")
    app_name: str = Field(default="LinkIntel AI", alias="APP_NAME")
    app_port: int = Field(default=4000, alias="APP_PORT")

    # LLM Provider settings: "gemini", "openai", "anthropic", "mock"
    llm_provider: str = Field(default="gemini", alias="LLM_PROVIDER")
    llm_model: str = Field(default="gemini-2.5-flash", alias="LLM_MODEL")

    # Provider API credentials (always stripped of accidental quotes and whitespace)
    gemini_api_key: str = Field(default="", alias="GEMINI_API_KEY")
    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")
    anthropic_api_key: str = Field(default="", alias="ANTHROPIC_API_KEY")

    # Web search provider for live competitor research ("duckduckgo", "brave", "tavily")
    search_provider: str = Field(default="duckduckgo", alias="SEARCH_PROVIDER")
    search_api_key: str = Field(default="", alias="SEARCH_API_KEY")

    # CORS origins (comma-separated string in env, includes 8080 for current dev environment)
    frontend_origins: str = Field(
        default="http://localhost:8080,http://127.0.0.1:8080,http://localhost:3000,http://localhost:5173,http://localhost:4173",
        alias="FRONTEND_ORIGINS",
    )

    # Database persistence URL (SQLite by default, PostgreSQL in production)
    database_url: str = Field(default="sqlite:///./linkintel.db", alias="DATABASE_URL")

    # HTTP safe fetcher limits
    request_timeout_seconds: float = Field(default=20.0, alias="REQUEST_TIMEOUT_SECONDS")
    max_response_bytes: int = Field(default=5_000_000, alias="MAX_RESPONSE_BYTES")
    max_redirects: int = Field(default=3, alias="MAX_REDIRECTS")
    max_internal_pages: int = Field(default=4, alias="MAX_INTERNAL_PAGES")
    max_extracted_chars: int = Field(default=40_000, alias="MAX_EXTRACTED_CHARS")
    cache_ttl_seconds: int = Field(default=3600, alias="CACHE_TTL_SECONDS")

    @field_validator("app_port")
    @classmethod
    def validate_port(cls, v: int) -> int:
        if not (1 <= v <= 65535):
            raise ValueError(f"Invalid APP_PORT: {v}. Must be between 1 and 65535.")
        return v

    @field_validator("llm_provider")
    @classmethod
    def validate_provider(cls, v: str) -> str:
        clean = (v or "").strip().lower()
        allowed = {"gemini", "openai", "anthropic", "mock"}
        if clean not in allowed:
            raise ValueError(f"Invalid LLM_PROVIDER '{v}'. Allowed providers: {', '.join(sorted(allowed))}")
        return clean

    @field_validator("gemini_api_key", "openai_api_key", "anthropic_api_key", "search_api_key", "llm_model")
    @classmethod
    def strip_whitespace_and_quotes(cls, v: Optional[str]) -> str:
        if v is None:
            return ""
        return v.strip().strip("'\"")

    @property
    def backend_env_file(self) -> Path:
        return BACKEND_ENV_FILE

    @property
    def is_gemini_configured(self) -> bool:
        return bool(self.gemini_api_key)

    @property
    def has_llm_key(self) -> bool:
        if self.llm_provider == "gemini":
            return bool(self.gemini_api_key)
        elif self.llm_provider == "openai":
            return bool(self.openai_api_key)
        elif self.llm_provider == "anthropic":
            return bool(self.anthropic_api_key)
        return True

    @property
    def is_search_configured(self) -> bool:
        if self.search_provider == "duckduckgo":
            return True  # DuckDuckGo HTML/Instant API requires no API key
        return bool(self.search_api_key)

    @property
    def parsed_frontend_origins(self) -> List[str]:
        origins = []
        for orig in self.frontend_origins.split(","):
            cleaned = orig.strip().rstrip("/")
            if cleaned and cleaned not in origins:
                origins.append(cleaned)
        return origins

    def safe_diagnostic_report(self) -> dict:
        """Returns safe environment and diagnostic information with masked secrets."""
        def mask_key(k: str) -> str:
            if not k:
                return "<not_set>"
            if len(k) <= 8:
                return "***"
            return f"{k[:6]}...{k[-4:]}"

        return {
            "configuration": {
                "app_name": self.app_name,
                "app_env": self.app_env,
                "app_port": self.app_port,
                "provider": self.llm_provider,
                "model": self.llm_model,
                "search_provider": self.search_provider,
                "cache_ttl_seconds": self.cache_ttl_seconds,
                "backend_env_file": str(self.backend_env_file),
            },
            "credentials": {
                "gemini_api_key": mask_key(self.gemini_api_key),
                "gemini_configured": self.is_gemini_configured,
                "openai_api_key": mask_key(self.openai_api_key),
                "anthropic_api_key": mask_key(self.anthropic_api_key),
                "search_configured": self.is_search_configured,
            },
        }


# Singleton settings instance
settings = Settings()


def print_safe_diagnostics() -> None:
    """Prints environment diagnostics without exposing secret credentials."""
    env_located = BACKEND_ENV_FILE.is_file() or ROOT_ENV_FILE.is_file()
    print("Application configuration")
    print("-------------------------")
    print(f"Python executable: {sys.executable}")
    print(f"Python version: {sys.version.split()[0]}")
    print("Pydantic available: YES")
    print("Pydantic-settings available: YES")
    print(f"Backend .env path: {BACKEND_ENV_FILE}")
    print(f"Environment file located: {'YES' if env_located else 'NO'}")
    print(f"Environment files active: {list(ACTIVE_ENV_FILES)}")
    print(f"App environment: {settings.app_env}")
    print(f"API port: {settings.app_port}")
    print(f"Provider selected: {settings.llm_provider}")
    print(f"Model selected: {settings.llm_model}")
    print(f"Gemini API key present: {'YES' if settings.is_gemini_configured else 'NO'}")
    print(f"OpenAI API key present: {'YES' if bool(settings.openai_api_key) else 'NO'}")
    print(f"Anthropic API key present: {'YES' if bool(settings.anthropic_api_key) else 'NO'}")
    print(f"Search provider: {settings.search_provider}")
    print(f"Search provider configured: {'YES' if settings.is_search_configured else 'NO'}")
    print(f"Frontend origins: {settings.parsed_frontend_origins}")
    print(f"Cache TTL: {settings.cache_ttl_seconds}s")
    print(f"Max response bytes: {settings.max_response_bytes} bytes")


if __name__ == "__main__":
    print_safe_diagnostics()
