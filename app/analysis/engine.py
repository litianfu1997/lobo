import json

from app.analysis.features import FEATURE_KEYS
from app.analysis.scoring import score_to_level

_POSITION_FIELDS = [
    "org_name", "position_name", "major_req", "age_req",
    "education_req", "experience_req", "cert_req", "headcount",
]


def parse_analysis(raw: str) -> dict:
    try:
        data = json.loads(raw)
    except (json.JSONDecodeError, TypeError) as exc:
        raise ValueError(f"模型返回非合法 JSON: {exc}") from exc

    if "suspicion_score" not in data:
        raise ValueError("模型返回缺少 suspicion_score")

    try:
        score = int(data["suspicion_score"])
    except (TypeError, ValueError) as exc:
        raise ValueError("suspicion_score 不是整数") from exc
    score = max(0, min(100, score))

    raw_pos = data.get("position") or {}
    position = {field: raw_pos.get(field) for field in _POSITION_FIELDS}

    hit_features = [
        {"key": h.get("key"), "evidence": h.get("evidence", ""), "quote": h.get("quote", "")}
        for h in data.get("hit_features", [])
        if isinstance(h, dict) and h.get("key") in FEATURE_KEYS
    ]

    highlights = [
        {"text": h.get("text", ""), "reason": h.get("reason", "")}
        for h in data.get("highlights", [])
        if isinstance(h, dict)
    ]

    return {
        "position": position,
        "analysis": {
            "suspicion_score": score,
            "level": score_to_level(score),
            "hit_features": hit_features,
            "reasoning": data.get("reasoning", ""),
            "highlights": highlights,
        },
    }
