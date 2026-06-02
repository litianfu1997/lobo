from __future__ import annotations

from pydantic import BaseModel, Field


class AnalyzeRequest(BaseModel):
    text: str = Field(min_length=1)


class HitFeatureOut(BaseModel):
    key: str
    evidence: str = ""
    quote: str = ""


class HighlightOut(BaseModel):
    text: str = ""
    reason: str = ""


class PositionOut(BaseModel):
    id: int | None = None
    org_name: str | None = None
    position_name: str | None = None
    major_req: str | None = None
    age_req: str | None = None
    education_req: str | None = None
    experience_req: str | None = None
    cert_req: str | None = None
    headcount: int | None = None


class AnalysisOut(BaseModel):
    id: int
    suspicion_score: int
    level: str
    hit_features: list[HitFeatureOut]
    reasoning: str
    highlights: list[HighlightOut]
    model_version: str


class AnalyzeResponse(BaseModel):
    position: PositionOut
    analysis: AnalysisOut
