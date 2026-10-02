"""Progress, budget, and estimates, computed from the checkpoint store and the ledger."""
import json, statistics
from collections import Counter, defaultdict
from pathlib import Path
from .config import AGENT_MODELS, JUDGE_MODEL, FREE_LIMITS, SAFETY_FRACTION, ESTIMATED_TOKENS, PROMPT_VERSIONS, run_key
from .plans import jobs

DAILY_TOKENS = int(FREE_LIMITS["tpd"] * SAFETY_FRACTION)

def measured_tokens(runs: list[dict]) -> dict:
    """Average tokens per run by (model, condition), from finished runs of this prompt version."""
    groups = defaultdict(list)
    for r in runs:
        if r.get("prompt_version") == PROMPT_VERSIONS.get(r["condition"]):
            groups[(r["model"], r["condition"])].append(r["tokens"])
    return {k: statistics.mean(v) for k, v in groups.items() if v}

def progress(plan: str, tasks_dir: Path, runs: list[dict], ledger) -> list[dict]:
    done = {r["key"] for r in runs}
    avg = measured_tokens(runs)
    rows = []
    for model in AGENT_MODELS:
        row = {"model": model}
        need = 0.0
        for cond in ("blind", "agent"):
            js = [j for j in jobs(plan, tasks_dir) if j[0] == model and j[1] == cond]
            left = [j for j in js if run_key(*j) not in done]
            per_run = avg.get((model, cond), ESTIMATED_TOKENS[cond])
            row[cond] = (len(js) - len(left), len(js))
            row[f"{cond}_tokens_per_run"] = (round(per_run), (model, cond) in avg)
            need += len(left) * per_run
        row.update(ledger.summary(model))
        row["tokens_needed"] = round(need)
        row["days_left"] = need / DAILY_TOKENS
        rows.append(row)
    return rows

def judge_estimate(plan: str, tasks_dir: Path) -> dict:
    n = len(jobs(plan, tasks_dir))
    need = n * ESTIMATED_TOKENS["judge"]
    return {"model": JUDGE_MODEL, "transcripts": n, "tokens_needed": need, "days": need / DAILY_TOKENS}

def print_progress(plan, tasks_dir, runs, ledger):
    print(f"Plan: {plan}   (daily budget per model: {DAILY_TOKENS:,} tokens = 90% of {FREE_LIMITS['tpd']:,})\n")
    for r in progress(plan, tasks_dir, runs, ledger):
        b, a = r["blind"], r["agent"]
        bt, at = r["blind_tokens_per_run"], r["agent_tokens_per_run"]
        tag = lambda t: "measured" if t[1] else "estimate"
        print(f"{r['model']}")
        print(f"  runs done        blind {b[0]}/{b[1]}   agent {a[0]}/{a[1]}   remaining {b[1]-b[0] + a[1]-a[0]}")
        print(f"  tokens per run   blind {bt[0]:,} ({tag(bt)})   agent {at[0]:,} ({tag(at)})")
        print(f"  last 24h         {r['requests_24h']:,} requests, {r['tokens_24h']:,} tokens")
        print(f"  left today       {r['requests_left']:,} requests, {r['tokens_left']:,} tokens")
        print(f"  still needed     {r['tokens_needed']:,} tokens  ->  about {r['days_left']:.1f} day(s)\n")
    j = judge_estimate(plan, tasks_dir)
    print(f"{j['model']} (judge, Day 4; estimate only)")
    print(f"  {j['transcripts']} transcripts x {ESTIMATED_TOKENS['judge']:,} tokens = {j['tokens_needed']:,}  ->  about {j['days']:.1f} day(s)")

def outcome_table(runs: list[dict]) -> str:
    cats = ["true_success", "false_success", "true_failure", "false_failure", "unclear", "flagged"]
    lines = [f"{'model':<22}{'cond':<7}{'n':>3}  " + "  ".join(f"{c:>13}" for c in cats)]
    groups = defaultdict(list)
    for r in runs:
        groups[(r["model"], r["condition"])].append(r["outcome"])
    for (m, c), outs in sorted(groups.items()):
        cnt = Counter(outs)
        lines.append(f"{m:<22}{c:<7}{len(outs):>3}  " + "  ".join(f"{cnt[k]:>13}" for k in cats))
    return "\n".join(lines)
