"""Command-line entry point: `abo list | run | report`."""
from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

from .agent import run_scenario
from .defenses import get_defense
from .judges import evaluate
from .models import get_model
from .report import to_markdown
from .scenario import load_scenarios

DEFAULT_SCENARIOS = Path(__file__).resolve().parents[2] / "scenarios"


def cmd_list(a) -> None:
    for s in load_scenarios(a.scenarios):
        print(f"{s.id:10} {s.category:20} {s.severity:8} {s.title}")


def cmd_run(a) -> None:
    scenarios = load_scenarios(a.scenarios, a.ids.split(",") if a.ids else None)
    records = []
    for spec in a.models.split(","):
        for dname in a.defenses.split(","):
            model, defense = get_model(spec), get_defense(dname)
            for s in scenarios:
                res = run_scenario(s, model, defense, max_steps=a.max_steps)
                rec = asdict(res) | {"verdict": evaluate(s, res)}
                records.append(rec)
                v = rec["verdict"]
                flag = "PWNED" if v["attack_success"] else "safe "
                print(f"[{flag}] {spec:28} {dname:13} {s.id:10} blocked={v['blocked_calls']} task={v['task_success']}")
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(records, indent=2, ensure_ascii=False), encoding="utf-8")
    out.with_suffix(".md").write_text(to_markdown(records), encoding="utf-8")
    print(f"\nSaved {out} and {out.with_suffix('.md')}")


def cmd_report(a) -> None:
    print(to_markdown(json.loads(Path(a.path).read_text(encoding="utf-8"))))


def main() -> None:
    p = argparse.ArgumentParser(prog="abo", description="Security evaluation harness for LLM agents")
    sub = p.add_subparsers(dest="cmd", required=True)

    pl = sub.add_parser("list", help="list scenarios")
    pl.add_argument("--scenarios", default=str(DEFAULT_SCENARIOS))
    pl.set_defaults(fn=cmd_list)

    pr = sub.add_parser("run", help="run scenarios against models x defenses")
    pr.add_argument("--models", default="mock", help="comma list, e.g. mock,anthropic:claude-sonnet-4-6,deepseek:deepseek-chat")
    pr.add_argument("--defenses", default="none", help="comma list: none,spotlighting,tool_guard")
    pr.add_argument("--scenarios", default=str(DEFAULT_SCENARIOS))
    pr.add_argument("--ids", default="", help="comma list of scenario ids to run")
    pr.add_argument("--max-steps", type=int, default=8)
    pr.add_argument("--out", default="results/run.json")
    pr.set_defaults(fn=cmd_run)

    rp = sub.add_parser("report", help="render a saved run as markdown")
    rp.add_argument("path")
    rp.set_defaults(fn=cmd_report)

    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
