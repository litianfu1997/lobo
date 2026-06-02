import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db.models import Base
from app.db.session import get_db


@pytest.fixture
def client():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    TestingSession = sessionmaker(bind=engine, autoflush=False)

    def override_get_db():
        db = TestingSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


def _fake_engine(text):
    return {
        "position": {"org_name": "某局", "position_name": "研究岗", "major_req": "古生物学",
                     "age_req": "精确", "education_req": "博士", "experience_req": None,
                     "cert_req": None, "headcount": 1},
        "analysis": {"suspicion_score": 88, "level": "high",
                     "hit_features": [{"key": "precise_age", "evidence": "e", "quote": "q"}],
                     "reasoning": "理由", "highlights": [{"text": "t", "reason": "r"}]},
    }


def test_analyze_endpoint(client, monkeypatch):
    monkeypatch.setattr("app.api.routes_analysis.analyze", _fake_engine)
    resp = client.post("/api/analyze", json={"text": "某招聘公告"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["analysis"]["suspicion_score"] == 88
    assert body["analysis"]["level"] == "high"
    assert body["position"]["org_name"] == "某局"
    aid = body["analysis"]["id"]

    got = client.get(f"/api/analyses/{aid}")
    assert got.status_code == 200
    assert got.json()["analysis"]["id"] == aid


def test_analyze_rejects_empty_text(client):
    resp = client.post("/api/analyze", json={"text": ""})
    assert resp.status_code == 422


def test_get_missing_analysis_returns_404(client):
    assert client.get("/api/analyses/99999").status_code == 404
