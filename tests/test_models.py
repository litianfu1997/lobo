from app.db.models import Announcement, Position, Analysis


def test_create_and_relate(db_session):
    ann = Announcement(raw_text="公告原文", source_type="submit", content_hash="abc")
    db_session.add(ann); db_session.flush()
    pos = Position(announcement_id=ann.id, position_name="研究岗", headcount=1)
    db_session.add(pos); db_session.flush()
    ana = Analysis(position_id=pos.id, suspicion_score=88, level="high",
                   hit_features=[{"key": "precise_age"}], reasoning="r",
                   highlights=[{"text": "t", "reason": "x"}], model_version="deepseek-chat")
    db_session.add(ana); db_session.commit()

    got = db_session.get(Analysis, ana.id)
    assert got.suspicion_score == 88
    assert got.hit_features[0]["key"] == "precise_age"
    assert got.position_id == pos.id
    assert ann.fetched_at is not None
