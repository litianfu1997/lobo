from openai import OpenAI

from app.config import settings


class DeepSeekClient:
    def __init__(self, api_key=None, base_url=None, model=None, _client=None):
        self.model = model or settings.deepseek_model
        if _client is not None:
            self._client = _client
        else:
            self._client = OpenAI(
                api_key=api_key or settings.deepseek_api_key,
                base_url=base_url or settings.deepseek_base_url,
            )

    def complete(self, messages: list[dict]) -> str:
        resp = self._client.chat.completions.create(
            model=self.model,
            messages=messages,
            response_format={"type": "json_object"},
            temperature=0.2,
        )
        return resp.choices[0].message.content
