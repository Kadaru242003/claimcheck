"""`claimcheck <command>`: one entry point for the scripts in scripts/.

Each command runs the existing script unchanged, with the same arguments, so
`claimcheck status` and `python scripts/status.py` behave identically.
Works from a source checkout (pip install -e .), where tasks/ and scripts/ live.
"""
import runpy, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
COMMANDS = {
    "check-tasks": ("check_tasks.py", "verify every task behaves as labeled"),
    "probe": ("probe_exploits.py", "try known cheats against every unsolvable task"),
    "sandbox-test": ("test_sandbox.py", "prove the Docker sandbox blocks network, file, memory, process attacks"),
    "preflight": ("preflight.py", "check API key, models, and Docker before any call"),
    "run": ("run_eval.py", "run agents: --plan pilot|full"),
    "pilot-report": ("pilot_report.py", "review the agent pilot"),
    "judge": ("run_judge.py", "run the LLM judge: --plan pilot|full"),
    "judge-report": ("judge_report.py", "review the judge"),
    "status": ("status.py", "progress and remaining free-tier budget"),
    "analyze": ("analyze.py", "pre-registered analysis -> results/analysis.md"),
    "pt-judge": ("train_pt_judge.py", "PyTorch judge experiment (needs: pip install -e .[pt])"),
}

def usage() -> str:
    lines = ["usage: claimcheck <command> [args]", "", "commands:"]
    lines += [f"  {name:<14} {desc}" for name, (_, desc) in COMMANDS.items()]
    return "\n".join(lines)

def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if not argv or argv[0] in ("-h", "--help", "help"):
        print(usage()); return 0
    name, rest = argv[0], argv[1:]
    if name not in COMMANDS:
        print(f"unknown command: {name}\n\n{usage()}"); return 2
    script = ROOT / "scripts" / COMMANDS[name][0]
    if not script.exists():
        print(f"{script} not found: claimcheck commands need a source checkout (pip install -e .)"); return 2
    old = sys.argv
    sys.argv = [str(script), *rest]
    try:
        runpy.run_path(str(script), run_name="__main__")
    except SystemExit as e:
        return int(e.code or 0) if not isinstance(e.code, str) else 1
    finally:
        sys.argv = old
    return 0

if __name__ == "__main__":
    sys.exit(main())
