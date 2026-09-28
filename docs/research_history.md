# Research history

JATOBÁ was developed under the internal name NorDecision. Frozen result files keep that name.

## Path to v1.1

1. **Legacy tasks.** The first heads were trained and selected on MASSIVE, ASSIN 2, ToLD-Br and HateBR. These sources shaped the architecture, which is why they are reported only as `legacy_exposed`.
2. **Architecture v1.1.**
   - v1.1 combines candidate→context cross-attention with a positionless set transformer on top of the frozen NorBERTo-base encoder.
   - A head trained on the legacy tasks (best step 3,000) became the initialization for the general run.
3. **General mixture.** Three sources were added: InferBR (entailment), BRIGHTER (a new emotion family) and Community Alignment (a new preference family), and training moved to a family-balanced sampler with variable K. The configuration, seeds, candidate texts, splits and selection metric were frozen before training. See [`methodology.md`](methodology.md).
4. **Frozen evaluation.** JATOBÁ-ID, legacy, family shift (NormasTCU, JurisTCU) and the K curve were evaluated once.
   - The pre-registered unseen-family criterion **failed**: on NormasTCU the model is worse than uniform in ε-CE.
   - The failure was kept as the headline limitation rather than tuned away.
5. **External comparison.** Laya multilingual, GLiNER2.5-multi-Decide, Julia-1 and Jev were compared under one frozen protocol with amendments recorded before outputs were seen. The results are in [`results/`](../results/).

## v2 research: nothing replaced v1.1

After v1.1 was frozen, several directions were tested against gates written before their outputs were seen. None passed. The released model is v1.1.

The gates were:
- **Development gate:** development-role primary metric against a matched control, with a guard that no family gets worse by more than 0.05.
- **Diagnostic gate:** for the later directions, a paired cluster bootstrap on the development diagnostic (FaQuAD).

Source: [`results/data/v2_research.json`](../results/data/v2_research.json), which records the hashes of the research artifacts it was extracted from.

| direction | outcome |
|---|---|
| contrastive auxiliary loss | **negative**: development metric worse than control (+0.020 at step 1,000) |
| hard-negative curriculum | **negative**: +0.015 overall, emotion family +0.068 over the guard. Large-K ranking was sharper (K = 60 top-1 +0.027), but probabilities were not better. |
| pointwise compatibility auxiliary | **null**: no measurable effect at either stage |
| NorBERTo-large, fresh head (exploratory) | **negative** under the gate: development −0.034, but entailment +0.073 over the guard |
| partial backbone unfreezing | **blocked**: about 19 GB footprint on an 18 GB machine; projected > 9 h per 500 steps; not run |
| label smoothing α = 0.05 | **null** at seed 1 (diagnostic ε-CE −0.026, CI [−0.055, +0.007]); an independent seed-2 confirmation failed on direction. Replicated in both seeds: confident in-domain errors (p(gold) < 0.01) were reduced 5–14×. |
| focal loss γ = 2 | **no eligible checkpoint**: under-confident (development ECE ≈ 0.11), with regressions in three families |
| NorBERTo-large, matched confirmation | **not confirmed**: development equal (−0.002), semantic similarity +0.087 over the guard. Large-K ranking better (K = 60 top-1 +0.050), but diagnostic ε-CE not better (+0.024, CI [−0.020, +0.061]). |

Two lessons carried forward:
- **Ranking and calibration separate.** Several directions improved top-1 at large K without improving probabilities, the same split seen on NormasTCU.
- **Encoder size alone did not help.** Under these gates, the larger frozen NorBERTo encoder did not pass.
