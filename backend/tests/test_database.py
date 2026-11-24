"""Tests for database URL normalization, PostgreSQL compatibility, and connection health."""

import pytest
from app.database import normalize_db_url, check_db_health, engine


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
