from dataclasses import dataclass

import torch

PRIMITIVES = {"choice": 0, "score": 1, "noul": 2}  # ids of the primitive embedding in the released checkpoint

# Frozen prompt text. Changing any character changes the model input distribution.
INSTRUCTIONS = {
    "choice": "Escolha a alternativa que responde à pergunta.",
    "noul": "Avalie se a afirmação é verdadeira ou falsa.",
    "score": "Avalie a distribuição entre os níveis ordinais descritos.",
}

TRUNCATION_POLICIES = ("error", "keep_start", "keep_end")


class ContextTooLong(ValueError):
    pass


@dataclass(frozen=True)
class Decision:
    """One typed decision. `options` maps candidate id -> candidate description, in presentation order.

    SCORE options must be listed from the lowest to the highest level. NOUL options must be exactly
    {"false": ..., "true": ...} in that order.
    """

    kind: str
    state: str
    question: str
    options: dict[str, str]

    def __post_init__(self):
        if self.kind not in PRIMITIVES:
            raise ValueError(f"kind must be one of {sorted(PRIMITIVES)}")
        if len(self.options) < 2:
            raise ValueError("a decision needs at least two options")
        if self.kind == "noul" and list(self.options) != ["false", "true"]:
            raise ValueError('NOUL options must be exactly "false", "true" in that order')
        if any(not str(text).strip() for text in self.options.values()):
            raise ValueError("candidate descriptions must not be empty")


def special_ids(tokenizer) -> tuple[int, int, int]:
    # NorBERTo's tokenizer exposes CLS/SEP as BOS/EOS; the frozen collator fell back the same way.
    cls = tokenizer.cls_token_id if tokenizer.cls_token_id is not None else tokenizer.bos_token_id
    sep = tokenizer.sep_token_id if tokenizer.sep_token_id is not None else tokenizer.eos_token_id
    return cls, sep, tokenizer.pad_token_id


def _encode(tokenizer, text: str) -> list[int]:
    return list(tokenizer(text, add_special_tokens=False)["input_ids"])


def context_ids(tokenizer, decision: Decision, max_tokens: int, truncation: str = "error") -> tuple[list[int], dict]:
    """[CLS] instruction + question [SEP] state [SEP]. The state is only shortened if the caller asked for it."""
    if truncation not in TRUNCATION_POLICIES:
        raise ValueError(f"truncation must be one of {TRUNCATION_POLICIES}")
    cls, sep, _ = special_ids(tokenizer)
    prefix = [cls, *_encode(tokenizer, f"{INSTRUCTIONS[decision.kind]} Pergunta: {decision.question}"), sep]
    state = _encode(tokenizer, decision.state)
    needed = len(prefix) + len(state) + 1
    room = max_tokens - len(prefix) - 1
    info = {"context_tokens": needed, "truncated": False, "truncation": truncation}
    if needed > max_tokens:
        if truncation == "error" or room < 1:
            raise ContextTooLong(f"context needs {needed} tokens, max_context_tokens is {max_tokens}")
        state = state[:room] if truncation == "keep_start" else state[-room:]
        info.update(context_tokens=max_tokens, truncated=True, dropped_tokens=needed - max_tokens)
    return [*prefix, *state, sep], info


def candidate_ids(tokenizer, description: str, max_tokens: int) -> list[int]:
    cls, sep, _ = special_ids(tokenizer)
    ids = [cls, *_encode(tokenizer, description), sep]
    if len(ids) > max_tokens:
        raise ValueError(f"candidate has {len(ids)} tokens > {max_tokens}; candidates are never truncated")
    return ids


def _pad(sequences: list[list[int]], pad_id: int) -> tuple[torch.Tensor, torch.Tensor]:
    width = max(map(len, sequences))
    ids = torch.full((len(sequences), width), pad_id, dtype=torch.long)
    mask = torch.zeros_like(ids)
    for row, seq in enumerate(sequences):
        ids[row, :len(seq)] = torch.tensor(seq)
        mask[row, :len(seq)] = 1
    return ids, mask


def encode_batch(tokenizer, decisions: list[Decision], max_context_tokens: int = 256, max_candidate_tokens: int = 96,
                 truncation: str = "error", orders: list[list[int]] | None = None) -> tuple[dict[str, torch.Tensor], list[dict]]:
    """Tensors for JatobaModel.forward. `orders[i]` optionally presents decision i's options in another order
    (slot j holds option orders[i][j]); probabilities are always reported back per candidate id."""
    contexts, infos, candidates, owner, slots = [], [], [], [], []
    width = max(len(d.options) for d in decisions)
    set_mask = torch.zeros((len(decisions), width), dtype=torch.bool)
    for i, decision in enumerate(decisions):
        ids, info = context_ids(tokenizer, decision, max_context_tokens, truncation)
        contexts.append(ids)
        infos.append(info)
        texts = list(decision.options.values())
        order = orders[i] if orders else range(len(texts))
        for slot, index in enumerate(order):
            candidates.append(candidate_ids(tokenizer, texts[index], max_candidate_tokens))
            owner.append(i)
            slots.append(slot)
            set_mask[i, slot] = True
    pad = special_ids(tokenizer)[2]
    context, context_mask = _pad(contexts, pad)
    candidate, candidate_mask = _pad(candidates, pad)
    batch = {
        "context_input_ids": context, "context_attention_mask": context_mask,
        "candidate_input_ids": candidate, "candidate_attention_mask": candidate_mask,
        "candidate_to_example": torch.tensor(owner), "candidate_slots": torch.tensor(slots),
        "candidate_mask": set_mask, "primitive_ids": torch.tensor([PRIMITIVES[d.kind] for d in decisions]),
    }
    return batch, infos
