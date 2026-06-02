from app.analysis.features import (
    FEATURES, FEATURE_KEYS, CATEGORIES, feature_checklist_text,
)


def test_feature_fields_complete():
    for f in FEATURES:
        assert f.key and f.name and f.description and f.judge_hint
        assert f.category in CATEGORIES


def test_keys_unique():
    keys = [f.key for f in FEATURES]
    assert len(keys) == len(set(keys))
    assert FEATURE_KEYS == set(keys)


def test_covers_four_categories():
    assert {f.category for f in FEATURES} == {"A", "B", "C", "D"}


def test_checklist_text_lists_every_feature():
    text = feature_checklist_text()
    for f in FEATURES:
        assert f.key in text
        assert f.name in text
