"""Render results/tables/*.md and the README results block from results/data/*.json (the frozen numbers).

    python scripts/reproduce_tables.py          # write
    python scripts/reproduce_tables.py --check  # fail if any committed table or the README block is stale
"""

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "results/data"
TABLES = ROOT / "results/tables"
README = ROOT / "README.md"
START, END = "<!-- results:start -->", "<!-- results:end -->"


def load(name: str) -> dict:
    return json.loads((DATA / f"{name}.json").read_text(encoding="utf-8"))


def f3(x) -> str:
    return "—" if x is None or isinstance(x, str) else f"{x:.3f}"


def ci(lo, hi) -> str:
    return "" if lo is None else f" [{lo:.3f}, {hi:.3f}]"


def table(header: list[str], rows: list[list]) -> str:
    lines = ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
    lines += ["| " + " | ".join(str(c) for c in row) + " |" for row in rows]
    return "\n".join(lines) + "\n"


def julia_rows() -> dict:
    return {r["block"]: r for r in load("t7_julia1_external")["rows"] if r.get("model") == "Julia"}


def trained_families() -> str:
    t1, julia = load("t1_pristine_per_task"), julia_rows()
    rows = [[r["task"], f3(r["NorDecision_RAW_ce_eps"]), f3(r["NorDecision_RAW_top1"]), f3(r["Laya_multilingual_ce_eps"]),
             f3(r["Laya_multilingual_top1"]), f3(r.get("GLiNER_ce_eps")), f3(r.get("GLiNER_top1"))] for r in t1["rows"]]
    hier = load("../metrics")["pristine"]["gliner_three_model_hier_ce_eps"]
    rows.append(["**hierarchical ε-CE (these tasks)**", f"**{f3(hier['NorDecision_RAW'])}**", "", f"**{f3(hier['Laya_multilingual'])}**", "",
                 f"**{f3(hier['GLiNER'])}**", ""])
    body = table(["task", "JATOBÁ ε-CE", "JATOBÁ top-1", "Laya ε-CE", "Laya top-1", "GLiNER ε-CE", "GLiNER top-1"], rows)
    p = julia["pristine"]
    return ("# Table 2. JATOBÁ-ID (unseen examples of trained PT-BR families)\n\n"
            f"Common subset of JATOBÁ, Laya multilingual and GLiNER2.5-multi-Decide: {t1['records']:,} of {t1['decisions']:,} decisions "
            "(decisions every model can read without truncation; the 650 Community Alignment decisions are excluded because Laya cannot "
            "read them). ε-CE uses a 0.005 floor for every model. Lower ε-CE is better.\n\n" + body +
            f"\nJulia-1 on its own exact-fit subset ({p['records']:,} decisions): hierarchical ε-CE {f3(p['hier_ce_eps'])}, top-1 {f3(p['top1'])} "
            "(JATOBÁ on the same subset: see `results/data/t7_julia1_external.json`).\n"
            "Jev: N/A (partial operational coverage of this block).\n")


def variable_k() -> str:
    julia = julia_rows()
    rows = []
    for r in load("t2_massive_top1_vs_k")["rows"]:
        j = julia.get(f"massive_K{r['K']}")
        rows.append([r["K"], f3(r["NorDecision_RAW_top1_all"]), f3(r["Laya_multilingual_top1_common"]),
                     f3(r["GLiNER_top1"]), f3(j["top1"]) if j else "N/A (native limit 20)"])
    return ("# Table 3. MASSIVE PT-BR intent top-1 vs number of candidates K\n\n"
            "LEGACY / previously exposed data: MASSIVE was used during architecture development, so this measures candidate-set scaling, "
            "not unseen-family generalization. Nested candidate sets (`benchmark/manifests/k_sets.json.gz`). Laya is N/A where its input "
            "would be cut; Julia-1 accepts at most 20 options.\n\n" +
            table(["K", "JATOBÁ", "Laya multilingual", "GLiNER2.5-multi-Decide", "Julia-1"], rows))


def family_shift() -> str:
    names = {"NorDecision_RAW": "JATOBÁ (RAW)", "NorDecision_M0": "JATOBÁ (M0)", "Jev": "Jev (PARTIAL protocol)",
             "Laya_multilingual": "Laya multilingual", "B0": "uniform", "BM25_frozen": "BM25"}
    t3 = load("t3_normas_complete1024")
    rows = [[names.get(r["model"], r["model"]), f3(r["ce_epsilon"]) + ci(r["ce_epsilon_ci_lo"], r["ce_epsilon_ci_hi"]),
             f3(r["ndcg@10"]) + ci(r["ndcg@10_ci_lo"], r["ndcg@10_ci_hi"]), f3(r["mrr"])] for r in t3["rows"]]
    julia = [r for r in load("t7_julia1_external")["rows"] if r.get("block") == "normas_complete1024" and r.get("model") == "Julia"][0]
    rows.insert(-2, ["Julia-1", f3(julia["ce_eps"]), f3(julia["ndcg10"]), f3(julia["mrr"])])
    juris = [[names.get(r["model"], r["model"]).replace("Julia", "Julia-1"), f3(r["ce_eps"]), f3(r["ndcg10"]), f3(r["mrr"])]
             for r in load("t7_julia1_external")["rows"] if r.get("block") == "juris"]
    return ("# Table 4. Family shift (relevance judgement, never trained on)\n\n"
            f"NormasTCU, complete_1024 stratum common to all models: {t3['pairs']} (query, document) pairs, {t3['queries']} queries. "
            "Query-weighted means; 95% query-bootstrap CIs (10,000 resamples). Ranking by expected relevance.\n\n" +
            table(["model", "ε-CE", "nDCG@10", "MRR"], rows) +
            "\nEvery probabilistic model is worse than uniform in ε-CE. Jev ranks far better than JATOBÁ; Jev vs BM25 nDCG@10 is not "
            "statistically decisive (CI crosses zero).\n\n## JurisTCU (2,246 pairs)\n\n" + table(["model", "ε-CE", "nDCG@10", "MRR"], juris) +
            "\nJev's JurisTCU coverage is partial and not comparable; it is not reported.\n")


def efficiency() -> str:
    rows = [[{"nordecision": "JATOBÁ", "laya_multilingual": "Laya multilingual"}[r["model"]], r["device"], f"{r['p50_ms']:.1f}", f"{r['p95_ms']:.1f}",
             f"{r['peak_footprint_mb'] / 1024:.2f}"] for r in load("t6_matched_local_efficiency")["rows"]]
    j = load("julia_efficiency")
    rows.append(["Julia-1", "cpu", f"{j['p50_ms']:.1f}", f"{j['p95_ms']:.1f}", f"{j['peak_footprint_mb'] / 1024:.2f}"])
    return ("# Table 5. Local latency, one decision at a time\n\n"
            "Same Apple-silicon laptop (18 GB), the same frozen sample of 1,000 decisions, batch size 1, 20 warm-up decisions, timing from input "
            "formatting to probabilities. Devices differ by necessity (Julia-1's engine does not support MPS). Not comparable with hosted "
            "API latency.\n\n" + table(["model", "device", "p50 (ms)", "p95 (ms)", "peak memory (GB)"], rows))


def permutation() -> str:
    data = load("julia_permutation")
    rows = [[name.replace("S2_", "MASSIVE ").replace("S1_PRISTINE_choice", "JATOBÁ-ID CHOICE"), s["decisions"], f3(s["argmax_flip_rate"]),
             f3(s["mean_max_abs_prob_dev"]), f3(s["mean_js_divergence"])] for name, s in sorted(data["julia"].items())]
    nd = data["nordecision_v11_same_S1_records_same_orders"]
    rows.append(["JATOBÁ on the same JATOBÁ-ID records and orders", nd["decisions"], f3(nd["argmax_flip_rate"]),
                 f"{nd['mean_max_abs_prob_dev']:.1e}", f"{nd['mean_js_divergence']:.1e}"])
    return ("# Table 7. Candidate-order sensitivity\n\n"
            "Each decision re-scored under its reversed order and three seeded shuffles; probabilities compared per candidate id. "
            "Julia-1's reported results use the canonical order only.\n\n" +
            table(["subset (Julia-1 unless stated)", "decisions", "top-1 flip rate", "mean max |Δp|", "mean JS divergence"], rows))


def jevbench() -> str:
    rows = [[r["variant"], r["tier"], r["items"], f3(r["accuracy"]), f3(r["chance_item_mean"]), f3(r["brier"])]
            for r in load("t5_jevbench_public")["rows"] if r["variant"] == "RAW"]
    return ("# Table 8. JevBench v1.4.2 public items (English)\n\n"
            "Self-run on the public items; not a sealed or official score. JATOBÁ is a PT-BR model and is at chance level in English.\n\n" +
            table(["output", "tier", "items", "accuracy", "chance", "Brier"], rows))


def research() -> str:
    rows = [[r["direction"], r["conclusion"]] for r in load("v2_research")["rows"]]
    return ("# Table 6. v2 research directions (none changed the released model)\n\n"
            "Each gate was frozen before its results were seen. Details: `docs/research_history.md`.\n\n" +
            table(["direction", "outcome"], rows))


def overview() -> str:
    rows = [[m["model"], m["parameters"], m["language"], m["primitives"], m["native_max_k"], m["order_invariance"], m["output"], m["context"]]
            for m in load("model_overview")["rows"]]
    return ("# Table 1. Evaluated models\n\n" +
            table(["model", "parameters", "language focus", "primitives", "native max K", "candidate order", "probabilities", "context"], rows))


def readme_block() -> str:
    m = load("../metrics")
    hier = m["pristine"]["gliner_three_model_hier_ce_eps"]
    k60 = [r for r in load("t2_massive_top1_vs_k")["rows"] if r["K"] == 60][0]
    normas = {r["model"]: r for r in load("t3_normas_complete1024")["rows"]}
    jb = m["jevbench_public"]["RAW/ALL"]
    rows = [
        ["JATOBÁ-ID: unseen InferBR and BRIGHTER examples (trained families; 15,025 decisions Laya and GLiNER can also read)", "hierarchical ε-CE ↓",
         f"**{f3(hier['NorDecision_RAW'])}**", f"Laya {f3(hier['Laya_multilingual'])}, GLiNER {f3(hier['GLiNER'])}"],
        ["MASSIVE intent, K = 60 candidates (previously exposed data)", "top-1 ↑", f"**{f3(k60['NorDecision_RAW_top1_all'])}**",
         "GLiNER " + f3(k60["GLiNER_top1"]) + "; Laya N/A (input would be cut); Julia-1 N/A (at most 20 options)"],
        ["NormasTCU (family never trained on)", "ε-CE ↓", f"**{f3(normas['NorDecision_RAW']['ce_epsilon'])}**",
         f"uniform {f3(normas['B0']['ce_epsilon'])}, Jev {f3(normas['Jev']['ce_epsilon'])}"],
        ["NormasTCU (family never trained on)", "nDCG@10 ↑", f"**{f3(normas['NorDecision_RAW']['ndcg@10'])}**",
         f"Jev {f3(normas['Jev']['ndcg@10'])}, BM25 {f3(normas['BM25_frozen']['ndcg@10'])}"],
        ["JevBench public items (English)", "accuracy ↑", f"**{f3(jb['accuracy'])}**", f"chance {f3(jb['chance'])}"],
    ]
    return table(["evaluation", "metric", "JATOBÁ", "comparison"], rows)


OUTPUTS = {"table1_models.md": overview, "table2_trained_families.md": trained_families, "table3_variable_k.md": variable_k,
           "table4_family_shift.md": family_shift, "table5_efficiency.md": efficiency, "table6_v2_research.md": research,
           "table7_candidate_order.md": permutation, "table8_jevbench.md": jevbench}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    stale = []
    for name, render in OUTPUTS.items():
        text, path = render(), TABLES / name
        if args.check:
            if not path.exists() or path.read_text(encoding="utf-8") != text:
                stale.append(str(path.relative_to(ROOT)))
        else:
            TABLES.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
    readme = README.read_text(encoding="utf-8")
    head, rest = readme.split(START, 1)
    body, tail = rest.split(END, 1)
    block = "\n" + readme_block()
    if args.check and body != block:
        stale.append("README.md results block")
    if not args.check:
        README.write_text(head + START + block + END + tail, encoding="utf-8")
    if stale:
        sys.exit("stale generated files: " + ", ".join(stale))


if __name__ == "__main__":
    main()
