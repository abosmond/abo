from __future__ import annotations

import os

from .base import Message


class AnthropicModel:
    def __init__(self, model: str) -> None:
        import anthropic  # pip install "abo[anthropic]"
        self.client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
        self.model = model
        self.name = f"anthropic:{model}"

    def complete(self, system: str, messages: list[Message]) -> str:
        resp = self.client.messages.create(
            model=self.model,
            max_tokens=800,
            system=system,
            messages=[{"role": m.role, "content": m.content} for m in messages],
        )
        return "".join(b.text for b in resp.content if b.type == "text")
