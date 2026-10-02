"""Run the pre-registered analysis.   python scripts/analyze.py
Writes results/analysis.md. Works on partial data and says how many runs are missing."""
import sys
from collections import Counter
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from claimcheck.analysis import analyze, report
from claimcheck.plans import jobs
from claimcheck.store import Store

def main(results=ROOT / "results"):
    runs = Store(results).runs()
    jpath = results / "judgments.jsonl"
    judgments = Store(results, filename="judgments.jsonl", transcripts="judge_transcripts").runs() if jpath.exists() else None
    planned = Counter((m, c) for m, c, _, _ in jobs("full", ROOT / "tasks"))
    text = report(analyze(runs, judgments, planned))
    (results / "analysis.md").write_text(text)
    print(text)

if __name__ == "__main__":
    main()
