"""PyTorch judge experiment (PYTORCH_JUDGE_PLAN.md). Uses no API calls.

  python scripts/train_pt_judge.py --dry-run   # synthetic data + tiny offline model: checks the pipeline only
  python scripts/train_pt_judge.py             # the real experiment, once, after all 530 runs are finished

The real run downloads distilbert-base-uncased once (about 260 MB) from Hugging Face.
"""
import argparse, json, random, statistics, sys, time
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from claimcheck.analysis import prepare
from claimcheck.plans import jobs
from claimcheck.config import run_key
from claimcheck.store import Store
from claimcheck import pt_judge

def real_factory():
    from transformers import AutoTokenizer, AutoModelForSequenceClassification
    name = pt_judge.BERT["name"]
    return AutoTokenizer.from_pretrained(name), AutoModelForSequenceClassification.from_pretrained(name, num_labels=2)

def tiny_factory_for(texts):
    """A tiny DistilBERT with a tokenizer trained on the given texts. Offline; for checks only."""
    from tokenizers import Tokenizer, models, trainers, pre_tokenizers
    from transformers import PreTrainedTokenizerFast, DistilBertConfig, DistilBertForSequenceClassification
    tk = Tokenizer(models.WordPiece(unk_token="[UNK]"))
    tk.pre_tokenizer = pre_tokenizers.Whitespace()
    tk.train_from_iterator(texts, trainers.WordPieceTrainer(vocab_size=400, special_tokens=["[PAD]", "[UNK]", "[CLS]", "[SEP]"]))
    def factory():
        import torch
        torch.manual_seed(pt_judge.SEED)
        tok = PreTrainedTokenizerFast(tokenizer_object=tk, pad_token="[PAD]", unk_token="[UNK]")
        cfg = DistilBertConfig(vocab_size=tk.get_vocab_size(), dim=32, n_layers=1, n_heads=2, hidden_dim=64, num_labels=2)
        return tok, DistilBertForSequenceClassification(cfg)
    return factory

def synthetic_data(n_tasks=40, seed=7):
    rng = random.Random(seed); data = []
    for t in range(n_tasks):
        broken = t % 3 == 0
        for model in ("big", "small"):
            body = ("from helper_missing import cases" if broken else "def test_ok(): assert f(2) == 4") + f" task {t} " + " ".join(rng.choice(["alpha", "beta", "gamma", "delta"]) for _ in range(20))
            data.append({"key": f"{model}|blind|t{t}", "task": f"t{t}", "category": "broken_env" if broken else "solvable",
                         "model": model, "condition": "blind", "label": int(broken), "text": "claim: success\n" + body})
    return data

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--force", action="store_true", help="rerun even though results exist (must be logged as a deviation)")
    ap.add_argument("--results", default=str(ROOT / "results"))
    a = ap.parse_args()
    res_dir = Path(a.results)
    if a.dry_run:
        data = synthetic_data()
        print(f"DRY RUN: {len(data)} synthetic examples, tiny offline model. Results are meaningless; this checks the pipeline.")
        cfg = dict(pt_judge.BERT, epochs=2, max_len=64)
        res = pt_judge.run_experiment(data, tiny_factory_for([d["text"] for d in data]), judgments=None, cfg=cfg)
        print(pt_judge.report(res))
        print(f"\nDevice used: {pt_judge.pick_device()}. Pipeline OK.")
        return 0
    out_md = res_dir / "pytorch_judge.md"
    if out_md.exists() and not a.force:
        print("Refusing: the PyTorch judge has already run (results/pytorch_judge.md). The plan says it runs once.\n"
              "If a rerun is truly needed, use --force AND add a Deviation to PYTORCH_JUDGE_PLAN.md first."); return 1
    runs = Store(res_dir).runs()
    done = {r["key"] for r in prepare(runs)}
    expected = {run_key(*j) for j in jobs("full", ROOT / "tasks")}
    missing = expected - done
    if missing:
        print(f"Refusing: {len(missing)} of {len(expected)} runs are not finished yet. The plan trains once, on complete data."); return 1
    judgments = Store(res_dir, filename="judgments.jsonl", transcripts="judge_transcripts").runs()
    data = pt_judge.build_dataset(runs, res_dir, ROOT / "tasks")
    print(f"{len(data)} success claims, {sum(d['label'] for d in data)} false. Device: {pt_judge.pick_device()}")
    t0 = time.time()
    res = pt_judge.run_experiment(data, real_factory, judgments=judgments)
    qtok = statistics.mean(j["tokens"] for j in judgments) if judgments else None
    text = pt_judge.report(res, qtok)
    out_md.write_text(text)
    with open(res_dir / "pt_predictions.jsonl", "w") as f:
        for p in res["predictions"]:
            f.write(json.dumps(p) + "\n")
    print(text)
    print(f"\nTotal time {time.time() - t0:.0f} s. Saved results/pytorch_judge.md and results/pt_predictions.jsonl")
    return 0

if __name__ == "__main__":
    sys.exit(main())
