from app.analysis.prompt import build_messages
from app.analysis.features import FEATURES


def test_message_roles():
    msgs = build_messages("某招聘公告正文")
    roles = [m["role"] for m in msgs]
    assert roles[0] == "system"
    assert roles[-1] == "user"
    assert "assistant" in roles  # 含 few-shot


def test_system_contains_feature_keys():
    sys = build_messages("x")[0]["content"]
    for f in FEATURES:
        assert f.key in sys


def test_user_contains_announcement_text():
    text = "这是一段独特的公告文本ABC123"
    assert text in build_messages(text)[-1]["content"]


def test_system_requires_json_and_suspicion_wording():
    sys = build_messages("x")[0]["content"]
    assert "JSON" in sys
    assert "疑似" in sys
