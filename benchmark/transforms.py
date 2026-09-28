"""Frozen transformations from upstream rows to typed decisions.

Each function yields plain dicts: id, source, task, family, type, state, question, options [[id, description], ...],
target. Candidate descriptions come from candidate_dictionary.json (frozen; do not edit without a new benchmark
version). Record ids and field formats reproduce the frozen evaluation files byte-for-byte; see manifests/.
"""

import hashlib
import json
import re
import unicodedata
from collections import Counter, defaultdict
from html import unescape
from html.parser import HTMLParser
from pathlib import Path

DICTIONARY = json.loads((Path(__file__).parent / "candidate_dictionary.json").read_text())["tasks"]

# Official AmazonScience/massive _INTENTS order; Magurofg/massive-pt-br keeps these integer ids without names.
MASSIVE_INTENTS = (
    "datetime_query", "iot_hue_lightchange", "transport_ticket", "takeaway_query", "qa_stock", "general_greet",
    "recommendation_events", "music_dislikeness", "iot_wemo_off", "cooking_recipe", "qa_currency", "transport_traffic",
    "general_quirky", "weather_query", "audio_volume_up", "email_addcontact", "takeaway_order", "email_querycontact",
    "iot_hue_lightup", "recommendation_locations", "play_audiobook", "lists_createoradd", "news_query", "alarm_query",
    "iot_wemo_on", "general_joke", "qa_definition", "social_query", "music_settings", "audio_volume_other", "calendar_remove",
    "iot_hue_lightdim", "calendar_query", "email_sendemail", "iot_cleaning", "audio_volume_down", "play_radio",
    "cooking_query", "datetime_convert", "qa_maths", "iot_hue_lightoff", "iot_hue_lighton", "transport_query",
    "music_likeness", "email_query", "play_music", "audio_volume_mute", "social_post", "alarm_set", "qa_factoid",
    "calendar_set", "play_game", "alarm_remove", "lists_remove", "transport_taxi", "recommendation_movies", "iot_coffee",
    "music_query", "play_podcasts", "lists_query",
)
TOLD_DIMENSIONS = {"homophobia": "LGBTQ+fobia", "obscene": "linguagem obscena", "insult": "insulto", "racism": "racismo",
                   "misogyny": "misoginia", "xenophobia": "xenofobia"}
EMOTIONS = {"anger": "raiva", "disgust": "nojo", "fear": "medo", "joy": "alegria", "sadness": "tristeza", "surprise": "surpresa"}
FAMILY = {"massive_intent": "intent_routing", "assin2_entailment": "entailment", "inferbr_nli3": "entailment",
          "assin2_similarity": "semantic_similarity", "offensive_language": "toxicity_safety",
          "first_turn_preference": "preference_ranking", **{f"{d}_detection": "toxicity_safety" for d in TOLD_DIMENSIONS},
          **{f"{e}_intensity": "emotion_affect" for e in EMOTIONS},
          "normastcu_relevance": "evidence_retrieval_relevance", "juristcu_relevance": "evidence_retrieval_relevance",
          "faquad_evidence_sentence": "evidence_selection"}


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", unicodedata.normalize("NFC", str(text)).casefold()).strip()


def one_hot(index: int, size: int) -> list[float]:
    return [1.0 if i == index else 0.0 for i in range(size)]


def decision(rid, source, task, kind, state, question, options, target):
    return {"id": rid, "source": source, "task": task, "family": FAMILY[task], "type": kind, "state": state,
            "question": question, "options": [list(o) for o in options], "target": list(target)}


def from_dictionary(rid, source, task, kind, state, question, identities, target):
    """Render candidates from the frozen dictionary; its question, when present, replaces the adapter question."""
    entry = DICTIONARY[task]
    text = {c["identity"]: c["text"] for c in entry["candidates"]}
    return decision(rid, source, task, kind, state, entry.get("question", question), [(i, text[i]) for i in identities], target)


def content_hash(record: dict) -> str:
    core = {k: record[k] for k in ("id", "type", "state", "question", "options", "target")}
    return hashlib.sha256(json.dumps(core, ensure_ascii=False, sort_keys=True).encode()).hexdigest()


# --- sources of the frozen phase-2 corpus (ids carry the official split) --------------------------------------------------

def massive(rows, split):
    for row in rows:
        gold = MASSIVE_INTENTS[int(row["intent"])]
        state = str(row.get("utt_br", row.get("utt", "")))
        yield from_dictionary(f"massive_ptbr:{row['id']}:{split}", "massive_ptbr", "massive_intent", "choice", state,
                              "Qual categoria melhor descreve o pedido do usuário?", MASSIVE_INTENTS,
                              one_hot(MASSIVE_INTENTS.index(gold), len(MASSIVE_INTENTS)))


def assin2(rows, split):
    for index, row in enumerate(rows):
        base = str(row.get("sentence_pair_id", index))
        state = f"Premissa: {row['premise']}\nHipótese: {row['hypothesis']}"
        yield from_dictionary(f"assin2:{base}:entailment:{split}", "assin2", "assin2_entailment", "noul", state,
                              "A hipótese decorre da premissa?", ("false", "true"),
                              (0.0, 1.0) if int(row["entailment_judgment"]) == 1 else (1.0, 0.0))
        # Continuous gold s in [1, 5] -> mass (ceil(s) - s) on floor(s) and (s - floor(s)) on ceil(s): expected level == s.
        s = min(5.0, max(1.0, float(row["relatedness_score"])))
        lower, upper = int(s), min(5, int(s) + 1)
        target = [0.0] * 5
        if lower == upper:
            target[lower - 1] = 1.0
        else:
            target[lower - 1], target[upper - 1] = upper - s, s - lower
        yield from_dictionary(f"assin2:{base}:{split}:similarity", "assin2", "assin2_similarity", "score", state,
                              "Qual é o nível de similaridade semântica entre premissa e hipótese?", ("1", "2", "3", "4", "5"), target)


def told_br(rows, split="train"):
    # ToLD-Br: three annotators per text; target = share of annotators flagging the property.
    for index, row in enumerate(rows):
        for field, name in TOLD_DIMENSIONS.items():
            columns = [f"{field}_{n}" for n in (1, 2, 3)]
            if all(row.get(c) is not None for c in columns):
                votes = sum(int(float(row[c])) for c in columns)
            elif row.get(field) is not None:
                votes = int(float(row[field]))
            else:
                continue
            yield from_dictionary(f"told_br:{row.get('id', index)}:{field}:{split}", "told_br", f"{field}_detection", "noul",
                                  str(row["text"]), f"Este conteúdo apresenta {name}?", ("false", "true"), (1 - votes / 3, votes / 3))


def hatebr(rows, split="train"):
    for index, row in enumerate(rows):
        positives = sum(int(row[f"anotator{n}"]) for n in (1, 2, 3))
        yield from_dictionary(f"hatebr:{row.get('id', index)}:offensive_language:{split}", "hatebr", "offensive_language", "noul",
                              str(row["comentario"]), "Este conteúdo apresenta linguagem ofensiva?", ("false", "true"),
                              (1 - positives / 3, positives / 3))


# --- sources added for the general mixture ---------------------------------------------------------------------------------

INFERBR_CLASSES = ("CONTRADICTION", "ENTAILMENT", "NEUTRAL")  # ClassLabel ids at the pinned revision
INFERBR_OPTIONS = (("implicação", "ENTAILMENT"), ("neutro", "NEUTRAL"), ("contradição", "CONTRADICTION"))


def inferbr(rows, split):
    order = [name for _, name in INFERBR_OPTIONS]
    for row in rows:
        gold = INFERBR_CLASSES[int(row["label"])]
        yield from_dictionary(f"inferbr:{split}:{row['sentence_pair_id']}", "inferbr", "inferbr_nli3", "choice",
                              f"Premissa: {row['premise']}\nHipótese: {row['hypothesis']}", "Qual é a relação entre a premissa e a hipótese?",
                              [i for i, _ in INFERBR_OPTIONS], one_hot(order.index(gold), 3))


def brighter_key(text: str) -> str:
    return "brighter_ptbr:" + hashlib.sha256(normalize(text).encode()).hexdigest()[:20]


def brighter(rows, split):
    # One text -> six SCORE decisions (0-3). Ids are text hashes because upstream ids differ across tracks.
    for row in rows:
        key = brighter_key(row["text"])
        for emotion, pt in EMOTIONS.items():
            yield from_dictionary(f"{key}:{emotion}", "brighter_ptbr", f"{emotion}_intensity", "score", row["text"],
                                  f"Qual é a intensidade de {pt} expressa no texto?", ("ausente", "baixa", "moderada", "alta"),
                                  one_hot(int(row[emotion]), 4))


def _response_id(text: str) -> str:
    return "resp:" + hashlib.sha256(text.encode()).hexdigest()[:16]


def community_alignment(rows):
    """First-turn preference sets. Candidate identity is the response text hash, never the A-D slot (slots carry a strong
    position bias upstream). Votes on the identical prompt + response set are pooled, one vote per annotator."""
    groups = defaultdict(list)
    for row in rows:
        texts = [row.get(f"first_turn_response_{s}") for s in "abcd"]
        if not isinstance(row.get("first_turn_prompt"), str) or not all(isinstance(t, str) for t in texts) \
                or row.get("first_turn_preferred_response") not in {f"response_{s}" for s in "abcd"}:
            continue
        key = hashlib.sha256((row["first_turn_prompt"] + "\x00" + "\x00".join(sorted(texts))).encode()).hexdigest()[:20]
        groups[key].append(row)
    for key, members in sorted(groups.items()):
        first = members[0]
        texts = sorted({first[f"first_turn_response_{s}"] for s in "abcd"}, key=_response_id)
        if len({normalize(t) for t in texts}) != 4 or any(len(t.strip()) < 5 for t in texts):
            continue
        votes, annotators = Counter(), set()
        for m in sorted(members, key=lambda m: str(m["conversation_id"])):
            if m["annotator_id"] not in annotators:
                annotators.add(m["annotator_id"])
                votes[_response_id(m[f"first_turn_{m['first_turn_preferred_response']}"])] += 1
        n = sum(votes.values())
        ids = [_response_id(t) for t in texts]
        yield decision(f"community_alignment_pt:{key}", "community_alignment_pt", "first_turn_preference", "choice",
                       first["first_turn_prompt"], DICTIONARY["community_alignment_first_turn_preference"]["question"],
                       list(zip(ids, texts)), [votes.get(i, 0) / n for i in ids])


# --- family shift: NormasTCU / JurisTCU -------------------------------------------------------------------------------------

class _TextOnly(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []

    def handle_data(self, data):
        self.parts.append(data)


def strip_html(text) -> str:
    if not isinstance(text, str):
        return ""
    parser = _TextOnly()
    parser.feed(unescape(text))
    return re.sub(r"\s+", " ", " ".join(parser.parts)).strip()


def normas(query_csv, docs_csv, votes_csv, pairs):
    """Target = distribution of raw human votes (0/1/2) per (query, document) pair."""
    import pandas as pd

    queries = pd.read_csv(query_csv).assign(KEY=lambda d: d.KEY.astype(str)).set_index("KEY")["TEXT"]
    wanted = {d for _, d in pairs}
    docs = pd.concat(c[c.KEY.astype(str).isin(wanted)] for c in pd.read_csv(docs_csv, chunksize=2000))
    docs = docs.assign(KEY=docs.KEY.astype(str)).set_index("KEY")
    votes = pd.read_csv(votes_csv)
    counts = defaultdict(Counter)
    for q, d, v in zip(votes.QUERY_KEY.astype(str), votes.DOC_KEY.astype(str), votes.AVALIACAO):
        counts[(q, d)][int(v)] += 1
    for q, d in pairs:
        doc = docs.loc[d]
        parts = [str(doc.TITULO).rstrip(". ")] + ([str(doc.ASSUNTO).rstrip(". ")] if isinstance(doc.ASSUNTO, str) else [])
        state = f"Consulta: {queries[q]}\nDocumento: " + ". ".join(parts + [strip_html(doc.TEXTONORMA)])
        n = sum(counts[(q, d)].values())
        yield from_dictionary(f"normastcu:{q}|{d}", "normastcu", "normastcu_relevance", "score", state, "",
                              ("0", "1", "2"), [counts[(q, d)].get(level, 0) / n for level in range(3)])


def juris(query_csv, qrel_csv, doc_csv, pairs):
    """Target = one-hot of the released 0-3 relevance score."""
    import pandas as pd

    queries = pd.read_csv(query_csv).assign(ID=lambda d: d.ID.astype(str)).set_index("ID")
    qrel = pd.read_csv(qrel_csv)
    score = {(str(q), str(d)): int(s) for q, d, s in zip(qrel.QUERY_ID, qrel.DOC_ID, qrel.SCORE)}
    docs = pd.read_csv(doc_csv)
    docs = docs[docs.KEY.astype(str).isin({d for _, d in pairs})].assign(KEY=lambda d: d.KEY.astype(str)).set_index("KEY")
    for q, d in pairs:
        state = f"Consulta: {queries.TEXT[q]}\nDocumento: {strip_html(docs.ENUNCIADO[d])}"
        yield from_dictionary(f"juristcu:{q}|{d}", "juristcu", "juristcu_relevance", "score", state, "",
                              ("0", "1", "2", "3"), one_hot(score[(q, d)], 4))


# --- development generalization diagnostic: FaQuAD evidence selection ---------------------------------------------------------

SENTENCE_BREAK = re.compile(r"(?<=[.!?])\s+(?=[\"“(A-ZÁÉÍÓÚÂÊÔÃÕÇ0-9])")


def _sentences(text: str) -> list[tuple[int, int, str]]:
    out, pos = [], 0
    for part in SENTENCE_BREAK.split(text):
        start = text.index(part, pos)
        out.append((start, start + len(part), part.strip()))
        pos = start + len(part)
    return [s for s in out if s[2]]


def faquad_evidence(data: dict, split: str):
    """State = the question; candidates = the paragraph's sentences; gold = the sentence holding the first answer span.
    Questions whose answer crosses a sentence boundary, or with fewer than 2 / more than 60 sentences, are skipped."""
    for article in data["data"]:
        for paragraph in article["paragraphs"]:
            sents = _sentences(paragraph["context"])
            for qa in paragraph["qas"]:
                answer = qa["answers"][0]
                start, end = answer["answer_start"], answer["answer_start"] + len(answer["text"])
                gold = [i for i, (b, e, _) in enumerate(sents) if b <= start and end <= e]
                if not gold or not 2 <= len(sents) <= 60:
                    continue
                record = decision(f"faquad:{split}:{qa['id']}", "faquad", "faquad_evidence_sentence", "choice", qa["question"],
                                  "Qual frase do texto contém a resposta à pergunta?",
                                  [(f"s{i + 1:02d}", t) for i, (_, _, t) in enumerate(sents)], one_hot(gold[0], len(sents)))
                record["paragraph_title"] = article.get("title")
                yield record
