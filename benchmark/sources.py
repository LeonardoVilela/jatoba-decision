"""Pinned upstream sources. Every file is fetched at an exact revision; nothing is read from a moving branch."""

from pathlib import Path

SOURCES = {
    "massive_ptbr": {"hf": "Magurofg/massive-pt-br", "revision": "907f905b4b237c34ba805f942bfbb6d92ec9c81f"},
    "assin2": {"hf": "nilc-nlp/assin2", "revision": "0ff9c86779e06855536d8775ce5550550e1e5a2d"},
    "hatebr": {"hf": "franciellevargas/HateBR", "revision": "077db456f6c4b376540ef07fbcfdec61e7806cc7"},
    "told_br": {"url": "https://raw.githubusercontent.com/JAugusto97/ToLD-Br/6b325d26a9d25b321a3e9ba98ef98832b56729f5/ToLD-BR_alpha.csv"},
    "inferbr": {"hf": "hapaxlegomenon/InferBR", "revision": "304b2ca358c4f315a908b69d3d0c607ee101176d"},
    "brighter_ptbr": {"hf": "brighter-dataset/BRIGHTER-emotion-intensities", "revision": "08a5d61d3fc33036f97c8c76a61ff8d6f02f5157"},
    "community_alignment_pt": {"hf": "facebook/community-alignment-dataset", "revision": "4d21f8db61c857e7d3aab33cbc3c6caf14a12df6",
                               "note": "refs/convert/parquet of main@97343c7f6399fcbea430ed0f37c1768281a78d56"},
    "normastcu": {"hf": "LeandroRibeiro/NormasTCU", "revision": "f34d92d438def5978dac63270ca287571749ba42"},
    "juristcu": {"hf": "LeandroRibeiro/JurisTCU", "revision": "5a520e1f65dcddb17a02b98f6cfc044d681e0ee3"},
    "faquad": {"url": "https://raw.githubusercontent.com/liafacom/faquad/6ad978f20672bb41625b3b71fbe4a88b893d0a86/data/{split}.json"},
}


def hf_file(source: str, filename: str) -> Path:
    from huggingface_hub import hf_hub_download

    spec = SOURCES[source]
    return Path(hf_hub_download(spec["hf"], filename, repo_type="dataset", revision=spec["revision"]))


def hf_dataset(source: str) -> dict[str, list[dict]]:
    """Rows per split through the `datasets` loader, exactly as the frozen corpus was built (keeps float32 scores)."""
    from datasets import load_dataset

    spec = SOURCES[source]
    loaded = load_dataset(spec["hf"], revision=spec["revision"])
    return {split: [dict(row) for row in data] for split, data in loaded.items()}


def csv_rows(url: str) -> list[dict]:
    from datasets import load_dataset

    return [dict(row) for row in load_dataset("csv", data_files={"train": url})["train"]]


def json_url(url: str) -> dict:
    import json
    import urllib.request

    with urllib.request.urlopen(url, timeout=120) as response:
        return json.loads(response.read().decode("utf-8"))
