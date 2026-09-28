# Table 5. Local latency, one decision at a time

Same Apple-silicon laptop (18 GB), the same frozen sample of 1,000 decisions, batch size 1, 20 warm-up decisions, timing from input formatting to probabilities. Devices differ by necessity (Julia-1's engine does not support MPS). Not comparable with hosted API latency.

| model | device | p50 (ms) | p95 (ms) | peak memory (GB) |
|---|---|---|---|---|
| JATOBÁ | mps | 40.0 | 60.3 | 2.22 |
| Laya multilingual | mps | 25.1 | 34.0 | 4.87 |
| Julia-1 | cpu | 22.6 | 34.2 | 2.28 |
