"""Laya (convaiinnovations/laya @ 55cf4c4e), evaluated with its own RLAgent.system_one code, as shipped.

Laya's build_sequence silently cuts options to 48 tokens, shrinks the option list when it exceeds the head budget, and
cuts the instruction and the state to the remaining room. A decision is scored only when none of these cuts happens;
otherwise it is N/A. `exact_fit` replicates that budget arithmetic.

    git clone https://huggingface.co/convaiinnovations/laya && git -C laya checkout 55cf4c4ebb4ebe31b2550e8bdf3bd21b99753851
"""

import importlib
import sys
from pathlib import Path

REVISION = "55cf4c4ebb4ebe31b2550e8bdf3bd21b99753851"
OPTION_TOKEN_CAP = 48
MIN_OPTION_BUDGET = 16


def load(root: Path, variant: str = "multilingual"):
    sys.path.insert(0, str(root))
    rl_common, api = importlib.import_module("rl_common"), importlib.import_module("rl_agent_api")
    return rl_common, api.RLAgent(str(root / variant))


def exact_fit(tokenizer, rl_common, state: str, question: dict, max_len: int, head_max_len: int) -> bool:
    criteria = question.get("criteria")
    if question["type"] == "choice" and isinstance(criteria, list):
        criteria = {c: None for c in criteria}
    internal = {"t": question["type"], "ins": question["instructions"], "crit": criteria}
    mask = tokenizer.mask_token
    count = lambda text: len(tokenizer(text, add_special_tokens=False)["input_ids"])  # noqa: E731
    option_lengths = [count(" " + o.replace(mask, " ")) for o in rl_common.render_options(internal)]
    options_total = sum(1 + min(n, OPTION_TOKEN_CAP) for n in option_lengths)
    option_budget = head_max_len - options_total
    head = count(f"{internal['t']} question: {str(internal['ins']).replace(mask, ' ')}")
    used = 1 + min(head, max(8, option_budget)) + 1 + options_total + 1
    room = max(0, max_len - used - 1)
    return (max(option_lengths) <= OPTION_TOKEN_CAP and option_budget >= MIN_OPTION_BUDGET
            and head <= max(8, option_budget) and count(state.replace(mask, " ")) <= room)


def ask(agent, state: str, question: dict) -> dict:
    return agent.system_one(state, {"q": question})["q"]
