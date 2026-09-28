"""The three primitives through the public API.

    python examples/basic.py [path/to/head.pt]

Without a head checkpoint the decision head is randomly initialised: the code path is real, the probabilities are not.
"""

import sys

from transformers import AutoTokenizer

from jatoba import Jatoba, JatobaModel
from jatoba.model import BACKBONE, BACKBONE_REVISION

if len(sys.argv) > 1:
    model = Jatoba.from_checkpoint(sys.argv[1])
else:
    print("no head checkpoint given: random decision head, outputs are meaningless\n")
    tokenizer = AutoTokenizer.from_pretrained(BACKBONE, revision=BACKBONE_REVISION)
    model = Jatoba(JatobaModel.from_backbone(), tokenizer)

choice = model.decide(
    state="me acorda amanhã às sete, por favor",
    question="Qual categoria melhor descreve o pedido do usuário?",
    options={
        "alarm_set": "criar alarme: definir um alarme para um horário",
        "alarm_query": "consultar alarmes: perguntar quais alarmes estão definidos",
        "weather_query": "consultar o tempo: perguntar a previsão do tempo, a temperatura ou as condições climáticas",
    },
)
print("CHOICE", choice.probabilities)

noul = model.decide(
    state="Premissa: O menino está jogando bola no parque.\nHipótese: Uma criança está brincando ao ar livre.",
    question="A hipótese decorre da premissa?",
    options={"false": "Não — a hipótese não é implicada pela premissa.", "true": "Sim — a hipótese é implicada pela premissa."},
    kind="noul",
)
print("NOUL", noul.probabilities)

score = model.decide(
    state="Estou furioso! Nunca mais compro aqui.",
    question="Qual é a intensidade de raiva expressa no texto?",
    options={
        "ausente": "Nível ordinal 0: ausente. a emoção não está presente",
        "baixa": "Nível ordinal 1: baixa. a emoção está presente com baixa intensidade",
        "moderada": "Nível ordinal 2: moderada. a emoção está presente com intensidade moderada",
        "alta": "Nível ordinal 3: alta. a emoção está presente com alta intensidade",
    },
    kind="score",
)
print("SCORE", score.probabilities, "expected level", round(score.expected_level, 3))
