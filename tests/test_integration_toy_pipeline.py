from __future__ import annotations

import numpy as np
import pandas as pd

from stil_semantic_change.runner import run_experiment
from stil_semantic_change.utils.artifacts import (
    build_artifact_paths,
    ensure_directories,
    read_json,
    stage_manifest_path,
    write_dataframe,
)
from stil_semantic_change.utils.config import build_experiment_config
from stil_semantic_change.word2vec.score import score_candidates
from stil_semantic_change.word2vec.vector_store import VectorStore, save_vector_store
from tests.helpers import make_raw_cfg


def test_score_candidates_prioritizes_planted_shift(
    project_root,
    toy_dataset_dir,
    tmp_path,
) -> None:
    raw_cfg = make_raw_cfg(project_root, tmp_path / "outputs", toy_dataset_dir, force=True)
    cfg = build_experiment_config(raw_cfg)
    paths = build_artifact_paths(cfg, raw_cfg)
    ensure_directories(paths)
    paths.prepared_root.mkdir(parents=True, exist_ok=True)
    paths.aligned_root.mkdir(parents=True, exist_ok=True)

    slice_summary = pd.DataFrame(
        [
            {"slice_id": "2001", "document_count": 4, "token_count": 20, "sort_key": "2001-00"},
            {"slice_id": "2002", "document_count": 4, "token_count": 20, "sort_key": "2002-00"},
            {"slice_id": "2003", "document_count": 4, "token_count": 20, "sort_key": "2003-00"},
        ]
    )
    lemma_stats = pd.DataFrame(
        [
            {"slice_id": "2001", "lemma": "reforma", "frequency": 5, "document_count": 2},
            {"slice_id": "2002", "lemma": "reforma", "frequency": 5, "document_count": 2},
            {"slice_id": "2003", "lemma": "reforma", "frequency": 5, "document_count": 2},
            {"slice_id": "2001", "lemma": "presidente", "frequency": 5, "document_count": 2},
            {"slice_id": "2002", "lemma": "presidente", "frequency": 5, "document_count": 2},
            {"slice_id": "2003", "lemma": "presidente", "frequency": 5, "document_count": 2},
        ]
    )
    write_dataframe(paths.prepared_root / "slice_summary.parquet", slice_summary)
    write_dataframe(paths.prepared_root / "lemma_slice_stats.parquet", lemma_stats)

    replicate_dir = paths.aligned_root / "replicate_0"
    for slice_id, matrix in {
        "2001": np.array([[1.0, 0.0], [0.0, 1.0]]),
        "2002": np.array([[0.0, 1.0], [0.0, 1.0]]),
        "2003": np.array([[-1.0, 0.0], [0.0, 1.0]]),
    }.items():
        save_vector_store(
            replicate_dir / slice_id / "vectors",
            VectorStore(
                words=("reforma", "presidente"),
                matrix=matrix,
                counts=np.array([5, 5]),
            ),
        )

    summary, _ = score_candidates(cfg, paths.prepared_root, paths.aligned_root, paths.scores_root)
    summary = summary.set_index("lemma")
    assert (
        summary.loc["reforma", "primary_drift_mean"]
        > summary.loc["presidente", "primary_drift_mean"]
    )


def test_toy_pipeline_smoke(project_root, toy_dataset_dir, tmp_path) -> None:
    raw_cfg = make_raw_cfg(project_root, tmp_path / "outputs", toy_dataset_dir, force=True)
    cfg = build_experiment_config(raw_cfg)
    run_experiment(cfg, raw_cfg)
    paths = build_artifact_paths(cfg, raw_cfg)
    assert (paths.reports_root / "coverage_by_slice.png").exists()
    assert (paths.reports_root / "drift_vs_frequency_dispersion.png").exists()
    assert (paths.reports_root / "drift_trajectories.png").exists()
    assert (paths.scores_root / "candidate_sets.json").exists()

    manifest_specs = [
        ("prepare_corpus", paths.prepared_root),
        ("train_word2vec", paths.models_root),
        ("align_embeddings", paths.aligned_root),
        ("score_candidates", paths.scores_root),
        ("report_candidates", paths.reports_root),
    ]
    for stage_name, stage_root in manifest_specs:
        manifest = read_json(stage_manifest_path(stage_root, stage_name))
        assert manifest["stage_name"] == stage_name
        assert manifest["task_name"] == cfg.task.name
        assert manifest["dataset_name"] == cfg.dataset.name
        assert isinstance(manifest["started_at"], str)
        assert isinstance(manifest["completed_at"], str)
        assert manifest["duration_seconds"] >= 0.0
