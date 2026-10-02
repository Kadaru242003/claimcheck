"""Prove the Docker sandbox contains model-written code.

Each attack below WORKS on a normal machine. Inside the sandbox, every one must fail.
The static scanner is turned off here on purpose, so we test the container alone.

Usage (Docker Desktop must be running):
    python scripts/test_sandbox.py
"""
import sys, tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from claimcheck.grading import grade, build_image

ROOT = Path(__file__).resolve().parent.parent

ATTACKS = {
    "network access": "import socket\ndef attack():\n    socket.create_connection(('1.1.1.1', 53), timeout=3).close()\n    return True\n",
    "write to task files": "def attack():\n    with open('/work/hacked.txt', 'w') as f:\n        f.write('x')\n    return True\n",
    "write outside /tmp": "def attack():\n    with open('/home/runner/x', 'w') as f:\n        f.write('x')\n    return True\n",
    "use 1 GB of memory": "def attack():\n    blob = b\"\\x01\" * (1024 * 1024 * 1024)  # filled, so the memory is really used\n    return len(blob) > 0\n",
    "start 200 processes": "import os\ndef attack():\n    pids = []\n    for _ in range(200):\n        pid = os.fork()\n        if pid == 0:\n            import time; time.sleep(5); os._exit(0)\n        pids.append(pid)\n    return True\n",
    "run forever": "def attack():\n    while True:\n        pass\n",
}
TEST_FILE = "from solution import attack\n\ndef test_attack():\n    assert attack() is True\n"

def main() -> int:
    print("Building sandbox image (first time takes a minute)...")
    build_image()
    failures = 0
    # Sanity: a normal solvable task must still pass inside the sandbox.
    ok = grade(ROOT / "tasks" / "s001", ROOT / "tasks" / "s001" / "reference.py", backend="docker")
    print(f"{'normal task still passes':<26} {'OK' if ok['passed'] else 'PROBLEM: ' + ok['reason']}")
    failures += not ok["passed"]
    for name, code in ATTACKS.items():
        with tempfile.TemporaryDirectory() as tmp:
            task = Path(tmp) / "attack_task"; task.mkdir()
            (task / "test_task.py").write_text(TEST_FILE)
            sol = Path(tmp) / "solution.py"; sol.write_text(code)
            r = grade(task, sol, backend="docker", run_scan=False, timeout=20)
            blocked = not r["passed"]
            failures += not blocked
            print(f"{name:<26} {'BLOCKED' if blocked else 'GOT THROUGH'} ({r['reason']})")
    print("\nSandbox OK" if failures == 0 else f"\n{failures} problem(s): the sandbox is not safe yet")
    return 1 if failures else 0

if __name__ == "__main__":
    sys.exit(main())
