"""Scenario schema and YAML loader."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


@dataclass
class Scenario:
    id: str
    category: str
    title: str
    system_prompt: str
    user_task: str
    tools: list[str]
    environment: dict[str, Any] = field(default_factory=dict)
    attack_success: list[dict[str, Any]] = field(default_factory=list)  # judge criteria
    task_success: list[dict[str, Any]] = field(default_factory=list)    # utility criteria
    policy: dict[str, Any] = field(default_factory=dict)                # used by tool_guard
    severity: str = "medium"
    description: str = ""
    benign_plan: list[dict[str, Any]] = field(default_factory=list)     # used by mock model only

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Scenario":
        known = {k: d[k] for k in cls.__dataclass_fields__ if k in d}
        return cls(**known)


def load_scenarios(root: str | Path, ids: list[str] | None = None) -> list[Scenario]:
    root = Path(root)
    files = sorted(root.rglob("*.yaml")) if root.is_dir() else [root]
    out = [Scenario.from_dict(yaml.safe_load(f.read_text(encoding="utf-8"))) for f in files]
    if ids:
        out = [s for s in out if s.id in ids]
    return out
