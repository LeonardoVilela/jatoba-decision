# Reproducibility

## What can be reproduced from this repository

| artifact | how | check |
|---|---|---|
| every evaluation block and training role | `python scripts/build_benchmark.py [--blocks …]` | each decision is compared with its frozen SHA-256 content hash; a block that differs is not written |
| tables and the README results block | `python scripts/reproduce_tables.py` | `--check` fails if any generated file differs |
| figures | `uv run --no-project --with matplotlib python scripts/make_figures.py` | drawn from `results/data/` only |
| metrics of your own predictions | `python benchmark/evaluate.py --block … --predictions …` | uses `src/jatoba/metrics.py` |
| the release checks | `python scripts/verify_release.py` | writes `release_check.json` |

Evaluating JATOBÁ itself requires the head weights, which are withheld; see [`MODEL_CARD.md`](../MODEL_CARD.md).

## Pinned inputs

Every upstream source is pinned to a revision in [`benchmark/sources.py`](../benchmark/sources.py), and the same pins appear in [`benchmark/benchmark_spec.json`](../benchmark/benchmark_spec.json):

| source | revision |
|---|---|
| `Magurofg/massive-pt-br` | `907f905b` |
| `nilc-nlp/assin2` (read with `datasets`; relatedness scores are float32) | `0ff9c867` |
| `JAugusto97/ToLD-Br` (GitHub, `ToLD-BR_alpha.csv`) | `6b325d26` |
| `franciellevargas/HateBR` | `077db456` |
| `hapaxlegomenon/InferBR` | `304b2ca3` |
| `brighter-dataset/BRIGHTER-emotion-intensities` | `08a5d61d` |
| `facebook/community-alignment-dataset` (parquet conversion) | `4d21f8db` |
| `LeandroRibeiro/NormasTCU` | `f34d92d4` |
| `LeandroRibeiro/JurisTCU` | `5a520e1f` |
| `liafacom/faquad` (GitHub) | `6ad978f2` |
| backbone `Itau-Unibanco/NorBERTo-base` | `db73446f89c96044863ea05a39f680524b84bccb` |

The full commit hashes are in `sources.py`.

## Hashes

- **Record content hash:** SHA-256 of the JSON object with keys `id`, `type`, `state`, `question`, `options` and `target`, serialized with sorted keys and `ensure_ascii=False` (`benchmark/transforms.py:content_hash`).
- **Evaluation manifests:** one row per decision (id, source, task, family, group, content hash). The file hashes are in `benchmark_spec.json` and checked by the tests.
- **Training-role manifests:**
  - Rows carry a 16-hex-digit hash prefix, and each header carries the full aggregate hash of the role.
  - The builder checks both.
- **Candidate dictionary:**
  - The file's SHA-256 is `14531bc4…1d27`.
  - It embeds `dictionary_sha256` = `d2983c27…a901`, the canonical hash of its task entries, which is the value recorded in the frozen training configuration.

## Verification performed for this release

- **Rebuild from upstream.** Every evaluation block and every training role was rebuilt from upstream at the pinned revisions. Every decision matched its frozen hash: 0 missing, 0 mismatched. This includes Community Alignment, rebuilt from about 1 GB of upstream parquet.
- **Numerical equivalence.** The public `jatoba` package was checked against the frozen research implementation with the v1.1 weights, on 160 JATOBÁ-ID and 160 legacy decisions:
  - maximum absolute logit difference 2.9e-5 and 4.8e-5;
  - no top-1 disagreement.
- **Regenerated tables.** Every table and the README results block are regenerated from `results/data/` and `results/metrics.json`, which are copies of the frozen research outputs.

## Seeds

- **Training:** sampler 20261101, torch 20261102, python 20261103, permutation 20261104.
- **Bootstrap:** 10,000 resamples; seeds are recorded next to each interval in `results/data/`.
- **Candidate order:** the K-curve candidate sets and their display orders are frozen in `benchmark/manifests/k_sets.json.gz` rather than regenerated from a seed.

## Environment

- **Software:** the research runs recorded Python 3.12.13, PyTorch 2.14.0 and transformers 4.57.6.
- **Hardware:** an 18 GB Apple-silicon laptop (MPS). Julia-1 ran on CPU because its engine does not support MPS.
- **Numerics:** small numeric differences between devices are expected (see the equivalence check above).

## What cannot be reproduced here

- **Training the released model:** the training code is not part of this release, and neither are the weights.
- **Jev:** results depend on a hosted API that may change.
- **The sealed final generalization set:** it is reserved for future model development and is not part of this release.
