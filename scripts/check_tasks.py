"""Verify every task behaves as labeled.

Solvable tasks: the reference solution must pass.
Impossible and broken_env tasks: the best-effort reference must fail.
Every task: the empty stub must fail.
"""
import json, sys
from collections import Counter
from pathlib import Path
from grading import grade

ROOT = Path(__file__).resolve().parent.parent
TASKS = ROOT / "tasks"

def main() -> int:
    problems, rows, cats = 0, [], Counter()
    for task_dir in sorted(p for p in TASKS.iterdir() if p.is_dir()):
        meta = json.loads((task_dir / "meta.json").read_text())
        cats[meta["category"]] += 1
        ref = grade(task_dir, task_dir / "reference.py")
        stub = grade(task_dir, task_dir / "solution_stub.py")
        ok = ref["passed"] == meta["solvable"] and not stub["passed"]
        problems += not ok
        rows.append((meta["id"], meta["category"], ref["passed"], stub["passed"], "OK" if ok else "MISMATCH: " + ref["reason"]))
    print(f"{'id':<6} {'category':<12} {'ref passes':<11} {'stub passes':<12} result")
    for r in rows:
        print(f"{r[0]:<6} {r[1]:<12} {str(r[2]):<11} {str(r[3]):<12} {r[4]}")
    print(f"\n{len(rows)} tasks ({', '.join(f'{k}: {v}' for k, v in sorted(cats.items()))}), {problems} problems")
    return 1 if problems else 0

if __name__ == "__main__":
    sys.exit(main())
