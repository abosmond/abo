"""Aggregate run records into attack-success-rate (ASR) and utility tables."""
from __future__ import annotations

from collections import defaultdict


def summarize(records: list[dict]) -> list[dict]:
    groups: dict[tuple, list[dict]] = defaultdict(list)
    for r in records:
        groups[(r["model"], r["defense"])].append(r)
    rows = []
    for (model, defense), rs in sorted(groups.items()):
        n = len(rs)
        util = [r["verdict"]["task_success"] for r in rs if r["verdict"]["task_success"] is not None]
        rows.append({
            "model": model,
            "defense": defense,
            "n": n,
            "asr": sum(r["verdict"]["attack_success"] for r in rs) / n,
            "utility": (sum(util) / len(util)) if util else None,
            "errors": sum(1 for r in rs if r.get("error")),
        })
    return rows


def by_category(records: list[dict]) -> dict[str, dict[str, float]]:
    out: dict[str, dict[str, list[bool]]] = defaultdict(lambda: defaultdict(list))
    for r in records:
        out[r["category"]][f'{r["model"]} / {r["defense"]}'].append(r["verdict"]["attack_success"])
    return {cat: {k: sum(v) / len(v) for k, v in d.items()} for cat, d in out.items()}


def to_markdown(records: list[dict]) -> str:
    lines = ["# ABO results", "", "| model | defense | n | ASR ↓ | utility ↑ | errors |",
             "|---|---|---|---|---|---|"]
    for row in summarize(records):
        util = "-" if row["utility"] is None else f'{row["utility"]:.0%}'
        lines.append(f'| {row["model"]} | {row["defense"]} | {row["n"]} | {row["asr"]:.0%} | {util} | {row["errors"]} |')
    lines += ["", "## ASR by category", ""]
    for cat, d in sorted(by_category(records).items()):
        lines.append(f"**{cat}**: " + ", ".join(f"{k}: {v:.0%}" for k, v in d.items()))
    return "\n".join(lines) + "\n"
