# benchmark/

| file | contents |
|---|---|
| `BENCHMARK_CARD.md` | regimes, construction, metrics, limits |
| `DATA_LICENSES.md` | per-source license evidence and redistribution status |
| `ADAPTER_AUDIT.md` | how each dataset becomes NOUL / CHOICE / SCORE decisions, and the caveats found |
| `CANDIDATE_DESCRIPTIONS.md` | every fixed candidate text, its provenance and caveats |
| `benchmark_spec.json` | machine-readable summary: sources, revisions, blocks, seeds, metric constants |
| `sources.py` | pinned upstream revisions and download helpers |
| `transforms.py` | frozen upstream-row → decision transformations |
| `candidate_dictionary.json` | frozen candidate texts (`general-candidates-v1`) |
| `manifests/` | ids, groups and content hashes of every block and training role; K-curve candidate sets |
| `adapters/` | the shared payload and the external-model adapters (Julia-1, Laya, GLiNER2.5-multi-Decide, Jev) |
| `evaluate.py` | scores a predictions file against a rebuilt block |
| `adapter_audit.json` | machine-readable adapter checks over the rebuilt blocks |

Build:

```bash
pip install -e ".[benchmark]"
python scripts/build_benchmark.py                      # evaluation blocks
python scripts/build_benchmark.py --blocks role_train  # training data of the released model
```

Community Alignment is derived from about 1 GB of upstream parquet. `--community-parquet` accepts a local Portuguese first-turn extract with the same columns.
