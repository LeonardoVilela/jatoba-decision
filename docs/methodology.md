# Methodology

## Task definition

A decision is a state (text), a question, a primitive (NOUL, CHOICE or SCORE) and K candidates, each with an id and a natural-language description. The target is a probability distribution over the candidates. It may be one-hot (a gold label) or soft (annotator shares, pooled votes, an interpolated continuous score). How each dataset becomes decisions is in [`benchmark/ADAPTER_AUDIT.md`](../benchmark/ADAPTER_AUDIT.md).

## Training data

Six semantic families, all PT-BR:

| family | tasks (sources) |
|---|---|
| intent routing | MASSIVE intent, 60 intents (MASSIVE pt-BR) |
| entailment | ASSIN 2 entailment (NOUL), InferBR 3-way NLI |
| semantic similarity | ASSIN 2 relatedness (SCORE, 5 levels) |
| toxicity and safety | six ToLD-Br categories, HateBR offensive language (NOUL) |
| emotion and affect | six BRIGHTER intensity rubrics (SCORE, 4 levels) |
| preference ranking | Community Alignment first-turn preference among 4 responses |

Roles are assigned by group, never by record (`benchmark/manifests/role_*.jsonl.gz`): 166,465 training, 7,790 development and 7,826 calibration decisions. Evaluation decisions whose group or normalized state collides with any of them were removed.

## Training

The frozen configuration of the released run:

- **Frozen backbone.** Only the 20.1M-parameter head trains. The encoder hash was verified unchanged after training.
- **Initialization.** The head starts from an earlier head trained on the MASSIVE, ASSIN 2, ToLD-Br and HateBR training decisions (a subset of the training role; seed 20260921, best step 3,000).
- **Sampler.** Family uniform (1/6), then task uniform within family, then source; deterministic shuffled cycling within each leaf; no class balancing.
  - MASSIVE K is drawn per decision from 2–60 (40% K ∈ {2, 3, 4, 6}, 25% {8, 12}, 20% {16, 32}, 15% K = 60). K ∈ {5, 10, 24, 48} was never used in training.
  - 10% of MASSIVE draws with K < 60 include one intent from the same official scenario as the gold intent.
  - InferBR: 75% with all three classes, 25% as a pair.
  - Community Alignment: 90% single-annotator choices, 10% multi-annotator distributions.
- **Loss.** Cross-entropy against the target distribution.
- **Optimizer.** AdamW, learning rate 5e-5, betas (0.9, 0.999), weight decay 0.01, gradient clipping 1.0, float32. Linear warm-up for 1,000 steps, then cosine decay over a planned 20,000 steps. Effective batch 32 decisions.
- **Selection.** Every 500 steps on the development role, by hierarchical excess cross-entropy (families equal, tasks equal within a family; MASSIVE fixed at K = 6 so that K = 60 does not dominate). Early stopping with patience 4 stopped the run at step 7,000; step 5,000 was selected.
- **Seeds.** Sampler 20261101, torch 20261102, python 20261103, permutation 20261104.

All of this was frozen before training started. There is one training seed; no multi-seed variance exists for the released model.

## Calibration

M0 fits one temperature per primitive on the calibration role, and nothing else. RAW remains the primary output.

## Evaluation regimes

| regime | block | status |
|---|---|---|
| in-distribution held-out | `jatoba_id` (historical name PRISTINE) | unseen examples and groups of three trained families: InferBR test, BRIGHTER test, held-out Community Alignment prompts |
| legacy / exposed | `legacy_exposed` | MASSIVE, ASSIN 2, ToLD-Br and HateBR test sets; these were used throughout architecture development and are never presented as held out |
| family shift | `shift_normastcu`, `shift_juristcu` | legal relevance judgement, a family never trained on |
| development diagnostic | `gdev_faquad` | FaQuAD evidence selection; used repeatedly during v2 research, so it is a development set |
| candidate-set scaling | MASSIVE K curve | the same 2,901 legacy decisions at K = 2 … 60 with nested candidate sets |

A separate final generalization set remains sealed for future model development.

### Family-shift context budget

Family-shift states join a query with a long legal document, so they are far above the 256-token training regime.
- **Inference budget:** JATOBÁ was run on them with a frozen inference budget above that regime, up to 2,048 tokens.
- **Main comparison:** the NormasTCU comparison uses the `complete_1024` stratum. It holds the 388 pairs whose full formatted JATOBÁ context fits in 1,024 tokens with no truncation (`benchmark/manifests/shift_normastcu_complete_1024.json`).
- **Common stratum:** 34 of those 388 pairs could not be read by Laya without cutting, which leaves a common stratum of 354 pairs over 46 queries.

## Metrics

Defined in [`src/jatoba/metrics.py`](../src/jatoba/metrics.py):

- **ε-CE.** Every prediction is floored at 0.005 and renormalized before cross-entropy. This applies to every model, so a model that outputs exact zeros is not infinitely penalized.
- **Brier** score over the candidate set.
- **top-1**, counted fractionally when several candidates tie for the maximum probability.
- **ECE** with 15 equal-mass bins.
- **Ranking (family shift):** per query, documents are ranked by expected relevance level. nDCG@10 and expected MRR use a relevance threshold of 1.5, and ties are averaged.
- **Aggregation:** record → group → task → family → macro mean. Family-shift metrics are query-weighted.

No composite score is reported.

## External models

Laya multilingual, GLiNER2.5-multi-Decide, Julia-1 and Jev received the same semantic payload: question, candidate descriptions and primitive (`benchmark/adapters/payload.py`). The comparison protocol was frozen before any external output was seen. Two rules follow from it:

- **Truncation.** A decision that a model could not read without cutting its input is N/A for that model. It is never silently truncated. Common subsets are reported where coverage differs.
- **Jev coverage.** Jev was called with a frozen retry policy (4 attempts, waits of 1, 2 and 4 s). Its coverage is **PARTIAL**, and partial blocks are not compared.

The results depend on this protocol. For example, Julia-1 is weak on JATOBÁ's PT-BR evaluation under this protocol; that is not a general statement about Julia-1.

## Statistics

Confidence intervals are paired cluster bootstraps with 10,000 resamples. Clusters are groups (in-distribution) or queries (family shift). Differences whose interval crosses zero are reported as not decisive.
