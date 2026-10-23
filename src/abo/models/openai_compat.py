"""Adapter for OpenAI and OpenAI-compatible APIs (DeepSeek, etc.)."""
from __future__ import annotations

import os

from .base import Message

ENDPOINTS = {
    "openai": (None, "OPENAI_API_KEY"),
    "deepseek": ("https://api.deepseek.com", "DEEPSEEK_API_KEY"),
}


class OpenAICompatModel:
    def __init__(self, provider: str, model: str) -> None:
        from openai import OpenAI  # pip install "abo[openai]"
        base_url, key_env = ENDPOINTS[provider]
        self.client = OpenAI(api_key=os.environ[key_env], base_url=base_url)
        self.model = model
        self.name = f"{provider}:{model}"

    def complete(self, system: str, messages: list[Message]) -> str:
        resp = self.client.chat.completions.create(
            model=self.model,
            max_tokens=800,
            messages=[{"role": "system", "content": system}]
            + [{"role": m.role, "content": m.content} for m in messages],
        )
        return resp.choices[0].message.content or ""
