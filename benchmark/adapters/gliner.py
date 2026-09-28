"""GLiNER2.5-multi-Decide (fastino/GLiNER2.5-multi-Decide @ 6bc1d43d) through gliner2 v2.0.0's Classifier, as shipped.

We read the package's own `result.probabilities(task)` (a softmax over the declared labels for single/ordinal tasks)
and never re-normalise or re-temper it. GLiNER has no NOUL primitive: a NOUL without criteria is asked as a single
choice {"yes": "Yes", "no": "No"} (the JevBench GLiNER2 convention); yes -> "true", no -> "false".
Inputs longer than the checkpoint's max_len (4096 sub-words) are N/A, never truncated.
"""

REPO, REVISION = "fastino/GLiNER2.5-multi-Decide", "6bc1d43d201b0691e733626389af8c57eea3ea68"
TASK = "decision"


def labels_for(question: dict, candidate_ids: list[str]) -> tuple[dict[str, str], list[str]]:
    """GLiNER labels, and the GLiNER label that stands for each candidate id (in candidate order)."""
    if question["type"] == "noul":
        return {"yes": "Yes", "no": "No"}, ["no", "yes"]
    if question["type"] == "score":
        return {str(i): str(d) for i, d in enumerate(question["criteria"])}, [str(i) for i in range(len(candidate_ids))]
    return {k: str(v) for k, v in question["criteria"].items()}, list(candidate_ids)


def ask(classifier, state: str, question: dict, candidate_ids: list[str]) -> dict[str, float]:
    from gliner2.classification import ClassificationSchema

    labels, order = labels_for(question, candidate_ids)
    schema = ClassificationSchema()
    make = schema.ordinal if question["type"] == "score" else schema.single
    result = classifier.classify(state, make(TASK, labels, instruction=question["instructions"]))
    probabilities = dict(result.probabilities(TASK))
    return {c: float(probabilities[g]) for c, g in zip(candidate_ids, order)}
