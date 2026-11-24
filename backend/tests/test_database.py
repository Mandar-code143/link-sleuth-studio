"""Tests for database URL normalization, PostgreSQL compatibility, connection health, and production safeguards."""

import pytest
from app.database import (
    normalize_db_url,
    check_db_health,
    verify_production_database,
    engine,
)
from app.config import settings


def test_normalize_db_url_handles_render_postgres_prefix():
    # Render PostgreSQL URLs typically begin with postgres://
    render_url = "postgres://user:secret123@dpg-abc12345:5432/linkintel_db"
    normalized = normalize_db_url(render_url)
    assert normalized.startswith("postgresql+psycopg2://")
    assert "user:secret123@dpg-abc12345:5432/linkintel_db" in normalized


def test_normalize_db_url_handles_standard_postgresql_prefix():
    std_url = "postgresql://user:secret123@host.render.com:5432/linkintel"
    normalized = normalize_db_url(std_url)
    assert normalized.startswith("postgresql+psycopg2://")


def test_normalize_db_url_preserves_explicit_driver():
    custom_url = "postgresql+psycopg2://user:secret@host:5432/db"
    normalized = normalize_db_url(custom_url)
    assert normalized == custom_url


def test_normalize_db_url_resolves_sqlite_relative_path():
    sqlite_url = "sqlite:///./linkintel.db"
    normalized = normalize_db_url(sqlite_url)
    assert normalized.startswith("sqlite:///")
    assert "linkintel.db" in normalized


def test_check_db_health_returns_true_for_active_engine():
    health = check_db_health()
    assert health is True


def test_production_database_fails_with_sqlite(monkeypatch):
    """Verifies that running in production with SQLite raises RuntimeError."""
    monkeypatch.setattr(settings, "app_env", "production")
    with pytest.raises(RuntimeError, match="CRITICAL CONFIGURATION ERROR.*PostgreSQL"):
        verify_production_database()


def test_check_db_health_reports_false_for_sqlite_in_production(monkeypatch):
    """Verifies that check_db_health flags SQLite as unhealthy when in production."""
    monkeypatch.setattr(settings, "app_env", "production")
    assert check_db_health() is False
