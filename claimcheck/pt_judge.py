"""PyTorch judge experiment (PYTORCH_JUDGE_PLAN.md).

Predict, from what a reviewer can see, whether a run's "success" claim is false.
Compared on identical out-of-fold runs: majority class, TF-IDF + logistic regression,
fine-tuned DistilBERT, and the zero-shot Qwen judge.
"""
import json, math, random, time
from pathlib import Path
from .analysis import prepare
from .judge import build_messages, judge_key
from .stats import wilson_ci, mcnemar_exact

SEED = 2026
N_FOLDS = 5
BERT = {"name": "distilbert-base-uncased", "epochs": 4, "lr": 3e-5, "batch": 8, "weight_decay": 0.01, "max_len": 512}

# ---------- dataset ----------
def example_text(record: dict, transcript: dict, task_dir: Path) -> str:
    """Claim and summary first (survive truncation), then exactly what the Qwen judge saw."""
    user = build_messages(record, transcript, task_dir)[1]["content"].replace("\n\n/no_think", "")
    return f"claim: {record['claim']}\nsummary: {record.get('summary') or '(none)'}\n\n{user}"

def build_dataset(runs: list[dict], results: Path, tasks_dir: Path) -> list[dict]:
    out = []
    for r in prepare(runs):
        if r["claim"] != "success":
            continue
        transcript = json.loads((Path(results) / r["transcript"]).read_text())
        out.append({"key": r["key"], "task": r["task"], "category": r["category"], "model": r["model"],
                    "condition": r["condition"], "label": int(not (r["solvable"] and r["passed"])),
                    "text": example_text(r, transcript, Path(tasks_dir) / r["task"])})
    return out

def folds(data: list[dict], n: int = N_FOLDS, seed: int = SEED) -> list[int]:
    """Fold index per example; a task never appears in two folds."""
    from sklearn.model_selection import StratifiedGroupKFold
    y = [d["label"] for d in data]
    groups = [d["task"] for d in data]
    fold = [0] * len(data)
    splitter = StratifiedGroupKFold(n_splits=n, shuffle=True, random_state=seed)
    for k, (_, test_idx) in enumerate(splitter.split([0] * len(data), y, groups)):
        for i in test_idx:
            fold[i] = k
    return fold

# ---------- methods ----------
def majority(train: list[dict], test: list[dict]) -> list[float]:
    p = sum(d["label"] for d in train) / len(train)
    return [float(p >= 0.5)] * len(test)

def tfidf_logreg(train: list[dict], test: list[dict]) -> list[float]:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression
    vec = TfidfVectorizer(ngram_range=(1, 2), max_features=20_000, sublinear_tf=True)
    X = vec.fit_transform([d["text"] for d in train])
    clf = LogisticRegression(C=1.0, class_weight="balanced", max_iter=2000, random_state=SEED)
    clf.fit(X, [d["label"] for d in train])
    return list(clf.predict_proba(vec.transform([d["text"] for d in test]))[:, 1])

def pick_device():
    import torch
    if torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")

def distilbert(train: list[dict], test: list[dict], factory, device=None, cfg: dict = BERT, log=print) -> list[float]:
    """Fine-tune a fresh model per fold. factory() -> (tokenizer, model) so tests can use a tiny offline model."""
    import torch
    torch.manual_seed(SEED); random.seed(SEED)
    device = device or pick_device()
    tok, model = factory()
    model.to(device)
    import inspect
    accepted = set(inspect.signature(model.forward).parameters)
    def enc(ds):
        # Pass only inputs the model accepts. Some tokenizer/library versions add token_type_ids,
        # which DistilBERT's forward() rejects (seen with transformers 4.57).
        out = tok([d["text"] for d in ds], truncation=True, max_length=cfg["max_len"], padding=True, return_tensors="pt")
        return {k: v for k, v in out.items() if k in accepted}
    Xtr, ytr = enc(train), torch.tensor([d["label"] for d in train])
    pos = int(ytr.sum()); neg = len(ytr) - pos
    weights = torch.tensor([len(ytr) / (2 * max(neg, 1)), len(ytr) / (2 * max(pos, 1))], dtype=torch.float, device=device)
    loss_fn = torch.nn.CrossEntropyLoss(weight=weights)
    opt = torch.optim.AdamW(model.parameters(), lr=cfg["lr"], weight_decay=cfg["weight_decay"])
    order = list(range(len(train)))
    rng = random.Random(SEED)
    model.train()
    for epoch in range(cfg["epochs"]):
        rng.shuffle(order)
        total = 0.0
        for s in range(0, len(order), cfg["batch"]):
            idx = order[s:s + cfg["batch"]]
            batch = {k: v[idx].to(device) for k, v in Xtr.items()}
            loss = loss_fn(model(**batch).logits, ytr[idx].to(device))
            opt.zero_grad(); loss.backward(); opt.step()
            total += loss.item() * len(idx)
        log(f"    epoch {epoch + 1}/{cfg['epochs']}  loss {total / len(order):.4f}")
    model.eval()
    Xte = enc(test)
    probs = []
    with torch.no_grad():
        for s in range(0, len(test), 32):
            batch = {k: v[s:s + 32].to(device) for k, v in Xte.items()}
            probs += torch.softmax(model(**batch).logits, dim=-1)[:, 1].cpu().tolist()
    return probs

def qwen_predictions(data: list[dict], judgments: list[dict]) -> dict[str, int | None]:
    """Fixed mapping: false success predicted when genuine_solution is 'no' or 'unsure'.
    None = no parsed verdict (excluded from Qwen's comparisons, counted)."""
    by_run = {j["run_key"]: j for j in judgments}
    out = {}
    for d in data:
        j = by_run.get(d["key"])
        if not j or not j.get("judge_parsed"):
            out[d["key"]] = None
        else:
            out[d["key"]] = int(j["genuine_solution"] in ("no", "unsure"))
    return out

# ---------- evaluation ----------
def metrics(y: list[int], p: list[int]) -> dict:
    n = len(y)
    tp = sum(1 for a, b in zip(y, p) if a == 1 and b == 1); tn = sum(1 for a, b in zip(y, p) if a == 0 and b == 0)
    fp = sum(1 for a, b in zip(y, p) if a == 0 and b == 1); fn = sum(1 for a, b in zip(y, p) if a == 1 and b == 0)
    prec = tp / (tp + fp) if tp + fp else float("nan")
    rec = tp / (tp + fn) if tp + fn else float("nan")
    f1 = 2 * prec * rec / (prec + rec) if (prec == prec and rec == rec and prec + rec) else float("nan")
    tpr = rec; tnr = tn / (tn + fp) if tn + fp else float("nan")
    return {"n": n, "correct": tp + tn, "accuracy": (tp + tn) / n if n else float("nan"),
            "accuracy_ci": wilson_ci(tp + tn, n), "balanced_accuracy": (tpr + tnr) / 2 if tpr == tpr and tnr == tnr else float("nan"),
            "precision": prec, "recall": rec, "f1": f1, "tp": tp, "tn": tn, "fp": fp, "fn": fn}

def run_experiment(data: list[dict], factory, judgments: list[dict] | None = None, device=None, cfg: dict = BERT, log=print) -> dict:
    fold = folds(data)
    probs = {"majority": [None] * len(data), "tfidf_logreg": [None] * len(data), "distilbert": [None] * len(data)}
    seconds = {"tfidf_logreg": 0.0, "distilbert": 0.0}
    for k in range(N_FOLDS):
        tr = [d for d, f in zip(data, fold) if f != k]; te_idx = [i for i, f in enumerate(fold) if f == k]
        te = [data[i] for i in te_idx]
        if not te:
            continue
        assert not ({d["task"] for d in tr} & {d["task"] for d in te}), "task leaked across folds"
        log(f"fold {k + 1}/{N_FOLDS}: train {len(tr)}, test {len(te)}")
        for name, fn in [("majority", majority), ("tfidf_logreg", tfidf_logreg)]:
            t0 = time.time(); out = fn(tr, te)
            if name in seconds: seconds[name] += time.time() - t0
            for i, v in zip(te_idx, out): probs[name][i] = v
        t0 = time.time(); out = distilbert(tr, te, factory, device, cfg, log)
        seconds["distilbert"] += time.time() - t0
        for i, v in zip(te_idx, out): probs["distilbert"][i] = v
    y = [d["label"] for d in data]
    preds = {m: [int(v >= 0.5) for v in ps] for m, ps in probs.items()}
    res = {"n": len(data), "positives": sum(y), "fold_of": fold, "methods": {}, "by_category": {}, "tests": {}, "seconds": seconds}
    for m, p in preds.items():
        res["methods"][m] = metrics(y, p)
    q = qwen_predictions(data, judgments or []) if judgments is not None else None
    if q is not None:
        keep = [i for i, d in enumerate(data) if q[d["key"]] is not None]
        res["methods"]["qwen_zero_shot"] = metrics([y[i] for i in keep], [q[data[i]["key"]] for i in keep])
        res["qwen_unscored"] = len(data) - len(keep)
        preds["qwen_zero_shot"] = [q[d["key"]] for d in data]
    for cat in sorted({d["category"] for d in data}):
        idx = [i for i, d in enumerate(data) if d["category"] == cat]
        res["by_category"][cat] = {m: metrics([y[i] for i in idx], [p[i] for i in idx if p[i] is not None] if m == "qwen_zero_shot" else [p[i] for i in idx])
                                   for m, p in preds.items() if m != "qwen_zero_shot" or all(p[i] is not None for i in idx)}
    def paired(a, b):
        idx = [i for i in range(len(data)) if preds[a][i] is not None and preds[b][i] is not None]
        return mcnemar_exact([(preds[a][i] == y[i], preds[b][i] == y[i]) for i in idx])
    if q is not None:
        res["tests"]["DistilBERT vs Qwen"] = paired("distilbert", "qwen_zero_shot")
    res["tests"]["DistilBERT vs TF-IDF"] = paired("distilbert", "tfidf_logreg")
    res["predictions"] = [{"key": d["key"], "task": d["task"], "category": d["category"], "label": d["label"],
                           **{m: preds[m][i] for m in preds}, "distilbert_prob": probs["distilbert"][i]} for i, d in enumerate(data)]
    return res

def report(res: dict, qwen_tokens: float | None = None) -> str:
    f = lambda x: "n/a" if x != x else f"{x:.2f}"
    pc = lambda x: "n/a" if x != x else f"{100 * x:.0f}%"
    L = ["# PyTorch judge results", "", f"Success claims: {res['n']} ({res['positives']} false). "
         f"5-fold cross-validation split by task (PYTORCH_JUDGE_PLAN.md).", "",
         "| Method | n | Accuracy | 95% CI | Balanced acc. | Precision | Recall | F1 |", "|---|---|---|---|---|---|---|---|"]
    for m, v in res["methods"].items():
        lo, hi = v["accuracy_ci"]
        L.append(f"| {m} | {v['n']} | {pc(v['accuracy'])} | [{pc(lo)}, {pc(hi)}] | {pc(v['balanced_accuracy'])} | "
                 f"{f(v['precision'])} | {f(v['recall'])} | {f(v['f1'])} |")
    if "qwen_unscored" in res:
        L.append(f"\nQwen had no parsed verdict for {res['qwen_unscored']} run(s); they are excluded from its row and from its test.")
    L += ["", "## Accuracy by task category", "", "| Category | " + " | ".join(next(iter(res["by_category"].values())).keys()) + " |",
          "|---|" + "---|" * len(next(iter(res["by_category"].values())))]
    for cat, ms in res["by_category"].items():
        L.append(f"| {cat} | " + " | ".join(f"{pc(v['accuracy'])} (n={v['n']})" for v in ms.values()) + " |")
    L += ["", "## Planned tests (exact McNemar on per-run correctness)", ""]
    for name, t in res["tests"].items():
        L.append(f"- **{name}**: {t['n_pairs']} runs; first right and second wrong {t['a_only']}, the reverse {t['b_only']}; p = {t['p']:.3g}")
    L += ["", "## Cost and speed", "",
          f"- DistilBERT: {res['seconds']['distilbert']:.0f} s total for 5 folds (training + prediction), $0, runs offline.",
          f"- TF-IDF + logistic regression: {res['seconds']['tfidf_logreg']:.1f} s total, $0."]
    if qwen_tokens:
        L.append(f"- Qwen judge: about {qwen_tokens:,.0f} tokens per run through the API (free tier).")
    L += ["", "_Generated by claimcheck/pt_judge.py, implementing PYTORCH_JUDGE_PLAN.md._"]
    return "\n".join(L)
