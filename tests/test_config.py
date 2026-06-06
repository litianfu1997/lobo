from app.config import Settings


def test_defaults():
    s = Settings(_env_file=None)
    assert s.deepseek_base_url == "https://api.deepseek.com"
    assert s.deepseek_model == "deepseek-v4-flash"
    assert s.score_low_max == 39
    assert s.score_mid_max == 69


def test_env_override(monkeypatch):
    monkeypatch.setenv("DEEPSEEK_MODEL", "deepseek-reasoner")
    s = Settings(_env_file=None)
    assert s.deepseek_model == "deepseek-reasoner"
