"""Tests for backend configuration, .env path resolution, and security diagnostics."""

import os
import pytest
from pathlib import Path
from pydantic import ValidationError

from app.config import Settings, BACKEND_DIR


def test_env_path_anchored_to_backend_dir():
    """Verify .env path resolution is anchored absolutely to the backend directory."""
    settings = Settings()
    expected_env = BACKEND_DIR / ".env"
    assert settings.backend_env_file == expected_env
    assert expected_env.is_absolute()


def test_api_key_whitespace_stripping():
    """Verify leading and trailing whitespace are automatically stripped from API keys."""
    raw_key = "  AIzaSyDummyKeyWithSpaces  \n"
    settings = Settings(gemini_api_key=raw_key)
    assert settings.gemini_api_key == "AIzaSyDummyKeyWithSpaces"


def test_gemini_key_detection():
    """Verify is_gemini_configured accurately detects present and absent keys."""
    unconfigured = Settings(gemini_api_key="")
    assert unconfigured.is_gemini_configured is False
    assert unconfigured.has_llm_key is False

    configured = Settings(gemini_api_key="AIzaSyValidLengthKey12345")
    assert configured.is_gemini_configured is True
    assert configured.has_llm_key is True


def test_invalid_llm_provider_rejected():
    """Verify unsupported LLM providers raise a validation error."""
    with pytest.raises(ValidationError):
        Settings(llm_provider="unsupported_provider_xyz")


def test_invalid_port_rejected():
    """Verify invalid port numbers outside 1-65535 are rejected."""
    with pytest.raises(ValidationError):
        Settings(app_port=99999)


def test_safe_diagnostic_report_never_leaks_secrets():
    """Verify safe diagnostic report masks credentials and exposes no secrets."""
    secret_key = "AIzaSyRealSecretKey1234567890abcdef"
    settings = Settings(gemini_api_key=secret_key, llm_provider="gemini")
    report = settings.safe_diagnostic_report()

    # The full secret key must NEVER appear in the report
    assert secret_key not in str(report)
    assert "AIzaSy..." in str(report["credentials"]["gemini_api_key"])
    assert report["configuration"]["provider"] == "gemini"
    assert report["credentials"]["gemini_configured"] is True
