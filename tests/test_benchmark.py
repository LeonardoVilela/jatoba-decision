import gzip
import hashlib
import json
from collections import defaultdict
from pathlib import Path

import pytest

from benchmark import transforms as tf
from benchmark.adapters.gliner import labels_for
from benchmark.adapters.payload import to_candidate_probabilities, to_question

ROOT = Path(__file__).resolve().parents[1]
MANIFESTS = ROOT / "benchmark/manifests"
DICTIONARY_SHA256 = "14531bc4e8cb1bee2c7c04b52379b4c12dba31e014ae69c9cedb695ffc4e1d27"


def check(record: dict, gold: str | None = None):
    ids = [c for c, _ in record["options"]]
    assert len(ids) == len(set(ids)), "duplicate candidate ids"
    assert all(str(text).strip() for _, text in record["options"]), "empty candidate description"
    assert abs(sum(record["target"]) - 1) < 1e-9 and min(record["target"]) >= 0
    assert record["state"] and record["question"] and record["family"]
    if gold is not None:
        assert ids[max(range(len(ids)), key=record["target"].__getitem__)] == gold
    if record["type"] == "noul":
        assert ids == ["false", "true"]
    return record


def test_candidate_dictionary_is_the_frozen_one():
    assert hashlib.sha256((ROOT / "benchmark/candidate_dictionary.json").read_bytes()).hexdigest() == DICTIONARY_SHA256


def test_massive_full_taxonomy_in_official_order():
    record = check(next(tf.massive([{"id": "7", "utt_br": "me acorde às sete", "intent": 48}], "test")), "alarm_set")
    assert [c for c, _ in record["options"]] == list(tf.MASSIVE_INTENTS) and record["id"] == "massive_ptbr:7:test"


def test_assin2_entailment_and_interpolated_similarity():
    entailment, similarity = tf.assin2([{"sentence_pair_id": 3, "premise": "a", "hypothesis": "b", "entailment_judgment": 1,
                                         "relatedness_score": 3.25}], "test")
    check(entailment, "true")
    check(similarity)
    assert [c for c, _ in similarity["options"]] == ["1", "2", "3", "4", "5"]  # SCORE levels stay ordered
    assert sum(i * t for i, t in enumerate(similarity["target"])) == pytest.approx(3.25 - 1)  # expected level == gold score


def test_told_br_and_hatebr_use_annotator_shares():
    row = {"text": "texto", **{f"{d}_{n}": 0 for d in tf.TOLD_DIMENSIONS for n in (1, 2, 3)}, "insult_1": 1, "insult_2": 1}
    records = {r["task"]: check(r) for r in tf.told_br([row])}
    assert len(records) == 6 and records["insult_detection"]["target"] == pytest.approx([1 / 3, 2 / 3])
    hate = check(next(tf.hatebr([{"comentario": "c", "anotator1": 1, "anotator2": 0, "anotator3": 0, "label_final": 0}])))
    assert hate["target"] == pytest.approx([2 / 3, 1 / 3])


def test_inferbr_maps_by_class_name():
    record = check(next(tf.inferbr([{"sentence_pair_id": 1, "premise": "p", "hypothesis": "h", "label": 0}], "test")), "contradição")
    assert record["id"] == "inferbr:test:1"


def test_brighter_six_ordered_score_decisions_per_text():
    row = {"text": "fiquei muito feliz", "anger": 0, "disgust": 0, "fear": 0, "joy": 3, "sadness": 0, "surprise": 1}
    records = {r["task"]: check(r) for r in tf.brighter([row], "test")}
    assert len(records) == 6 and len({r["id"].rsplit(":", 1)[0] for r in records.values()}) == 1
    check(records["joy_intensity"], "alta")
    assert [c for c, _ in records["joy_intensity"]["options"]] == ["ausente", "baixa", "moderada", "alta"]


def test_community_alignment_pools_votes_by_text_not_slot():
    base = {"first_turn_prompt": "oi", **{f"first_turn_response_{s}": f"resposta {s} longa" for s in "abcd"}}
    rows = [{**base, "conversation_id": "1", "annotator_id": "x", "first_turn_preferred_response": "response_a"},
            {**base, "conversation_id": "2", "annotator_id": "y", "first_turn_preferred_response": "response_a"},
            {**base, "conversation_id": "3", "annotator_id": "y", "first_turn_preferred_response": "response_b"},  # second vote, same annotator
            {**base, "first_turn_response_a": "resposta b longa", "conversation_id": "4", "annotator_id": "z",
             "first_turn_preferred_response": "response_a"}]  # duplicate candidates -> excluded set
    records = [check(r) for r in tf.community_alignment(rows)]
    assert len(records) == 1
    probability = dict(zip([c for c, _ in records[0]["options"]], records[0]["target"]))
    assert probability[tf._response_id("resposta a longa")] == 1.0
    assert all(c.startswith("resp:") for c in probability)


def test_faquad_gold_is_the_sentence_holding_the_answer():
    context = "Primeira frase aqui. A UFMS fica em Campo Grande. Última frase."
    data = {"data": [{"title": "UFMS", "paragraphs": [{"context": context, "qas": [
        {"id": "q1", "question": "Onde fica a UFMS?", "answers": [{"text": "Campo Grande", "answer_start": context.index("Campo Grande")}]}]}]}]}
    record = check(next(tf.faquad_evidence(data, "dev")), "s02")
    assert record["paragraph_title"] == "UFMS"


def test_content_hash_ignores_extra_fields_and_is_stable():
    record = next(tf.inferbr([{"sentence_pair_id": 1, "premise": "p", "hypothesis": "h", "label": 1}], "test"))
    assert tf.content_hash(record) == tf.content_hash({**record, "group": "g", "family": "other"})


def test_shared_payload_and_answer_mapping():
    record = next(tf.assin2([{"sentence_pair_id": 1, "premise": "a", "hypothesis": "b", "entailment_judgment": 0, "relatedness_score": 2.0}],
                            "test"))
    question, ids = to_question(record)
    assert question == {"type": "noul", "instructions": record["question"]} and ids == ["false", "true"]
    assert to_candidate_probabilities(question, {"noul": 0.25}, ids) == {"false": 0.75, "true": 0.25}
    score = next(r for r in tf.brighter([{"text": "t", "anger": 2, "disgust": 0, "fear": 0, "joy": 0, "sadness": 0, "surprise": 0}], "x"))
    q, ids = to_question(score)
    assert q["criteria"] == [text for _, text in score["options"]]
    assert labels_for(q, ids)[1] == ["0", "1", "2", "3"]


def read(name: str) -> list[dict]:
    with gzip.open(MANIFESTS / f"{name}.jsonl.gz", "rt", encoding="utf-8") as fh:
        rows = [json.loads(line) for line in fh]
    return [r for r in rows if "_role" not in r]


EVAL = ("jatoba_id", "legacy_exposed", "shift_normastcu", "shift_juristcu", "gdev_faquad")
SPEC = json.loads((ROOT / "benchmark/benchmark_spec.json").read_text(encoding="utf-8"))


@pytest.mark.parametrize("block", EVAL)
def test_evaluation_manifest_integrity(block):
    rows = read(block)
    assert len(rows) == SPEC["blocks"][block]["decisions"]
    assert len({r["id"] for r in rows}) == len(rows)
    assert all(r["group"] and len(r["sha256"]) == 64 for r in rows)
    digest = hashlib.sha256((MANIFESTS / f"{block}.jsonl.gz").read_bytes()).hexdigest()
    assert digest == SPEC["blocks"][block]["manifest_sha256"]


def test_training_roles_are_group_disjoint_and_never_evaluated():
    role_of_group, train_ids = defaultdict(set), set()
    for role in ("train", "development", "calibration"):
        for r in read(f"role_{role}"):
            role_of_group[(r["source"], r["group"])].add(role)
            train_ids.add(r["id"])
    assert all(len(roles) == 1 for roles in role_of_group.values())
    for block in EVAL:
        assert not train_ids & {r["id"] for r in read(block)}, block


def test_k_sets_are_nested_and_contain_gold():
    with gzip.open(MANIFESTS / "k_sets.json.gz", "rt", encoding="utf-8") as fh:
        k_sets = json.load(fh)
    massive = k_sets["sets"]["LEGACY_EXPOSED"]["massive_intent"]
    assert massive["K_grid"] == SPEC["k_curve"]["K"]
    for record in list(massive["records"].values())[:200]:
        sets = {k: v for k, v in record.items() if k.isdigit()}
        grids = sorted(sets, key=int)
        for small, large in zip(grids, grids[1:]):
            assert set(sets[small][0]) <= set(sets[large][0])
        assert len({candidates[gold] for candidates, gold in sets.values()}) == 1  # same gold intent at every K
