# Launch figure: what each panel shows

Files: `jatoba_linkedin_main.png` / `.svg`. Every plotted number is in `linkedin_main_data.csv` (source file and JSON path per value)
and was checked against its source by `scripts/make_launch_figure.py` (`linkedin_main_figure_check.json`).

## Top-1 as the candidate set grows

- **One sentence:** JATOBÁ keeps top-1 0.785 with 60 candidates (from 0.989 at K = 2), while GLiNER falls to 0.289.
- **Data:** MASSIVE PT-BR intent test set, the same 2,901 decisions at every K. Candidate sets are nested (`benchmark/manifests/k_sets.json.gz`).
- **Metric:** top-1 (higher is better).
- **Sources:** `results/data/t2_massive_top1_vs_k.json`, and `results/data/t7_julia1_external.json` for Julia-1.
- **Caveats:**
  - MASSIVE is a legacy block: it was used during JATOBÁ's architecture development. It shows candidate-set scaling, not generalization to new data.
  - Julia-1 accepts at most 20 options, so its line stops at K = 16 (last value 0.254).
  - Laya is drawn only for K = 2–6, the only K values where it read all 2,901 decisions. Laya values also exist at K = 8 (2,900 decisions) and K = 10 (2,606 decisions); they are in `t2` and not drawn. Above K = 10, Laya's input would be cut.

## PT-BR typed decisions

- **One sentence:** on held-out examples of trained PT-BR families, JATOBÁ's ε-CE is 0.508, against GLiNER 1.291, Laya 1.381 and Julia-1 2.745.
- **Data:** JATOBÁ-ID (historical name PRISTINE), the common subset that all four models read exactly: 15,025 decisions (InferBR 3-way NLI and the six BRIGHTER emotion-intensity tasks).
- **Metric:** group-hierarchical ε-CE (0.005 floor for every model; lower is better).
- **Source:** `results/data/pristine_four_model_common.json`, extracted from the frozen Julia-1 comparison artifact; its hash matches the one recorded in `t7`. The JATOBÁ, GLiNER and Laya values are identical to `results/metrics.json`.
- **Caveat:** these are unseen examples from families JATOBÁ was trained on, not unseen families.

## PT-BR: JATOBÁ vs Julia-1

- **One sentence:** on the JATOBÁ-ID decisions Julia-1 can read, top-1 is 0.848 for JATOBÁ and 0.101 for Julia-1.
- **Data:** JATOBÁ-ID, the JATOBÁ–Julia-1 common subset: 15,028 decisions. These are the 15,025 above plus 3 Community Alignment decisions.
- **Metric:** top-1 (higher is better).
- **Source:** `results/data/t7_julia1_external.json` (block `pristine`).
- **Caveats:**
  - Julia-1 is a model, evaluated here on JATOBÁ's frozen PT-BR payload. This is not Julia-1's own benchmark and not a general statement about Julia-1.
  - The hierarchical ε-CE for this subset is not plotted. The 3 Community Alignment decisions form a whole family in the hierarchical mean, which makes that aggregate unrepresentative. The ε-CE comparison is in the panel above.

## Candidate-order stability

- **One sentence:** reordering the candidates never changed JATOBÁ's answer (0% of reorderings) but changed Julia-1's in 45%.
- **Data:** 22 JATOBÁ-ID CHOICE decisions. Each was re-scored under its reversed order and 3 seeded shuffles (88 reorderings), with identical orders for both models.
- **Metric:** argmax flip rate (lower is better).
- **Source:** `results/data/julia_permutation.json`.
- **Caveats:**
  - JATOBÁ is permutation-equivariant by construction, but it was measured only on these 22 decisions.
  - Julia-1 was also measured on MASSIVE subsets of 40 decisions: K = 2: 20%, K = 4: 35%, K = 8: 38%, K = 10: 60%, K = 16: 60%. JATOBÁ was not run on those subsets, so they are not plotted.

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
