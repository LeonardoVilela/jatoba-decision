"""The single semantic payload every evaluated model receives, and the mapping of its answers back to candidate ids.

Frozen before any external model output was seen: state verbatim; the question as `instructions`; CHOICE criteria
{candidate id: description} in presented order; SCORE criteria as the ordered level descriptions; NOUL as the
proposition only (no criteria). Adapters may not paraphrase or re-order anything to suit a particular model.
"""


def to_question(record: dict) -> tuple[dict, list[str]]:
    ids = [candidate for candidate, _ in record["options"]]
    kind = record["type"]
    if kind == "noul":
        if ids != ["false", "true"]:
            raise ValueError(f"{record['id']}: NOUL candidates must be ('false', 'true')")
        return {"type": "noul", "instructions": record["question"]}, ids
    if kind == "choice":
        return {"type": "choice", "instructions": record["question"], "criteria": dict(record["options"])}, ids
    if kind == "score":
        return {"type": "score", "instructions": record["question"], "criteria": [text for _, text in record["options"]]}, ids
    raise ValueError(f"unknown decision type {kind}")


def to_candidate_probabilities(question: dict, answer: dict, candidate_ids: list[str]) -> dict[str, float]:
    """Jev / Laya answer shape -> {candidate id: probability}. NOUL answers are P(true); SCORE index i is level i."""
    if question["type"] == "noul":
        p = float(answer["noul"])
        return {candidate_ids[0]: 1 - p, candidate_ids[1]: p}
    if question["type"] == "choice":
        return {c: float(answer["probabilities"][c]) for c in candidate_ids}
    return {c: float(answer["probabilities"][str(i)]) for i, c in enumerate(candidate_ids)}
