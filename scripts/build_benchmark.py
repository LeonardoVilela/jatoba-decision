"""Rebuild the JATOBÁ evaluation suite from upstream datasets at pinned revisions and verify every record.

    python scripts/build_benchmark.py                          # all evaluation blocks
    python scripts/build_benchmark.py --blocks jatoba_id,legacy_exposed
    python scripts/build_benchmark.py --blocks role_train      # training data of the released model

Records are selected by the ids in benchmark/manifests/ and compared with the frozen content hashes. The build stops
on the first missing id or hash mismatch: a different upstream revision must never be silently mixed in.
Output goes to benchmark/build/<block>.jsonl (git-ignored; upstream texts are not redistributed by this repository).
"""

import argparse
import gzip
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "benchmark"))
import sources as src  # noqa: E402
import transforms as tf  # noqa: E402

MANIFESTS = ROOT / "benchmark/manifests"
EVAL_BLOCKS = ("jatoba_id", "legacy_exposed", "shift_normastcu", "shift_juristcu", "gdev_faquad")
ROLE_BLOCKS = ("role_train", "role_development", "role_calibration")
CA_COLUMNS = ["conversation_id", "annotator_id", "assigned_lang", "first_turn_prompt", "first_turn_preferred_response",
              *[f"first_turn_response_{s}" for s in "abcd"]]


def read_manifest(block: str) -> tuple[dict | None, list[dict]]:
    with gzip.open(MANIFESTS / f"{block}.jsonl.gz", "rt", encoding="utf-8") as fh:
        rows = [json.loads(line) for line in fh]
    header = rows.pop(0) if "_role" in rows[0] else None
    return header, rows


def community_rows(local_parquet: str | None) -> list[dict]:
    """Portuguese first-turn rows of Community Alignment. Downloads ~1 GB of upstream parquet unless a local extract
    with the same columns is given."""
    import pandas as pd

    if local_parquet:
        frame = pd.read_parquet(local_parquet)
    else:
        shards = [src.hf_file("community_alignment_pt", f"default/train/{i:04d}.parquet") for i in range(3)]
        frame = pd.concat(pd.read_parquet(s, columns=CA_COLUMNS) for s in shards)
    return frame[frame.assigned_lang == "pt"].to_dict("records")


def generate(sources_needed: set[str], args, pairs: dict[str, list]) -> dict[str, dict]:
    """Transform every needed source once; the first occurrence of an id wins (as in the frozen loaders)."""
    records: dict[str, dict] = {}

    def add(stream):
        for record in stream:
            records.setdefault(record["id"], record)

    if "massive_ptbr" in sources_needed:
        for split, rows in src.hf_dataset("massive_ptbr").items():
            add(tf.massive(rows, split))
    if "assin2" in sources_needed:
        for split, rows in src.hf_dataset("assin2").items():
            add(tf.assin2(rows, split))
    if "hatebr" in sources_needed:
        for split, rows in src.hf_dataset("hatebr").items():
            add(tf.hatebr(rows, split))
    if "told_br" in sources_needed:
        add(tf.told_br(src.csv_rows(src.SOURCES["told_br"]["url"])))
    if "inferbr" in sources_needed:
        import pandas as pd

        for split in args.inferbr_splits:
            add(tf.inferbr(pd.read_csv(src.hf_file("inferbr", f"{split}.csv")).to_dict("records"), split))
    if "brighter_ptbr" in sources_needed:
        import pandas as pd

        for split in args.brighter_splits:
            add(tf.brighter(pd.read_parquet(src.hf_file("brighter_ptbr", f"ptbr/{split}-00000-of-00001.parquet")).to_dict("records"), split))
    if "community_alignment_pt" in sources_needed:
        add(tf.community_alignment(community_rows(args.community_parquet)))
    if "normastcu" in sources_needed:
        files = [src.hf_file("normastcu", n) for n in ("query.csv", "docs.csv", "raw_human_eval.csv")]
        add(tf.normas(*files, pairs["normastcu"]))
    if "juristcu" in sources_needed:
        files = [src.hf_file("juristcu", n) for n in ("query.csv", "qrel.csv", "doc.csv")]
        add(tf.juris(*files, pairs["juristcu"]))
    if "faquad" in sources_needed:
        for split in ("train", "dev"):
            add(tf.faquad_evidence(src.json_url(src.SOURCES["faquad"]["url"].format(split=split)), split))
    return records


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--blocks", default=",".join(EVAL_BLOCKS))
    parser.add_argument("--out", type=Path, default=ROOT / "benchmark/build")
    parser.add_argument("--community-parquet", help="local Portuguese first-turn extract (skips the ~1 GB download)")
    args = parser.parse_args()
    blocks = args.blocks.split(",")
    unknown = set(blocks) - set(EVAL_BLOCKS) - set(ROLE_BLOCKS)
    if unknown:
        raise SystemExit(f"unknown blocks: {sorted(unknown)}")

    manifests = {b: read_manifest(b) for b in blocks}
    needed = {row["source"] for _, rows in manifests.values() for row in rows}
    # Official splits feeding each block: evaluation never reads training splits of the new sources and vice versa.
    training = any(b in ROLE_BLOCKS for b in blocks)
    args.inferbr_splits = (["train", "val"] if training else []) + (["test"] if "jatoba_id" in blocks else [])
    args.brighter_splits = (["train", "dev"] if training else []) + (["test"] if "jatoba_id" in blocks else [])
    if training and "jatoba_id" in blocks:
        raise SystemExit("build training roles and jatoba_id separately (BRIGHTER texts repeat across official splits)")
    pairs = {s: [tuple(row["id"].split(":", 1)[1].split("|")) for row in manifests[b][1]]
             for s, b in (("normastcu", "shift_normastcu"), ("juristcu", "shift_juristcu")) if b in blocks}
    records = generate(needed, args, pairs)

    args.out.mkdir(parents=True, exist_ok=True)
    report = {}
    for block, (header, rows) in manifests.items():
        missing, mismatched, lines = [], [], []
        for row in rows:
            record = records.get(row["id"])
            if record is None:
                missing.append(row["id"])
                continue
            digest = tf.content_hash(record)
            if digest != row.get("sha256", digest) or digest[:16] != row.get("sha16", digest[:16]):
                mismatched.append(row["id"])
                continue
            lines.append(json.dumps({**record, "group": row["group"]}, ensure_ascii=False, sort_keys=True))
        if header:
            joined = "".join(f"{row['id']}\t{tf.content_hash(records[row['id']])}\n" for row in rows if row["id"] in records)
            if hashlib.sha256(joined.encode()).hexdigest() != header["aggregate_sha256"]:
                mismatched.append("<aggregate>")
        report[block] = {"expected": len(rows), "missing": len(missing), "hash_mismatch": len(mismatched)}
        if missing or mismatched:
            print(json.dumps(report[block] | {"examples": (missing + mismatched)[:5]}))
            raise SystemExit(f"{block}: rebuilt records differ from the frozen manifest; refusing to write it")
        (args.out / f"{block}.jsonl").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=1))


if __name__ == "__main__":
    main()
