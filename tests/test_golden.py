import json
from pathlib import Path

import pytest

from app.analysis.engine import analyze

SAMPLES = sorted((Path(__file__).parent / "fixtures" / "golden_samples").glob("*.json"))


@pytest.mark.integration
@pytest.mark.parametrize("sample_path", SAMPLES, ids=lambda p: p.stem)
def test_golden_sample_scores(sample_path):
    sample = json.loads(sample_path.read_text(encoding="utf-8"))
    result = analyze(sample["text"])
    score = result["analysis"]["suspicion_score"]
    if "expect_min_score" in sample:
        assert score >= sample["expect_min_score"], f"{sample['name']} 得分过低: {score}"
    if "expect_max_score" in sample:
        assert score <= sample["expect_max_score"], f"{sample['name']} 得分过高: {score}"
