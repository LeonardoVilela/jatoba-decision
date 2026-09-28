"""Pre-publication checks for this repository. Writes release_check.json and exits non-zero on any failure.

    python scripts/verify_release.py               # all checks, including pytest
    python scripts/verify_release.py --skip-tests

When benchmark/build/ exists (after scripts/build_benchmark.py), it also writes benchmark/adapter_audit.json:
aggregate structural checks over the rebuilt decisions, with no upstream text.
"""

import argparse
import gzip
import hashlib
import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED = [
    "README.md", "MODEL_CARD.md", "LICENSE", "CITATION.cff", "pyproject.toml", "RELEASE_REVIEW.md", ".github/workflows/ci.yml",
    "src/jatoba/model.py", "src/jatoba/decision.py", "src/jatoba/inference.py", "src/jatoba/metrics.py",
    "benchmark/README.md", "benchmark/BENCHMARK_CARD.md", "benchmark/DATA_LICENSES.md", "benchmark/ADAPTER_AUDIT.md",
    "benchmark/CANDIDATE_DESCRIPTIONS.md", "benchmark/benchmark_spec.json", "benchmark/candidate_dictionary.json",
    "benchmark/evaluate.py", "benchmark/transforms.py", "benchmark/sources.py", "benchmark/manifests/k_sets.json.gz",
    "scripts/build_benchmark.py", "scripts/reproduce_tables.py", "results/metrics.json",
    "docs/architecture.md", "docs/methodology.md", "docs/limitations.md", "docs/reproducibility.md", "docs/research_history.md",
]
WEIGHT_SUFFIXES = {".pt", ".pth", ".bin", ".safetensors", ".ckpt", ".onnx", ".gguf", ".h5", ".npz", ".pkl"}
RAW_DATA_SUFFIXES = {".jsonl", ".parquet", ".csv", ".tsv", ".arrow", ".xlsx"}
MAX_BYTES = 10_000_000
TEXT_SUFFIXES = {".py", ".md", ".json", ".toml", ".cff", ".yml", ".yaml", ".txt", ".cfg", ".ini", ""}
SECRET_PATTERNS = {
    "huggingface token": r"\bhf_[A-Za-z0-9]{30,}",
    "openai-style key": r"\bsk-[A-Za-z0-9_-]{20,}",
    "vercel key": r"\bvck_[A-Za-z0-9]{20,}",
    "github token": r"\bgh[pousr]_[A-Za-z0-9]{30,}",
    "aws access key": r"\bAKIA[0-9A-Z]{16}\b",
    "private key": r"-----BEGIN [A-Z ]*PRIVATE KEY-----",
    "bearer token": r"Bearer\s+[A-Za-z0-9._~+/-]{20,}",
    "assigned secret": r"(?i)(api[_-]?key|secret|password|token)\s*[:=]\s*['\"][^'\"\s]{16,}['\"]",
}
LOCAL_PATH = re.compile(r"/Use[r]s/|/hom[e]/[a-z]|/privat[e]/tmp|[A-Z]:\\\\Use[r]s")
# Names that must never appear in the public tree, stored as SHA-256 of the lowercased word so this file does not name them.
FORBIDDEN_WORD_SHA256 = {
    "1d402e4ff0e06ca0bc5fb13ce377da185874ac74dadd7ab47b6d7076f0bd4125",
    "ca3175a9ac7250f9e43f7e5429e28b6744c6ceea48ae51a8fcb44a0dee7af1c0",
}


def release_files() -> list[Path]:
    """Tracked plus untracked-but-not-ignored files: exactly what a commit of the working tree would publish."""
    out = subprocess.run(["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"], cwd=ROOT, check=True,
                         capture_output=True).stdout.decode()
    return sorted(ROOT / p for p in out.split("\0") if p and (ROOT / p).is_file())


def text_of(path: Path) -> str | None:
    if path.suffix == ".gz":
        return gzip.decompress(path.read_bytes()).decode("utf-8")
    if path.suffix not in TEXT_SUFFIXES:
        return None
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return None


def check_files(files: list[Path]) -> dict:
    rel = {str(p.relative_to(ROOT)) for p in files}
    problems = [f"missing {name}" for name in REQUIRED if name not in rel]
    for p in files:
        name = str(p.relative_to(ROOT))
        if p.suffix in WEIGHT_SUFFIXES:
            problems.append(f"weights file {name}")
        if (p.suffix in RAW_DATA_SUFFIXES and not name.startswith("results/")) or name.startswith("benchmark/build/"):
            problems.append(f"raw data file {name}")
        if p.name.startswith(".env"):
            problems.append(f"environment file {name}")
        if p.stat().st_size > MAX_BYTES:
            problems.append(f"large file {name} ({p.stat().st_size:,} bytes)")
    return {"ok": not problems, "files": len(files), "problems": problems}


def check_contents(files: list[Path]) -> dict:
    secrets, paths, words = [], [], []
    compiled = {k: re.compile(v) for k, v in SECRET_PATTERNS.items()}
    for p in files:
        text = text_of(p)
        if text is None:
            continue
        name = str(p.relative_to(ROOT))
        for lineno, line in enumerate(text.splitlines(), 1):
            # Report location and kind only; a matched value is never printed or stored.
            secrets += [f"{name}:{lineno} {kind}" for kind, rx in compiled.items() if rx.search(line)]
            if LOCAL_PATH.search(line):
                paths.append(f"{name}:{lineno}")
            if any(hashlib.sha256(w.encode()).hexdigest() in FORBIDDEN_WORD_SHA256 for w in re.findall(r"[a-z0-9]+", line.lower())):
                words.append(f"{name}:{lineno}")
    return {"secrets": {"ok": not secrets, "hits": secrets},
            "local_paths": {"ok": not paths, "hits": paths},
            "sealed_set_references": {"ok": not words, "hits": words}}


def check_manifests() -> dict:
    spec = json.loads((ROOT / "benchmark/benchmark_spec.json").read_text(encoding="utf-8"))
    problems = []
    for block, info in spec["blocks"].items():
        path = ROOT / "benchmark" / info["manifest"]
        if hashlib.sha256(path.read_bytes()).hexdigest() != info["manifest_sha256"]:
            problems.append(f"{block}: manifest hash differs from benchmark_spec.json")
        with gzip.open(path, "rt", encoding="utf-8") as fh:
            if sum(1 for _ in fh) != info["decisions"]:
                problems.append(f"{block}: decision count differs from benchmark_spec.json")
    for role, info in spec["training_roles"].items():
        with gzip.open(ROOT / "benchmark" / info["manifest"], "rt", encoding="utf-8") as fh:
            header = json.loads(fh.readline())
            rows = sum(1 for _ in fh)
        if (header["aggregate_sha256"], header["records"], rows) != (info["aggregate_sha256"], info["decisions"], info["decisions"]):
            problems.append(f"role {role}: header or count differs from benchmark_spec.json")
    dictionary = hashlib.sha256((ROOT / "benchmark/candidate_dictionary.json").read_bytes()).hexdigest()
    if dictionary != spec["candidate_dictionary"]["sha256"]:
        problems.append("candidate_dictionary.json hash differs from benchmark_spec.json")
    return {"ok": not problems, "blocks": len(spec["blocks"]), "roles": len(spec["training_roles"]), "problems": problems}


def run(cmd: list[str]) -> dict:
    result = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    tail = [re.sub(r" in [0-9.]+s\b", "", line) for line in (result.stdout + result.stderr).strip().splitlines()[-3:]]
    return {"ok": result.returncode == 0, "command": " ".join(cmd[1:]), "tail": tail}


def adapter_audit(build: Path) -> dict:
    blocks = {}
    for path in sorted(build.glob("*.jsonl")):
        ids, types, ks, soft, problems = set(), Counter(), Counter(), 0, Counter()
        for line in path.open(encoding="utf-8"):
            r = json.loads(line)
            options = [c for c, _ in r["options"]]
            if r["id"] in ids:
                problems["duplicate id"] += 1
            ids.add(r["id"])
            types[r["type"]] += 1
            ks[len(options)] += 1
            soft += max(r["target"]) < 1
            if len(options) != len(r["target"]):
                problems["target length != candidates"] += 1
            if abs(sum(r["target"]) - 1) > 1e-6 or min(r["target"]) < 0:
                problems["target not a distribution"] += 1
            if len(set(options)) != len(options):
                problems["duplicate candidate id"] += 1
            if any(not str(text).strip() for _, text in r["options"]):
                problems["empty candidate description"] += 1
            if not str(r["state"]).strip() or not str(r["question"]).strip():
                problems["empty state or question"] += 1
            if not r.get("group") or not r.get("family"):
                problems["missing group or family"] += 1
            if r["type"] == "noul" and options != ["false", "true"]:
                problems["NOUL candidates are not false,true"] += 1
        blocks[path.stem] = {"decisions": len(ids), "primitives": dict(types), "soft_targets": soft,
                             "k_min": min(ks), "k_max": max(ks), "problems": dict(problems)}
    return {"note": "Structural checks over benchmark/build/ as rebuilt by scripts/build_benchmark.py; no upstream text.",
            "ok": all(not b["problems"] for b in blocks.values()), "blocks": blocks}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--skip-tests", action="store_true")
    args = parser.parse_args()

    files = release_files()
    checks = {"files": check_files(files), **check_contents(files), "manifests": check_manifests(),
              "tables_and_readme_headline": run([sys.executable, "scripts/reproduce_tables.py", "--check"])}
    if not args.skip_tests:
        checks["tests"] = run([sys.executable, "-m", "pytest", "-q"])
    build = ROOT / "benchmark/build"
    if build.is_dir() and any(build.glob("*.jsonl")):
        audit = adapter_audit(build)
        (ROOT / "benchmark/adapter_audit.json").write_text(json.dumps(audit, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        checks["adapter_audit"] = {"ok": audit["ok"], "blocks": len(audit["blocks"])}

    report = {"ok": all(c["ok"] for c in checks.values()), "checks": checks}
    (ROOT / "release_check.json").write_text(json.dumps(report, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    for name, c in checks.items():
        print(f"{'PASS' if c['ok'] else 'FAIL'}  {name}")
    sys.exit(0 if report["ok"] else 1)


if __name__ == "__main__":
    main()
