from __future__ import annotations

import pandas as pd

from stil_semantic_change.selection import (
    build_candidate_sets,
    candidate_exclusion_flags,
    eligible_vocabulary,
)


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
    eligible = eligible_vocabulary(lemma_slice_stats, cfg, total_slices=3)
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
    eligible = eligible_vocabulary(lemma_slice_stats, cfg, total_slices=3)
    assert bool(eligible.loc[eligible["lemma"] == "tratar se", "eligible"].iloc[0]) is False
    assert bool(eligible.loc[eligible["lemma"] == "tratar se", "excluded"].iloc[0]) is True


def test_candidate_sets_exclude_low_content_drift_terms(built_cfg) -> None:
    _, cfg = built_cfg
    summary = pd.DataFrame(
        [
            {"lemma": "acaso", "primary_drift_mean": 0.50, "dominant_pos": "NOUN"},
            {"lemma": "novidade", "primary_drift_mean": 0.49, "dominant_pos": "NOUN"},
            {"lemma": "corrupção", "primary_drift_mean": 0.30, "dominant_pos": "NOUN"},
            {"lemma": "democracia", "primary_drift_mean": 0.28, "dominant_pos": "NOUN"},
            {"lemma": "previdência", "primary_drift_mean": 0.27, "dominant_pos": "NOUN"},
            {"lemma": "imposto", "primary_drift_mean": 0.26, "dominant_pos": "NOUN"},
            {"lemma": "reforma", "primary_drift_mean": 0.20, "dominant_pos": "NOUN"},
        ]
    )
    cfg = cfg.__class__(
        **{
            **cfg.__dict__,
            "selection": cfg.selection.__class__(
                **{
                    **cfg.selection.__dict__,
                    "drift_candidate_exclude_lemmas": ("acaso", "novidade"),
                }
            ),
        }
    )
    annotated = candidate_exclusion_flags(summary, cfg)
    candidate_sets = build_candidate_sets(annotated, cfg, ["2001", "2002", "2003"])

    assert "acaso" not in candidate_sets["drift_candidates"]
    assert "novidade" not in candidate_sets["drift_candidates"]
    assert "previdência" in candidate_sets["drift_candidates"]
    assert "imposto" in candidate_sets["drift_candidates"]


def test_candidate_sets_exclude_procedural_stable_controls(built_cfg) -> None:
    _, cfg = built_cfg
    summary = pd.DataFrame(
        [
            {"lemma": "sessão", "primary_drift_mean": 0.10, "dominant_pos": "NOUN"},
            {"lemma": "art.", "primary_drift_mean": 0.11, "dominant_pos": "NOUN"},
            {"lemma": "juridicidade", "primary_drift_mean": 0.12, "dominant_pos": "NOUN"},
            {"lemma": "orçamentária", "primary_drift_mean": 0.13, "dominant_pos": "ADJ"},
            {"lemma": "recurso", "primary_drift_mean": 0.14, "dominant_pos": "NOUN"},
            {"lemma": "democracia", "primary_drift_mean": 0.25, "dominant_pos": "NOUN"},
        ]
    )
    cfg = cfg.__class__(
        **{
            **cfg.__dict__,
            "selection": cfg.selection.__class__(
                **{
                    **cfg.selection.__dict__,
                    "stable_control_exclude_lemmas": ("sessão", "art."),
                }
            ),
        }
    )
    annotated = candidate_exclusion_flags(summary, cfg)
    candidate_sets = build_candidate_sets(annotated, cfg, ["2001", "2002", "2003"])

    assert "sessão" not in candidate_sets["stable_controls"]
    assert "art." not in candidate_sets["stable_controls"]
    assert "juridicidade" in candidate_sets["stable_controls"]


def test_candidate_sets_exclude_disallowed_pos(built_cfg) -> None:
    _, cfg = built_cfg
    summary = pd.DataFrame(
        [
            {"lemma": "intervenção", "primary_drift_mean": 0.41, "dominant_pos": "NOUN"},
            {"lemma": "puder", "primary_drift_mean": 0.42, "dominant_pos": "VERB"},
            {"lemma": "corrupção", "primary_drift_mean": 0.30, "dominant_pos": "NOUN"},
            {"lemma": "democracia", "primary_drift_mean": 0.28, "dominant_pos": "NOUN"},
        ]
    )
    annotated = candidate_exclusion_flags(summary, cfg)
    candidate_sets = build_candidate_sets(annotated, cfg, ["2001", "2002", "2003"])

    assert "puder" not in candidate_sets["drift_candidates"]
    assert "intervenção" in candidate_sets["drift_candidates"]
