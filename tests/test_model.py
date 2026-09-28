import random

import pytest
import torch

from jatoba import ContextTooLong, Decision, Jatoba
from jatoba.decision import encode_batch

STATE = "quero ouvir uma música tranquila agora por favor"
OPTIONS = {f"c{i}": f"opção número {i} sobre {w}" for i, w in enumerate(["clima", "música", "alarme", "notícias", "trânsito", "lista"])}


def probabilities(model, tokenizer, decision, order):
    batch, _ = encode_batch(tokenizer, [decision], orders=[order])
    with torch.inference_mode():
        p = torch.softmax(model(batch)[0, :len(order)].double(), -1)
    ids = list(decision.options)
    return {ids[option]: float(p[slot]) for slot, option in enumerate(order)}


def test_permutation_equivariance(model, tokenizer):
    decision = Decision("choice", STATE, "Qual é a intenção?", OPTIONS)
    reference = probabilities(model, tokenizer, decision, list(range(len(OPTIONS))))
    rng = random.Random(0)
    for _ in range(5):
        order = list(range(len(OPTIONS)))
        rng.shuffle(order)
        permuted = probabilities(model, tokenizer, decision, order)
        assert max(abs(permuted[k] - reference[k]) for k in reference) < 1e-6


def test_variable_k_in_one_batch(model, tokenizer):
    decisions = [Decision("choice", STATE, "Qual?", dict(list(OPTIONS.items())[:2])), Decision("choice", STATE, "Qual?", OPTIONS)]
    batch, _ = encode_batch(tokenizer, decisions)
    with torch.inference_mode():
        logits = model(batch)
    assert logits.shape == (2, len(OPTIONS))
    assert torch.all(logits[0, 2:] == torch.finfo(logits.dtype).min)
    for row, k in ((0, 2), (1, len(OPTIONS))):
        assert abs(float(torch.softmax(logits[row, :k].double(), -1).sum()) - 1) < 1e-9


def test_decide_keeps_candidate_ids_and_order(model, tokenizer):
    options = {"z_last": "texto z", "a_first": "texto a", "m_mid": "texto m"}
    result = Jatoba(model, tokenizer).decide(STATE, "Qual?", options)
    assert list(result.probabilities) == list(options)
    assert abs(sum(result.probabilities.values()) - 1) < 1e-9
    assert result.expected_level is None


def test_score_expected_level(model, tokenizer):
    levels = {"0": "ausente", "1": "baixa", "2": "moderada", "3": "alta"}
    result = Jatoba(model, tokenizer).decide(STATE, "Qual intensidade?", levels, kind="score")
    p = list(result.probabilities.values())
    assert result.expected_level == pytest.approx(sum(i * x for i, x in enumerate(p)))


def test_noul_requires_false_then_true():
    with pytest.raises(ValueError):
        Decision("noul", STATE, "É verdade?", {"true": "sim", "false": "não"})
    Decision("noul", STATE, "É verdade?", {"false": "não", "true": "sim"})


def test_context_is_never_silently_truncated(model, tokenizer):
    long_state = " ".join(["palavra"] * 300)
    decision = Decision("choice", long_state, "Qual?", dict(list(OPTIONS.items())[:3]))
    with pytest.raises(ContextTooLong):
        encode_batch(tokenizer, [decision], max_context_tokens=64)
    for policy in ("keep_start", "keep_end"):
        batch, infos = encode_batch(tokenizer, [decision], max_context_tokens=64, truncation=policy)
        assert infos[0]["truncated"] and infos[0]["dropped_tokens"] > 0
        assert batch["context_input_ids"].shape[1] == 64
    _, infos = encode_batch(tokenizer, [decision], max_context_tokens=512)
    assert not infos[0]["truncated"] and infos[0]["context_tokens"] > 300


def test_candidates_are_never_truncated(tokenizer):
    decision = Decision("choice", STATE, "Qual?", {"a": "curta", "b": " ".join(["longa"] * 200)})
    with pytest.raises(ValueError):
        encode_batch(tokenizer, [decision])


def test_m0_calibration_only_rescales(model, tokenizer):
    jatoba = Jatoba(model, tokenizer)
    raw = jatoba.decide(STATE, "Qual?", OPTIONS)
    calibrated = jatoba.decide(STATE, "Qual?", OPTIONS, calibrated=True)
    assert max(raw.probabilities, key=raw.probabilities.get) == max(calibrated.probabilities, key=calibrated.probabilities.get)
