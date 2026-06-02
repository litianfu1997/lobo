import pytest
from app.analysis.scoring import score_to_level


@pytest.mark.parametrize("score,level", [
    (0, "low"), (39, "low"),
    (40, "mid"), (69, "mid"),
    (70, "high"), (100, "high"),
])
def test_boundaries(score, level):
    assert score_to_level(score) == level


def test_custom_thresholds():
    assert score_to_level(50, low_max=49, mid_max=80) == "mid"
    assert score_to_level(49, low_max=49, mid_max=80) == "low"
