"""Everything to review before the full run.   python scripts/pilot_report.py

1. Actual token usage vs our estimates
2. Rate-limit headers Groq sent back, checked against config limits
3. Ledger and checkpoint integrity
4. Pilot outcomes
5. Updated completion estimate for the full experiment
"""
import json, statistics, sys
from collections import defaultdict
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from claimcheck.config import ESTIMATED_TOKENS, FREE_LIMITS, run_key
from claimcheck.ledger import Ledger
from claimcheck.plans import jobs
from claimcheck.report import outcome_table, print_progress
from claimcheck.store import Store

def main(results=ROOT / "results") -> int:
    store, ledger = Store(results), Ledger(results / "ledger.sqlite")
    pilot_keys = {run_key(*j) for j in jobs("pilot", ROOT / "tasks")}
    runs = [r for r in store.runs() if r["key"] in pilot_keys]
    calls = [c for c in ledger.calls() if c["run_key"] in pilot_keys]
    problems = []

    print("=" * 70 + "\n1. TOKEN USAGE (actual vs estimate)\n" + "=" * 70)
    by = defaultdict(list)
    for r in runs:
        by[(r["model"], r["condition"])].append(r["tokens"])
    for (m, c), toks in sorted(by.items()):
        est = ESTIMATED_TOKENS[c]
        print(f"{m:<22} {c:<6} runs={len(toks):>2}  avg={statistics.mean(toks):>7,.0f}  "
              f"min={min(toks):>6,}  max={max(toks):>6,}  estimate={est:,}  ({statistics.mean(toks) / est:.0%} of estimate)")
    ok_calls = [c for c in calls if c["status"] == "ok"]
    if ok_calls:
        for m in sorted({c["model"] for c in ok_calls}):
            mc = [c for c in ok_calls if c["model"] == m]
            mean = lambda k: statistics.mean(c[k] for c in mc)
            print(f"{m:<22} per call: prompt={mean('prompt_tokens'):,.0f}  output={mean('completion_tokens'):,.0f}  "
                  f"(reasoning={mean('reasoning_tokens'):,.0f})  latency={mean('latency_s'):.1f}s  "
                  f"max single call={max(c['total_tokens'] for c in mc):,} tokens (per-minute cap {FREE_LIMITS['tpm']:,})")

    print("\n" + "=" * 70 + "\n2. RATE-LIMIT HEADERS from Groq\n" + "=" * 70)
    seen = defaultdict(dict)
    for c in sorted(calls, key=lambda c: c["ts"]):
        for k, v in json.loads(c["headers"] or "{}").items():
            seen[c["model"]][k] = v
    if not seen:
        problems.append("no rate-limit headers recorded")
        print("None recorded.")
    for m, hdrs in seen.items():
        print(m)
        for k, v in sorted(hdrs.items()):
            print(f"   {k}: {v}")
        checks = {"x-ratelimit-limit-requests": FREE_LIMITS["rpd"], "x-ratelimit-limit-tokens": FREE_LIMITS["tpm"]}
        for k, ours in checks.items():
            if k in hdrs:
                try:
                    theirs = int(float(hdrs[k]))
                except ValueError:
                    continue
                verdict = "matches config" if theirs == ours else ("LOWER than config: lower it in config.py" if theirs < ours else "higher than config (config stays conservative)")
                print(f"   -> {k} = {theirs:,}; config = {ours:,}: {verdict}")
                if theirs < ours:
                    problems.append(f"{m}: provider {k} {theirs} < config {ours}")
    limited = [c for c in calls if c["status"] == "rate_limited"]
    print(f"\n429 responses during pilot: {len(limited)} (each was waited out or paused, never retried blindly)")

    print("\n" + "=" * 70 + "\n3. LEDGER AND CHECKPOINTS\n" + "=" * 70)
    keys = [r["key"] for r in runs]
    dupes = {k for k in keys if keys.count(k) > 1}
    missing = pilot_keys - set(keys)
    print(f"pilot runs expected {len(pilot_keys)}, saved {len(set(keys))}, duplicates {len(dupes)}, missing {len(missing)}")
    if dupes: problems.append(f"duplicate runs: {sorted(dupes)}")
    if missing: problems.append(f"missing runs: {sorted(missing)}")
    mism = []
    for r in runs:
        ledger_tokens = sum(c["total_tokens"] for c in calls if c["run_key"] == r["key"] and c["status"] == "ok")
        ledger_calls = sum(1 for c in calls if c["run_key"] == r["key"] and c["status"] == "ok")
        if ledger_tokens != r["tokens"] or ledger_calls != r["calls"]:
            mism.append(r["key"])
        if not (results / r["transcript"]).exists():
            problems.append(f"missing transcript for {r['key']}")
    print(f"runs whose ledger tokens/calls don't match the saved record: {len(mism)}")
    if mism:
        print("  (a run that was cut off and redone also leaves ledger calls from the first attempt)")
    from collections import Counter
    by_status = Counter(c["status"] for c in calls)
    print("ledger rows for pilot: " + ", ".join(f"{n} {st}" for st, n in sorted(by_status.items())))
    print("Resume check: run `python scripts/run_eval.py --plan pilot` again; it must say '0 to run now'.")

    print("\n" + "=" * 70 + "\n4. PILOT OUTCOMES\n" + "=" * 70)
    print(outcome_table(runs) if runs else "No runs yet.")
    print("\nPer run:")
    for r in sorted(runs, key=lambda r: (r["model"], r["condition"], r["task"])):
        extra = ""
        if r["condition"] == "agent":
            how = r.get("claim_channel") or ("tool" if r.get("gave_final_report") else ("forced" if r.get("forced_report") else "none"))
            extra = (f" report={how} empty={r.get('empty_replies', 0)} no_tool={r.get('no_tool_replies', 0)} "
                     f"parse_fail={r.get('parse_failures', 0)} length_stops={r.get('length_stops', 0)} "
                     f"gaming_attempts={r.get('gaming_attempt_count', 0)}")
        print(f"  {r['model']:<22} {r['condition']:<6} {r['task']} ({r['category']:<10}) claim={r['claim']:<8}"
              f"passed={str(r['passed']):<6}{r['outcome']:<14}turns={r['turns']} read_tests={r['read_test_file']}{extra}")
    agent_runs = [r for r in runs if r["condition"] == "agent"]
    if agent_runs:
        unclear = sum(r["claim"] == "unclear" for r in agent_runs)
        forced = sum(bool(r.get("forced_report")) for r in agent_runs)
        lengths = sum(r.get("length_stops", 0) for r in agent_runs)
        chans = Counter(r.get("claim_channel", "?") for r in agent_runs)
        gaming = sum(1 for r in agent_runs if r.get("gaming_attempt_count"))
        print(f"\nAgent protocol health: {unclear}/{len(agent_runs)} without a claim, {forced} forced reports, "
              f"{lengths} replies cut off at the output cap")
        print("Claim channels: " + ", ".join(f"{k}={v}" for k, v in sorted(chans.items())))
        print(f"Runs with a gaming attempt (any write flagged by the scanner): {gaming}")
        if unclear > len(agent_runs) // 3:
            problems.append(f"{unclear}/{len(agent_runs)} agent runs ended without a claim: protocol problem, not a result")
        if lengths:
            problems.append(f"{lengths} replies hit the {1200}-token output cap: consider raising it")
    print("\n(Small pilot: these numbers check that the pipeline works. They are not results.)")

    print("\n" + "=" * 70 + "\n5. UPDATED ESTIMATE FOR THE FULL EXPERIMENT\n" + "=" * 70)
    print_progress("full", ROOT / "tasks", store.runs(), ledger, results)

    print("\n" + "=" * 70)
    if problems:
        print("PROBLEMS FOUND:\n  " + "\n  ".join(problems))
    else:
        print("No problems found.")
    print("Send this whole report to Claude. Do NOT create results/PILOT_APPROVED until it is reviewed.")
    return 1 if problems else 0

if __name__ == "__main__":
    sys.exit(main())
