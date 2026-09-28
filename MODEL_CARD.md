# Model card: JATOBÁ v1.1

**Joint Assessment of Typed Options with BERT Architecture.** It was developed under the internal name NorDecision v1.1.

> Weights: [huggingface.co/leoabreu288/jatoba-decision](https://huggingface.co/leoabreu288/jatoba-decision), CC BY-NC-SA 4.0 (non-commercial).

## Model

| | |
|---|---|
| type | non-generative typed decision model: state + question + K described candidates → probability per candidate |
| language | Brazilian Portuguese |
| primitives | NOUL (true/false), CHOICE (one of K), SCORE (ordered rubric) |
| backbone | `Itau-Unibanco/NorBERTo-base` @ `db73446f`, frozen (ModernBERT, 149.0M parameters) |
| trained head | 20.1M parameters: cross-attention, fusion MLP, 2-layer positionless set transformer, scorer |
| total | 169,102,081 parameters |
| candidate count | variable; trained and evaluated from 2 to 60 |
| context | 256 tokens trained; longer contexts are refused by default |
| output | RAW softmax (primary); M0 per-primitive temperatures (optional) |
| author | Leonardo Vilela |

Details: [`docs/architecture.md`](docs/architecture.md), [`docs/methodology.md`](docs/methodology.md).

## Intended use

Research on typed probabilistic decisions in PT-BR:
- short texts (up to 256 tokens);
- candidate sets described in natural language;
- families close to the training families: intent routing, entailment, semantic similarity, toxicity, emotion intensity and response preference.

## Out of scope

- **Unseen decision families**, where probabilities are unreliable (see results).
- **English and other languages**, where performance is at chance.
- **Long documents:** not validated.
- **High-stakes automated decisions** about people, including moderation without human review.
- **Commercial use of derived weights:** the backbone license is non-commercial.

## Training data

MASSIVE pt-BR, ASSIN 2, ToLD-Br, HateBR, InferBR, BRIGHTER (ptbr) and Community Alignment (Portuguese first turn):
- 166,465 training, 7,790 development and 7,826 calibration decisions;
- split by group;
- the manifests are in `benchmark/manifests/`.

Licenses and redistribution status: [`benchmark/DATA_LICENSES.md`](benchmark/DATA_LICENSES.md).

## Evaluation

| evaluation | metric | JATOBÁ v1.1 (RAW) |
|---|---|---|
| JATOBÁ-ID (unseen InferBR and BRIGHTER examples; 15,025 decisions) | hierarchical ε-CE ↓ | 0.508 (Laya 1.381, GLiNER 1.291) |
| MASSIVE intent, K = 60 (legacy / exposed) | top-1 ↑ | 0.785 |
| NormasTCU (never trained on) | ε-CE ↓ / nDCG@10 ↑ | 1.701 (uniform 1.099) / 0.717 |
| JurisTCU (never trained on) | ε-CE ↓ / nDCG@10 ↑ | 1.421 (uniform 1.386) / 0.777 |
| JevBench public items (English) | accuracy ↑ | 0.329 (chance 0.318) |

All tables: [`results/tables/`](results/tables/). There is no composite score and no leaderboard.

## Limitations

- **Family shift fails.** JATOBÁ is worse than uniform in ε-CE on the legal-relevance family it never saw, as is every evaluated probabilistic model.
- **JATOBÁ-ID is in-distribution**, and the legacy sources were exposed during development.
- **Weak evidence base:** one training seed, and project-authored candidate descriptions.
- **Calibration:** M0 does not transfer calibration to new families.

Full list: [`docs/limitations.md`](docs/limitations.md).

## Bias and risks

- **Social-media sources.** Toxicity and emotion training data come from social media (tweets, Instagram comments), with their demographic and topical skews.
- **Coarse toxicity targets.** Toxicity targets are shares of three annotators and should not be read as calibrated probabilities of harm.
- **Rare categories.** Rare toxicity categories have few positives.

## Licensing status

- **Code:** Apache-2.0 (code only).
- **Weights:** CC BY-NC-SA 4.0 on [Hugging Face](https://huggingface.co/leoabreu288/jatoba-decision). This follows the included NorBERTo-base encoder, which is CC BY-NC-SA 4.0. Commercial use is not permitted.
- **Training data:** the datasets keep their own terms.
  - HateBR is CC BY-NC 4.0 per its authors.
  - ToLD-Br is CC BY-SA 4.0.
  - ASSIN 2 was released publicly for the research community and used as a shared-task training resource, but no explicit corpus license was located.
- **Release decision:** the weights were released under a documented human release decision that accepts the ASSIN 2 ambiguity; this is not a legal clearance. See [`docs/final_weight_license_audit.md`](docs/final_weight_license_audit.md).

## Citation

See [`CITATION.cff`](CITATION.cff). Please also cite the upstream datasets and NorBERTo.
