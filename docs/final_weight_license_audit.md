# Final weight-license audit (2026-09-28)

## Verdict

**Automatic gate:** `WEIGHT_RELEASE_BLOCKED`. ASSIN 2 has no formal license.

**Human release decision (2026-09-28):** `USER_ACCEPTED_NONCOMMERCIAL_WEIGHT_RELEASE_WITH_DOCUMENTED_ASSIN2_LICENSE_AMBIGUITY`, by Leonardo Vilela.
- **What it covers:** the JATOBÁ v1.1 model weights under CC BY-NC-SA 4.0.
- **What it does not cover:** ASSIN 2 text stays unredistributed; the benchmark policy remains `REBUILD_FROM_UPSTREAM_ONLY`.
- **What it is not:** a legal clearance. The ambiguity below remains and is disclosed.

**Release status:** `WEIGHTS_RELEASED_NONCOMMERCIAL_WITH_DOCUMENTED_LICENSE_AMBIGUITY`.

**Scope and method.**
- **What is audited:** the training sources of the frozen JATOBÁ v1.1 checkpoint (NorDecision v1.1, step 5,000) and its frozen encoder.
- **What each source was read from, at the pinned revisions:**
  - the Hugging Face card metadata (YAML and Hub API);
  - the authors' own LICENSE and README files;
  - the official project pages and task papers.
- **Evidence:** SHA-256 hashes of the evidence files are in [`final_weight_license_audit.json`](final_weight_license_audit.json).
- **Not legal advice:** the statuses record what the sources state. They are not a legal determination.

## Training sources

| source (revision) | stated license | applies to | training / weights | status |
|---|---|---|---|---|
| NorBERTo-base, frozen encoder (`db73446f`) | CC BY-NC-SA 4.0 (card YAML and Hub tag) | model | derivation allowed under NC + SA | `NONCOMMERCIAL_ONLY` (floor for JATOBÁ) |
| MASSIVE pt-BR localization (`907f905b`) | CC BY 4.0 ("derivado do MASSIVE © Amazon.com, sob CC-BY-4.0") | data | no restriction stated | `AMBIGUOUS` (provenance) |
| ASSIN 2 (`0ff9c867`) | **not specified** | — | released openly for the research community for a shared task in which systems were trained on it | **`OPEN_RESEARCH_USE_EVIDENCE_STRONG / FORMAL_LICENSE_UNSPECIFIED`** |
| InferBR (`304b2ca3`; original repository MIT) | MIT | repository including data | no restriction | `CLEAR_FOR_TRAINING_AND_WEIGHT_RELEASE` |
| ToLD-Br (`6b325d26`) | CC BY-SA 4.0 (LICENSE_ToLD-Br.txt) | data | nothing stated about trained weights | `SHAREALIKE_OR_ATTRIBUTION` |
| HateBR (`077db456`; authors' GitHub) | CC BY-NC 4.0, "research purposes only" (GitHub); the HF card says Apache-2.0 | data | non-commercial | `NONCOMMERCIAL_ONLY` |
| BRIGHTER ptbr (`08a5d61d`) | CC BY 4.0 | data | no restriction stated | `SHAREALIKE_OR_ATTRIBUTION` (attribution) |
| Community Alignment pt (`97343c7f`) | CC BY 4.0 | data | training use explicitly contemplated by the card | `SHAREALIKE_OR_ATTRIBUTION` (attribution) |

The head was initialized from an earlier head trained only on MASSIVE, ASSIN 2, ToLD-Br and HateBR training decisions, so no other source enters the weights.

## Findings

**NorBERTo-base.** The card at `db73446f` declares `license: cc-by-nc-sa-4.0`.
- The full JATOBÁ checkpoint contains these weights unchanged, so any release must be CC BY-NC-SA 4.0 or compatible, non-commercial, with attribution to Itaú Unibanco and a citation of the NorBERTo paper.
- A head-only release would not escape the dataset questions below.

**ASSIN 2: open research use documented; formal license unspecified.**
- **Evidence of open research use:**
  - The official site (`sites.google.com/view/assin2`) publicly distributes the train, validation and test data.
  - The task paper (CEUR-WS Vol-2583) says ASSIN 2 "offered the interested community a new benchmark". It thanks the annotators for "producing open resources for the community interested on the computational processing Portuguese".
  - The paper documents participating teams training models on the ASSIN 2 train collection.
- **Evidence of a license: none found.**
  - The Hugging Face card says `license: unknown` and "Licensing Information: [More Information Needed]". The official site has no license or terms.
  - The paper's only CC BY 4.0 notice reads "Copyright © 2020 *for this paper* by its authors". It covers the paper, not the corpus.
  - `github.com/erickrf/assin` is MIT, but it holds only the evaluation scripts.
  - ASSIN 2 is built on SICK-BR, which states no license. SICK-BR translates SICK, whose Zenodo record is CC BY-NC-SA 3.0.
  - No clause explicitly permits or restricts redistributing trained weights.
- **Not treated as permission:** public download, the Apache-2.0 header of loader code, and third-party models trained on ASSIN 2.
- **Decision:** Leonardo accepted this documented ambiguity for a non-commercial weight release. The decision covers the weights only, not the corpus text.

**MASSIVE pt-BR: provenance ambiguity.** The pt-BR text is not Amazon's; upstream MASSIVE has no pt-BR locale.
- The localizer created it from the pt-PT split with an unnamed "LLM teacher" and declares CC BY 4.0.
- The generating model and its output terms are identified neither in the card nor in the author's public repositories (the linked repository returns 404).
- There is no known restriction, but the question needs clarification.

**ToLD-Br.**
- **License:** CC BY-SA 4.0 on the data; the code is MIT.
- **Trained weights:** neither the license nor the authors say whether trained weights are Adapted Material. The authors do distribute their own fine-tuned model, with no license stated for it.
- **Not decided here:** this audit does not decide whether ShareAlike reaches weights.
- **Compatibility:** a CC BY-NC-SA 4.0 release would be share-alike in any case.

**HateBR.**
- **Conflict:** the authors' repository LICENSE and README say CC BY-NC 4.0, "intended for research purposes only. Commercial use is not permitted", while the same author's Hugging Face card says Apache-2.0.
- **Adopted:** the stricter statement. JATOBÁ is non-commercial.
- **Open point:** "research purposes only" is narrower than CC BY-NC. The authors' confirmation that a public non-commercial weight release fits it would remove doubt.

**InferBR, BRIGHTER, Community Alignment.**
- **Licenses:** explicit permissive licenses on the data (MIT, CC BY 4.0, CC BY 4.0), with attribution obligations.
- **Community Alignment:** its card explicitly addresses use "for training purposes" and asks users to filter annotator-initiated prompts. No further consent terms were reviewed, and none are claimed here.

## Evaluation-only sources (do not affect the weights)

| source | license | note |
|---|---|---|
| NormasTCU | CC BY 4.0 (README) | family shift |
| JurisTCU | CC BY 4.0 (README) | family shift |
| FaQuAD | not stated at the source (the HF mirror metadata says cc-by-4.0) | development diagnostic |

## Reducing the remaining ambiguity

**1. Ask the ASSIN 2 organizers.**
- Addresses from the 2020 task paper (they may have changed): livyreal@gmail.com, erick.fonseca@lx.it.pt, hroliv@dei.uc.pt.
- Nothing has been sent. The draft:

> **Subject:** ASSIN 2 corpus — model weights trained on it (non-commercial release)
>
> Dear Dr. Real, Dr. Fonseca and Prof. Gonçalo Oliveira,
>
> I trained JATOBÁ, a small research model for typed probabilistic decisions in Brazilian Portuguese (https://github.com/LeonardoVilela/jatoba-decision). Its training data includes the ASSIN 2 training split, cited as Real et al. (2020). The weights are published for non-commercial use under CC BY-NC-SA 4.0 at https://huggingface.co/leoabreu288/jatoba-decision. No ASSIN 2 text is redistributed.
>
> I could not find a license for the ASSIN 2 corpus itself. Could you confirm that this use is acceptable, or point me to the corpus license? I will adjust or withdraw the release if you prefer.
>
> Thank you for creating ASSIN 2.
>
> Leonardo Vilela

**2. If the organizers object.** Withdraw the weights. A candidate trained without ASSIN 2 would be a different model with its own version, not v1.1; it has not been run.

**Also worth clarifying** (not blockers):
- the MASSIVE pt-BR localizer: which LLM was used, and its terms;
- HateBR: whether a non-commercial weight release fits "research purposes only";
- ToLD-Br: the authors' view on ShareAlike and trained weights.
