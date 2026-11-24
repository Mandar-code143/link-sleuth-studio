"""LinkIntel AI Database Persistence Layer with SQLite/PostgreSQL support and workspace isolation."""

import json
from datetime import datetime
from typing import Generator, Optional
from pathlib import Path
import uuid

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    Integer,
    String,
    Text,
    create_engine,
    text,
)
from sqlalchemy.orm import declarative_base, sessionmaker, Session

from app.config import settings, BACKEND_DIR
from app.utils.logging import logger

def normalize_db_url(url: str) -> str:
    """Normalizes database URLs for SQLite (relative paths) and PostgreSQL (Render driver compatibility)."""
    clean = (url or "").strip()
    if clean.startswith("postgres://"):
        return clean.replace("postgres://", "postgresql+psycopg2://", 1)
    if clean.startswith("postgresql://") and "+psycopg2" not in clean and "+" not in clean[:15]:
        return clean.replace("postgresql://", "postgresql+psycopg2://", 1)
    if clean.startswith("sqlite:///./"):
        # Resolve relative to backend directory so db location is consistent
        db_filename = clean.replace("sqlite:///./", "")
        resolved_path = (BACKEND_DIR / db_filename).resolve()
        resolved_path.parent.mkdir(parents=True, exist_ok=True)
        return f"sqlite:///{resolved_path}"
    return clean

engine_url = normalize_db_url(settings.database_url)

# Production verification: log prominent alert if SQLite is configured in production
if settings.app_env.lower() in ("production", "prod") and engine_url.startswith("sqlite"):
    logger.warning(
        "CRITICAL PERSISTENCE ALERT: Backend is running in production with an ephemeral SQLite database! "
        "Render instances do not persist disk state across deploys or container restarts. "
        "Configure DATABASE_URL to point to Render PostgreSQL (e.g. postgresql://user:pass@host/db)."
    )

if engine_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}
    engine = create_engine(engine_url, connect_args=connect_args)
else:
    # Hardened PostgreSQL connection pool for Render
    engine = create_engine(
        engine_url,
        pool_pre_ping=True,  # Proactively test connections before checkout to avoid idle timeout drops
        pool_recycle=300,   # Recycle connections every 5 minutes to prevent stale sockets on Render
        pool_size=10,       # Base connection pool size
        max_overflow=20,    # Max burst connections under load
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class ReportRecord(Base):
    """Persistent storage for analyzed business website intelligence reports."""

    __tablename__ = "analysis_reports"

    id = Column(String(64), primary_key=True, index=True, default=lambda: f"rep_{uuid.uuid4().hex[:12]}")
    workspace_id = Column(String(64), index=True, nullable=False, default="default")
    url = Column(String(2048), nullable=False)
    brand_name = Column(String(255), nullable=True, default="")
    category = Column(String(255), nullable=True, default="")
    summary = Column(Text, nullable=True, default="")
    report_json = Column(Text, nullable=False)  # Full AnalysisResponse serialized
    model_used = Column(String(64), nullable=True, default="gemini-2.5-flash")
    is_sample = Column(Boolean, default=False, nullable=False)
    tokens_used = Column(Integer, default=0, nullable=False)
    cost_usd = Column(Float, default=0.0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True, nullable=False)

    def to_dict(self) -> dict:
        """Converts record to API-ready dictionary summary."""
        return {
            "id": self.id,
            "workspace_id": self.workspace_id,
            "url": self.url,
            "brand_name": self.brand_name,
            "category": self.category,
            "summary": self.summary,
            "model_used": self.model_used,
            "is_sample": self.is_sample,
            "tokens_used": self.tokens_used,
            "cost_usd": self.cost_usd,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def get_full_report(self) -> dict:
        """Parses and returns full analysis JSON."""
        return json.loads(self.report_json)


class BenchmarkRecord(Base):
    """Persistent storage for multi-model benchmark evaluation runs."""

    __tablename__ = "benchmark_runs"

    id = Column(String(64), primary_key=True, index=True, default=lambda: f"bmk_{uuid.uuid4().hex[:12]}")
    workspace_id = Column(String(64), index=True, nullable=False, default="default")
    target_url = Column(String(2048), nullable=False)
    benchmark_mode = Column(String(64), default="comprehensive", nullable=False)
    is_simulated = Column(Boolean, default=False, nullable=False)
    winner_model = Column(String(64), nullable=True, default="")
    results_json = Column(Text, nullable=False)  # Full BenchmarkRunResponse serialized
    created_at = Column(DateTime, default=datetime.utcnow, index=True, nullable=False)

    def to_dict(self) -> dict:
        """Converts record to API-ready dictionary summary."""
        return {
            "id": self.id,
            "workspace_id": self.workspace_id,
            "target_url": self.target_url,
            "benchmark_mode": self.benchmark_mode,
            "is_simulated": self.is_simulated,
            "winner_model": self.winner_model,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def get_full_results(self) -> dict:
        """Parses and returns full benchmark JSON."""
        return json.loads(self.results_json)


def init_db() -> None:
    """Creates database tables if they do not exist."""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info(f"Database schema initialized successfully with engine dialect '{engine.dialect.name}'.")
    except Exception as exc:
        logger.error(f"Failed to initialize database tables: {exc}", exc_info=True)
        if settings.app_env.lower() in ("production", "prod"):
            raise


def check_db_health() -> bool:
    """Executes a lightweight query to verify active database connectivity."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as exc:
        logger.warning(f"Database health check failed: {exc}")
        return False


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency yielding an isolated database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
