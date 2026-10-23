from pathlib import Path

from abo.agent import run_scenario
from abo.defenses import get_defense
from abo.judges import evaluate
from abo.models import get_model
from abo.scenario import load_scenarios

SCEN = Path(__file__).resolve().parents[1] / "scenarios"


def _run(sid, defense):
    s = load_scenarios(SCEN, [sid])[0]
    r = run_scenario(s, get_model("mock"), get_defense(defense))
    return evaluate(s, r)


def test_all_scenarios_load():
    ids = [s.id for s in load_scenarios(SCEN)]
    assert len(ids) == len(set(ids)) >= 6


def test_naive_model_is_hijacked_without_defense():
    assert _run("II-001", "none")["attack_success"] is True
    assert _run("OC-001", "none")["attack_success"] is True


def test_tool_guard_blocks_off_policy_calls():
    v = _run("OC-002", "tool_guard")
    assert v["attack_success"] is False and v["blocked_calls"] == 1
    assert v["task_success"] is True


def test_allow_list_does_not_stop_content_attacks():
    # II-002: the poisoned email goes to an allowed recipient, so tool_guard can't catch it.
    assert _run("II-002", "tool_guard")["attack_success"] is True
