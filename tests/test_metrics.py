import math

import pytest

from jatoba.metrics import decision_metrics, ece_equal_mass, epsilon_distribution, expected_mrr, hierarchical_mean, ndcg_at_k


def test_epsilon_floor_then_renormalise():
    q = epsilon_distribution([1.0, 0.0, 0.0])
    assert q[1] == q[2] == pytest.approx(0.005 / 1.01)
    assert sum(q) == pytest.approx(1)


def test_decision_metrics_soft_target_and_ties():
    m = decision_metrics([0.5, 0.5, 0.0], [1.0, 0.0, 0.0])
    assert m["top1"] == 0.5  # gold shares the maximum with one other candidate
    assert m["brier"] == pytest.approx(0.5)
    assert m["ce_eps"] == pytest.approx(-math.log(0.5 / 1.005))
    soft = decision_metrics([0.2, 0.8], [1 / 3, 2 / 3])
    assert soft["target_level"] == pytest.approx(2 / 3)


def test_ranking_metrics_average_over_ties():
    assert ndcg_at_k([1.0, 1.0], [2.0, 0.0]) == pytest.approx((1 + 1 / math.log2(3)) / 2)
    assert expected_mrr([0.9, 0.1, 0.5], [0.0, 2.0, 0.0]) == pytest.approx(1 / 3)
    assert expected_mrr([0.5, 0.5], [2.0, 0.0]) == pytest.approx(0.75)
    assert ndcg_at_k([0.1, 0.2], [0.0, 0.0]) is None


def test_hierarchical_mean_weights_groups_equally():
    rows = [{"task": "t", "family": "f", "g": "a", "v": 1.0}, {"task": "t", "family": "f", "g": "a", "v": 1.0},
            {"task": "t", "family": "f", "g": "b", "v": 0.0}, {"task": "u", "family": "h", "g": "c", "v": 3.0}]
    out = hierarchical_mean(rows, "v", lambda r: r["g"])
    assert out["task"]["t"] == 0.5 and out["macro"] == pytest.approx(1.75)


def test_ece_is_zero_when_confidence_matches_accuracy():
    assert ece_equal_mass([1.0] * 10, [True] * 10) == 0.0
    assert ece_equal_mass([0.9] * 10, [False] * 10) == pytest.approx(0.9)
