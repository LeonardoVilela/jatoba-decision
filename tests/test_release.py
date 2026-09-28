import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import reproduce_tables  # noqa: E402
import verify_release  # noqa: E402

METRICS = json.loads((ROOT / "results/metrics.json").read_text(encoding="utf-8"))


def readme_results() -> str:
    text = (ROOT / "README.md").read_text(encoding="utf-8")
    return text[text.index(reproduce_tables.START) + len(reproduce_tables.START):text.index(reproduce_tables.END)]


def test_readme_block_is_generated():
    assert readme_results().strip() == reproduce_tables.readme_block().strip()


def test_readme_headline_numbers_come_from_the_frozen_metrics():
    block = readme_results()
    pristine = METRICS["pristine"]["gliner_three_model_hier_ce_eps"]
    normas = METRICS["normas_complete_1024"]["models"]
    expected = [
        pristine["NorDecision_RAW"], pristine["Laya_multilingual"], pristine["GLiNER"],
        METRICS["massive_top1_vs_k_LEGACY"]["60"]["NorDecision"], METRICS["massive_top1_vs_k_LEGACY"]["60"]["GLiNER"],
        normas["NorDecision_RAW"]["ce_epsilon"], normas["NorDecision_RAW"]["ndcg@10"], normas["B0"]["ce_epsilon"],
        normas["Jev"]["ce_epsilon"], normas["Jev"]["ndcg@10"], normas["BM25_frozen"]["ndcg@10"],
        METRICS["jevbench_public"]["RAW/ALL"]["accuracy"], METRICS["jevbench_public"]["RAW/ALL"]["chance"],
    ]
    for value in expected:
        assert f"{value:.3f}" in block, value


def test_readme_keeps_the_claim_boundaries():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "Model weights are available on Hugging Face under CC BY-NC-SA 4.0" in readme
    assert "previously exposed data" in readme
    assert "chance" in readme
    assert "worse than a uniform guess" in readme
    assert "A separate final generalization set remains sealed for future model development." in readme
    assert not re.search(r"(?i)leaderboard|state[- ]of[- ]the[- ]art|\bSOTA\b", readme)


def test_public_tree_has_no_local_paths_secrets_or_sealed_set_references():
    checks = verify_release.check_contents(verify_release.release_files())
    assert all(c["ok"] for c in checks.values()), {k: c["hits"] for k, c in checks.items() if not c["ok"]}


def test_no_weights_or_raw_data_in_the_public_tree():
    problems = [p for p in verify_release.check_files(verify_release.release_files())["problems"] if not p.startswith("missing")]
    assert not problems
