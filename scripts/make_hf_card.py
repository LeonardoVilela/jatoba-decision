"""Write the Hugging Face model card (hf/README.md) with every number read from results/.

    python scripts/make_hf_card.py
"""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GITHUB = "https://github.com/LeonardoVilela/jatoba-decision"
REPO = "leoabreu288/jatoba-decision"
BLOB = f"{GITHUB}/blob/release/jatoba-v1.1"


def load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def values() -> dict:
    four = load("results/data/pristine_four_model_common.json")["models"]
    k = {r["K"]: r for r in load("results/data/t2_massive_top1_vs_k.json")["rows"]}
    perm = load("results/data/julia_permutation.json")
    metrics = load("results/metrics.json")
    equivalence = load("docs/hf_release_equivalence.json")
    normas = metrics["normas_complete_1024"]["models"]
    jatoba_overview = load("results/data/model_overview.json")["rows"][0]["parameters"]
    match = re.match(r"([0-9.]+M) \(([0-9.]+M) trainable", jatoba_overview)
    assert match, jatoba_overview
    total, trainable = match.groups()
    return {
        "total": total, "trainable": trainable, "n_common": load("results/data/pristine_four_model_common.json")["records"],
        "ce_jatoba": four["NorDecision_RAW"]["hierarchical_ce_epsilon_group"], "ce_gliner": four["GLiNER"]["hierarchical_ce_epsilon_group"],
        "ce_laya": four["Laya_multilingual"]["hierarchical_ce_epsilon_group"], "ce_julia": four["Julia"]["hierarchical_ce_epsilon_group"],
        "k2": k[2]["NorDecision_RAW_top1_all"], "k60": k[60]["NorDecision_RAW_top1_all"], "k60_gliner": k[60]["GLiNER_top1"],
        "k_decisions": k[60]["decisions"],
        "flip_jatoba": perm["nordecision_v11_same_S1_records_same_orders"]["argmax_flip_rate"],
        "flip_julia": perm["julia"]["S1_PRISTINE_choice"]["argmax_flip_rate"],
        "flip_decisions": perm["julia"]["S1_PRISTINE_choice"]["decisions"], "flip_orders": perm["julia"]["S1_PRISTINE_choice"]["comparisons"],
        "normas_jatoba": normas["NorDecision_RAW"]["ce_epsilon"], "normas_uniform": normas["B0"]["ce_epsilon"],
        "eq_logit": max(b["T3_max_abs_logit_vs_frozen_logits"] for b in equivalence["smoke_set"].values()),
        "eq_n": sum(b["decisions"] for b in equivalence["smoke_set"].values()),
        "jevbench": metrics["jevbench_public"]["RAW/ALL"]["accuracy"], "jevbench_chance": metrics["jevbench_public"]["RAW/ALL"]["chance"],
    }


CARD = """---
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

Weights: **CC BY-NC-SA 4.0 (non-commercial)**. Code, methodology and full results: [GitHub]({github}). The historical internal development name was NorDecision.

![JATOBÁ results](jatoba_linkedin_main.png)

## Architecture

- **Encoder:** a frozen [NorBERTo-base](https://huggingface.co/Itau-Unibanco/NorBERTo-base) (ModernBERT) encodes the context once and each candidate separately.
- **Decision path:**
  - candidate→context cross-attention, then a fusion MLP;
  - a positionless candidate-set transformer (2 layers), so the output does not depend on candidate order;
  - a shared scorer and a softmax over the supplied options.
- **Size:** {total} parameters in total, of which {trainable} are the trained decision path.

Details: [architecture]({blob}/docs/architecture.md).

## Primitives

| primitive | question | options |
|---|---|---|
| CHOICE | which option answers the question? | K described options, variable K (evaluated 2–60) |
| NOUL | is this proposition true? | `false`, `true` |
| SCORE | which level of an ordered rubric? | ordered levels; the expected level is also returned |

## Key results

These are frozen evaluations of JATOBÁ v1.1, where every model received the same PT-BR payload. The source files are in [`results/`]({blob}/results).

| evaluation | metric | JATOBÁ | others |
|---|---|---|---|
| held-out examples of trained PT-BR families, common subset of all four models (N = {n_common:,}) | ε-CE ↓ | **{ce_jatoba:.3f}** | GLiNER {ce_gliner:.3f} · Laya {ce_laya:.3f} · Julia-1 {ce_julia:.3f} |
| MASSIVE PT-BR intent, K = 60 candidates ({k_decisions:,} decisions) | top-1 ↑ | **{k60:.3f}** (K = 2: {k2:.3f}) | GLiNER {k60_gliner:.3f} |
| candidate reordering, the same {flip_decisions} decisions and {flip_orders} reorderings | argmax flips ↓ | **{flip_jatoba:.0%}** | Julia-1 {flip_julia:.0%} |

Julia-1, GLiNER2.5-multi-Decide and Laya multilingual are models evaluated under JATOBÁ's protocol. These results say nothing general about them.

## Limitations

- **Specialization to the trained families:** strong results are on unseen *examples* of trained families. On a family never trained on, JATOBÁ is worse than a uniform guess in ε-CE (NormasTCU {normas_jatoba:.3f} vs uniform {normas_uniform:.3f}).
- **English near chance:** JevBench public items, accuracy {jevbench:.3f} vs chance {jevbench_chance:.3f}.
- **Rare toxicity labels:** weak.
- **Long contexts:** trained at 256 tokens. Semantic behaviour on long contexts is not established.
- **Large K:** the evidence for large candidate sets comes mostly from MASSIVE, which was exposed during development.
- **Non-commercial license:** see below.

Full list: [limitations]({blob}/docs/limitations.md).

## Research transparency

After v1.1 was frozen, several variants were tested under pre-registered gates, and none replaced it:
- label smoothing;
- focal loss;
- a contrastive auxiliary loss;
- a hard-negative curriculum;
- a larger NorBERTo encoder.

See the [research history]({blob}/docs/research_history.md).

## Usage

The code is on GitHub (Apache-2.0):

```bash
pip install "git+{github}.git@release/jatoba-v1.1"
```

```python
from jatoba import Jatoba

model = Jatoba.from_pretrained("{repo}")

result = model.decide(
    state="me acorda amanhã às sete, por favor",
    question="Qual categoria melhor descreve o pedido do usuário?",
    options={{
        "alarm_set": "criar alarme: definir um alarme para um horário",
        "weather_query": "consultar o tempo: perguntar a previsão do tempo, a temperatura ou as condições climáticas",
    }},
)
print(result.probabilities)
```

The rules of the interface:
- **Primitive:** `kind` is `"choice"` (default), `"noul"` (options exactly `false`, `true`) or `"score"` (levels from lowest to highest).
- **Context length:** contexts above 256 tokens raise an error unless an explicit truncation policy is passed.
- **Calibration:** `calibrated=True` applies the frozen per-primitive temperatures.

[`examples/basic.py`]({blob}/examples/basic.py) shows all three primitives.

## Files

| file | contents |
|---|---|
| `model.safetensors` | full JATOBÁ v1.1 weights: frozen NorBERTo-base encoder (unchanged) and trained decision head, float32 |
| `config.json`, `tokenizer*.json`, `special_tokens_map.json` | NorBERTo-base configuration and tokenizer at revision `db73446f` |
| `jatoba_config.json` | JATOBÁ settings, provenance and hashes |
| `LICENSE_MODEL.md`, `ATTRIBUTIONS.md` | model license and credits |

The weights are the frozen v1.1 checkpoint converted to safetensors, with no retraining or quantization. The equivalence check found all tensors bitwise-identical, and the logits reproduce the frozen v1.1 outputs (max difference {eq_logit:.1e}, 0 top-1 changes over {eq_n} decisions). See [`docs/hf_release_manifest.json`]({blob}/docs/hf_release_manifest.json).

## Documentation

- [Benchmark methodology]({blob}/docs/methodology.md)
- [Benchmark card]({blob}/benchmark/BENCHMARK_CARD.md)
- [Adapter audit]({blob}/benchmark/ADAPTER_AUDIT.md)
- [Reproducibility]({blob}/docs/reproducibility.md)
- [Limitations]({blob}/docs/limitations.md)
- [Launch figure: data and caption]({blob}/results/figures/linkedin_main_caption.md)

## License

- **Weights:** CC BY-NC-SA 4.0 (`LICENSE_MODEL.md`). NorBERTo-base, which they include, is also CC BY-NC-SA 4.0. Commercial use is not permitted.
- **Datasets:** the training datasets retain their upstream terms (`ATTRIBUTIONS.md`). ASSIN 2 was released publicly for the research community and used as a shared-task training resource, but an explicit corpus license was not located. Users are responsible for reviewing upstream terms for their intended use. See the [license audit]({blob}/docs/final_weight_license_audit.md).
- **Code:** the GitHub code is separately Apache-2.0.

## Citation

JATOBÁ, Leonardo Vilela, 2026. {github}. Please also cite NorBERTo and the datasets listed in `ATTRIBUTIONS.md`.
"""


def main() -> None:
    (ROOT / "hf").mkdir(exist_ok=True)
    (ROOT / "hf/README.md").write_text(CARD.format(github=GITHUB, blob=BLOB, repo=REPO, **values()), encoding="utf-8")
    attributions = (ROOT / "ATTRIBUTIONS.md").read_text(encoding="utf-8")
    attributions = attributions.replace("(docs/final_weight_license_audit.md)", f"({BLOB}/docs/final_weight_license_audit.md)")
    (ROOT / "hf/ATTRIBUTIONS.md").write_text(attributions, encoding="utf-8")


if __name__ == "__main__":
    main()
