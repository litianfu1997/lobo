from app.services.analysis_service import analyze_and_store
from app.db.models import Announcement, Position, Analysis


def _fake_engine(text):
    return {
        "position": {
            "org_name": "某局", "position_name": "研究岗", "major_req": "古生物学",
            "age_req": "精确", "education_req": "博士", "experience_req": None,
            "cert_req": None, "headcount": 1,
        },
        "analysis": {
            "suspicion_score": 88, "level": "high",
            "hit_features": [{"key": "precise_age", "evidence": "e", "quote": "q"}],
            "reasoning": "理由", "highlights": [{"text": "t", "reason": "r"}],
        },
    }


def test_stores_three_records_and_returns_id(db_session):
    out = analyze_and_store("公告原文", db_session, analyze_fn=_fake_engine, model_version="deepseek-chat")

    assert db_session.query(Announcement).count() == 1
    assert db_session.query(Position).count() == 1
    assert db_session.query(Analysis).count() == 1

    assert out["analysis"]["id"] is not None
    assert out["analysis"]["suspicion_score"] == 88
    assert out["position"]["org_name"] == "某局"

    pos = db_session.query(Position).first()
    assert pos.announcement_id == db_session.query(Announcement).first().id
    ana = db_session.query(Analysis).first()
    assert ana.position_id == pos.id
    assert ana.model_version == "deepseek-chat"
