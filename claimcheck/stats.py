"""Statistics used by ANALYSIS_PLAN.md. Standard library only; checked against SciPy in tests.

wilson_ci        95% Wilson score interval for a proportion
mcnemar_exact    exact McNemar test for paired yes/no outcomes (two-sided binomial on discordant pairs)
fisher_exact     two-sided Fisher exact test for a 2x2 table
newcombe_diff_ci 95% CI for a difference of two independent proportions (Newcombe hybrid score)
paired_diff_ci   95% CI for a difference of paired proportions (seeded bootstrap over tasks)
cohen_kappa      chance-corrected agreement between two labelings
"""
import math, random

Z = 1.959963984540054  # 97.5th percentile of the standard normal

def wilson_ci(k: int, n: int, z: float = Z) -> tuple[float, float]:
    if n == 0:
        return (float("nan"), float("nan"))
    p = k / n
    denom = 1 + z * z / n
    center = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return (max(0.0, center - half), min(1.0, center + half))

def _binom_two_sided(k: int, n: int) -> float:
    """Exact two-sided binomial test with p = 0.5 (symmetric, so double the smaller tail)."""
    if n == 0:
        return 1.0
    tail = sum(math.comb(n, i) for i in range(0, min(k, n - k) + 1)) / 2 ** n
    return min(1.0, 2 * tail)

def mcnemar_exact(pairs: list[tuple[bool, bool]]) -> dict:
    """pairs = [(a_yes, b_yes), ...]. Uses only discordant pairs."""
    b = sum(1 for x, y in pairs if x and not y)
    c = sum(1 for x, y in pairs if y and not x)
    return {"n_pairs": len(pairs), "a_only": b, "b_only": c, "p": _binom_two_sided(min(b, c), b + c)}

def fisher_exact(a: int, b: int, c: int, d: int) -> float:
    """Table [[a, b], [c, d]]. Two-sided: sum of probabilities <= observed (SciPy's definition)."""
    r1, r2, c1, n = a + b, c + d, a + c, a + b + c + d
    def p(x):
        return math.comb(r1, x) * math.comb(r2, c1 - x) / math.comb(n, c1)
    lo, hi = max(0, c1 - r2), min(r1, c1)
    p_obs = p(a)
    return min(1.0, sum(p(x) for x in range(lo, hi + 1) if p(x) <= p_obs * (1 + 1e-7)))

def newcombe_diff_ci(k1: int, n1: int, k2: int, n2: int) -> tuple[float, float]:
    p1, p2 = k1 / n1, k2 / n2
    l1, u1 = wilson_ci(k1, n1); l2, u2 = wilson_ci(k2, n2)
    d = p1 - p2
    return (d - math.sqrt((p1 - l1) ** 2 + (u2 - p2) ** 2), d + math.sqrt((u1 - p1) ** 2 + (p2 - l2) ** 2))

def paired_diff_ci(pairs: list[tuple[bool, bool]], reps: int = 10_000, seed: int = 2026) -> tuple[float, float]:
    """Bootstrap over tasks (keeps each task's pair together). Difference = rate(a) - rate(b)."""
    if not pairs:
        return (float("nan"), float("nan"))
    rng = random.Random(seed)
    n = len(pairs)
    diffs = []
    for _ in range(reps):
        s = [pairs[rng.randrange(n)] for _ in range(n)]
        diffs.append(sum(x for x, _ in s) / n - sum(y for _, y in s) / n)
    diffs.sort()
    return (diffs[int(0.025 * reps)], diffs[int(0.975 * reps) - 1])

def cohen_kappa(a: list, b: list) -> float:
    n = len(a)
    if n == 0:
        return float("nan")
    labels = set(a) | set(b)
    po = sum(x == y for x, y in zip(a, b)) / n
    pe = sum((a.count(l) / n) * (b.count(l) / n) for l in labels)
    return 1.0 if pe == 1 else (po - pe) / (1 - pe)
