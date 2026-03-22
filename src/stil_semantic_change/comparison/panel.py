from __future__ import annotations

from pathlib import Path

import pandas as pd

from stil_semantic_change.utils.artifacts import (
    read_dataframe,
    read_json,
    write_dataframe,
    write_json,
)
from stil_semantic_change.utils.config.schema import ExperimentConfig


def _method_rank(frame: pd.DataFrame, score_column: str, rank_column: str) -> pd.DataFrame:
    ranked = frame.sort_values(score_column, ascending=False).reset_index(drop=True).copy()
    ranked[rank_column] = ranked.index + 1
    return ranked


def _bucket(row: pd.Series) -> str:
    if bool(row["selected_as_theory_seed"]):
        return "theory_seed"
    if bool(row["selected_as_stable_control"]):
        return "stable_control"
    if bool(row["selected_by_word2vec"]) and bool(row["selected_by_tfidf"]):
        return "shared_drift"
    if bool(row["selected_by_word2vec"]):
        return "word2vec_only_drift"
    if bool(row["selected_by_tfidf"]):
        return "tfidf_only_drift"
    return "scored_only"


def build_comparison_panel(
    cfg: ExperimentConfig,
    scores_root: Path,
    panel_root: Path,
) -> pd.DataFrame:
    w2v_scores = read_dataframe(scores_root / "scores_aggregated.parquet")
    tfidf_root = scores_root / "tfidf_drift"
    tfidf_scores = read_dataframe(tfidf_root / "scores.parquet")
    w2v_sets = read_json(scores_root / "candidate_sets.json")
    tfidf_sets = read_json(tfidf_root / "candidate_sets.json")

    w2v_scores = _method_rank(w2v_scores, "primary_drift_mean", "word2vec_rank")
    tfidf_scores = _method_rank(tfidf_scores, "primary_drift", "tfidf_rank")

    merged = w2v_scores[
        [
            "lemma",
            "primary_drift_mean",
            "first_last_drift_mean",
            "slice_count",
            "sample_count_total",
            "sample_count_min",
            "slice_presence_ratio",
            "dominant_pos",
            "word2vec_rank",
        ]
    ].rename(
        columns={
            "primary_drift_mean": "word2vec_primary_drift",
            "first_last_drift_mean": "word2vec_first_last_drift",
            "sample_count_total": "word2vec_sample_count_total",
            "sample_count_min": "word2vec_sample_count_min",
            "slice_count": "word2vec_slice_count",
            "slice_presence_ratio": "word2vec_slice_presence_ratio",
            "dominant_pos": "word2vec_dominant_pos",
        }
    )
    merged = merged.merge(
        tfidf_scores[
            [
                "lemma",
                "primary_drift",
                "first_last_drift",
                "slice_count",
                "sample_count_total",
                "sample_count_min",
                "slice_presence_ratio",
                "dominant_pos",
                "tfidf_rank",
            ]
        ].rename(
            columns={
                "primary_drift": "tfidf_primary_drift",
                "first_last_drift": "tfidf_first_last_drift",
                "sample_count_total": "tfidf_sample_count_total",
                "sample_count_min": "tfidf_sample_count_min",
                "slice_count": "tfidf_slice_count",
                "slice_presence_ratio": "tfidf_slice_presence_ratio",
                "dominant_pos": "tfidf_dominant_pos",
            }
        ),
        on="lemma",
        how="outer",
    )

    word2vec_drift = set(w2v_sets["drift_candidates"])
    tfidf_drift = set(tfidf_sets["drift_candidates"])
    word2vec_stable = set(w2v_sets["stable_controls"])
    tfidf_stable = set(tfidf_sets["stable_controls"])
    theory_seeds = set(w2v_sets["theory_seeds"]) | set(tfidf_sets["theory_seeds"])
    selected_terms = (
        word2vec_drift | tfidf_drift | word2vec_stable | tfidf_stable | theory_seeds
    )
    selected_frame = pd.DataFrame({"lemma": sorted(selected_terms)})
    merged = selected_frame.merge(merged, on="lemma", how="left")

    merged["selected_by_word2vec"] = merged["lemma"].isin(word2vec_drift)
    merged["selected_by_tfidf"] = merged["lemma"].isin(tfidf_drift)
    merged["selected_by_contextual"] = False
    merged["selected_as_stable_control_word2vec"] = merged["lemma"].isin(word2vec_stable)
    merged["selected_as_stable_control_tfidf"] = merged["lemma"].isin(tfidf_stable)
    merged["selected_as_stable_control"] = (
        merged["selected_as_stable_control_word2vec"]
        | merged["selected_as_stable_control_tfidf"]
    )
    merged["selected_as_theory_seed"] = merged["lemma"].isin(theory_seeds)
    merged["selected_as_disagreement_case"] = (
        merged["selected_by_word2vec"] ^ merged["selected_by_tfidf"]
    )
    merged["bucket"] = merged.apply(_bucket, axis=1)

    merged["slice_count"] = merged["word2vec_slice_count"].combine_first(
        merged["tfidf_slice_count"]
    )
    merged["total_frequency"] = merged["word2vec_sample_count_total"].combine_first(
        merged["tfidf_sample_count_total"]
    )
    merged["slice_presence_ratio"] = merged["word2vec_slice_presence_ratio"].combine_first(
        merged["tfidf_slice_presence_ratio"]
    )
    merged["dominant_pos"] = merged["word2vec_dominant_pos"].combine_first(
        merged["tfidf_dominant_pos"]
    )

    panel = merged.loc[
        merged[
            [
                "selected_by_word2vec",
                "selected_by_tfidf",
                "selected_as_stable_control",
                "selected_as_theory_seed",
            ]
        ].any(axis=1)
    ].copy()
    panel = panel.sort_values(
        [
            "selected_as_theory_seed",
            "selected_as_stable_control",
            "selected_by_word2vec",
            "selected_by_tfidf",
            "word2vec_rank",
            "tfidf_rank",
        ],
        ascending=[False, False, False, False, True, True],
        na_position="last",
    ).reset_index(drop=True)

    write_dataframe(panel_root / "comparison_panel.parquet", panel)
    write_json(
        panel_root / "summary.json",
        {
            "row_count": int(len(panel)),
            "word2vec_drift_count": int(panel["selected_by_word2vec"].sum()),
            "tfidf_drift_count": int(panel["selected_by_tfidf"].sum()),
            "shared_drift_count": int(
                (panel["selected_by_word2vec"] & panel["selected_by_tfidf"]).sum()
            ),
            "disagreement_count": int(panel["selected_as_disagreement_case"].sum()),
            "stable_control_count": int(panel["selected_as_stable_control"].sum()),
            "theory_seed_count": int(panel["selected_as_theory_seed"].sum()),
            "slice_order": list(w2v_sets["slice_order"]),
            "text_view": cfg.model.text_view,
        },
    )
    return panel
