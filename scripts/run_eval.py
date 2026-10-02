"""Run the experiment. Safe to stop and rerun any time: finished runs are skipped.

  python scripts/run_eval.py --plan pilot
  python scripts/run_eval.py --plan full      # refused until results/PILOT_APPROVED exists

Each agent model runs in its own thread, since each has its own free-tier budget.
A model stops for the day when its budget is at 90%. A billing, auth, or plan error
stops everything immediately.
"""
import argparse, subprocess, sys, threading, time
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from claimcheck.agent import run_blind, run_agent
from claimcheck.config import AGENT_MODELS
from claimcheck.ledger import Ledger
from claimcheck.plans import jobs, load_tasks
from claimcheck.providers import GroqClient, MockClient, DailyLimitReached, FatalProviderError, TransientError
from claimcheck.store import Store

TASKS = ROOT / "tasks"

def mock_script(messages, tools=None):
    """Offline stand-in: always claims success and never really solves anything."""
    import json
    if not tools:
        return json.dumps({"code": "def placeholder():\n    pass\n", "status": "success", "summary": "Done."})
    turn = sum(1 for m in messages if m["role"] == "assistant")
    steps = [("read_file", {"path": "test_task.py"}),
             ("write_solution", {"code": "def placeholder():\n    pass\n"}),
             ("run_tests", {}),
             ("final_report", {"status": "success", "summary": "All tests pass."})]
    name, args = steps[min(turn, len(steps) - 1)]
    return [{"id": f"call_{turn}", "type": "function", "function": {"name": name, "arguments": json.dumps(args)}}]

def worker(model, my_jobs, store, ledger, backend, mock, stop, lock, log):
    client = MockClient(model, ledger, mock_script) if mock else GroqClient(model, ledger)
    tasks = load_tasks(TASKS)
    for (m, condition, task_id, sample) in my_jobs:
        if stop.is_set():
            return
        run = run_blind if condition == "blind" else run_agent
        try:
            rec, transcript = run(client, TASKS / task_id, tasks[task_id], sample, backend)
        except DailyLimitReached as e:
            log(f"[{model}] stopping for today: {e}"); return
        except FatalProviderError as e:
            log(f"[{model}] FATAL, stopping everything: {e}"); stop.set(); return
        except TransientError as e:
            log(f"[{model}] {task_id} {condition}: temporary problem ({e}); will retry on next run"); continue
        with lock:
            store.save(rec, transcript)
        log(f"[{model}] {condition:<5} {task_id}  claim={rec['claim']:<7} passed={str(rec['passed']):<5} "
            f"-> {rec['outcome']:<13} tokens={rec['tokens']}")

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", choices=["pilot", "full"], required=True)
    ap.add_argument("--mock", action="store_true", help="offline fake model for testing; spends nothing")
    ap.add_argument("--backend", choices=["docker", "local"], default="docker")
    ap.add_argument("--results", default=str(ROOT / "results"))
    args = ap.parse_args()
    if args.backend == "local" and not args.mock:
        print("Refusing: model-written code only runs in the Docker sandbox."); return 1
    results = Path(args.results)
    if args.plan == "full" and not (results / "PILOT_APPROVED").exists():
        print("Refusing: the full run starts only after the pilot is reviewed and results/PILOT_APPROVED exists.")
        return 1
    if not args.mock:
        if subprocess.run([sys.executable, str(ROOT / "scripts" / "preflight.py")]).returncode != 0:
            return 1
        if args.backend == "docker":
            from claimcheck.grading import build_image
            build_image()
    store, ledger = Store(results), Ledger(results / "ledger.sqlite")
    done = store.done_keys()
    from claimcheck.config import run_key
    todo = [j for j in jobs(args.plan, TASKS)
            if run_key(*j) not in done]
    total = len(jobs(args.plan, TASKS))
    print(f"Plan '{args.plan}': {total} runs, {total - len(todo)} already done, {len(todo)} to run now.")
    if not todo:
        return 0
    stop, lock = threading.Event(), threading.Lock()
    log = lambda s: print(time.strftime("%H:%M:%S"), s, flush=True)
    threads = [threading.Thread(target=worker, args=(m, [j for j in todo if j[0] == m], store, ledger,
                                                     args.backend, args.mock, stop, lock, log), daemon=True)
               for m in AGENT_MODELS]
    for t in threads:
        t.start()
    try:
        while any(t.is_alive() for t in threads):
            time.sleep(0.5)
    except KeyboardInterrupt:
        stop.set()
        print("\nStopping after the current runs. Finished runs are saved; rerun to resume.")
        for t in threads:
            t.join(timeout=300)
    print("\nRun `python scripts/status.py` for progress and remaining budget.")
    return 2 if stop.is_set() else 0

if __name__ == "__main__":
    sys.exit(main())
