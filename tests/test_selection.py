from __future__ import annotations

import pandas as pd

from stil_semantic_change.word2vec.score import _eligible_vocabulary


def test_eligible_vocabulary_filters_by_slice_presence(built_cfg) -> None:
    _, cfg = built_cfg
    lemma_slice_stats = pd.DataFrame(
        [
            {"slice_id": "2001", "lemma": "reforma", "frequency": 3, "document_count": 1},
            {"slice_id": "2002", "lemma": "reforma", "frequency": 3, "document_count": 1},
            {"slice_id": "2003", "lemma": "reforma", "frequency": 3, "document_count": 1},
            {"slice_id": "2001", "lemma": "raro", "frequency": 1, "document_count": 1},
            {"slice_id": "2002", "lemma": "raro", "frequency": 0, "document_count": 0},
            {"slice_id": "2003", "lemma": "raro", "frequency": 1, "document_count": 1},
        ]
    )
    eligible = _eligible_vocabulary(lemma_slice_stats, cfg, total_slices=3)
    assert bool(eligible.loc[eligible["lemma"] == "reforma", "eligible"].iloc[0]) is True
    assert bool(eligible.loc[eligible["lemma"] == "raro", "eligible"].iloc[0]) is False


def test_eligible_vocabulary_excludes_whitespace_lemmas(built_cfg) -> None:
    _, cfg = built_cfg
    lemma_slice_stats = pd.DataFrame(
        [
            {"slice_id": "2001", "lemma": "tratar se", "frequency": 10, "document_count": 3},
            {"slice_id": "2002", "lemma": "tratar se", "frequency": 11, "document_count": 3},
            {"slice_id": "2003", "lemma": "tratar se", "frequency": 12, "document_count": 3},
        ]
    )
    eligible = _eligible_vocabulary(lemma_slice_stats, cfg, total_slices=3)
    assert bool(eligible.loc[eligible["lemma"] == "tratar se", "eligible"].iloc[0]) is False
    assert bool(eligible.loc[eligible["lemma"] == "tratar se", "excluded"].iloc[0]) is True
