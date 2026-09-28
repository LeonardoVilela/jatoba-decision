# Adapter audit: how each dataset becomes typed decisions

This audit was written from the transforms in `benchmark/transforms.py`, which were ported from the frozen research code. The transforms reproduce every frozen record: `scripts/build_benchmark.py` rebuilt all 212,000+ decisions (evaluation blocks and training roles) from upstream at the pinned revisions, with 0 missing ids and 0 content-hash mismatches.

**Transformation types:**
- **DIRECT:** the upstream label becomes the target of an equivalent decision.
- **SEMANTIC_REFORMULATION:** the upstream task is re-expressed as a different primitive or target form.
- **DERIVED_CANDIDATE_SET:** the candidate set itself is constructed by us.

**Shared rules:**
- Every state is the upstream text verbatim, unless a state template is shown.
- Every question comes from the frozen dictionary where it defines one, and otherwise from the adapter.
- Candidate descriptions are listed in `CANDIDATE_DESCRIPTIONS.md`.

## Mapping table

| Dataset | Original task | Source fields | Primitive | State | Question | Candidates | Target | Group key | Type |
|---|---|---|---|---|---|---|---|---|---|
| MASSIVE pt-BR | intent classification (60 intents) | `utt_br` (or `utt`), `intent` (official integer id) | CHOICE, K = 60 (nested subsets K = 2..60 for the K curve) | utterance | "Qual categoria melhor descreve o pedido do usuário?" | 60 project-authored intent descriptions, official intent order | one-hot of the gold intent | union of base id and normalized utterance | SEMANTIC_REFORMULATION + DERIVED_CANDIDATE_SET (K subsets) |
| ASSIN 2 | entailment (entailment vs none) | `premise`, `hypothesis`, `entailment_judgment` | NOUL | `Premissa: … \nHipótese: …` | "A hipótese decorre da premissa?" | not entailed / entailed | one-hot (1 = entailment) | official pair number within its split | DIRECT |
| ASSIN 2 | semantic similarity (continuous 1–5) | same + `relatedness_score` | SCORE, 5 levels | same | "Qual é o nível de similaridade semântica entre premissa e hipótese?" | the five guideline levels, low → high | mass split between the two neighbouring levels so that the expected level equals the gold score | same | SEMANTIC_REFORMULATION |
| InferBR | 3-way NLI | `premise`, `hypothesis`, `label` (ClassLabel names at the pinned revision) | CHOICE, K = 3 | `Premissa: … \nHipótese: …` | "Qual é a relação entre a premissa e a hipótese?" | implicação, neutro, contradição | one-hot | premise (official train/val share premises, so roles are premise-grouped) | DIRECT |
| ToLD-Br | six binary toxicity properties, three annotators each | `text`, `{property}_1..3` | NOUL, one decision per property | tweet text | "Este conteúdo apresenta {property}?" | generic false/true texts | share of the three annotators who flagged the property (0, 1/3, 2/3, 1) | text | SEMANTIC_REFORMULATION (annotator distribution) |
| HateBR | offensive comment, three annotators | `comentario`, `anotator1..3` | NOUL | comment text | "Este conteúdo apresenta linguagem ofensiva?" | generic false/true texts | share of the three annotators | text | SEMANTIC_REFORMULATION (annotator distribution) |
| BRIGHTER (ptbr) | emotion intensity 0–3 for six emotions | `text`, `anger` … `surprise` | SCORE, 4 levels, six decisions per text | text | "Qual é a intensidade de {emoção} expressa no texto?" | generic ausente / baixa / moderada / alta rubric | one-hot of the author-aggregated level | normalized text (the six decisions share one group) | DIRECT |
| Community Alignment (pt, first turn) | human preference among four responses | prompt, responses a–d, preferred slot, annotator id | CHOICE, K = 4 | first-turn prompt | "Qual das respostas é a melhor para a mensagem do usuário?" | the four responses verbatim; id = hash of the text, never the A–D slot | pooled votes on the identical prompt + response set, one vote per annotator (soft when several annotators voted) | normalized prompt | SEMANTIC_REFORMULATION |
| NormasTCU | graded relevance of norm to query (0/1/2), several raters | query, document title/subject/text, raw human votes | SCORE, 3 levels | `Consulta: {query}\nDocumento: {title}. {subject}. {text}` (HTML stripped) | "Qual é o grau de relevância do documento para a consulta?" | three relevance levels (translated paper definitions) | distribution of raw human votes | query | SEMANTIC_REFORMULATION |
| JurisTCU | graded relevance of precedent to query (0–3) | query, `ENUNCIADO`, qrel score | SCORE, 4 levels | `Consulta: {query}\nDocumento: {enunciado}` (HTML stripped) | same | four relevance levels (verbatim paper prompt) | one-hot of the released score | query | SEMANTIC_REFORMULATION |
| FaQuAD | extractive QA | question, paragraph, first answer span | CHOICE over the paragraph's sentences (2–60 allowed; 2–10 in the released block) | the question | "Qual frase do texto contém a resposta à pergunta?" | the paragraph's sentences (deterministic regex split) | one-hot of the sentence containing the answer span | article title | DERIVED_CANDIDATE_SET |

## Findings

No mapping was found to be invalid, so no result is blocked. These caveats travel with the results:

1. **MASSIVE descriptions are project-authored.** Ten were revised after reading TRAIN utterances, and some add disambiguating clauses. See `CANDIDATE_DESCRIPTIONS.md`. MASSIVE is reported only as LEGACY / previously exposed.
2. **ASSIN 2 similarity targets carry float32 artifacts** from the upstream parquet (e.g. 0.20000004768…). They are kept, because the frozen results used them.
3. **ToLD-Br and HateBR targets are coarse annotator shares from three raters.** They are not calibrated probabilities of toxicity. HateBR's `label_final` is not used.
4. **Community Alignment keeps only sets whose four responses fit 384 tokens** (1,798 of 8,409 sets excluded). This favours shorter responses. Response slots A–D carry a strong position bias upstream, which is why candidates are identified by text, not slot.
5. **JurisTCU relevance labels were produced by GPT-4 judging and confirmed by experts** (per the JurisTCU paper). They are not independent human ratings.
6. **Normas and Juris states concatenate the query and a long legal document.** The trained model saw at most 256 context tokens; the family-shift results use the frozen evaluation budgets (see `docs/methodology.md`).
7. **FaQuAD evidence sentences come from a regex sentence split.** Questions whose answer crosses a sentence boundary are skipped.
8. **InferBR's official train and validation splits share 586 premises.** Roles are therefore assigned by premise group, never by the official split.

## Validation tests

`tests/test_benchmark.py` runs each transform on hand-made upstream rows and checks:
- the gold label lands on the expected candidate id;
- targets sum to 1;
- SCORE levels stay ordered;
- no description is empty;
- candidate ids are unique;
- group keys exist;
- role manifests are group-disjoint.

`scripts/verify_release.py` also writes `adapter_audit.json` after a local build. It runs structural checks over every rebuilt decision:
- targets are distributions;
- candidate ids are unique, and NOUL candidates are exactly `false`, `true`;
- no state, question or description is empty;
- every decision has a group and a family.

It also records primitive counts, K range and soft-target counts per block. It contains no upstream text. For this release it reported no problems in any of the 5 evaluation blocks or 3 training roles.
