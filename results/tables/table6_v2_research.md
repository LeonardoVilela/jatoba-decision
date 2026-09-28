# Table 6. v2 research directions (none changed the released model)

Each gate was frozen before its results were seen. Details: `docs/research_history.md`.

| direction | outcome |
|---|---|
| contrastive auxiliary loss (V2-B) | NEGATIVE_RESULT: DEV primary worse than control (+0.020 at step 1000) |
| hard-negative curriculum (V2-C) | NEGATIVE_RESULT at step 1500: +0.015 overall, emotion family +0.068 over the 0.05 guard; sharper large-K ranking (K60 top-1 +0.027) without better probabilities |
| pointwise compatibility auxiliary (V2-B2) | NULL: no measurable effect at either stage |
| NorBERTo-large capacity, exploratory (V2-A, fresh head) | NEGATIVE_RESULT under the frozen gate: DEV -0.034 but entailment +0.073 over the guard |
| partial backbone unfreezing (V2-D) | BLOCKED_MEMORY on the 18 GB development machine; not run |
| label smoothing alpha=0.05 (R1) | NULL_RESULT at seed 1 (eps-CE -0.026 [-0.055, +0.007]); independent seed-2 confirmation failed (V2_BASE_NOT_CONFIRMED). Replicated in both seeds: in-domain confident errors p(gold)<0.01 cut 5-14x |
| focal loss gamma=2 (R2) | no eligible checkpoint: under-confident (DEV ECE ~0.11), regressions in three families |
| NorBERTo-large capacity, matched confirmation (F0 loss, FP32 context cache) | V2_LARGE_NOT_CONFIRMED: DEV equal (-0.002), semantic similarity +0.087 over the guard; large-K ranking better (K60 top-1 +0.050) but GDEV eps-CE not better (+0.024 [-0.020, +0.061]) |
