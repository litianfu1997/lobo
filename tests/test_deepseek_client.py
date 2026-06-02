from app.analysis.deepseek_client import DeepSeekClient


class _FakeMessage:
    def __init__(self, content): self.content = content


class _FakeChoice:
    def __init__(self, content): self.message = _FakeMessage(content)


class _FakeResp:
    def __init__(self, content): self.choices = [_FakeChoice(content)]


class _FakeCompletions:
    def __init__(self): self.called_with = None
    def create(self, **kwargs):
        self.called_with = kwargs
        return _FakeResp('{"ok": true}')


class _FakeOpenAI:
    def __init__(self):
        self.chat = type("C", (), {"completions": _FakeCompletions()})()


def test_complete_returns_content_and_passes_params():
    fake = _FakeOpenAI()
    client = DeepSeekClient(api_key="k", base_url="http://x", model="deepseek-chat", _client=fake)
    out = client.complete([{"role": "user", "content": "hi"}])
    assert out == '{"ok": true}'
    sent = fake.chat.completions.called_with
    assert sent["model"] == "deepseek-chat"
    assert sent["response_format"] == {"type": "json_object"}
    assert sent["messages"] == [{"role": "user", "content": "hi"}]
