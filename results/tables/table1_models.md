# Table 1. Evaluated models

| model | parameters | language focus | primitives | native max K | candidate order | probabilities | context |
|---|---|---|---|---|---|---|---|
| JATOBÁ v1.1 | 169.1M (20.1M trainable; frozen NorBERTo-base) | PT-BR | NOUL, CHOICE, SCORE | no fixed limit; evaluated up to 60 | permutation-equivariant by construction; 0 flips measured | full softmax | 256 tokens in training/evaluation; inference path runs to 8,192 (semantics not validated) |
| Laya multilingual (convaiinnovations/laya @ 55cf4c4e) | 321.9M | multilingual | NOUL, CHOICE, SCORE | bounded by its head token budget (N/A from K = 16 on MASSIVE) | not measured | full distribution | shared token budget; decisions that would be cut are N/A |
| GLiNER2.5-multi-Decide (fastino @ 6bc1d43d) | 287.4M | multilingual | CHOICE, SCORE (NOUL as yes/no) | no fixed limit; evaluated up to 60 | not measured systematically (unchanged on smoke items) | softmax over declared labels | 4,096 sub-words |
| Julia-1 (SupersonicLabs @ a85b1273) | 144.3M | multilingual | NOUL, CHOICE, SCORE | 2-20 | order-sensitive: 20-60% top-1 flips under reordering | full softmax | 8,192 tokens; options at most 48 tokens |
| Jev (typesafe-ai/jev, hosted API) | undisclosed | multilingual | NOUL, CHOICE, SCORE | not documented | not measured | probabilities rounded to 0.01 | hosted; coverage in this study PARTIAL |
