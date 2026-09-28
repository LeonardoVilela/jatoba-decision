# Table 2. JATOBÁ-ID (unseen examples of trained PT-BR families)

Common subset of JATOBÁ, Laya multilingual and GLiNER2.5-multi-Decide: 15,025 of 15,711 decisions (decisions every model can read without truncation; the 650 Community Alignment decisions are excluded because Laya cannot read them). ε-CE uses a 0.005 floor for every model. Lower ε-CE is better.

| task | JATOBÁ ε-CE | JATOBÁ top-1 | Laya ε-CE | Laya top-1 | GLiNER ε-CE | GLiNER top-1 |
|---|---|---|---|---|---|---|
| anger_intensity | 0.785 | 0.691 | 2.001 | 0.152 | 1.534 | 0.130 |
| disgust_intensity | 0.168 | 0.968 | 2.583 | 0.018 | 1.585 | 0.098 |
| fear_intensity | 0.264 | 0.937 | 2.148 | 0.057 | 1.510 | 0.117 |
| inferbr_nli3 | 0.557 | 0.789 | 0.624 | 0.810 | 1.057 | 0.465 |
| joy_intensity | 0.716 | 0.765 | 1.716 | 0.176 | 1.472 | 0.180 |
| sadness_intensity | 0.534 | 0.842 | 1.951 | 0.115 | 1.501 | 0.128 |
| surprise_intensity | 0.300 | 0.929 | 2.402 | 0.034 | 1.534 | 0.115 |
| **hierarchical ε-CE (these tasks)** | **0.508** |  | **1.381** |  | **1.291** |  |

Julia-1 on its own exact-fit subset (15,028 decisions): hierarchical ε-CE 2.558, top-1 0.101 (JATOBÁ on the same subset: see `results/data/t7_julia1_external.json`).
Jev: N/A (partial operational coverage of this block).
