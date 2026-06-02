from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.analysis.engine import analyze
from app.db.session import get_db
from app.db.models import Analysis, Position
from app.schemas.analysis import AnalyzeRequest, AnalyzeResponse
from app.services.analysis_service import analyze_and_store

router = APIRouter(prefix="/api", tags=["analysis"])


@router.post("/analyze", response_model=AnalyzeResponse)
def analyze_endpoint(req: AnalyzeRequest, db: Session = Depends(get_db)):
    return analyze_and_store(req.text, db, analyze_fn=analyze)


@router.get("/analyses/{analysis_id}", response_model=AnalyzeResponse)
def get_analysis(analysis_id: int, db: Session = Depends(get_db)):
    ana = db.get(Analysis, analysis_id)
    if ana is None:
        raise HTTPException(status_code=404, detail="分析结果不存在")
    pos = db.get(Position, ana.position_id)
    return {
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
