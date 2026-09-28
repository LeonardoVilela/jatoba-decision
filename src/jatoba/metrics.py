"""Evaluation metrics, exactly as frozen for the reported JATOBÁ results.

Probability quality (epsilon-CE, Brier, ECE) and ranking quality (top-1, MRR, nDCG) are reported separately:
a model can rank the gold candidate first while assigning it a poorly calibrated probability, and vice versa.
"""

import math
from collections import defaultdict
from collections.abc import Callable, Mapping, Sequence

EPSILON = 0.005  # floor applied to EVERY model before cross-model CE, then renormalised
NDCG_CUTOFF = 10
RELEVANT_THRESHOLD = 1.5  # graded relevance >= 1.5 counts as relevant for MRR / top-1 relevant


def epsilon_distribution(p: Sequence[float], eps: float = EPSILON) -> list[float]:
    q = [max(float(x), eps) for x in p]
    total = sum(q)
    return [x / total for x in q]


def decision_metrics(p: Sequence[float], target: Sequence[float]) -> dict:
    """Per-decision metrics. `target` may be soft (annotator distributions); ties in p count fractionally."""
    if len(p) != len(target):
        raise ValueError("probabilities and target differ in length")
    q = epsilon_distribution(p)
    gold = max(range(len(target)), key=target.__getitem__)
    top = [i for i, x in enumerate(p) if x == max(p)]
    return {
        "ce_eps": -sum(t * math.log(x) for t, x in zip(target, q) if t > 0),
        "brier": sum((x - t) ** 2 for x, t in zip(p, target)),
        "top1": (gold in top) / len(top),
        "confidence": max(p),
        "p_gold": p[gold],
        "expected_level": sum(i * x for i, x in enumerate(p)),
        "target_level": sum(i * t for i, t in enumerate(target)),
    }


def hierarchical_mean(rows: Sequence[Mapping], key: str, group_of: Callable[[Mapping], str]) -> dict:
    """Record mean within group -> equal-weight mean over groups within task -> over tasks within family -> over
    families. Keeps large tasks and heavily repeated groups from dominating the headline number."""
    per_task: dict[str, dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))
    family_of = {}
    for r in rows:
        per_task[r["task"]][group_of(r)].append(r[key])
        family_of[r["task"]] = r["family"]
    task = {t: sum(sum(v) / len(v) for v in groups.values()) / len(groups) for t, groups in per_task.items()}
    families: dict[str, list[float]] = defaultdict(list)
    for t, value in task.items():
        families[family_of[t]].append(value)
    family = {f: sum(v) / len(v) for f, v in sorted(families.items())}
    return {"macro": sum(family.values()) / len(family), "family": family, "task": dict(sorted(task.items()))}


def ece_equal_mass(confidences: Sequence[float], correct: Sequence[bool], bins: int = 15) -> float:
    order = sorted(range(len(confidences)), key=lambda i: confidences[i])  # stable sort
    n = len(order)
    total = 0.0
    for b in range(bins):
        bucket = order[b * n // bins:(b + 1) * n // bins]
        if bucket:
            acc = sum(correct[i] for i in bucket) / len(bucket)
            conf = sum(confidences[i] for i in bucket) / len(bucket)
            total += len(bucket) / n * abs(acc - conf)
    return total


def _tie_blocks(scores: Sequence[float]) -> list[list[int]]:
    by_score: dict[float, list[int]] = defaultdict(list)
    for i, s in enumerate(scores):
        by_score[float(s)].append(i)
    return [by_score[s] for s in sorted(by_score, reverse=True)]


def _discount(position: int, cutoff: int) -> float:
    return 1.0 / math.log2(position + 1) if position <= cutoff else 0.0


def ndcg_at_k(scores: Sequence[float], gains: Sequence[float], cutoff: int = NDCG_CUTOFF) -> float | None:
    """Expected nDCG@k under a uniformly random order within ties (linear gain). None when no document has gain."""
    idcg = sum(g * _discount(i + 1, cutoff) for i, g in enumerate(sorted(gains, reverse=True)))
    if idcg == 0:
        return None
    dcg, start = 0.0, 0
    for block in _tie_blocks(scores):
        mean_discount = sum(_discount(start + j + 1, cutoff) for j in range(len(block))) / len(block)
        dcg += mean_discount * sum(gains[i] for i in block)
        start += len(block)
    return dcg / idcg


def expected_mrr(scores: Sequence[float], gains: Sequence[float], threshold: float = RELEVANT_THRESHOLD) -> float | None:
    relevant = [g >= threshold for g in gains]
    if not any(relevant):
        return None
    start = 0
    for block in _tie_blocks(scores):
        m, r = len(block), sum(relevant[i] for i in block)
        if r:
            # expected 1/rank of the first relevant item when the block is shuffled uniformly
            return sum(math.comb(m - j, r - 1) / math.comb(m, r) / (start + j) for j in range(1, m - r + 2))
        start += m
    return None


def expected_top1_relevant(scores: Sequence[float], gains: Sequence[float], threshold: float = RELEVANT_THRESHOLD) -> float:
    top = _tie_blocks(scores)[0]
    return sum(gains[i] >= threshold for i in top) / len(top)
