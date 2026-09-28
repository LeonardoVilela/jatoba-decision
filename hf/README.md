---
license: cc-by-nc-sa-4.0
language:
- pt
tags:
- portuguese
- pt-br
- encoder
- modernbert
- classification
- decision-model
- probabilistic-classification
- non-generative
base_model:
- Itau-Unibanco/NorBERTo-base
datasets:
- Magurofg/massive-pt-br
- nilc-nlp/assin2
- hapaxlegomenon/InferBR
- JAugusto97/told-br
- franciellevargas/HateBR
- brighter-dataset/BRIGHTER-emotion-intensities
- facebook/community-alignment-dataset
---

# JATOBÁ

**Joint Assessment of Typed Options with BERT Architecture**

A compact, non-generative model for typed probabilistic decisions in Brazilian Portuguese:

```text
context + question + described options  →  probability distribution over the options
```

Weights: **CC BY-NC-SA 4.0 (non-commercial)**. Code, methodology and full results: [GitHub](https://github.com/LeonardoVilela/jatoba-decision). The historical internal development name was NorDecision.

![JATOBÁ results](jatoba_linkedin_main.png)

## Architecture

- **Encoder:** a frozen [NorBERTo-base](https://huggingface.co/Itau-Unibanco/NorBERTo-base) (ModernBERT) encodes the context once and each candidate separately.
- **Decision path:**
  - candidate→context cross-attention, then a fusion MLP;
  - a positionless candidate-set transformer (2 layers), so the output does not depend on candidate order;
  - a shared scorer and a softmax over the supplied options.
- **Size:** 169.1M parameters in total, of which 20.1M are the trained decision path.

Details: [architecture](https://github.com/LeonardoVilela/jatoba-decision/blob/release/jatoba-v1.1/docs/architecture.md).

## Primitives

| primitive | question | options |
|---|---|---|
| CHOICE | which option answers the question? | K described options, variable K (evaluated 2–60) |
| NOUL | is this proposition true? | `false`, `true` |
| SCORE | which level of an ordered rubric? | ordered levels; the expected level is also returned |

## Key results

These are frozen evaluations of JATOBÁ v1.1, where every model received the same PT-BR payload. The source files are in [`results/`](https://github.com/LeonardoVilela/jatoba-decision/blob/release/jatoba-v1.1/results).

| evaluation | metric | JATOBÁ | others |
|---|---|---|---|
| held-out examples of trained PT-BR families, common subset of all four models (N = 15,025) | ε-CE ↓ | **0.508** | GLiNER 1.291 · Laya 1.381 · Julia-1 2.745 |
| MASSIVE PT-BR intent, K = 60 candidates (2,901 decisions) | top-1 ↑ | **0.785** (K = 2: 0.989) | GLiNER 0.289 |
| candidate reordering, the same 22 decisions and 88 reorderings | argmax flips ↓ | **0%** | Julia-1 45% |

Julia-1, GLiNER2.5-multi-Decide and Laya multilingual are models evaluated under JATOBÁ's protocol. These results say nothing general about them.

## Limitations

- **Specialization to the trained families:** strong results are on unseen *examples* of trained families. On a family never trained on, JATOBÁ is worse than a uniform guess in ε-CE (NormasTCU 1.701 vs uniform 1.099).
- **English near chance:** JevBench public items, accuracy 0.329 vs chance 0.318.
- **Rare toxicity labels:** weak.
- **Long contexts:** trained at 256 tokens. Semantic behaviour on long contexts is not established.
- **Large K:** the evidence for large candidate sets comes mostly from MASSIVE, which was exposed during development.
- **Non-commercial license:** see below.

Full list: [limitations](https://github.com/LeonardoVilela/jatoba-decision/blob/release/jatoba-v1.1/docs/limitations.md).

## Research transparency

After v1.1 was frozen, several variants were tested under pre-registered gates, and none replaced it:
- label smoothing;
- focal loss;
- a contrastive auxiliary loss;
- a hard-negative curriculum;
- a larger NorBERTo encoder.

See the [research history](https://github.com/LeonardoVilela/jatoba-decision/blob/release/jatoba-v1.1/docs/research_history.md).

## Usage

The code is on GitHub (Apache-2.0):

```bash
pip install "git+https://github.com/LeonardoVilela/jatoba-decision.git@release/jatoba-v1.1"
```

```python
from jatoba import Jatoba

model = Jatoba.from_pretrained("leoabreu288/jatoba-decision")

result = model.decide(
    state="me acorda amanhã às sete, por favor",
    question="Qual categoria melhor descreve o pedido do usuário?",
    options={
        "alarm_set": "criar alarme: definir um alarme para um horário",
        "weather_query": "consultar o tempo: perguntar a previsão do tempo, a temperatura ou as condições climáticas",
    },
)
print(result.probabilities)
```

The rules of the interface:
- **Primitive:** `kind` is `"choice"` (default), `"noul"` (options exactly `false`, `true`) or `"score"` (levels from lowest to highest).
- **Context length:** contexts above 256 tokens raise an error unless an explicit truncation policy is passed.
- **Calibration:** `calibrated=True` applies the frozen per-primitive temperatures.

[`examples/basic.py`](https://github.com/LeonardoVilela/jatoba-decision/blob/release/jatoba-v1.1/examples/basic.py) shows all three primitives.

## Files

| file | contents |
|---|---|
| `model.safetensors` | full JATOBÁ v1.1 weights: frozen NorBERTo-base encoder (unchanged) and trained decision head, float32 |
| `config.json`, `tokenizer*.json`, `special_tokens_map.json` | NorBERTo-base configuration and tokenizer at revision `db73446f` |
| `jatoba_config.json` | JATOBÁ settings, provenance and hashes |
| `LICENSE_MODEL.md`, `ATTRIBUTIONS.md` | model license and credits |

The weights are the frozen v1.1 checkpoint converted to safetensors, with no retraining or quantization. The equivalence check found all tensors bitwise-identical, and the logits reproduce the frozen v1.1 outputs (max difference 4.8e-05, 0 top-1 changes over 320 decisions). See [`docs/hf_release_manifest.json`](https://github.com/LeonardoVilela/jatoba-decision/blob/release/jatoba-v1.1/docs/hf_release_manifest.json).

## Documentation

- [Benchmark methodology](https://github.com/LeonardoVilela/jatoba-decision/blob/release/jatoba-v1.1/docs/methodology.md)
- [Benchmark card](https://github.com/LeonardoVilela/jatoba-decision/blob/release/jatoba-v1.1/benchmark/BENCHMARK_CARD.md)
- [Adapter audit](https://github.com/LeonardoVilela/jatoba-decision/blob/release/jatoba-v1.1/benchmark/ADAPTER_AUDIT.md)
- [Reproducibility](https://github.com/LeonardoVilela/jatoba-decision/blob/release/jatoba-v1.1/docs/reproducibility.md)
- [Limitations](https://github.com/LeonardoVilela/jatoba-decision/blob/release/jatoba-v1.1/docs/limitations.md)
- [Launch figure: data and caption](https://github.com/LeonardoVilela/jatoba-decision/blob/release/jatoba-v1.1/results/figures/linkedin_main_caption.md)

## License

- **Weights:** CC BY-NC-SA 4.0 (`LICENSE_MODEL.md`). NorBERTo-base, which they include, is also CC BY-NC-SA 4.0. Commercial use is not permitted.
- **Datasets:** the training datasets retain their upstream terms (`ATTRIBUTIONS.md`). ASSIN 2 was released publicly for the research community and used as a shared-task training resource, but an explicit corpus license was not located. Users are responsible for reviewing upstream terms for their intended use. See the [license audit](https://github.com/LeonardoVilela/jatoba-decision/blob/release/jatoba-v1.1/docs/final_weight_license_audit.md).
- **Code:** the GitHub code is separately Apache-2.0.

## Citation

JATOBÁ, Leonardo Vilela, 2026. https://github.com/LeonardoVilela/jatoba-decision. Please also cite NorBERTo and the datasets listed in `ATTRIBUTIONS.md`.
