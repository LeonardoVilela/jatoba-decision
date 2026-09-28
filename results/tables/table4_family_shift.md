# Table 4. Family shift (relevance judgement, never trained on)

NormasTCU, complete_1024 stratum common to all models: 354 (query, document) pairs, 46 queries. Query-weighted means; 95% query-bootstrap CIs (10,000 resamples). Ranking by expected relevance.

| model | ε-CE | nDCG@10 | MRR |
|---|---|---|---|
| JATOBÁ (RAW) | 1.701 [1.607, 1.793] | 0.717 [0.645, 0.787] | 0.527 |
| JATOBÁ (M0) | 1.795 [1.691, 1.898] | 0.714 [0.643, 0.784] | 0.526 |
| Jev (PARTIAL protocol) | 1.498 [1.227, 1.770] | 0.858 [0.790, 0.919] | 0.796 |
| Laya multilingual | 3.792 [3.445, 4.118] | 0.714 [0.645, 0.782] | 0.604 |
| Julia-1 | 1.859 | 0.787 | 0.562 |
| uniform | 1.099 [1.099, 1.099] | 0.712 [0.664, 0.760] | 0.521 |
| BM25 | — | 0.829 [0.767, 0.884] | 0.728 |

Every probabilistic model is worse than uniform in ε-CE. Jev ranks far better than JATOBÁ; Jev vs BM25 nDCG@10 is not statistically decisive (CI crosses zero).

## JurisTCU (2,246 pairs)

| model | ε-CE | nDCG@10 | MRR |
|---|---|---|---|
| JATOBÁ (RAW) | 1.421 | 0.777 | 0.824 |
| JATOBÁ (M0) | 1.447 | 0.776 | 0.824 |
| Julia-1 | 1.952 | 0.652 | 0.629 |
| uniform | 1.386 | 0.686 | 0.740 |
| BM25 | — | 0.856 | 0.958 |

Jev's JurisTCU coverage is partial and not comparable; it is not reported.
