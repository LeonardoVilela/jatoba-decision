# Limitations

## What the evidence supports

- JATOBÁ learns six PT-BR decision families with one set of weights.
  - On unseen InferBR and BRIGHTER examples, it clearly beats the evaluated Laya and GLiNER configurations. Hierarchical ε-CE is 0.508 vs 1.381; the 95% CI of the difference is −0.906 to −0.841.
  - That subset is the 15,025 decisions all three can read; the 650 Community Alignment decisions are excluded from the comparison because Laya cannot read them.
- Candidate sets can be described at inference time and can vary in size. MASSIVE top-1 goes from 0.989 at K = 2 to 0.785 at K = 60.
- The model is invariant to candidate order by construction, and no order effect was measured.

## What it does not show

- **Unseen families are not solved.**
  - On NormasTCU (legal relevance, never trained on), JATOBÁ's ε-CE (1.701) is worse than a uniform guess (1.099).
  - So is every evaluated probabilistic model's: Jev 1.498, Julia-1 1.859, Laya 3.792.
  - The pre-registered unseen-family criterion failed.
- **Ranking is not probability quality.**
  - Jev ranks NormasTCU far better (nDCG@10 0.858 vs 0.717), yet its ε-CE is also worse than uniform.
  - Jev vs BM25 on nDCG@10 is not decisive: the CI crosses zero.
- **JATOBÁ-ID is in-distribution.** It measures specialization to trained families on unseen examples, not general decision-making.
  - Laya has higher top-1 on InferBR (0.810 vs 0.789).
  - On the legacy block, Laya also has higher top-1 on ASSIN 2 entailment (0.875 vs 0.852).
- **Legacy data is exposed.** MASSIVE, ASSIN 2, ToLD-Br and HateBR were used throughout architecture development. The K curve is evidence about candidate-set scaling, not generalization.
- **The development diagnostic is not a test.** FaQuAD was used repeatedly during later research.
- **English is at chance.** On the JevBench public items (English), accuracy is 0.329 against a chance level of 0.318. This is a self-run result on public items, not an official score.
- **Julia-1 comparisons are scoped.** Julia-1 is weak on JATOBÁ's PT-BR evaluation under this protocol: a fixed PT-BR payload, at most 20 options, and N/A where its input would be cut. It is also order-sensitive: 20–60% of reorderings change its top-1. None of this is a general statement about Julia-1.
- **Jev coverage is partial.** It is a hosted API that was unstable under the frozen retry policy; partial blocks are not compared.
- **One training seed.** There is no variance estimate for the released model.

## Long contexts

JATOBÁ was trained and evaluated on contexts of at most 256 tokens.
- **Runtime:** the inference path runs up to 8,192 tokens; see `architecture.md` for timings and memory.
- **Semantics:** nothing supports using it at those lengths. On NormasTCU, inference budgets of 128 to 8,192 tokens did not recover performance, and the failure is already visible on short examples, so context length alone does not explain it.
- **API:** the public API refuses longer contexts unless you pass an explicit truncation policy.

## Probabilities

- **RAW** is the primary output.
- **M0** (per-primitive temperatures) was fitted on in-distribution calibration data and does not fix calibration on unseen families. On NormasTCU, M0 is slightly worse than RAW.
- **Low-support categories:** do not treat probabilities as calibrated for rare toxicity categories, where positives are few.

## Latency

Local timings (Apple silicon laptop, batch size 1) depend on hardware and must not be compared with hosted-API latency. In the matched local run, Laya multilingual was faster per decision (p50 25 ms vs 40 ms) but used about 2.2× the peak memory.

## Candidate descriptions

- **Authorship:** the fixed candidate texts were written by the project and were not validated by outside annotators.
- **Overlap check:** one MASSIVE description shares a 5-gram with one test utterance ([`benchmark/CANDIDATE_DESCRIPTIONS.md`](../benchmark/CANDIDATE_DESCRIPTIONS.md)).

## Licensing

- **Weights:** withheld pending a source-license review.
- **Backbone:** NorBERTo-base is CC-BY-NC-SA-4.0, so derived weights can never be described as commercially unrestricted.
- **Data:** see [`benchmark/DATA_LICENSES.md`](../benchmark/DATA_LICENSES.md).
