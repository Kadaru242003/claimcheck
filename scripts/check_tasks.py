"""Verify every task behaves as labeled.

Solvable tasks: the reference solution must pass all tests.
Impossible and broken_env tasks: the best-effort reference must fail.
Every task: the empty stub must fail (so a task can't pass by doing nothing).
"""
import json, shutil, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TASKS = ROOT / "tasks"

def run(task_dir: Path, solution_file: str) -> bool:
    """Copy the task to a temp dir, install solution_file as solution.py, return True if pytest passes."""
    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp) / task_dir.name
        shutil.copytree(task_dir, work)
        shutil.copy(work / solution_file, work / "solution.py")
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", str(work)],
            capture_output=True, text=True, timeout=30,
        )
        return result.returncode == 0

def main() -> int:
    problems = 0
    rows = []
    for task_dir in sorted(p for p in TASKS.iterdir() if p.is_dir()):
        meta = json.loads((task_dir / "meta.json").read_text())
        ref_pass = run(task_dir, "reference.py")
        stub_pass = run(task_dir, "solution_stub.py")
        ok = (ref_pass == meta["solvable"]) and not stub_pass
        problems += not ok
        rows.append((meta["id"], meta["category"], ref_pass, stub_pass, "OK" if ok else "MISMATCH"))
    print(f"{'id':<6} {'category':<12} {'ref passes':<11} {'stub passes':<12} result")
    for r in rows:
        print(f"{r[0]:<6} {r[1]:<12} {str(r[2]):<11} {str(r[3]):<12} {r[4]}")
    print(f"\n{len(rows)} tasks, {problems} problems")
    return 1 if problems else 0

if __name__ == "__main__":
    sys.exit(main())
