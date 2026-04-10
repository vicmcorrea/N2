from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from stil_semantic_change.preprocessing.views import (
    prepared_content_tokens_dir,
    prepared_doc_metadata_dir,
)
from stil_semantic_change.reporting.qualitative import (
    collect_context_samples,
    write_context_reports,
)


def test_context_sampling_roundtrip(tmp_path: Path) -> None:
    run_root = tmp_path / "run"
    prepared_root = run_root / "prepared"
    prepared_doc_metadata_dir(prepared_root).mkdir(parents=True, exist_ok=True)
    prepared_content_tokens_dir(prepared_root).mkdir(parents=True, exist_ok=True)
    (run_root / "scores").mkdir(parents=True, exist_ok=True)
    (run_root / "reports").mkdir(parents=True, exist_ok=True)

    docs = pd.DataFrame(
        [
            {
                "doc_id": "d1",
                "slice_id": "2003",
                "date": "2003-01-01",
                "source_file": "floor_2003.csv",
            },
            {
                "doc_id": "d2",
                "slice_id": "2004",
                "date": "2004-12-31",
                "source_file": "floor_2004.csv",
            },
        ]
    )
    docs.to_parquet(prepared_doc_metadata_dir(prepared_root) / "shard.parquet", index=False)

    tokens = pd.DataFrame(
        [
            {
                "doc_id": "d1",
                "slice_id": "2003",
                "token_index": 0,
                "token": "a",
                "lemma": "a",
            },
            {
                "doc_id": "d1",
                "slice_id": "2003",
                "token_index": 1,
                "token": "texto",
                "lemma": "texto",
            },
            {
                "doc_id": "d1",
                "slice_id": "2003",
                "token_index": 2,
                "token": "sobre",
                "lemma": "sobre",
            },
            {
                "doc_id": "d1",
                "slice_id": "2003",
                "token_index": 3,
                "token": "democracia",
                "lemma": "democracia",
            },
            {
                "doc_id": "d2",
                "slice_id": "2004",
                "token_index": 0,
                "token": "nova",
                "lemma": "nova",
            },
            {
                "doc_id": "d2",
                "slice_id": "2004",
                "token_index": 1,
                "token": "fase",
                "lemma": "fase",
            },
            {
                "doc_id": "d2",
                "slice_id": "2004",
                "token_index": 2,
                "token": "democracia",
                "lemma": "democracia",
            },
            {
                "doc_id": "d2",
                "slice_id": "2004",
                "token_index": 3,
                "token": "brasil",
                "lemma": "brasil",
            },
        ]
    )
    tokens.to_parquet(prepared_content_tokens_dir(prepared_root) / "shard.parquet", index=False)

    candidate_sets = {
        "drift_candidates": ["democracia"],
        "stable_controls": ["paz"],
        "theory_seeds": ["cultura"],
        "slice_order": ["2003", "2004"],
    }
    (run_root / "scores" / "candidate_sets.json").write_text(
        json.dumps(candidate_sets, ensure_ascii=False), encoding="utf-8"
    )

    contexts = collect_context_samples(
        run_root,
        per_term_per_phase=1,
        context_window=1,
        seed=7,
    )
    assert not contexts.empty
    assert "democracia" in contexts["term"].unique()
    write_context_reports(run_root, contexts)
    parquet_path = run_root / "reports" / "qualitative_contexts.parquet"
    md_path = run_root / "reports" / "qualitative_contexts.md"
    assert parquet_path.exists()
    assert md_path.exists()
    assert "qualitative context packet" in md_path.read_text(encoding="utf-8").lower()
