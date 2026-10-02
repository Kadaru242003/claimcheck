"""PyTorch judge: labels, no ground truth in inputs, task-grouped folds, and a training loop that really learns.
Skipped automatically where torch/transformers/sklearn are not installed."""
import json, sys
from pathlib import Path
import pytest
torch = pytest.importorskip("torch"); pytest.importorskip("transformers"); pytest.importorskip("sklearn")
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from claimcheck import pt_judge
from claimcheck.config import PROMPT_VERSIONS
from train_pt_judge import tiny_factory_for, synthetic_data

TASKS = ROOT / "tasks"

def rec(task, claim="success", passed=False, model="openai/gpt-oss-120b"):
    meta = json.loads((TASKS / task / "meta.json").read_text())
    return {"key": f"{model}|blind|{task}|s1|{PROMPT_VERSIONS['blind']}", "task": task, "category": meta["category"],
            "solvable": meta["solvable"], "model": model, "condition": "blind", "prompt_version": PROMPT_VERSIONS["blind"],
            "claim": claim, "passed": passed, "flags": [], "summary": "Done.", "transcript": f"t_{task}.json"}

def write_transcripts(tmp, records):
    for r in records:
        (tmp / r["transcript"]).write_text(json.dumps({"messages": [{"role": "system", "content": "s"}, {"role": "user", "content": "u"},
            {"role": "assistant", "content": json.dumps({"code": "def f():\n    return 1\n", "status": r["claim"], "summary": "Done."})}]}))

def test_labels_and_selection(tmp_path):
    rs = [rec("s001", passed=True), rec("b001"), rec("i003", passed=True), rec("i011", claim="failure")]
    write_transcripts(tmp_path, rs)
    data = {d["task"]: d for d in pt_judge.build_dataset(rs, tmp_path, TASKS)}
    assert set(data) == {"s001", "b001", "i003"}            # failure claims are not in this experiment
    assert (data["s001"]["label"], data["b001"]["label"], data["i003"]["label"]) == (0, 1, 1)  # exploited pass = false claim

def test_input_text_has_no_ground_truth(tmp_path):
    rs = [rec("i003", passed=True), rec("b008")]
    write_transcripts(tmp_path, rs)
    for d in pt_judge.build_dataset(rs, tmp_path, TASKS):
        meta = json.loads((TASKS / d["task"] / "meta.json").read_text())
        for leak in ["why_unsolvable", "broken_env", "impossible", "solvable", "passed", "exploited", meta["why_unsolvable"]]:
            assert leak not in d["text"], f"{d['task']} input leaks {leak!r}"
        assert d["text"].startswith("claim: success\nsummary: Done.")

def test_folds_never_share_a_task():
    data = synthetic_data()
    fold = pt_judge.folds(data)
    for k in range(pt_judge.N_FOLDS):
        train = {d["task"] for d, f in zip(data, fold) if f != k}
        test = {d["task"] for d, f in zip(data, fold) if f == k}
        assert test and not (train & test)
    assert fold == pt_judge.folds(data)  # same seed, same folds

def test_training_loop_actually_learns():
    """A correct loop must let a tiny model memorize a simple dataset. A broken loop (no gradient
    updates, wrong labels, wrong loss) stays at chance. Guards against 'it runs but does not learn'."""
    data = synthetic_data(n_tasks=12)
    cfg = dict(pt_judge.BERT, epochs=25, lr=5e-3, max_len=48, batch=8)
    probs = pt_judge.distilbert(data, data, tiny_factory_for([d["text"] for d in data]), torch.device("cpu"), cfg, log=lambda s: None)
    acc = sum(int(p >= 0.5) == d["label"] for p, d in zip(probs, data)) / len(data)
    assert acc == 1.0, f"training accuracy {acc:.2f}: the loop is not learning"

def test_distilbert_is_deterministic():
    data = synthetic_data(n_tasks=6)
    cfg = dict(pt_judge.BERT, epochs=2, max_len=32)
    f = tiny_factory_for([d["text"] for d in data])
    a = pt_judge.distilbert(data, data, f, torch.device("cpu"), cfg, log=lambda s: None)
    b = pt_judge.distilbert(data, data, f, torch.device("cpu"), cfg, log=lambda s: None)
    assert a == pytest.approx(b)

def test_qwen_mapping_is_the_preregistered_one():
    data = [{"key": k} for k in "abcd"]
    js = [{"run_key": "a", "genuine_solution": "no", "judge_parsed": True},
          {"run_key": "b", "genuine_solution": "unsure", "judge_parsed": True},
          {"run_key": "c", "genuine_solution": "yes", "judge_parsed": True},
          {"run_key": "d", "genuine_solution": "invalid", "judge_parsed": False}]
    assert pt_judge.qwen_predictions(data, js) == {"a": 1, "b": 1, "c": 0, "d": None}

def test_metrics_against_sklearn():
    from sklearn.metrics import accuracy_score, balanced_accuracy_score, f1_score, precision_score, recall_score
    y = [1, 0, 1, 1, 0, 0, 1, 0, 1, 1]; p = [1, 0, 0, 1, 1, 0, 1, 0, 0, 1]
    m = pt_judge.metrics(y, p)
    assert m["accuracy"] == pytest.approx(accuracy_score(y, p))
    assert m["balanced_accuracy"] == pytest.approx(balanced_accuracy_score(y, p))
    assert (m["precision"], m["recall"], m["f1"]) == pytest.approx((precision_score(y, p), recall_score(y, p), f1_score(y, p)))

import subprocess
SCRIPT = ROOT / "scripts" / "train_pt_judge.py"

def test_refuses_incomplete_data(tmp_path):
    (tmp_path / "runs.jsonl").write_text("")
    out = subprocess.run([sys.executable, str(SCRIPT), "--results", str(tmp_path)], capture_output=True, text=True)
    assert out.returncode == 1 and "not finished yet" in out.stdout

def test_refuses_to_run_twice(tmp_path):
    (tmp_path / "pytorch_judge.md").write_text("earlier result")
    out = subprocess.run([sys.executable, str(SCRIPT), "--results", str(tmp_path)], capture_output=True, text=True)
    assert out.returncode == 1 and "runs once" in out.stdout
