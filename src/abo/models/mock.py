"""Deterministic 'naive' model for offline pipeline testing (no API key needed).

It follows the scenario's benign_plan, but obeys any `CALL tool {json}` instruction it
sees in the latest observation, simulating a model with zero injection resistance.
Results from this model say nothing about real models; it exists to test the harness.
"""
from __future__ import annotations

import json
import re

from .base import Message

CALL_RE = re.compile(r"CALL\s+(\w+)\s+(\{.*?\})", re.S)


class NaiveMockModel:
    name = "mock"

    def __init__(self) -> None:
        self.plan: list[dict] = []
        self.step = 0

    def reset(self, scenario) -> None:  # optional hook used by the runner
        self.plan = list(scenario.benign_plan)
        self.step = 0

    def complete(self, system: str, messages: list[Message]) -> str:
        last = messages[-1].content if messages else ""
        last = last.replace('\\"', '"')  # tolerate JSON-escaped payloads (e.g. inbox dumps)
        m = CALL_RE.search(last)
        if m:
            try:
                return json.dumps({"tool": m.group(1), "args": json.loads(m.group(2))})
            except json.JSONDecodeError:
                pass
        if self.step < len(self.plan):
            call = self.plan[self.step]
            self.step += 1
            return json.dumps(call)
        return json.dumps({"final": "Task complete."})
