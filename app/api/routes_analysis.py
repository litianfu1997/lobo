from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.analysis.engine import analyze
from app.db.session import get_db
from app.db.models import Analysis, Position, Announcement
from app.schemas.analysis import AnalyzeRequest, AnalyzeResponse
from app.services.analysis_service import analyze_and_store

router = APIRouter(prefix="/api", tags=["analysis"])


@router.post("/analyze", response_model=AnalyzeResponse)
def analyze_endpoint(req: AnalyzeRequest, db: Session = Depends(get_db)):
    return analyze_and_store(req.text, db, analyze_fn=analyze, source_url=req.source_url)


@router.get("/analyses")
def list_analyses(
    limit: int = Query(default=100, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    rows = (
        db.query(Analysis, Position, Announcement)
        .join(Position, Analysis.position_id == Position.id)
        .join(Announcement, Position.announcement_id == Announcement.id)
        .order_by(desc(Analysis.suspicion_score))
        .offset(offset)
        .limit(limit)
        .all()
    )
    total = db.query(Analysis).count()
    return {
        "total": total,
        "items": [
            {
                "analysis_id": ana.id,
                "suspicion_score": ana.suspicion_score,
                "level": ana.level,
                "hit_features": ana.hit_features,
                "analyzed_at": ana.analyzed_at.isoformat(),
                "position": {
                    "id": pos.id,
                    "org_name": pos.org_name,
                    "position_name": pos.position_name,
                    "major_req": pos.major_req,
                    "education_req": pos.education_req,
                    "headcount": pos.headcount,
                },
                "source_url": ann.source_url,
            }
            for ana, pos, ann in rows
        ],
    }


@router.get("/analyses/{analysis_id}", response_model=AnalyzeResponse)
def get_analysis(analysis_id: int, db: Session = Depends(get_db)):
    ana = db.get(Analysis, analysis_id)
    if ana is None:
        raise HTTPException(status_code=404, detail="分析结果不存在")
    pos = db.get(Position, ana.position_id)
    ann = db.get(Announcement, pos.announcement_id)
    return {
        "source_url": ann.source_url if ann else None,
        "position": {
            "id": pos.id, "org_name": pos.org_name, "position_name": pos.position_name,
            "major_req": pos.major_req, "age_req": pos.age_req,
            "education_req": pos.education_req, "experience_req": pos.experience_req,
            "cert_req": pos.cert_req, "headcount": pos.headcount,
        },
        "analysis": {
            "id": ana.id, "suspicion_score": ana.suspicion_score, "level": ana.level,
            "hit_features": ana.hit_features, "reasoning": ana.reasoning,
            "highlights": ana.highlights, "model_version": ana.model_version,
        },
    }
