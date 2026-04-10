from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import pandas as pd

from stil_semantic_change.preprocessing.views import prepared_content_tokens_dir
from stil_semantic_change.utils.config.schema import ExperimentConfig


def eligible_vocabulary(
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
    stats["qualified_frequency"] = stats["frequency"].where(stats["qualifies"])
    stats["qualified_document_count"] = stats["document_count"].where(stats["qualifies"])

    grouped = (
        stats.groupby("lemma")
        .agg(
            qualifying_slices=("qualifies", "sum"),
            observed_slices=("slice_id", "nunique"),
            total_frequency=("frequency", "sum"),
            mean_frequency=("frequency", "mean"),
            min_frequency=("frequency", "min"),
            mean_document_count=("document_count", "mean"),
            min_document_count=("document_count", "min"),
            min_qualifying_frequency=("qualified_frequency", "min"),
            min_qualifying_document_count=("qualified_document_count", "min"),
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


def candidate_exclusion_flags(summary: pd.DataFrame, cfg: ExperimentConfig) -> pd.DataFrame:
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


def lemma_pos_summary(
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


def build_candidate_sets(
    summary: pd.DataFrame,
    cfg: ExperimentConfig,
    slice_order: list[str],
    *,
    drift_column: str = "primary_drift",
) -> dict[str, object]:
    if drift_column not in summary.columns:
        if "primary_drift_mean" in summary.columns:
            drift_column = "primary_drift_mean"
        else:
            raise KeyError(f"Missing drift column '{drift_column}' in candidate summary")

    seed_set = set(cfg.selection.theory_seeds)
    drift_pool = summary.loc[
        ~summary["lemma"].isin(seed_set) & ~summary["drift_candidate_excluded"]
    ]
    stable_pool = summary.loc[
        ~summary["lemma"].isin(seed_set) & ~summary["stable_control_excluded"]
    ]

    drift_candidates = (
        drift_pool.sort_values(drift_column, ascending=False)
        .head(cfg.selection.top_drift_candidates)["lemma"]
        .tolist()
    )
    stable_controls = (
        stable_pool.sort_values(drift_column, ascending=True)
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
