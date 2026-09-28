"""Different numbers of candidates in one batch, and why candidate order does not matter.

    python examples/variable_k.py [hugging-face-repo-or-local-dir]
"""

import sys

import torch

from jatoba import Decision, Jatoba
from jatoba.decision import encode_batch

jatoba = Jatoba.from_pretrained(*sys.argv[1:2])

intents = {
    "alarm_set": "criar alarme: definir um alarme para um horário",
    "alarm_query": "consultar alarmes: perguntar quais alarmes estão definidos",
    "weather_query": "consultar o tempo: perguntar a previsão do tempo, a temperatura ou as condições climáticas",
    "play_music": "tocar música: tocar uma música, um artista, um álbum ou uma playlist",
    "calendar_set": "criar evento ou lembrete: marcar um compromisso ou criar um lembrete na agenda",
}
state, question = "me acorda amanhã às sete, por favor", "Qual categoria melhor descreve o pedido do usuário?"
small = Decision("choice", state, question, dict(list(intents.items())[:2]))
large = Decision("choice", state, question, intents)
for result in jatoba.decide_batch([small, large]):
    print(len(result.probabilities), "candidates:", {k: round(v, 3) for k, v in result.probabilities.items()})

# Present the five options in reverse. Candidates have no position embedding and interact through a
# positionless set transformer, so each candidate keeps its probability.
batch, _ = encode_batch(jatoba.tokenizer, [large, large], orders=[[0, 1, 2, 3, 4], [4, 3, 2, 1, 0]])
with torch.inference_mode():
    p = torch.softmax(jatoba.model({k: v.to(jatoba.device) for k, v in batch.items()}).double(), -1)
print("max |p(original) - p(reversed)| =", float((p[0] - p[1].flip(0)).abs().max()))
