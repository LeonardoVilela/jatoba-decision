from dataclasses import dataclass
from pathlib import Path

import torch

from .decision import Decision, encode_batch
from .model import BACKBONE, BACKBONE_REVISION, JatobaModel

RELEASE_REPO = "leoabreu288/jatoba-decision"
# Per-primitive temperatures of the released v1.1 "M0" calibration. RAW (T = 1) is the primary output.
M0_TEMPERATURES = {"choice": 1.3990257637762193, "noul": 1.2062703558373884, "score": 0.8972051812186663}


@dataclass
class Result:
    probabilities: dict[str, float]
    expected_level: float | None  # SCORE only: sum_i i * p_i, levels indexed in the order given
    context_tokens: int
    truncated: bool


class Jatoba:
    def __init__(self, model: JatobaModel, tokenizer, device: str = "cpu", max_context_tokens: int = 256,
                 max_candidate_tokens: int = 96, truncation: str = "error"):
        backbone_max = int(getattr(model.encoder.config, "max_position_embeddings", 8192))
        if not 2 < max_context_tokens <= backbone_max:
            raise ValueError(f"max_context_tokens must be in (2, {backbone_max}]")
        self.model = model.to(device).eval()
        self.tokenizer = tokenizer
        self.device = device
        self.max_context_tokens = max_context_tokens
        self.max_candidate_tokens = max_candidate_tokens
        self.truncation = truncation

    @classmethod
    def from_pretrained(cls, repo: str | Path = RELEASE_REPO, revision: str | None = None, device: str = "cpu", **kwargs) -> "Jatoba":
        """Load the released model (frozen encoder + decision head) from a Hugging Face repository or a local directory."""
        from huggingface_hub import snapshot_download
        from safetensors.torch import load_file
        from transformers import AutoConfig, AutoModel, AutoTokenizer

        path = Path(repo)
        if not path.is_dir():
            path = Path(snapshot_download(str(repo), revision=revision, allow_patterns=["*.json", "*.safetensors"]))
        config = AutoConfig.from_pretrained(path)
        if hasattr(config, "reference_compile"):
            config.reference_compile = False
        model = JatobaModel(AutoModel.from_config(config))
        model.load_state_dict(load_file(path / "model.safetensors"), strict=True)
        model.freeze_backbone()
        return cls(model, AutoTokenizer.from_pretrained(path), device=device, **kwargs)

    @classmethod
    def from_checkpoint(cls, head_path: str | Path, device: str = "cpu", backbone: str = BACKBONE,
                        revision: str | None = BACKBONE_REVISION, **kwargs) -> "Jatoba":
        """Load the frozen backbone from the Hugging Face Hub and a decision-head state dict from `head_path`."""
        from transformers import AutoTokenizer

        model = JatobaModel.from_backbone(backbone, revision=revision)
        state = torch.load(head_path, map_location="cpu", weights_only=True)
        state = state.get("head_state", state)
        if any(name.startswith("encoder.") for name in state):
            raise ValueError("head checkpoint must not contain encoder weights")
        missing, unexpected = model.load_state_dict(state, strict=False)
        head_missing = [n for n in missing if not n.startswith("encoder.")]
        if head_missing or unexpected:
            raise ValueError(f"head checkpoint does not match the model: missing {head_missing}, unexpected {unexpected}")
        tokenizer = AutoTokenizer.from_pretrained(backbone, revision=revision)
        return cls(model, tokenizer, device=device, **kwargs)

    @torch.inference_mode()
    def decide_batch(self, decisions: list[Decision], calibrated: bool = False) -> list[Result]:
        batch, infos = encode_batch(self.tokenizer, decisions, self.max_context_tokens, self.max_candidate_tokens, self.truncation)
        logits = self.model({k: v.to(self.device) for k, v in batch.items()}).double().cpu()
        results = []
        for i, (decision, info) in enumerate(zip(decisions, infos)):
            k = len(decision.options)
            temperature = M0_TEMPERATURES[decision.kind] if calibrated else 1.0
            p = torch.softmax(logits[i, :k] / temperature, dim=-1)
            expected = float((torch.arange(k, dtype=p.dtype) * p).sum()) if decision.kind == "score" else None
            results.append(Result(dict(zip(decision.options, p.tolist())), expected, info["context_tokens"], info["truncated"]))
        return results

    def decide(self, state: str, question: str, options: dict[str, str], kind: str = "choice", calibrated: bool = False) -> Result:
        """Probabilities keyed by the caller's candidate ids, in the order the options were given."""
        return self.decide_batch([Decision(kind, state, question, options)], calibrated)[0]
