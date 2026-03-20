from __future__ import annotations

import numpy as np
import pandas as pd

from stil_semantic_change.contextual.confirmatory import (
    score_prototype_distances,
    select_confirmatory_terms,
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
