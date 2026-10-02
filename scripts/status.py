"""Progress and remaining free-tier budget.   python scripts/status.py [--plan pilot|full]"""
import argparse, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from claimcheck.ledger import Ledger
from claimcheck.report import print_progress
from claimcheck.store import Store

ap = argparse.ArgumentParser(); ap.add_argument("--plan", default="full", choices=["pilot", "full"])
ap.add_argument("--results", default=str(ROOT / "results")); a = ap.parse_args()
res = Path(a.results)
print_progress(a.plan, ROOT / "tasks", Store(res).runs(), Ledger(res / "ledger.sqlite"))
