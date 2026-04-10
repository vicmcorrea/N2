from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from stil_semantic_change.comparison.panel import build_comparison_panel
from stil_semantic_change.utils.config import build_experiment_config
from tests.helpers import make_raw_cfg


def test_build_comparison_panel_merges_method_panels(
    project_root: Path,
    toy_dataset_dir: Path,
    tmp_path: Path,
) -> None:
    raw_cfg = make_raw_cfg(project_root, tmp_path / "outputs", toy_dataset_dir, force=True)
    cfg = build_experiment_config(raw_cfg)
    run_root = tmp_path / "comparison_run"
    scores_root = run_root / "scores"
    (scores_root / "tfidf_drift").mkdir(parents=True, exist_ok=True)

    pd.DataFrame(
        [
            {
                "lemma": "reforma",
                "primary_drift_mean": 0.40,
                "first_last_drift_mean": 0.50,
                "slice_count": 3,
                "sample_count_total": 30,
                "sample_count_min": 8,
                "slice_presence_ratio": 1.0,
                "dominant_pos": "NOUN",
                "drift_candidate_excluded": False,
                "stable_control_excluded": False,
            },
            {
                "lemma": "democracia",
                "primary_drift_mean": 0.10,
                "first_last_drift_mean": 0.12,
                "slice_count": 3,
                "sample_count_total": 25,
                "sample_count_min": 7,
                "slice_presence_ratio": 1.0,
                "dominant_pos": "NOUN",
                "drift_candidate_excluded": False,
                "stable_control_excluded": False,
            },
        ]
    ).to_parquet(scores_root / "scores_aggregated.parquet", index=False)
    (scores_root / "candidate_sets.json").write_text(
        json.dumps(
            {
                "drift_candidates": ["reforma"],
                "stable_controls": ["democracia"],
                "theory_seeds": ["economia"],
                "slice_order": ["2001", "2002", "2003"],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    pd.DataFrame(
        [
            {
                "lemma": "reforma",
                "primary_drift": 0.25,
                "first_last_drift": 0.35,
                "slice_count": 3,
                "sample_count_total": 30,
                "sample_count_min": 8,
                "slice_presence_ratio": 1.0,
                "dominant_pos": "NOUN",
                "drift_candidate_excluded": False,
                "stable_control_excluded": False,
            },
            {
                "lemma": "corrupção",
                "primary_drift": 0.22,
                "first_last_drift": 0.30,
                "slice_count": 3,
                "sample_count_total": 24,
                "sample_count_min": 6,
                "slice_presence_ratio": 1.0,
                "dominant_pos": "NOUN",
                "drift_candidate_excluded": False,
                "stable_control_excluded": False,
            },
        ]
    ).to_parquet(scores_root / "tfidf_drift" / "scores.parquet", index=False)
    (scores_root / "tfidf_drift" / "candidate_sets.json").write_text(
        json.dumps(
            {
                "drift_candidates": ["reforma", "corrupção"],
                "stable_controls": [],
                "theory_seeds": ["economia"],
                "slice_order": ["2001", "2002", "2003"],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    panel_root = scores_root / "comparison_panel"
    panel = build_comparison_panel(cfg, scores_root, panel_root)

    assert set(panel["lemma"]) == {"reforma", "democracia", "corrupção", "economia"}
    assert bool(panel.loc[panel["lemma"] == "reforma", "selected_by_word2vec"].iloc[0]) is True
    assert bool(panel.loc[panel["lemma"] == "reforma", "selected_by_tfidf"].iloc[0]) is True
    assert (
        panel.loc[panel["lemma"] == "reforma", "bucket"].iloc[0]
        == "shared_drift"
    )
    assert (
        panel.loc[panel["lemma"] == "democracia", "bucket"].iloc[0]
        == "stable_control"
    )
    assert (panel_root / "comparison_panel.parquet").exists()
    assert (panel_root / "summary.json").exists()
