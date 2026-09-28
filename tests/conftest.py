import zlib

import pytest
import torch


class ToyTokenizer:
    """Deterministic word-hash tokenizer. Mirrors NorBERTo in exposing CLS/SEP only as BOS/EOS."""

    cls_token_id = None
    sep_token_id = None
    bos_token_id, eos_token_id, pad_token_id = 1, 2, 0

    def __call__(self, text, add_special_tokens=False):
        return {"input_ids": [3 + zlib.crc32(w.encode()) % 90 for w in text.split()]}


@pytest.fixture(scope="session")
def tokenizer():
    return ToyTokenizer()


@pytest.fixture(scope="session")
def model():
    from transformers import ModernBertConfig, ModernBertModel

    from jatoba import JatobaModel

    torch.manual_seed(0)
    config = ModernBertConfig(vocab_size=100, hidden_size=64, intermediate_size=128, num_hidden_layers=2, num_attention_heads=2,
                              max_position_embeddings=512, pad_token_id=0, bos_token_id=1, eos_token_id=2, cls_token_id=1,
                              sep_token_id=2, global_attn_every_n_layers=1, reference_compile=False)
    model = JatobaModel(ModernBertModel(config))
    model.freeze_backbone()
    return model.eval()
