from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from stil_semantic_change.contextual.confirmatory import (
    _build_comparison_frame,
    _load_confirmatory_inputs,
    score_prototype_distances,
    select_confirmatory_terms,
    select_confirmatory_terms_from_panel,
)


def test_select_confirmatory_terms_deduplicates_preserving_order() -> None:
    terms = select_confirmatory_terms(
        {
            "drift_candidates": ["reforma", "democracia"],
            "stable_controls": ["democracia", "presidente"],
            "theory_seeds": ["economia", "reforma"],
        }
    )
    assert terms == ["reforma", "democracia", "presidente", "economia"]


def test_select_confirmatory_terms_from_panel_preserves_panel_order() -> None:
    panel = pd.DataFrame(
        [
            {"lemma": "reforma"},
            {"lemma": "democracia"},
            {"lemma": "reforma"},
            {"lemma": "economia"},
        ]
    )
    terms = select_confirmatory_terms_from_panel(panel)
    assert terms == ["reforma", "democracia", "economia"]


def test_load_confirmatory_inputs_prefers_comparison_panel(tmp_path: Path) -> None:
    scores_root = tmp_path / "scores"
    panel_root = scores_root / "comparison_panel"
    panel_root.mkdir(parents=True)
    pd.DataFrame(
        [
            {"lemma": "reforma"},
            {"lemma": "corrupção"},
        ]
    ).to_parquet(panel_root / "comparison_panel.parquet", index=False)
    (panel_root / "summary.json").write_text(
        json.dumps({"slice_order": ["2001", "2002"]}, ensure_ascii=False),
        encoding="utf-8",
    )
    (scores_root / "candidate_sets.json").write_text(
        json.dumps(
            {
                "drift_candidates": ["democracia"],
                "stable_controls": ["presidente"],
                "theory_seeds": ["economia"],
                "slice_order": ["1999", "2000"],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    terms, slice_order, selection_source, panel = _load_confirmatory_inputs(scores_root)

    assert terms == ["reforma", "corrupção"]
    assert slice_order == ["2001", "2002"]
    assert selection_source == "comparison_panel"
    assert panel is not None


def test_build_comparison_frame_uses_panel_metadata() -> None:
    bert_scores = pd.DataFrame(
        [
            {
                "lemma": "reforma",
                "primary_drift": 0.4,
                "first_last_drift": 0.5,
                "slice_count": 2,
                "sample_count_total": 8,
                "sample_count_min": 4,
            }
        ]
    )
    comparison_panel = pd.DataFrame(
        [
            {
                "lemma": "reforma",
                "bucket": "shared_drift",
                "word2vec_rank": 5,
                "word2vec_primary_drift": 0.2,
                "word2vec_first_last_drift": 0.25,
                "tfidf_rank": 3,
                "tfidf_primary_drift": 0.3,
                "tfidf_first_last_drift": 0.35,
                "selected_by_word2vec": True,
                "selected_by_tfidf": True,
                "selected_as_stable_control": False,
                "selected_as_theory_seed": True,
                "selected_as_disagreement_case": False,
            }
        ]
    )

    comparison = _build_comparison_frame(bert_scores, Path("."), comparison_panel)

    assert comparison.loc[0, "bucket"] == "shared_drift"
    assert comparison.loc[0, "bert_word2vec_gap"] == pytest.approx(0.2)
    assert comparison.loc[0, "bert_tfidf_gap"] == pytest.approx(0.1)


def test_score_prototype_distances_prefers_larger_shift() -> None:
    prototypes = pd.DataFrame(
        [
            {
                "layer": -1,
                "lemma": "reforma",
                "slice_id": "2001",
                "sample_count": 2,
                "embedding": np.array([1.0, 0.0], dtype=np.float32),
            },
            {
                "layer": -1,
                "lemma": "reforma",
                "slice_id": "2002",
                "sample_count": 2,
                "embedding": np.array([0.0, 1.0], dtype=np.float32),
            },
            {
                "layer": -1,
                "lemma": "presidente",
                "slice_id": "2001",
                "sample_count": 2,
                "embedding": np.array([1.0, 0.0], dtype=np.float32),
            },
            {
                "layer": -1,
                "lemma": "presidente",
                "slice_id": "2002",
                "sample_count": 2,
                "embedding": np.array([0.98, 0.02], dtype=np.float32),
            },
        ]
    )

    scores, trajectory = score_prototype_distances(prototypes, ["2001", "2002"])
    scores = scores.set_index("lemma")

    assert scores.loc["reforma", "primary_drift"] > scores.loc["presidente", "primary_drift"]
    assert len(trajectory) == 2
