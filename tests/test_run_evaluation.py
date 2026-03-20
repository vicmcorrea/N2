from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from stil_semantic_change.reporting.evaluation import evaluate_run, write_readiness_reports


def test_run_evaluation(tmp_path: Path) -> None:
    run_root = tmp_path / "run"
    (run_root / "prepared").mkdir(parents=True)
    (run_root / "aligned").mkdir(parents=True)
    (run_root / "scores").mkdir(parents=True)
    (run_root / "reports").mkdir(parents=True)

    slice_summary = pd.DataFrame(
        [
            {"slice_id": "2003", "document_count": 100, "token_count": 1000, "sort_key": "2003-00"},
            {"slice_id": "2004", "document_count": 120, "token_count": 1300, "sort_key": "2004-00"},
            {"slice_id": "2005", "document_count": 110, "token_count": 1250, "sort_key": "2005-00"},
        ]
    )
    slice_summary.to_parquet(run_root / "prepared" / "slice_summary.parquet", index=False)

    eligible_vocab = pd.DataFrame(
        [{"lemma": "democracia"}, {"lemma": "corrupcao"}, {"lemma": "reforma"}]
    )
    eligible_vocab.to_parquet(run_root / "scores" / "eligible_vocabulary.parquet", index=False)

    summary = pd.DataFrame(
        [
            {
                "lemma": "democracia",
                "primary_drift_mean": 0.08,
                "slice_presence_ratio": 0.95,
                "total_frequency": 500,
            },
            {
                "lemma": "corrupcao",
                "primary_drift_mean": 0.07,
                "slice_presence_ratio": 0.9,
                "total_frequency": 420,
            },
            {
                "lemma": "reforma",
                "primary_drift_mean": 0.01,
                "slice_presence_ratio": 0.99,
                "total_frequency": 600,
            },
        ]
    )
    summary.to_parquet(run_root / "scores" / "scores_aggregated.parquet", index=False)

    candidate_sets = {
        "drift_candidates": ["democracia", "corrupcao"],
        "stable_controls": ["reforma"],
        "theory_seeds": ["democracia"],
        "slice_order": ["2003", "2004", "2005"],
    }
    (run_root / "scores" / "candidate_sets.json").write_text(
        json.dumps(candidate_sets, ensure_ascii=False), encoding="utf-8"
    )

    anchor_summary = pd.DataFrame(
        [
            {"replicate": 0, "slice_id": "2003", "anchor_count": 500},
            {"replicate": 0, "slice_id": "2004", "anchor_count": 520},
            {"replicate": 0, "slice_id": "2005", "anchor_count": 510},
        ]
    )
    anchor_summary.to_parquet(run_root / "aligned" / "anchor_summary.parquet", index=False)

    result = evaluate_run(run_root)
    assert result["status"] == "ready"

    write_readiness_reports(run_root, result)
    json_path = run_root / "reports" / "stil_readiness.json"
    md_path = run_root / "reports" / "stil_readiness.md"
    assert json_path.exists()
    assert md_path.exists()
