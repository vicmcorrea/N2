from __future__ import annotations

import logging
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import pandas as pd

from stil_semantic_change.preprocessing.views import prepared_content_tokens_dir
from stil_semantic_change.utils.artifacts import write_dataframe, write_json
from stil_semantic_change.utils.config.schema import ExperimentConfig
from stil_semantic_change.word2vec.vector_store import load_vector_store

logger = logging.getLogger(__name__)


def _cosine_distance(left: np.ndarray, right: np.ndarray) -> float:
    denominator = np.linalg.norm(left) * np.linalg.norm(right)
    if denominator == 0:
        return 0.0
    return 1.0 - float(np.dot(left, right) / denominator)


def _eligible_vocabulary(
    lemma_slice_stats: pd.DataFrame,
    cfg: ExperimentConfig,
    total_slices: int,
) -> pd.DataFrame:
    stats = lemma_slice_stats.copy()
    excluded = set(cfg.selection.exclude_lemmas)
    stats["qualifies"] = (
        (stats["frequency"] >= cfg.selection.min_occurrences_per_slice)
        & (stats["document_count"] >= cfg.selection.min_documents_per_slice)
    )

    grouped = (
        stats.groupby("lemma")
        .agg(
            qualifying_slices=("qualifies", "sum"),
            total_frequency=("frequency", "sum"),
            mean_frequency=("frequency", "mean"),
            mean_document_count=("document_count", "mean"),
        )
        .reset_index()
    )
    grouped["slice_presence_ratio"] = grouped["qualifying_slices"] / float(total_slices)
    grouped["has_whitespace"] = grouped["lemma"].str.contains(r"\s", regex=True, na=False)
    grouped["excluded"] = grouped["has_whitespace"] | grouped["lemma"].isin(excluded)
    grouped["eligible"] = (
        (grouped["slice_presence_ratio"] >= cfg.selection.min_slice_presence_ratio)
        & ~grouped["excluded"]
    )
    return grouped.sort_values(
        ["eligible", "excluded", "slice_presence_ratio", "total_frequency"],
        ascending=[False, True, False, False],
    )


def _candidate_exclusion_flags(summary: pd.DataFrame, cfg: ExperimentConfig) -> pd.DataFrame:
    annotated = summary.copy()
    base_excluded = set(cfg.selection.exclude_lemmas)
    drift_excluded = base_excluded | set(cfg.selection.drift_candidate_exclude_lemmas)
    stable_excluded = base_excluded | set(cfg.selection.stable_control_exclude_lemmas)
    drift_allowed_pos = set(cfg.selection.drift_candidate_allowed_pos)
    stable_allowed_pos = set(cfg.selection.stable_control_allowed_pos)
    drift_disallowed_pos = (
        ~annotated["dominant_pos"].isin(drift_allowed_pos)
        if drift_allowed_pos
        else pd.Series(False, index=annotated.index)
    )
    stable_disallowed_pos = (
        ~annotated["dominant_pos"].isin(stable_allowed_pos)
        if stable_allowed_pos
        else pd.Series(False, index=annotated.index)
    )
    annotated["drift_candidate_excluded"] = (
        annotated["lemma"].isin(drift_excluded) | drift_disallowed_pos
    )
    annotated["stable_control_excluded"] = (
        annotated["lemma"].isin(stable_excluded) | stable_disallowed_pos
    )
    return annotated


def _lemma_pos_summary(
    prepared_root: Path,
    eligible_words: set[str],
) -> pd.DataFrame:
    tokens_dir = prepared_content_tokens_dir(prepared_root)
    pos_counts: dict[str, Counter[str]] = defaultdict(Counter)

    for shard_path in sorted(tokens_dir.glob("batch_*.parquet")):
        shard = pd.read_parquet(shard_path, columns=["lemma", "pos"])
        shard = shard.loc[shard["lemma"].isin(eligible_words)]
        if shard.empty:
            continue
        grouped = shard.groupby(["lemma", "pos"]).size()
        for (lemma, pos), count in grouped.items():
            pos_counts[str(lemma)][str(pos)] += int(count)

    rows: list[dict[str, object]] = []
    for lemma in sorted(eligible_words):
        counts = pos_counts.get(lemma, Counter())
        if not counts:
            rows.append(
                {
                    "lemma": lemma,
                    "dominant_pos": None,
                    "dominant_pos_count": 0,
                    "lemma_token_count": 0,
                    "dominant_pos_share": np.nan,
                }
            )
            continue
        dominant_pos, dominant_count = counts.most_common(1)[0]
        total_count = sum(counts.values())
        rows.append(
            {
                "lemma": lemma,
                "dominant_pos": dominant_pos,
                "dominant_pos_count": dominant_count,
                "lemma_token_count": total_count,
                "dominant_pos_share": dominant_count / float(total_count),
            }
        )
    return pd.DataFrame(rows)


def _build_candidate_sets(
    summary: pd.DataFrame,
    cfg: ExperimentConfig,
    slice_order: list[str],
) -> dict[str, object]:
    seed_set = set(cfg.selection.theory_seeds)
    drift_pool = summary.loc[
        ~summary["lemma"].isin(seed_set) & ~summary["drift_candidate_excluded"]
    ]
    stable_pool = summary.loc[
        ~summary["lemma"].isin(seed_set) & ~summary["stable_control_excluded"]
    ]

    drift_candidates = drift_pool.head(cfg.selection.top_drift_candidates)["lemma"].tolist()
    stable_controls = (
        stable_pool.sort_values("primary_drift_mean", ascending=True)
        .head(cfg.selection.top_stable_controls)["lemma"]
        .tolist()
    )
    seeds = [seed for seed in cfg.selection.theory_seeds if seed in set(summary["lemma"].tolist())]

    return {
        "drift_candidates": drift_candidates,
        "stable_controls": stable_controls,
        "theory_seeds": seeds[: cfg.selection.top_seed_terms],
        "slice_order": slice_order,
    }


def score_candidates(
    cfg: ExperimentConfig,
    prepared_root: Path,
    aligned_root: Path,
    scores_root: Path,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    slice_summary = pd.read_parquet(prepared_root / "slice_summary.parquet").sort_values("sort_key")
    slice_order = slice_summary["slice_id"].tolist()
    lemma_slice_stats = pd.read_parquet(prepared_root / "lemma_slice_stats.parquet")
    eligible_vocab = _eligible_vocabulary(lemma_slice_stats, cfg, total_slices=len(slice_order))
    write_dataframe(scores_root / "eligible_vocabulary.parquet", eligible_vocab)

    eligible_words = set(eligible_vocab.loc[eligible_vocab["eligible"], "lemma"].tolist())
    if not eligible_words:
        raise ValueError("No eligible vocabulary survived the slice-level selection filters")
    lemma_pos = _lemma_pos_summary(prepared_root, eligible_words)

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
                "slice_presence_ratio",
                "qualifying_slices",
                "total_frequency",
                "mean_frequency",
                "mean_document_count",
            ]
        ],
        on="lemma",
        how="left",
    )
    summary = summary.merge(lemma_pos, on="lemma", how="left")
    summary = _candidate_exclusion_flags(summary, cfg)
    summary = summary.sort_values("primary_drift_mean", ascending=False).reset_index(drop=True)

    candidate_sets = _build_candidate_sets(summary, cfg, slice_order)

    write_dataframe(scores_root / "scores_per_replicate.parquet", per_replicate)
    write_dataframe(scores_root / "scores_aggregated.parquet", summary)
    write_dataframe(scores_root / "trajectory.parquet", trajectory)
    write_json(
        scores_root / "candidate_sets.json",
        candidate_sets,
    )
    return summary, trajectory
