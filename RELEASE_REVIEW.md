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

## Weight release (2026-09-28)

**Status:** `WEIGHTS_RELEASED_NONCOMMERCIAL_WITH_DOCUMENTED_LICENSE_AMBIGUITY`.

- **Where:** https://huggingface.co/leoabreu288/jatoba-decision (public), upload commit `145f99385cc4ce842013e15fb4b1e5beebc1358a`.
- **License:** CC BY-NC-SA 4.0, which follows the included NorBERTo-base encoder. The GitHub code stays Apache-2.0.
- **Human release decision:**
  - `USER_ACCEPTED_NONCOMMERCIAL_WEIGHT_RELEASE_WITH_DOCUMENTED_ASSIN2_LICENSE_AMBIGUITY`.
  - ASSIN 2 is `OPEN_RESEARCH_USE_EVIDENCE_STRONG / FORMAL_LICENSE_UNSPECIFIED`.
  - The decision is a disclosed choice, not a legal clearance.
  - ASSIN 2 text is still never redistributed.
  - Details: [`docs/final_weight_license_audit.md`](docs/final_weight_license_audit.md).
- **Artifact:**
  - `model.safetensors` contains the full model: the frozen NorBERTo-base encoder unchanged, plus the trained head. It is float32, SHA-256 `0b8dbbbd3ccc5b24b0802c80cab3585252c2e5392fd7d6d6f3c7f6834091f8f2`.
  - It comes from the frozen checkpoint `78d22d758edcdf8529768d22730723d0a0edf17e84fc811f357ad8d150dd5882`, from which only the head was exported. Optimizer, scheduler, RNG and sampler state were not uploaded.
- **Equivalence:** PASS ([`docs/hf_release_equivalence.json`](docs/hf_release_equivalence.json)).
  - All 177 tensors are bitwise-identical to their sources.
  - The public load path matches the research path exactly (Δ 0.0).
  - Against the frozen v1.1 logits, on 320 decisions: max Δ 4.8e-5, 0 top-1 changes.
- **Clean test:** PASS. A fresh venv installed from GitHub, then ran the model card snippet with an empty Hugging Face cache and no token. The downloaded file hash matches.
  - **Caveat:** the GitHub repository is still **private**, so the install used this machine's git credentials. Public users cannot `pip install` it until the repository is made public. Manifest: [`docs/hf_release_manifest.json`](docs/hf_release_manifest.json).
- **Security:**
  - The Hugging Face token was read from the local `.env` inside the upload process only; it was never printed or written.
  - `.env` is git-ignored and absent from every commit.
  - The staging directory was scanned for tokens, local paths and sealed-set references before the upload. The only hit was 3 generic subword entries in NorBERTo's byte-identical upstream `tokenizer.json`.

## Not published

- **Built benchmark data:** `benchmark/build/`, which is git-ignored. No upstream dataset text is on GitHub or Hugging Face.
- **Research-only artifacts:** the full training checkpoint (optimizer and RNG state), raw predictions, run directories, external-model raw responses, and the training code.
- **The sealed final generalization set:** its data, manifest, ids and build output.

## Remaining licensing notes

1. NorBERTo-base is CC BY-NC-SA 4.0, so the weights are non-commercial and share-alike.
2. ASSIN 2 states no corpus license. A permission request to the organizers is drafted in the audit; it has not been sent.
3. HateBR's authors say CC BY-NC 4.0 and "research purposes only"; their Hugging Face card says Apache-2.0.
4. ToLD-Br is CC BY-SA 4.0. Whether ShareAlike reaches trained weights is not stated.
5. The MASSIVE pt-BR localization does not name the LLM used to create it.
6. FaQuAD has no license at its source; it is used for evaluation only.

## Before announcing publicly

- **Required:** make the GitHub repository public. It returns 404 to anonymous visitors, so the README and model card links, and the `pip install` line on Hugging Face, fail for readers.
- Confirm that the CI run on GitHub is green.
- Decide whether `main` should receive the release branch. This review did not merge, so the GitHub landing page still shows `main`.
- Optionally send the ASSIN 2 permission request and ask the HateBR, ToLD-Br and MASSIVE pt-BR authors to confirm their terms.
- Do not describe the weights as commercially usable, or the licensing as legally cleared.
