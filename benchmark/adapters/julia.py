"""Julia-1 (SupersonicLabs/Julia-1 @ a85b1273), through its own `julia/` FastEngine on CPU FP32 (MPS is unsupported).

Before any benchmark output we reproduced Julia's published typed-decisions CPU run exactly (426/600, 542/800, 483/600,
literal-NOUL 391/600), so these numbers are canonical for its runtime. Julia's named-question API returns a softmax over
2-20 options; options above 48 tokens, question + options above 512 tokens, or a state above 8192 tokens are N/A under
its strict encoding. Our payload's NOUL has no criteria, so Julia runs its documented literal false/true fallback,
which is weaker on Julia's own data (391/600 vs 483/600 with descriptions). Report NOUL separately.
The one runtime change: `julia.router.encoder.specialize_decision_encoder` is disabled (a transformers-5.0-only fast
path that Julia's source describes as the same computation; logits verified identical across transformers versions).
"""

REPO, REVISION = "SupersonicLabs/Julia-1", "a85b127321d580d65176c89ced8273f305745d85"
MAX_LENGTH, HEAD_LENGTH = 8192, 512


def load(snapshot_dir: str, device: str = "cpu"):
    import sys

    sys.path.insert(0, snapshot_dir)
    import julia.router.encoder as encoder
    from julia import load_model

    encoder.specialize_decision_encoder = lambda model: False
    return load_model(snapshot_dir, device=device, strict_encoding=True, max_length=MAX_LENGTH, head_length=HEAD_LENGTH)


def ask(engine, state: str, question: dict, candidate_ids: list[str]) -> dict[str, float]:
    named = {"type": question["type"], "instructions": question["instructions"]}
    if question["type"] == "choice":
        named["criteria"] = dict(question["criteria"])
        keys = list(candidate_ids)
    elif question["type"] == "score":
        named["criteria"] = list(question["criteria"])
        keys = [str(i) for i in range(len(candidate_ids))]
    else:
        keys = ["false", "true"]
    probabilities = engine.predict(state=state, questions={"q": named})["answers"]["q"]["probabilities"]
    return {c: float(probabilities[k]) for c, k in zip(candidate_ids, keys)}
