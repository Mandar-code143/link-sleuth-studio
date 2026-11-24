"""Tests for SQLite/SQLAlchemy database persistence layer, workspace isolation, and report archiving."""

import json
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, ReportRecord, BenchmarkRecord, get_db
from app.main import app

# Use in-memory SQLite with StaticPool so all connections share the same memory instance
TEST_DATABASE_URL = "sqlite:///:memory:"
test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True)
def setup_test_db():
    """Create all tables before each test and drop after."""
    Base.metadata.create_all(bind=test_engine)
    app.dependency_overrides[get_db] = override_get_db
    yield
    Base.metadata.drop_all(bind=test_engine)
    app.dependency_overrides.clear()


@pytest.fixture
def client():
    return TestClient(app)


def test_database_models_and_dict_conversion():
    """Verifies ORM model instantiations and dictionary exports."""
    session = TestingSessionLocal()
    try:
        report = ReportRecord(
            id="rep_test123",
            workspace_id="team-alpha",
            url="https://example.com",
            brand_name="Example Inc",
            category="Technology",
            summary="Next-gen cloud platform.",
            report_json=json.dumps({"success": True, "brand": "Example Inc"}),
            model_used="gemini-2.5-flash",
            is_sample=False,
            tokens_used=1200,
            cost_usd=0.00025,
        )
        session.add(report)

        benchmark = BenchmarkRecord(
            id="bmk_test456",
            workspace_id="team-alpha",
            target_url="https://example.com",
            benchmark_mode="synthetic",
            is_simulated=True,
            winner_model="gemini-2.5-flash",
            results_json=json.dumps({"winner": "gemini-2.5-flash"}),
        )
        session.add(benchmark)
        session.commit()

        # Check retrieval
        saved_report = session.query(ReportRecord).filter_by(id="rep_test123").first()
        assert saved_report is not None
        assert saved_report.brand_name == "Example Inc"
        assert saved_report.to_dict()["workspace_id"] == "team-alpha"
        assert saved_report.get_full_report()["brand"] == "Example Inc"

        saved_bmk = session.query(BenchmarkRecord).filter_by(id="bmk_test456").first()
        assert saved_bmk is not None
        assert saved_bmk.winner_model == "gemini-2.5-flash"
        assert saved_bmk.get_full_results()["winner"] == "gemini-2.5-flash"
    finally:
        session.close()


def test_workspace_isolation_in_reports_endpoints(client):
    """Ensures reports from workspace A cannot be read or deleted by workspace B."""
    session = TestingSessionLocal()
    try:
        # Create report in workspace A
        rep_a = ReportRecord(
            id="rep_alpha1",
            workspace_id="workspace-a",
            url="https://alpha.example",
            brand_name="Alpha Tech",
            category="SaaS",
            summary="Alpha flagship product.",
            report_json=json.dumps({"brand": "Alpha Tech"}),
            model_used="gemini-2.5-flash",
        )
        # Create report in workspace B
        rep_b = ReportRecord(
            id="rep_bravo1",
            workspace_id="workspace-b",
            url="https://bravo.example",
            brand_name="Bravo Logistics",
            category="Logistics",
            summary="Bravo supply chain engine.",
            report_json=json.dumps({"brand": "Bravo Logistics"}),
            model_used="gpt-4o-mini",
        )
        session.add_all([rep_a, rep_b])
        session.commit()
    finally:
        session.close()

    # Workspace A query
    res_a = client.get("/reports", headers={"X-Workspace-Id": "workspace-a"})
    assert res_a.status_code == 200
    data_a = res_a.json()
    assert data_a["total"] == 1
    assert data_a["items"][0]["id"] == "rep_alpha1"

    # Workspace B query
    res_b = client.get("/reports", headers={"X-Workspace-Id": "workspace-b"})
    assert res_b.status_code == 200
    data_b = res_b.json()
    assert data_b["total"] == 1
    assert data_b["items"][0]["id"] == "rep_bravo1"

    # Workspace B trying to access report A by ID must be 404
    cross_get = client.get("/reports/rep_alpha1", headers={"X-Workspace-Id": "workspace-b"})
    assert cross_get.status_code == 404

    # Workspace B trying to delete report A must be 404
    cross_delete = client.delete("/reports/rep_alpha1", headers={"X-Workspace-Id": "workspace-b"})
    assert cross_delete.status_code == 404

    # Workspace A can retrieve its own report
    own_get = client.get("/reports/rep_alpha1", headers={"X-Workspace-Id": "workspace-a"})
    assert own_get.status_code == 200
    assert own_get.json()["brand"] == "Alpha Tech"

    # Workspace A can delete its own report
    own_delete = client.delete("/reports/rep_alpha1", headers={"X-Workspace-Id": "workspace-a"})
    assert own_delete.status_code == 200
    assert own_delete.json()["status"] == "deleted"

    # After deletion, it's gone
    after_delete = client.get("/reports/rep_alpha1", headers={"X-Workspace-Id": "workspace-a"})
    assert after_delete.status_code == 404


def test_reports_search_and_pagination(client):
    """Tests search filtering across url, brand_name, category, and summary."""
    session = TestingSessionLocal()
    try:
        reps = [
            ReportRecord(
                id=f"rep_{i}",
                workspace_id="test-ws",
                url=f"https://company{i}.com",
                brand_name=f"Brand {i}",
                category="Cybersecurity" if i % 2 == 0 else "E-commerce",
                summary=f"Summary for company {i}",
                report_json=json.dumps({"id": i}),
            )
            for i in range(10)
        ]
        session.add_all(reps)
        session.commit()
    finally:
        session.close()

    # Search for "Cybersecurity"
    res_cat = client.get("/reports?q=Cybersecurity", headers={"X-Workspace-Id": "test-ws"})
    assert res_cat.status_code == 200
    assert res_cat.json()["total"] == 5

    # Pagination: limit 3
    res_page = client.get("/reports?limit=3", headers={"X-Workspace-Id": "test-ws"})
    assert res_page.status_code == 200
    assert len(res_page.json()["items"]) == 3
    assert res_page.json()["total"] == 10


def test_benchmark_endpoints_and_isolation(client):
    """Verifies /benchmarks and /benchmarks/{id} with workspace isolation."""
    session = TestingSessionLocal()
    try:
        bmk1 = BenchmarkRecord(
            id="bmk_ws1",
            workspace_id="ws1",
            target_url="https://site1.example",
            benchmark_mode="synthetic",
            is_simulated=True,
            winner_model="gemini-2.5-flash",
            results_json=json.dumps({"winner": "gemini-2.5-flash", "score": 95}),
        )
        session.add(bmk1)
        session.commit()
    finally:
        session.close()

    # WS1 access
    res = client.get("/benchmarks", headers={"X-Workspace-Id": "ws1"})
    assert res.status_code == 200
    assert res.json()["total"] == 1

    detail = client.get("/benchmarks/bmk_ws1", headers={"X-Workspace-Id": "ws1"})
    assert detail.status_code == 200
    assert detail.json()["winner"] == "gemini-2.5-flash"

    # WS2 access -> 404
    cross = client.get("/benchmarks/bmk_ws1", headers={"X-Workspace-Id": "ws2"})
    assert cross.status_code == 404
