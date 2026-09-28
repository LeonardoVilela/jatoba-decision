"""The three primitives through the public API.

    python examples/basic.py [hugging-face-repo-or-local-dir]
"""

import sys

from jatoba import Jatoba

model = Jatoba.from_pretrained(*sys.argv[1:2])

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
