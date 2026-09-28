# Data licenses and redistribution decisions

**What this repository distributes: no upstream text.**
- It holds, for every source:
  - record ids, group keys and content hashes (`manifests/`);
  - the transformation code;
  - the candidate dictionary.
- Decisions are rebuilt locally from each upstream dataset (`scripts/build_benchmark.py`). You must obtain every dataset under its own terms.

The status column says what we *would* allow ourselves to redistribute. It is conservative, and ambiguity is never read as permission:
- `REDISTRIBUTION_OK`: derived rows could be published with attribution.
- `REBUILD_FROM_UPSTREAM_ONLY`: publish builders, ids and hashes only.
- `DO_NOT_DISTRIBUTE`: nothing that recreates the data without upstream access.

**How the evidence was collected (2026-09-27):**
- Hugging Face dataset card metadata at the pinned revision, via the Hub API.
- The upstream README or LICENSE files.
- For ToLD-Br and FaQuAD, the authors' GitHub repositories at the pinned commits.

This is a record of declared terms, not legal advice.

| Dataset (use) | Upstream, pinned revision | Declared license (evidence) | Applies to data? | Attribution / derivative obligations | Platform concern | Status | Rationale |
|---|---|---|---|---|---|---|---|
| MASSIVE pt-BR (training, LEGACY, K curve) | `Magurofg/massive-pt-br` @ `907f905b`, derived from `AmazonScience/massive` @ `ff6bd8e4` | CC-BY-4.0 (both cards) | yes | attribute MASSIVE (FitzGerald et al., 2022) | none | REDISTRIBUTION_OK | explicit CC-BY-4.0 on the data. We still ship ids only, for uniformity. |
| ASSIN 2 (training, LEGACY) | `nilc-nlp/assin2` @ `0ff9c867` | `unknown` on the card; "Licensing Information: More Information Needed"; the official page gives no license | unclear | cite Real et al. (2020) | none | REBUILD_FROM_UPSTREAM_ONLY | no license stated |
| ToLD-Br (training, LEGACY) | GitHub `JAugusto97/ToLD-Br` @ `6b325d26` (`ToLD-BR_alpha.csv`) | CC-BY-SA-4.0 (repository LICENSE; HF card `JAugusto97/told-br` agrees) | yes | attribution; **ShareAlike** for adapted material | tweets (social-media text) | REBUILD_FROM_UPSTREAM_ONLY | ShareAlike scope plus social-media content |
| HateBR (training, LEGACY) | `franciellevargas/HateBR` @ `077db456` | **conflict**: HF card says Apache-2.0; the authors' GitHub repository (LICENSE and README) says **CC BY-NC 4.0** | yes | attribution; **NonCommercial** under the stricter reading | Instagram comments (social-media text) | REBUILD_FROM_UPSTREAM_ONLY | the stricter, authors' license is assumed |
| InferBR (training, JATOBÁ-ID) | `hapaxlegomenon/InferBR` @ `304b2ca3` | MIT (card) | stated for the dataset | keep the MIT notice; cite Bencke et al. (2024) | none known | REDISTRIBUTION_OK | explicit permissive license. The premises' own provenance was not independently audited. |
| BRIGHTER, ptbr intensity (training, JATOBÁ-ID) | `brighter-dataset/BRIGHTER-emotion-intensities` @ `08a5d61d` | CC-BY-4.0 (card) | yes | attribute BRIGHTER | part of the texts come from social media | REDISTRIBUTION_OK | explicit CC-BY-4.0; the social-media origin is noted |
| Community Alignment, pt first turn (training, JATOBÁ-ID) | `facebook/community-alignment-dataset` @ `97343c7f` (parquet conversion `4d21f8db`) | CC-BY-4.0 (card) | yes | attribution | crowd-worker conversations: privacy/consent documentation for model training was not found in the public material | REBUILD_FROM_UPSTREAM_ONLY | permissive license, but the provenance/privacy review is open |
| NormasTCU (family shift) | `LeandroRibeiro/NormasTCU` @ `f34d92d4` | CC-BY-4.0 (README "License"; card metadata empty) | yes | attribute NormasTCU | public legal documents | REDISTRIBUTION_OK | explicit CC-BY-4.0 in the README |
| JurisTCU (family shift) | `LeandroRibeiro/JurisTCU` @ `5a520e1f` | CC-BY-4.0 (README "License"; card metadata empty) | yes | attribute JurisTCU | public legal documents | REDISTRIBUTION_OK | explicit CC-BY-4.0 in the README |
| FaQuAD (development diagnostic) | GitHub `liafacom/faquad` @ `6ad978f2` | **no license file or statement** at that commit; the HF mirror `eraldoluis/faquad` declares cc-by-4.0 in metadata only | unclear | cite Sayama et al. (2019) | none | REBUILD_FROM_UPSTREAM_ONLY | the license appears only on a mirror |

## Project-authored and quoted material in `candidate_dictionary.json`

- **Written for this project:** the MASSIVE, InferBR, ToLD-Br, HateBR, BRIGHTER and ASSIN 2 entailment candidate texts. Covered by this repository's code license.
- **Quoted or translated from upstream:** a few short rubric sentences.
  - The ASSIN 2 similarity levels are quoted from the ASSIN 2 annotation guidelines.
  - The JurisTCU levels are quoted from the JurisTCU paper's judging prompt.
  - The NormasTCU levels are translated from the NormasTCU paper.
  - They are included because the reported results depend on them verbatim; the sources are cited.

## Models

- **NorBERTo-base** (`Itau-Unibanco/NorBERTo-base` @ `db73446f`): the frozen JATOBÁ encoder, **CC-BY-NC-SA-4.0** (card at the pinned revision). This constrains any redistribution of JATOBÁ weights. The weights are withheld pending review.
- **External models** (only called through their own code; not redistributed): Laya, GLiNER2.5-multi-Decide and Julia-1 are declared Apache-2.0 on their cards. Jev is a hosted API.

## Unresolved items

- ASSIN 2 has no stated license.
- HateBR's license statements conflict.
- FaQuAD has no license at its source.
- The scope of ToLD-Br's ShareAlike clause for trained weights is unclear.
- Community Alignment's consent/privacy documentation for model training is not public.
- NorBERTo-base is non-commercial and share-alike, which constrains weight distribution.
