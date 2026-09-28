# Release review: JATOBÁ v1.1 public repository

Scope: turn the research tree into a clean public repository.
- **Not in scope:** no training, no tuning, no new experiments, and no change to any reported number.
- **Status:** released v1.1 is the frozen NorDecision v1.1.
- **Sealed final generalization set:** its data was never opened. Only its protocol files were scanned for hash strings, to confirm that none appear in this repository (0 found).

## What is published

- **`src/jatoba/`:** model, decision encoding, inference API and metrics.
  - The model's submodule names match the frozen checkpoint.
  - It was checked numerically against the research implementation with the v1.1 weights on 320 decisions: max logit difference 4.8e-5, no top-1 disagreement.
- **`benchmark/`:**
  - pinned sources and the ported transforms;
  - manifests (ids, groups and content hashes; no text) and the frozen candidate dictionary;
  - external-model adapters and the evaluator;
  - the cards, the license table and the adapter audit.
- **`results/`:** copies of the frozen publication outputs. Tables, the README block and the figures are generated from them.
- **Documentation and project files:** `docs/`, `MODEL_CARD.md`, `CITATION.cff`, `LICENSE` (Apache-2.0, code only) and the CI workflow.

## Checks

| check | result |
|---|---|
| every evaluation block and training role rebuilt from upstream at pinned revisions | 214,243 decisions, 0 missing, 0 hash mismatches |
| public package vs research implementation (v1.1 weights) | equivalent (max logit Δ 4.8e-5, 0 argmax flips) |
| `ruff check .` | pass |
| `pytest` | pass |
| `scripts/reproduce_tables.py --check` (tables and README headline) | pass |
| `scripts/verify_release.py` | pass; see `release_check.json` |

`verify_release.py` checks the files a commit would publish:
- **Files:** required files are present; no weights, raw data or `.env` files; no file over 10 MB.
- **Contents:** no secret patterns, no local absolute paths, and no reference to the sealed set, including inside the compressed manifests.
- **Hashes and headline:** manifest hashes and counts match `benchmark_spec.json`, and the README headline matches `results/metrics.json`.

Secret findings are reported by location and kind only.

## Corrections made during review (wording only; no number changed)

- **README headline.** The JATOBÁ-ID row said "six trained families". The number is computed on the 15,025 InferBR and BRIGHTER decisions that Laya and GLiNER can also read, which cover three families with Community Alignment excluded. The label and the Table 2 note now say so.
- **Julia-1 results file.** A note in `results/data/t7_julia1_external.json` named the sealed set internally. It now says "sealed final generalization set untouched".
- **FaQuAD K range.** The adapter audit now states the actual range (2–10) next to the allowed one (2–60).
- **Candidate descriptions.** The claim "no description paraphrases a test example" was replaced by a mechanical 5-gram check. It found one generic shared phrase, which is disclosed.

## Adapter audit

No invalid mapping was found, and no scientific release blocker was raised. Caveats that travel with the results (`benchmark/ADAPTER_AUDIT.md`):

1. **MASSIVE intent descriptions.** They are project-authored, with disambiguating clauses; 10 of 60 were revised after reading TRAIN utterances. MASSIVE is reported only as legacy / exposed.
2. **ASSIN 2 similarity.** Targets carry float32 artifacts from the upstream loader.
3. **ToLD-Br and HateBR.** Targets are shares of three annotators, not calibrated probabilities.
4. **Community Alignment.**
   - Sets with responses over 384 tokens are excluded (1,798 of 8,409), which favours short responses.
   - Candidates are identified by text because of the upstream slot bias.
5. **JurisTCU labels.** They are GPT-4 judgements confirmed by experts, not independent human ratings.
6. **Normas and Juris states.** They are long and exceed the 256-token trained regime.
7. **FaQuAD.** Evidence sentences come from a regex split.
8. **InferBR.** The official train and validation splits share premises, so roles are premise-grouped.
9. **GLiNER2.5-multi-Decide is N/A on Normas and Juris.** Its schema validation rejects parentheses in the frozen relevance descriptions, and the descriptions were not rewritten for it.

Machine-readable structural checks: `benchmark/adapter_audit.json` (no problems in any block).

## Redistribution

| source | status |
|---|---|
| MASSIVE pt-BR, InferBR, BRIGHTER, NormasTCU, JurisTCU | REDISTRIBUTION_OK (ids and hashes shipped anyway) |
| ASSIN 2, ToLD-Br, HateBR, Community Alignment, FaQuAD | REBUILD_FROM_UPSTREAM_ONLY |

No upstream records are distributed. The candidate dictionary quotes short rubric sentences from the ASSIN 2 guidelines and the JurisTCU and NormasTCU papers, with citations.

## Withheld

- **Model weights:** the full checkpoint and the head-only file.
- **Built benchmark data:** `benchmark/build/`, which is git-ignored.
- **Research-only artifacts:** raw predictions, run directories, external-model raw responses, and the training code.
- **The sealed final generalization set:** its data, manifest, ids and build output.

## Licensing blockers for weights

1. NorBERTo-base is CC-BY-NC-SA-4.0: non-commercial and share-alike.
2. ASSIN 2 states no license.
3. HateBR's license statements conflict: Apache-2.0 on the Hugging Face card, CC BY-NC 4.0 on GitHub.
4. The scope of ToLD-Br's ShareAlike clause for trained weights is unclear.
5. Community Alignment's consent and privacy documentation for model training is not public.
6. FaQuAD has no license at its source. It affects evaluation only, not training.

## Before announcing publicly

- Read the rendered README, MODEL_CARD and BENCHMARK_CARD on GitHub. Check that the figures render and the Mermaid diagram displays.
- Confirm that the CI run on GitHub is green. It installs CPU torch and has only run locally so far.
- Decide whether `main` should receive the release branch; this review did not merge.
- Keep the weights statement until the licensing items above are resolved. Get legal advice before any weight release.
- Optionally ask the NorBERTo, HateBR, ASSIN 2 and ToLD-Br authors to confirm the terms.
- Do not describe JATOBÁ-ID or the legacy block as a generalization test, or any table as a leaderboard.
