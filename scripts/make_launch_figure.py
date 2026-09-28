"""Launch figure: every plotted number is read from results/ by path, written to a CSV, and checked back against the source.

    uv run --no-project --with matplotlib python scripts/make_launch_figure.py
"""

import csv
import hashlib
import json
import re
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.gridspec import GridSpec  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results/figures"
T2, T7 = "results/data/t2_massive_top1_vs_k.json", "results/data/t7_julia1_external.json"
FOUR, PERM = "results/data/pristine_four_model_common.json", "results/data/julia_permutation.json"
OVERVIEW, METRICS = "results/data/model_overview.json", "results/metrics.json"

INK, MUTED, GRID, BG = "#1f1f1e", "#6b6a64", "#e6e5e0", "#ffffff"
COLOR = {"JATOBÁ": "#2a78d6", "Julia-1": "#4a4944", "GLiNER": "#8a8882", "Laya": "#a9a79f"}
MARKER = {"JATOBÁ": "o", "Julia-1": "D", "GLiNER": "s", "Laya": "^"}
K_GRID = [2, 4, 5, 6, 8, 10, 16, 24, 32, 48, 60]
MASSIVE = "MASSIVE PT-BR intent test (legacy block), same 2,901 decisions at every K"


def resolve(source: str, path: str):
    """Follow a path like 'rows[block=pristine,model=Julia]/top1' through a JSON file."""
    node = json.loads((ROOT / source).read_text(encoding="utf-8"))
    for part in path.split("/"):
        name, _, cond = part.partition("[")
        if name:
            node = node[name]
        if cond:
            wanted = dict(kv.split("=", 1) for kv in cond.rstrip("]").split(","))
            node = next(r for r in node if all(str(r.get(k)) == v for k, v in wanted.items()))
    return node


def params_m(model_row: str) -> float:
    return float(re.match(r"([0-9.]+)M", model_row).group(1))


def spec() -> list[dict]:
    """(panel, model, metric, source, path, subset, N, direction) for every plotted value."""
    rows = []

    def add(panel, model, metric, source, path, subset, n, direction, fmt, k=""):
        rows.append({"panel": panel, "model": model, "metric": metric, "K": k, "source": source, "path": path,
                     "subset": subset, "N": n, "direction": direction, "fmt": fmt})

    four = "JATOBÁ-ID (held-out InferBR + BRIGHTER examples), common subset of JATOBÁ, GLiNER, Laya and Julia-1"
    for model, key in [("JATOBÁ", "NorDecision_RAW"), ("GLiNER", "GLiNER"), ("Laya", "Laya_multilingual"), ("Julia-1", "Julia")]:
        add("A", model, "hierarchical ε-CE", FOUR, f"models/{key}/hierarchical_ce_epsilon_group", four, 15025, "lower is better", "{:.3f}")

    pair = "JATOBÁ-ID, common subset of JATOBÁ and Julia-1 (InferBR, BRIGHTER, 3 Community Alignment decisions)"
    for model, key in [("JATOBÁ", "NorDecision_RAW"), ("Julia-1", "Julia")]:
        add("B", model, "top-1", T7, f"rows[block=pristine,model={key}]/top1", pair, 15028, "higher is better", "{:.3f}")

    for k in K_GRID:
        add("C", "JATOBÁ", "top-1", T2, f"rows[K={k}]/NorDecision_RAW_top1_all", MASSIVE, 2901, "higher is better", "{:.3f}", k)
        add("C", "GLiNER", "top-1", T2, f"rows[K={k}]/GLiNER_top1", MASSIVE, 2901, "higher is better", "{:.3f}", k)
        if k <= 16:  # Julia-1 accepts at most 20 options
            add("C", "Julia-1", "top-1", T7, f"rows[block=massive_K{k},model=Julia]/top1", MASSIVE, 2901, "higher is better", "{:.3f}", k)
        if k <= 6:  # Laya reads all 2,901 decisions only up to K = 6 (2,900 at K = 8, 2,606 at K = 10, none above)
            add("C", "Laya", "top-1", T2, f"rows[K={k}]/Laya_multilingual_top1_common", MASSIVE, 2901, "higher is better", "{:.3f}", k)

    reorder = "JATOBÁ-ID CHOICE decisions, reversed order + 3 seeded shuffles each (88 reorderings), same orders for both models"
    add("D", "JATOBÁ", "argmax flip rate", PERM, "nordecision_v11_same_S1_records_same_orders/argmax_flip_rate", reorder, 22,
        "lower is better", "{:.0%}")
    add("D", "Julia-1", "argmax flip rate", PERM, "julia/S1_PRISTINE_choice/argmax_flip_rate", reorder, 22, "lower is better", "{:.0%}")

    for model, i in [("JATOBÁ", 0), ("Laya", 1), ("GLiNER", 2), ("Julia-1", 3)]:
        add("E", model, "parameters (millions)", OVERVIEW, f"rows/{i}/parameters", "model size (total parameters)", "", "neither", "{:.1f}M")
    return rows


def value_of(row: dict) -> float:
    if row["panel"] == "E":
        node = json.loads((ROOT / row["source"]).read_text(encoding="utf-8"))["rows"][int(row["path"].split("/")[1])]["parameters"]
        return params_m(node)
    return resolve(row["source"], row["path"])


def style(ax, title: str, subtitle: str):
    ax.set_facecolor(BG)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(MUTED)
    ax.tick_params(colors=MUTED, labelsize=10)
    ax.titles = (title, subtitle)


def place_titles(fig, axes):
    """Start each panel title at the left edge of its y tick labels (or y label), so long titles are not clipped."""
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    for ax in axes:
        left = min(t.get_window_extent(renderer).x0 for t in [*ax.get_yticklabels(), ax.yaxis.label] if t.get_text())
        x = ax.transAxes.inverted().transform((left, 0))[0]
        title, subtitle = ax.titles
        ax.annotate(title, (x, 1), xycoords="axes fraction", xytext=(0, 24), textcoords="offset points", fontsize=13,
                    fontweight="bold", color=INK, va="bottom")
        ax.annotate(subtitle, (x, 1), xycoords="axes fraction", xytext=(0, 8), textcoords="offset points", fontsize=9.5,
                    color=MUTED, va="bottom")


def hbars(ax, items: list[tuple[str, float, str]], xmax: float, xlabel: str):
    names = [m for m, _, _ in items][::-1]
    values = [v for _, v, _ in items][::-1]
    labels = [t for _, _, t in items][::-1]
    ax.barh(names, values, color=[COLOR[m] for m in names], height=0.62, edgecolor=BG, linewidth=2)
    for y, (m, v, t) in enumerate(zip(names, values, labels)):
        ax.text(v + xmax * 0.015, y, t, va="center", fontsize=12, color=INK, fontweight="bold" if m == "JATOBÁ" else "normal")
    ax.set_xlim(0, xmax)
    ax.grid(axis="x", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    ax.set_xlabel(xlabel, fontsize=11, color=INK)
    ax.tick_params(axis="y", labelsize=11, colors=INK, length=0)
    for tick in ax.get_yticklabels():
        tick.set_fontweight("bold" if tick.get_text() == "JATOBÁ" else "normal")


def draw(rows: list[dict]):
    val = {(r["panel"], r["model"], r["K"]): r for r in rows}
    fig = plt.figure(figsize=(9, 5.8), dpi=200, facecolor=BG)
    gs = GridSpec(2, 3, figure=fig, left=0.105, right=0.975, top=0.75, bottom=0.08, wspace=0.5, hspace=0.95,
                  height_ratios=[1.25, 1])
    fig.text(0.04, 0.975, "JATOBÁ", fontsize=26, fontweight="bold", color=INK, va="top")
    fig.text(0.04, 0.905, "Joint Assessment of Typed Options with BERT Architecture", fontsize=12, color=MUTED, va="top")

    ax = fig.add_subplot(gs[0, :2])
    style(ax, "Top-1 as the candidate set grows", "MASSIVE PT-BR intent · same 2,901 decisions at every K")
    for model in ("Laya", "Julia-1", "GLiNER", "JATOBÁ"):
        points = [(r["K"], r["value"]) for r in rows if r["panel"] == "C" and r["model"] == model]
        ks, ys = zip(*points)
        ax.plot(ks, ys, color=COLOR[model], linewidth=3 if model == "JATOBÁ" else 2, marker=MARKER[model], markersize=8 if model == "Laya" else 6.5,
                linestyle=(0, (4, 2)) if model == "Laya" else "-",
                markeredgecolor=BG, markeredgewidth=1.2, zorder={"JATOBÁ": 4, "Laya": 3}.get(model, 2))
        end = val[("C", model, ks[-1])]["label"]
        text = {"JATOBÁ": f"JATOBÁ {end}", "GLiNER": f"GLiNER {end}", "Julia-1": f"Julia-1 {end}\n(max 20 options)",
                "Laya": f"Laya {end}"}[model]
        offset = {"JATOBÁ": (8, 0), "GLiNER": (8, 0), "Julia-1": (8, -2), "Laya": (4, 4)}[model]
        ax.annotate(text, (ks[-1], ys[-1]), xytext=offset, textcoords="offset points", fontsize=10.5, color=INK,
                    ha="left", va="bottom" if model == "Laya" else "center",
                    fontweight="bold" if model == "JATOBÁ" else "normal")
    ax.set_xscale("log", base=2)
    ax.set_xticks(K_GRID, [str(k) for k in K_GRID])
    ax.minorticks_off()
    ax.set_xlim(1.75, 135)
    ax.set_ylim(0, 1.05)
    ax.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
    ax.grid(axis="y", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    ax.set_xlabel("K (number of candidates)", fontsize=11, color=INK)
    ax.set_ylabel("Top-1 ↑", fontsize=11, color=INK)

    def items(panel, order):
        return [(m, val[(panel, m, "")]["value"], val[(panel, m, "")]["label"]) for m in order]

    ax = fig.add_subplot(gs[0, 2])
    style(ax, "PT-BR typed decisions", "held-out, trained families · N = 15,025")
    hbars(ax, items("A", ["JATOBÁ", "GLiNER", "Laya", "Julia-1"]), 3.4, "ε-CE ↓")

    ax = fig.add_subplot(gs[1, 0])
    style(ax, "PT-BR: JATOBÁ vs Julia-1", "JATOBÁ-ID common subset · N = 15,028")
    hbars(ax, items("B", ["JATOBÁ", "Julia-1"]), 1.25, "Top-1 ↑")
    ax.set_xticks([0, 0.5, 1.0])

    ax = fig.add_subplot(gs[1, 1])
    style(ax, "Candidate-order stability", "22 decisions × 4 reorderings, same orders")
    hbars(ax, items("D", ["JATOBÁ", "Julia-1"]), 1.25, "Argmax flips ↓")
    ax.set_xticks([0, 0.5, 1.0], ["0%", "50%", "100%"])

    ax = fig.add_subplot(gs[1, 2])
    style(ax, "Model size", "total parameters")
    hbars(ax, items("E", ["JATOBÁ", "Julia-1", "GLiNER", "Laya"]), 420, "millions")
    ax.set_xticks([0, 100, 200, 300])

    place_titles(fig, fig.axes)
    fig.savefig(OUT / "jatoba_linkedin_main.png", facecolor=BG)
    fig.savefig(OUT / "jatoba_linkedin_main.svg", facecolor=BG)


def caption(rows: list[dict]) -> str:
    v = {(r["panel"], r["model"], r["K"]): r["label"] for r in rows}
    perm = json.loads((ROOT / PERM).read_text(encoding="utf-8"))["julia"]
    julia_by_k = ", ".join(f"K = {k}: {perm[f'S2_K{k}']['argmax_flip_rate']:.0%}" for k in (2, 4, 8, 10, 16))
    return f"""# Launch figure: what each panel shows

Files: `jatoba_linkedin_main.png` / `.svg`. Every plotted number is in `linkedin_main_data.csv` (source file and JSON path per value)
and was checked against its source by `scripts/make_launch_figure.py` (`linkedin_main_figure_check.json`).

## Top-1 as the candidate set grows

- **One sentence:** JATOBÁ keeps top-1 {v[("C", "JATOBÁ", 60)]} with 60 candidates (from {v[("C", "JATOBÁ", 2)]} at K = 2), while GLiNER falls to {v[("C", "GLiNER", 60)]}.
- **Data:** MASSIVE PT-BR intent test set, the same 2,901 decisions at every K. Candidate sets are nested (`benchmark/manifests/k_sets.json.gz`).
- **Metric:** top-1 (higher is better).
- **Sources:** `results/data/t2_massive_top1_vs_k.json`, and `results/data/t7_julia1_external.json` for Julia-1.
- **Caveats:**
  - MASSIVE is a legacy block: it was used during JATOBÁ's architecture development. It shows candidate-set scaling, not generalization to new data.
  - Julia-1 accepts at most 20 options, so its line stops at K = 16 (last value {v[("C", "Julia-1", 16)]}).
  - Laya is drawn only for K = 2–6, the only K values where it read all 2,901 decisions. Laya values also exist at K = 8 (2,900 decisions) and K = 10 (2,606 decisions); they are in `t2` and not drawn. Above K = 10, Laya's input would be cut.

## PT-BR typed decisions

- **One sentence:** on held-out examples of trained PT-BR families, JATOBÁ's ε-CE is {v[("A", "JATOBÁ", "")]}, against GLiNER {v[("A", "GLiNER", "")]}, Laya {v[("A", "Laya", "")]} and Julia-1 {v[("A", "Julia-1", "")]}.
- **Data:** JATOBÁ-ID (historical name PRISTINE), the common subset that all four models read exactly: 15,025 decisions (InferBR 3-way NLI and the six BRIGHTER emotion-intensity tasks).
- **Metric:** group-hierarchical ε-CE (0.005 floor for every model; lower is better).
- **Source:** `results/data/pristine_four_model_common.json`, extracted from the frozen Julia-1 comparison artifact; its hash matches the one recorded in `t7`. The JATOBÁ, GLiNER and Laya values are identical to `results/metrics.json`.
- **Caveat:** these are unseen examples from families JATOBÁ was trained on, not unseen families.

## PT-BR: JATOBÁ vs Julia-1

- **One sentence:** on the JATOBÁ-ID decisions Julia-1 can read, top-1 is {v[("B", "JATOBÁ", "")]} for JATOBÁ and {v[("B", "Julia-1", "")]} for Julia-1.
- **Data:** JATOBÁ-ID, the JATOBÁ–Julia-1 common subset: 15,028 decisions. These are the 15,025 above plus 3 Community Alignment decisions.
- **Metric:** top-1 (higher is better).
- **Source:** `results/data/t7_julia1_external.json` (block `pristine`).
- **Caveats:**
  - Julia-1 is a model, evaluated here on JATOBÁ's frozen PT-BR payload. This is not Julia-1's own benchmark and not a general statement about Julia-1.
  - The hierarchical ε-CE for this subset is not plotted. The 3 Community Alignment decisions form a whole family in the hierarchical mean, which makes that aggregate unrepresentative. The ε-CE comparison is in the panel above.

## Candidate-order stability

- **One sentence:** reordering the candidates never changed JATOBÁ's answer ({v[("D", "JATOBÁ", "")]} of reorderings) but changed Julia-1's in {v[("D", "Julia-1", "")]}.
- **Data:** 22 JATOBÁ-ID CHOICE decisions. Each was re-scored under its reversed order and 3 seeded shuffles (88 reorderings), with identical orders for both models.
- **Metric:** argmax flip rate (lower is better).
- **Source:** `results/data/julia_permutation.json`.
- **Caveats:**
  - JATOBÁ is permutation-equivariant by construction, but it was measured only on these 22 decisions.
  - Julia-1 was also measured on MASSIVE subsets of 40 decisions: {julia_by_k}. JATOBÁ was not run on those subsets, so they are not plotted.

## Model size

- **One sentence:** total parameters, for context. Smaller is not better by itself.
- **Source:** `results/data/model_overview.json`.
- **How the counts were made:**
  - JATOBÁ from the model definition, including the frozen 149.0M-parameter NorBERTo-base encoder.
  - Laya from its safetensors.
  - GLiNER and Julia-1 from Hugging Face safetensors metadata at the evaluated revisions.

## Deliberately not in the figure

These results stay in the repository (`results/tables/`, `docs/limitations.md`) and belong in the post text:
- JevBench (English, chance level);
- family shift (NormasTCU and JurisTCU, where ε-CE is worse than uniform);
- the v2 research results;
- latency;
- long-context and licensing caveats.
"""


def sha256(path: str) -> str:
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def check() -> dict:
    """Re-read the CSV from disk and compare every plotted value and label with its source, independently of draw()."""
    with open(OUT / "linkedin_main_data.csv", encoding="utf-8") as fh:
        plotted = list(csv.DictReader(fh))
    results, ok = [], True
    for r in plotted:
        canonical = value_of({**r, "K": r["K"]})
        same = float(r["value"]) == canonical and r["label"] == r["fmt"].format(canonical)
        ok &= same
        results.append({"panel": r["panel"], "model": r["model"], "K": r["K"], "plotted": float(r["value"]), "label": r["label"],
                        "canonical": canonical, "source": r["source"], "path": r["path"], "match": same})
    # The four-model subset must agree with the three-model numbers published in metrics.json.
    three = json.loads((ROOT / METRICS).read_text(encoding="utf-8"))["pristine"]["gliner_three_model_hier_ce_eps"]
    four = json.loads((ROOT / FOUR).read_text(encoding="utf-8"))["models"]
    cross = {k: four[k]["hierarchical_ce_epsilon_group"] == three[m] for k, m in
             [("NorDecision_RAW", "NorDecision_RAW"), ("GLiNER", "GLiNER"), ("Laya_multilingual", "Laya_multilingual")]}
    t7_sources = json.loads((ROOT / T7).read_text(encoding="utf-8"))["sources"]
    extract_source = json.loads((ROOT / FOUR).read_text(encoding="utf-8"))["source"]["julia_comparison.json"]
    cross["four_model_extract_source_matches_t7"] = extract_source == t7_sources["julia_comparison.json"]
    excluded = ("JevBench", "Normas", "Juris")
    absent = not any(x.lower() in json.dumps(plotted).lower() for x in excluded)
    ok = ok and all(cross.values()) and absent
    sources = sorted({r["source"] for r in plotted} | {METRICS})
    return {"status": "PASS" if ok else "FAIL", "values": len(results), "cross_checks": cross, "excluded_results_absent": absent,
            "source_sha256": {s: sha256(s) for s in sources}, "checks": results}


def main():
    rows = spec()
    for r in rows:
        r["value"] = value_of(r)
        r["label"] = r["fmt"].format(r["value"])
    fields = ["panel", "model", "metric", "K", "value", "label", "fmt", "subset", "N", "direction", "source", "path"]
    with open(OUT / "linkedin_main_data.csv", "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows({**r, "value": repr(r["value"])} for r in rows)
    draw(rows)
    (OUT / "linkedin_main_caption.md").write_text(caption(rows), encoding="utf-8")
    report = check()
    (OUT / "linkedin_main_figure_check.json").write_text(json.dumps(report, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(report["status"], f"{report['values']} values")
    sys.exit(0 if report["status"] == "PASS" else 1)


if __name__ == "__main__":
    main()
