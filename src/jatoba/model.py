import torch
from torch import nn

BACKBONE = "Itau-Unibanco/NorBERTo-base"
BACKBONE_REVISION = "db73446f89c96044863ea05a39f680524b84bccb"


class JatobaModel(nn.Module):
    """Frozen encoder + decision head. Submodule names match the released v1.1 checkpoint and must not change."""

    def __init__(self, encoder: nn.Module, set_layers: int = 2, dropout: float = 0.1):
        super().__init__()
        self.encoder = encoder
        hidden = int(encoder.config.hidden_size)
        heads = max(1, hidden // 64)

        self.cross_query_norm = nn.LayerNorm(hidden)
        self.cross_context_norm = nn.LayerNorm(hidden)
        self.cross_attention = nn.MultiheadAttention(hidden, heads, dropout=dropout, batch_first=True)
        self.cross_dropout = nn.Dropout(dropout)
        self.cross_output_norm = nn.LayerNorm(hidden)

        self.primitive_embedding = nn.Embedding(3, hidden)
        self.fusion = nn.Sequential(
            nn.Linear(5 * hidden, hidden),
            nn.GELU(),
            nn.Linear(hidden, hidden),
            nn.LayerNorm(hidden),
        )
        # No positional encoding: the set transformer is permutation-equivariant over candidates.
        layer = nn.TransformerEncoderLayer(hidden, heads, dim_feedforward=4 * hidden, dropout=dropout, batch_first=True, norm_first=True)
        self.set_transformer = nn.TransformerEncoder(layer, set_layers, enable_nested_tensor=False)
        self.scorer = nn.Linear(hidden, 1)

    @classmethod
    def from_backbone(cls, name: str = BACKBONE, revision: str | None = BACKBONE_REVISION, **kwargs) -> "JatobaModel":
        from transformers import AutoModel

        encoder = AutoModel.from_pretrained(name, revision=revision, **kwargs)
        if hasattr(encoder.config, "reference_compile"):
            encoder.config.reference_compile = False
        model = cls(encoder)
        model.freeze_backbone()
        return model

    def freeze_backbone(self) -> None:
        for parameter in self.encoder.parameters():
            parameter.requires_grad_(False)
        self.encoder.eval()

    def train(self, mode: bool = True) -> "JatobaModel":
        super().train(mode)
        if not any(p.requires_grad for p in self.encoder.parameters()):
            self.encoder.eval()  # a frozen encoder never runs in training mode
        return self

    def encode(self, input_ids: torch.Tensor, attention_mask: torch.Tensor) -> torch.Tensor:
        return self.encoder(input_ids=input_ids, attention_mask=attention_mask).last_hidden_state

    @staticmethod
    def _masked_mean(hidden: torch.Tensor, mask: torch.Tensor) -> torch.Tensor:
        weights = mask.to(hidden.dtype).unsqueeze(-1)
        return (hidden * weights).sum(dim=1) / weights.sum(dim=1).clamp_min(1)

    def forward(self, batch: dict[str, torch.Tensor]) -> torch.Tensor:
        """Return one logit per (decision, candidate slot); padded slots are set to the dtype minimum."""
        context = self.encode(batch["context_input_ids"], batch["context_attention_mask"])
        candidates = self.encode(batch["candidate_input_ids"], batch["candidate_attention_mask"])
        return self.head(context, candidates, batch)

    def head(self, context: torch.Tensor, candidates: torch.Tensor, batch: dict[str, torch.Tensor]) -> torch.Tensor:
        context_mask = batch["context_attention_mask"]
        candidate_mask = batch["candidate_attention_mask"]
        owner = batch["candidate_to_example"]
        slots = batch["candidate_slots"]
        set_mask = batch["candidate_mask"]

        # Each candidate's tokens attend to the tokens of its own decision's context. The context is copied once
        # per candidate, so memory grows with K x context length.
        paired_context = context[owner]
        attended, _ = self.cross_attention(
            self.cross_query_norm(candidates),
            self.cross_context_norm(paired_context),
            self.cross_context_norm(paired_context),
            key_padding_mask=~context_mask[owner].bool(),
            need_weights=False,
        )
        conditioned = self.cross_output_norm(candidates + self.cross_dropout(attended))
        conditioned = conditioned.masked_fill(~candidate_mask.bool().unsqueeze(-1), 0)

        candidate_vec = self._masked_mean(conditioned, candidate_mask)
        context_vec = self._masked_mean(context, context_mask)[owner]
        primitive = self.primitive_embedding(batch["primitive_ids"][owner])
        fused = self.fusion(torch.cat([candidate_vec, context_vec, candidate_vec * context_vec,
                                       torch.abs(candidate_vec - context_vec), primitive], dim=-1))

        sets = fused.new_zeros((*set_mask.shape, fused.shape[-1]))
        sets[owner, slots] = fused
        interacted = self.set_transformer(sets, src_key_padding_mask=~set_mask)
        logits = self.scorer(interacted).squeeze(-1).float()
        return logits.masked_fill(~set_mask, torch.finfo(logits.dtype).min)
