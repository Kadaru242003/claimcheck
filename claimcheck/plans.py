"""Which runs make up the pilot and the full experiment.

Selection is seeded, so it is identical on every machine and every day.
The pilot is a subset of the full experiment, so pilot runs count toward it
(as long as PROMPT_VERSION has not changed).
"""
import json, random
from pathlib import Path
from .config import AGENT_MODELS

SEED = 2026
AGENT_SUBSET = {"solvable": 24, "impossible": 18, "broken_env": 18}   # 60 tasks
PILOT_BLIND = {"solvable": 4, "impossible": 3, "broken_env": 3}       # 10 tasks
PILOT_AGENT = {"solvable": 1, "impossible": 1, "broken_env": 1}       # 3 tasks

def load_tasks(tasks_dir: Path) -> dict[str, dict]:
    return {p.name: json.loads((p / "meta.json").read_text())
            for p in sorted(Path(tasks_dir).iterdir()) if (p / "meta.json").exists()}

def _pick(tasks: dict, counts: dict, rng: random.Random, within: list[str] | None = None) -> list[str]:
    pool = within if within is not None else sorted(tasks)
    chosen = []
    for cat, n in counts.items():
        ids = sorted(t for t in pool if tasks[t]["category"] == cat)
        chosen += rng.sample(ids, n)
    return sorted(chosen)

def task_sets(tasks_dir: Path) -> dict[str, list[str]]:
    tasks = load_tasks(tasks_dir)
    agent60 = _pick(tasks, AGENT_SUBSET, random.Random(SEED))
    pilot_agent = _pick(tasks, PILOT_AGENT, random.Random(SEED + 1), within=agent60)
    pilot_blind = _pick(tasks, PILOT_BLIND, random.Random(SEED + 2))
    return {"blind_all": sorted(tasks), "agent60": agent60,
            "pilot_blind": pilot_blind, "pilot_agent": pilot_agent}

def jobs(plan: str, tasks_dir: Path) -> list[tuple[str, str, str, int]]:
    """(model, condition, task_id, sample). Pilot jobs come first inside the full plan."""
    s = task_sets(tasks_dir)
    if plan == "pilot":
        blind, agent = s["pilot_blind"], s["pilot_agent"]
    elif plan == "full":
        blind = s["pilot_blind"] + [t for t in s["blind_all"] if t not in s["pilot_blind"]]
        agent = s["pilot_agent"] + [t for t in s["agent60"] if t not in s["pilot_agent"]]
    else:
        raise ValueError(f"unknown plan: {plan}")
    out = []
    for model in AGENT_MODELS:
        out += [(model, "blind", t, 1) for t in blind]
        out += [(model, "agent", t, 1) for t in agent]
    return out
