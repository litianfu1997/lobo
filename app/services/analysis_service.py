import hashlib

from app.analysis.engine import analyze as default_analyze
from app.config import settings
from app.db.models import Announcement, Position, Analysis


def analyze_and_store(
    text, db, analyze_fn=default_analyze, model_version=None,
    source_type="submit", source_url=None,
):
    model_version = model_version or settings.deepseek_model
    result = analyze_fn(text)
    pos_data = result["position"]
    ana_data = result["analysis"]

    ann = Announcement(
        raw_text=text, source_type=source_type, source_url=source_url,
        content_hash=hashlib.sha256(text.encode("utf-8")).hexdigest(),
        org_name=pos_data.get("org_name"),
    )
    db.add(ann); db.flush()

    pos = Position(announcement_id=ann.id, **pos_data)
    db.add(pos); db.flush()

    ana = Analysis(
        position_id=pos.id,
        suspicion_score=ana_data["suspicion_score"],
        level=ana_data["level"],
        hit_features=ana_data["hit_features"],
        reasoning=ana_data["reasoning"],
        highlights=ana_data["highlights"],
        model_version=model_version,
    )
    db.add(ana); db.commit(); db.refresh(ana)

    return {
        "source_url": source_url,
        "position": {"id": pos.id, **pos_data},
        "analysis": {
            "id": ana.id, "suspicion_score": ana.suspicion_score, "level": ana.level,
            "hit_features": ana.hit_features, "reasoning": ana.reasoning,
            "highlights": ana.highlights, "model_version": ana.model_version,
        },
    }
