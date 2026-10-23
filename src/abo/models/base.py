"""Provider-agnostic model interface.

Every adapter receives a system prompt plus a message list and returns raw text.
The agent runner owns the tool-call protocol (JSON), so any chat model can be tested
without relying on provider-specific function-calling features.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass
class Message:
    role: str  # "user" | "assistant"
    content: str


class ModelAdapter(Protocol):
    name: str

    def complete(self, system: str, messages: list[Message]) -> str: ...


def get_model(spec: str) -> ModelAdapter:
    """spec examples: 'mock', 'anthropic:claude-sonnet-4-6', 'openai:gpt-4o-mini',
    'deepseek:deepseek-chat'."""
    provider, _, model = spec.partition(":")
    if provider == "mock":
        from .mock import NaiveMockModel
        return NaiveMockModel()
    if provider == "anthropic":
        from .anthropic_adapter import AnthropicModel
        return AnthropicModel(model or "claude-sonnet-4-6")
    if provider in ("openai", "deepseek"):
        from .openai_compat import OpenAICompatModel
        default = "deepseek-chat" if provider == "deepseek" else "gpt-4o-mini"
        return OpenAICompatModel(provider, model or default)
    raise ValueError(f"Unknown model provider: {provider}")
