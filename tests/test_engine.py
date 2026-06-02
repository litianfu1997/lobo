import json
import pytest
from app.analysis.engine import parse_analysis


def _raw(**over):
    base = {
        "position": {
            "org_name": "某市直属事业单位", "position_name": "研究岗",
            "major_req": "古生物学", "age_req": "1995年8月-1996年2月出生",
            "education_req": "全日制博士", "experience_req": "需2年某特定研究所经历",
            "cert_req": None, "headcount": 1,
        },
        "suspicion_score": 88,
        "hit_features": [
            {"key": "precise_age", "evidence": "年龄精确到月", "quote": "1995年8月-1996年2月出生"},
            {"key": "major_too_narrow", "evidence": "专业极窄", "quote": "古生物学"},
        ],
        "reasoning": "多项条件高度具体。",
        "highlights": [{"text": "1995年8月-1996年2月出生", "reason": "年龄异常精确"}],
    }
    base.update(over)
    return json.dumps(base, ensure_ascii=False)


def test_parses_full_structure():
    r = parse_analysis(_raw())
    assert r["position"]["org_name"] == "某市直属事业单位"
    assert r["analysis"]["suspicion_score"] == 88
    assert r["analysis"]["level"] == "high"
    assert len(r["analysis"]["hit_features"]) == 2


def test_clamps_score():
    assert parse_analysis(_raw(suspicion_score=150))["analysis"]["suspicion_score"] == 100
    assert parse_analysis(_raw(suspicion_score=-5))["analysis"]["suspicion_score"] == 0


def test_drops_unknown_feature_keys():
    raw = _raw(hit_features=[
        {"key": "precise_age", "evidence": "e", "quote": "q"},
        {"key": "not_a_real_key", "evidence": "e", "quote": "q"},
    ])
    keys = [f["key"] for f in parse_analysis(raw)["analysis"]["hit_features"]]
    assert keys == ["precise_age"]


def test_fills_missing_position_fields_with_none():
    raw = _raw(position={"position_name": "研究岗"})
    pos = parse_analysis(raw)["position"]
    assert pos["org_name"] is None
    assert pos["position_name"] == "研究岗"
    assert pos["headcount"] is None


def test_raises_on_invalid_json():
    with pytest.raises(ValueError):
        parse_analysis("not json at all")


def test_raises_on_missing_score():
    bad = json.dumps({"position": {}, "hit_features": [], "reasoning": "", "highlights": []})
    with pytest.raises(ValueError):
        parse_analysis(bad)


from app.analysis.engine import analyze


class _StubClient:
    def __init__(self, content): self._content = content; self.messages = None
    def complete(self, messages):
        self.messages = messages
        return self._content


def test_analyze_uses_client_and_returns_structure():
    content = _raw(suspicion_score=75)
    client = _StubClient(content)
    result = analyze("某公告文本", client=client)
    assert result["analysis"]["suspicion_score"] == 75
    assert result["analysis"]["level"] == "high"
    # 公告文本应出现在发给模型的最后一条消息里
    assert "某公告文本" in client.messages[-1]["content"]
