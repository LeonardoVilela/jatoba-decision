# JATOBÁ evaluation suite: benchmark card

## Purpose

The suite evaluates **typed probabilistic decisions** in Brazilian Portuguese. A model receives a state, a question and a bounded set of described options, and must return a probability for each option. It was built to evaluate JATOBÁ and to compare it with other decision models under one fixed semantic payload. It is not an official community benchmark or leaderboard.

## Interface

- **NOUL:** is a proposition true? Two candidates, `false` and `true`.
- **CHOICE:** one of K described options, with K from 2 to 60.
- **SCORE:** an ordered rubric; the target is a distribution over levels, and the expected level is Σ i·pᵢ.

Targets may be soft: annotator shares, pooled votes, or interpolated continuous scores. See `ADAPTER_AUDIT.md`.

## Evaluation regimes

| block | regime | what it measures | decisions |
|---|---|---|---|
| `jatoba_id` (historical name PRISTINE) | in-distribution held-out | unseen examples and groups from families used in training: InferBR test, BRIGHTER test, held-out Community Alignment prompts | 15,711 |
| `legacy_exposed` | legacy / exposed | MASSIVE, ASSIN 2, ToLD-Br and HateBR test items. These sources were used throughout architecture development, so this is never pristine validation | 12,585 |
| `shift_normastcu`, `shift_juristcu` | family shift | relevance judgement of legal documents, a family never used in training | 804, 2,246 |
| `gdev_faquad` | development diagnostic | FaQuAD evidence-sentence selection. It was used repeatedly during later research, so it is a development set, not a test | 816 |
| MASSIVE K curve (`k_sets.json.gz`) | candidate-set scaling on LEGACY data | the same 2,901 decisions with nested candidate sets, K = 2 … 60 | 11 × 2,901 |

A separate final generalization set remains sealed for future model development. It is not part of this release.

> Strong performance on JATOBÁ-ID measures specialization to trained semantic families on unseen examples. It is not evidence of universal decision generalization.

## Construction

- **Sources and revisions:** `sources.py` pins each source (see `DATA_LICENSES.md`).
- **Transformations:** `transforms.py`, frozen (see `ADAPTER_AUDIT.md`).
- **Candidates:**
  - fixed taxonomies come from `candidate_dictionary.json`;
  - Community Alignment uses the response texts;
  - FaQuAD uses the paragraph's sentences.
- **Group splitting:** roles are assigned by group, never by record.
  - Groups are the premise (InferBR), the text (BRIGHTER, ToLD-Br, HateBR), the prompt (Community Alignment), the query (Normas/Juris), and base id plus normalized state (MASSIVE, ASSIN 2).
  - In the JATOBÁ-ID, legacy and family-shift blocks, decisions whose group key or normalized state collides with any training, development or calibration decision were removed before evaluation.
- **Variable K:** each MASSIVE decision gets nested candidate sets (gold plus the first K−1 negatives of one seeded order), and each set is shown in its own seeded order.
- **Reproducibility:** manifests hold ids, groups and SHA-256 content hashes. The builder reproduces every frozen decision byte-for-byte; this was verified for all blocks and all training roles.

## Metrics

- **Probability quality:**
  - ε-CE: a 0.005 floor applied to every model, then renormalized; this keeps models with exact zeros comparable.
  - Brier score.
  - ECE (15 equal-mass bins).
- **Ranking quality:**
  - top-1, counted fractionally over ties;
  - for the family-shift blocks, per-query MRR and nDCG@10, ranking documents by expected relevance.
- **Aggregation:** records are averaged within groups, groups within tasks, tasks within families, then families. Large tasks and repeated groups therefore do not dominate.
- **No composite score.** Ranking and probability quality are reported separately because they disagree. On NormasTCU, a model can rank well while its probabilities are worse than uniform.

## What it does not measure

- English or other languages. JevBench is reported separately; JATOBÁ is at chance level there.
- Long contexts. Training states are at most 256 tokens; see `docs/limitations.md`.
- Open-ended reasoning, generation or retrieval.
- Rare toxicity categories reliably (few positives).
- Human validation of the candidate descriptions by annotators outside the project.

## Known biases

- **Social-media sources:** ToLD-Br (tweets) and HateBR (Instagram comments), with their demographic and topical skews.
- **Class imbalance:** most emotion-intensity and toxicity decisions have the "absent / false" label.
- **Community Alignment filtering:** sets with long responses are excluded, and position bias exists upstream (candidates are identified by text).
- **Legal-domain confounds:** NormasTCU and JurisTCU mix a new decision family with a new domain and long documents, so a failure there cannot be attributed to the family alone.

## Licenses

See `DATA_LICENSES.md`. No upstream text is distributed.
