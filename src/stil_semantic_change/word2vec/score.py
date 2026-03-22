from __future__ import annotations

import logging
from pathlib import Path

import numpy as np
import pandas as pd

from stil_semantic_change.selection import (
    build_candidate_sets,
    candidate_exclusion_flags,
    eligible_vocabulary,
    lemma_pos_summary,
)
from stil_semantic_change.utils.artifacts import write_dataframe, write_json
from stil_semantic_change.utils.config.schema import ExperimentConfig
from stil_semantic_change.word2vec.vector_store import load_vector_store

logger = logging.getLogger(__name__)


def _cosine_distance(left: np.ndarray, right: np.ndarray) -> float:
    denominator = np.linalg.norm(left) * np.linalg.norm(right)
    if denominator == 0:
        return 0.0
    return 1.0 - float(np.dot(left, right) / denominator)


def score_candidates(
    cfg: ExperimentConfig,
    prepared_root: Path,
    aligned_root: Path,
    scores_root: Path,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    slice_summary = pd.read_parquet(prepared_root / "slice_summary.parquet").sort_values("sort_key")
    slice_order = slice_summary["slice_id"].tolist()
    lemma_slice_stats = pd.read_parquet(prepared_root / "lemma_slice_stats.parquet")
    eligible_vocab = eligible_vocabulary(lemma_slice_stats, cfg, total_slices=len(slice_order))
    write_dataframe(scores_root / "eligible_vocabulary.parquet", eligible_vocab)

    eligible_words = set(eligible_vocab.loc[eligible_vocab["eligible"], "lemma"].tolist())
    if not eligible_words:
        raise ValueError("No eligible vocabulary survived the slice-level selection filters")
    lemma_pos = lemma_pos_summary(prepared_root, eligible_words)

    score_rows: list[dict[str, object]] = []
    trajectory_rows: list[dict[str, object]] = []

    for replicate_dir in sorted(
        path
        for path in aligned_root.iterdir()
        if path.is_dir() and path.name.startswith("replicate_")
    ):
        replicate = int(replicate_dir.name.replace("replicate_", ""))
        stores = {
            slice_id: load_vector_store(replicate_dir / slice_id / "vectors")
            for slice_id in slice_order
            if (replicate_dir / slice_id / "vectors.npz").exists()
        }
        first_store = stores[slice_order[0]]
        last_store = stores[slice_order[-1]]
        first_index = first_store.word_to_index
        last_index = last_store.word_to_index

        for word in sorted(eligible_words):
            consecutive_distances: list[float] = []
            for left_slice, right_slice in zip(slice_order[:-1], slice_order[1:], strict=True):
                left_store = stores[left_slice]
                right_store = stores[right_slice]
                left_index = left_store.word_to_index
                right_index = right_store.word_to_index
                if word not in left_index or word not in right_index:
                    continue
                distance = _cosine_distance(
                    left_store.matrix[left_index[word]],
                    right_store.matrix[right_index[word]],
                )
                consecutive_distances.append(distance)
                trajectory_rows.append(
                    {
                        "replicate": replicate,
                        "lemma": word,
                        "from_slice": left_slice,
                        "to_slice": right_slice,
                        "transition": f"{left_slice}->{right_slice}",
                        "drift": distance,
                    }
                )

            if not consecutive_distances:
                continue

            first_last_distance = np.nan
            if word in first_index and word in last_index:
                first_last_distance = _cosine_distance(
                    first_store.matrix[first_index[word]],
                    last_store.matrix[last_index[word]],
                )

            score_rows.append(
                {
                    "replicate": replicate,
                    "lemma": word,
                    "primary_drift": float(np.mean(consecutive_distances)),
                    "first_last_drift": float(first_last_distance),
                    "transition_count": len(consecutive_distances),
                }
            )

    per_replicate = pd.DataFrame(score_rows)
    trajectory = pd.DataFrame(trajectory_rows)
    if per_replicate.empty:
        raise ValueError("No candidate scores were produced")

    summary = (
        per_replicate.groupby("lemma")
        .agg(
            primary_drift_mean=("primary_drift", "mean"),
            primary_drift_std=("primary_drift", "std"),
            first_last_drift_mean=("first_last_drift", "mean"),
            first_last_drift_std=("first_last_drift", "std"),
            replicate_count=("replicate", "nunique"),
            transition_count=("transition_count", "max"),
        )
        .reset_index()
    )
    summary = summary.merge(
        eligible_vocab[
            [
                "lemma",
                "observed_slices",
                "slice_presence_ratio",
                "qualifying_slices",
                "total_frequency",
                "mean_frequency",
                "min_frequency",
                "mean_document_count",
                "min_document_count",
                "min_qualifying_frequency",
                "min_qualifying_document_count",
            ]
        ],
        on="lemma",
        how="left",
    )
    summary = summary.merge(lemma_pos, on="lemma", how="left")
    summary["method"] = "word2vec"
    summary["primary_drift"] = summary["primary_drift_mean"]
    summary["first_last_drift"] = summary["first_last_drift_mean"]
    summary["slice_count"] = summary["qualifying_slices"]
    summary["sample_count_total"] = summary["total_frequency"]
    summary["sample_count_min"] = summary["min_qualifying_frequency"].fillna(
        summary["min_frequency"]
    )
    summary = candidate_exclusion_flags(summary, cfg)
    summary = summary.sort_values("primary_drift_mean", ascending=False).reset_index(drop=True)

    candidate_sets = build_candidate_sets(summary, cfg, slice_order, drift_column="primary_drift")

    write_dataframe(scores_root / "scores_per_replicate.parquet", per_replicate)
    write_dataframe(scores_root / "scores_aggregated.parquet", summary)
    write_dataframe(scores_root / "trajectory.parquet", trajectory)
    write_json(
        scores_root / "candidate_sets.json",
        candidate_sets,
    )
    return summary, trajectory
