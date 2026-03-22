from __future__ import annotations

import pandas as pd

from stil_semantic_change.preprocessing.views import prepared_text_view_by_slice_dir
from stil_semantic_change.tfidf.score import score_tfidf_drift
from stil_semantic_change.utils.artifacts import (
    build_artifact_paths,
    ensure_directories,
    write_dataframe,
)
from stil_semantic_change.utils.config import build_experiment_config
from tests.helpers import make_raw_cfg


def test_tfidf_drift_prioritizes_planted_shift(
    project_root,
    toy_dataset_dir,
    tmp_path,
) -> None:
    raw_cfg = make_raw_cfg(project_root, tmp_path / "outputs", toy_dataset_dir, force=True)
    cfg = build_experiment_config(raw_cfg)
    paths = build_artifact_paths(cfg, raw_cfg)
    ensure_directories(paths)
    paths.prepared_root.mkdir(parents=True, exist_ok=True)

    slice_summary = pd.DataFrame(
        [
            {"slice_id": "2001", "document_count": 4, "token_count": 20, "sort_key": "2001-00"},
            {"slice_id": "2002", "document_count": 4, "token_count": 20, "sort_key": "2002-00"},
            {"slice_id": "2003", "document_count": 4, "token_count": 20, "sort_key": "2003-00"},
        ]
    )
    lemma_stats = pd.DataFrame(
        [
            {"slice_id": "2001", "lemma": "reforma", "frequency": 8, "document_count": 2},
            {"slice_id": "2002", "lemma": "reforma", "frequency": 2, "document_count": 2},
            {"slice_id": "2003", "lemma": "reforma", "frequency": 8, "document_count": 2},
            {"slice_id": "2001", "lemma": "presidente", "frequency": 6, "document_count": 2},
            {"slice_id": "2002", "lemma": "presidente", "frequency": 6, "document_count": 2},
            {"slice_id": "2003", "lemma": "presidente", "frequency": 6, "document_count": 2},
        ]
    )
    token_rows = pd.DataFrame(
        [
            {
                "doc_id": "d1",
                "slice_id": "2001",
                "token_index": 0,
                "token": "reforma",
                "lemma": "reforma",
                "pos": "NOUN",
            },
            {
                "doc_id": "d2",
                "slice_id": "2002",
                "token_index": 0,
                "token": "reforma",
                "lemma": "reforma",
                "pos": "NOUN",
            },
            {
                "doc_id": "d3",
                "slice_id": "2003",
                "token_index": 0,
                "token": "reforma",
                "lemma": "reforma",
                "pos": "NOUN",
            },
            {
                "doc_id": "d4",
                "slice_id": "2001",
                "token_index": 1,
                "token": "presidente",
                "lemma": "presidente",
                "pos": "NOUN",
            },
            {
                "doc_id": "d5",
                "slice_id": "2002",
                "token_index": 1,
                "token": "presidente",
                "lemma": "presidente",
                "pos": "NOUN",
            },
            {
                "doc_id": "d6",
                "slice_id": "2003",
                "token_index": 1,
                "token": "presidente",
                "lemma": "presidente",
                "pos": "NOUN",
            },
        ]
    )

    write_dataframe(paths.prepared_root / "slice_summary.parquet", slice_summary)
    write_dataframe(paths.prepared_root / "lemma_slice_stats.parquet", lemma_stats)
    write_dataframe(paths.prepared_root / "tokens" / "content" / "batch_0001.parquet", token_rows)

    text_dir = prepared_text_view_by_slice_dir(paths.prepared_root, cfg.model.text_view)
    text_dir.mkdir(parents=True, exist_ok=True)
    filler = "apoio apoio apoio apoio apoio apoio apoio apoio"
    (text_dir / "2001.txt").write_text(
        f"reforma reforma reforma reforma presidente presidente {filler}\n",
        encoding="utf-8",
    )
    (text_dir / "2002.txt").write_text(
        f"reforma presidente presidente presidente presidente {filler}\n",
        encoding="utf-8",
    )
    (text_dir / "2003.txt").write_text(
        f"reforma reforma reforma reforma presidente presidente {filler}\n",
        encoding="utf-8",
    )

    summary, trajectory = score_tfidf_drift(
        cfg,
        paths.prepared_root,
        paths.scores_root / "tfidf_drift",
    )
    summary = summary.set_index("lemma")

    assert summary.loc["reforma", "primary_drift"] > summary.loc["presidente", "primary_drift"]
    assert summary.loc["reforma", "method"] == "tfidf_drift"
    assert len(trajectory) == 4
    assert (paths.scores_root / "tfidf_drift" / "scores.parquet").exists()
    assert (paths.scores_root / "tfidf_drift" / "trajectory.parquet").exists()
    assert (paths.scores_root / "tfidf_drift" / "summary.json").exists()
