"""Figures for the README and docs, drawn from results/data/ (needs matplotlib, not a package dependency):

    uv run --no-project --with matplotlib python scripts/make_figures.py
"""

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
DATA, OUT = ROOT / "results/data", ROOT / "results/figures"
# Categorical slots validated for colour-vision deficiency; low-contrast slots always get a marker shape and a direct label.
BLUE, ORANGE, AQUA, YELLOW, INK, MUTED, GRID = "#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#1f1f1e", "#6b6a64", "#e6e5e0"


def style(ax):
    ax.grid(axis="y", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(MUTED)
    ax.tick_params(colors=MUTED, labelsize=9)


def k_curve():
    rows = json.loads((DATA / "t2_massive_top1_vs_k.json").read_text())["rows"]
    julia = {r["block"]: r["top1"] for r in json.loads((DATA / "t7_julia1_external.json").read_text())["rows"]
             if r.get("model") == "Julia" and r["block"].startswith("massive_K")}
    series = [("JATOBÁ", BLUE, "o", [(r["K"], r["NorDecision_RAW_top1_all"]) for r in rows]),
              ("GLiNER2.5-multi-Decide", ORANGE, "s", [(r["K"], r["GLiNER_top1"]) for r in rows]),
              ("Laya multilingual", AQUA, "^", [(r["K"], r["Laya_multilingual_top1_common"]) for r in rows
                                                if isinstance(r["Laya_multilingual_top1_common"], float)]),
              ("Julia-1", YELLOW, "D", [(r["K"], julia[f"massive_K{r['K']}"]) for r in rows if f"massive_K{r['K']}" in julia])]
    fig, ax = plt.subplots(figsize=(7.2, 4.2), dpi=200)
    style(ax)
    for name, color, marker, points in series:
        ks, ys = zip(*points)
        ax.plot(ks, ys, color=color, linewidth=2, marker=marker, markersize=6, markeredgecolor="white", markeredgewidth=1, label=name)
        ax.annotate(name, (ks[-1], ys[-1]), xytext=(6, 0), textcoords="offset points", va="center", fontsize=8.5, color=INK)
    ax.set_xscale("log", base=2)
    ax.set_xticks([r["K"] for r in rows], [str(r["K"]) for r in rows])
    ax.set_xlim(1.8, 130)
    ax.set_ylim(0, 1.02)
    ax.set_xlabel("candidates per decision (K)", color=INK, fontsize=10)
    ax.set_ylabel("top-1 accuracy", color=INK, fontsize=10)
    ax.set_title("MASSIVE PT-BR intent (previously exposed data): accuracy as K grows", color=INK, fontsize=11, loc="left")
    ax.legend(frameon=False, fontsize=8.5, loc="lower left")
    fig.text(0.01, 0.01, "Laya: N/A where its input would be cut (K ≥ 16). Julia-1: at most 20 options.", fontsize=7.5, color=MUTED)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    fig.savefig(OUT / "massive_k_curve.png")


def order_sensitivity():
    data = json.loads((DATA / "julia_permutation.json").read_text())
    julia = data["julia"]
    ks = [2, 4, 8, 10, 16]
    labels = ["JATOBÁ-ID\nCHOICE (K 3-4)"] + [f"MASSIVE\nK = {k}" for k in ks]
    julia_rates = [julia["S1_PRISTINE_choice"]["argmax_flip_rate"]] + [julia[f"S2_K{k}"]["argmax_flip_rate"] for k in ks]
    fig, ax = plt.subplots(figsize=(7.2, 3.8), dpi=200)
    style(ax)
    x = list(range(len(labels)))
    bars = ax.bar([i + 0.18 for i in x], julia_rates, width=0.34, color=YELLOW, label="Julia-1", edgecolor="white", linewidth=1)
    jatoba = data["nordecision_v11_same_S1_records_same_orders"]["argmax_flip_rate"]
    ax.bar([x[0] - 0.18], [max(jatoba, 0.004)], width=0.34, color=BLUE, label="JATOBÁ (same decisions and orders)", edgecolor="white", linewidth=1)
    ax.annotate(f"{jatoba:.0%}", (x[0] - 0.18, 0.004), xytext=(0, 3), textcoords="offset points", ha="center", fontsize=8.5, color=INK)
    for bar, rate in zip(bars, julia_rates):
        ax.annotate(f"{rate:.0%}", (bar.get_x() + bar.get_width() / 2, rate), xytext=(0, 3), textcoords="offset points", ha="center",
                    fontsize=8.5, color=INK)
    ax.set_xticks(x, labels, fontsize=8.5)
    ax.set_ylim(0, 0.75)
    ax.set_ylabel("share of reorderings that change top-1", color=INK, fontsize=10)
    ax.set_title("Candidate-order sensitivity (reverse + 3 seeded shuffles per decision)", color=INK, fontsize=11, loc="left")
    ax.legend(frameon=False, fontsize=8.5, loc="upper left")
    fig.tight_layout()
    fig.savefig(OUT / "candidate_order_sensitivity.png")


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    k_curve()
    order_sensitivity()
