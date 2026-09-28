# Table 3. MASSIVE PT-BR intent top-1 vs number of candidates K

LEGACY / previously exposed data: MASSIVE was used during architecture development, so this measures candidate-set scaling, not unseen-family generalization. Nested candidate sets (`benchmark/manifests/k_sets.json.gz`). Laya is N/A where its input would be cut; Julia-1 accepts at most 20 options.

| K | JATOBÁ | Laya multilingual | GLiNER2.5-multi-Decide | Julia-1 |
|---|---|---|---|---|
| 2 | 0.989 | 0.854 | 0.853 | 0.733 |
| 4 | 0.966 | 0.728 | 0.720 | 0.557 |
| 5 | 0.955 | 0.689 | 0.663 | 0.513 |
| 6 | 0.948 | 0.661 | 0.619 | 0.473 |
| 8 | 0.935 | 0.599 | 0.551 | 0.406 |
| 10 | 0.921 | 0.555 | 0.503 | 0.344 |
| 16 | 0.893 | — | 0.422 | 0.254 |
| 24 | 0.862 | — | 0.365 | N/A (native limit 20) |
| 32 | 0.839 | — | 0.347 | N/A (native limit 20) |
| 48 | 0.808 | — | 0.312 | N/A (native limit 20) |
| 60 | 0.785 | — | 0.289 | N/A (native limit 20) |
