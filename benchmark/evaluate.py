"""Score a predictions file against a built block.

    python benchmark/evaluate.py --block jatoba_id --predictions my_model.jsonl

predictions: one JSON object per line, {"id": ..., "probabilities": {candidate id: p, ...}} covering every candidate.
Decisions without a prediction are reported as missing, never silently skipped from the denominator of a claim.
Family-shift blocks also get per-query ranking by expected relevance (sum_i i * p_i), averaged over queries.
"""

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from jatoba.metrics import decision_metrics, expected_mrr, hierarchical_mean, ndcg_at_k  # noqa: E402


def evaluate(records: list[dict], predictions: dict[str, dict]) -> dict:
    rows, missing = [], []
    for record in records:
        predicted = predictions.get(record["id"])
        if predicted is None:
            missing.append(record["id"])
            continue
        p = [float(predicted[candidate]) for candidate, _ in record["options"]]
        rows.append({**decision_metrics(p, record["target"]), "task": record["task"], "family": record["family"], "group": record["group"],
                     "id": record["id"]})
    by_task = defaultdict(list)
    for r in rows:
        by_task[r["task"]].append(r)
    out = {"decisions": len(records), "scored": len(rows), "missing": len(missing),
           "tasks": {t: {k: sum(r[k] for r in rs) / len(rs) for k in ("ce_eps", "brier", "top1", "confidence")} | {"count": len(rs)}
                     for t, rs in sorted(by_task.items())}}
    if rows:
        out["hierarchical_ce_eps"] = hierarchical_mean(rows, "ce_eps", lambda r: r["group"])
    if records and records[0]["source"] in ("normastcu", "juristcu"):
        queries = defaultdict(list)
        for r in rows:
            queries[r["id"].split(":", 1)[1].split("|")[0]].append((r["expected_level"], r["target_level"], r["ce_eps"]))
        per_query = {q: {"ce_eps": sum(x[2] for x in items) / len(items), "ndcg@10": ndcg_at_k([x[0] for x in items], [x[1] for x in items]),
                         "mrr": expected_mrr([x[0] for x in items], [x[1] for x in items])} for q, items in queries.items()}
        out["query_weighted"] = {m: _mean([v[m] for v in per_query.values() if v[m] is not None]) for m in ("ce_eps", "ndcg@10", "mrr")}
    return out


def _mean(values: list[float]) -> float | None:
    return sum(values) / len(values) if values else None


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--block", required=True)
    parser.add_argument("--predictions", type=Path, required=True)
    parser.add_argument("--build", type=Path, default=ROOT / "benchmark/build")
    args = parser.parse_args()
    records = [json.loads(line) for line in (args.build / f"{args.block}.jsonl").read_text(encoding="utf-8").splitlines() if line]
    predictions = {}
    for line in args.predictions.read_text(encoding="utf-8").splitlines():
        if line.strip():
            item = json.loads(line)
            predictions[item["id"]] = item["probabilities"]
    print(json.dumps(evaluate(records, predictions), indent=1))


if __name__ == "__main__":
    main()
