from __future__ import annotations

import logging
from collections import Counter
from pathlib import Path
from time import perf_counter

import numpy as np
import pandas as pd

from stil_semantic_change.preprocessing.views import prepared_text_view_by_slice_dir
from stil_semantic_change.selection import (
    build_candidate_sets,
    candidate_exclusion_flags,
    eligible_vocabulary,
    lemma_pos_summary,
)
from stil_semantic_change.utils.artifacts import write_dataframe, write_json
from stil_semantic_change.utils.config.schema import ExperimentConfig

logger = logging.getLogger(__name__)

TFIDF_DRIFT_CANDIDATE_EXCLUDE_LEMMAS: tuple[str, ...] = (
    "ano",
    "matéria",
    "medida",
    "nº",
    "sr.",
)
TFIDF_DRIFT_FREQUENCY_QUANTILE = 0.995


def _slice_term_counts(
    prepared_root: Path,
    text_view: str,
    slice_order: list[str],
    eligible_words: set[str],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    text_dir = prepared_text_view_by_slice_dir(prepared_root, text_view)
    rows: list[dict[str, object]] = []
    totals: list[dict[str, object]] = []

    for slice_id in slice_order:
        path = text_dir / f"{slice_id}.txt"
        if not path.exists():
            raise FileNotFoundError(f"Missing prepared text view for slice {slice_id}: {path}")

        counts: Counter[str] = Counter()
        token_total = 0
        with path.open("r", encoding="utf-8") as handle:
            for line in handle:
                tokens = line.strip().split()
                if not tokens:
                    continue
                token_total += len(tokens)
                counts.update(token for token in tokens if token in eligible_words)

        totals.append({"slice_id": slice_id, "slice_token_count": token_total})
        for lemma, frequency in counts.items():
            rows.append({"slice_id": slice_id, "lemma": lemma, "frequency": frequency})

    return pd.DataFrame(rows), pd.DataFrame(totals)


def _apply_tfidf_panel_filters(summary: pd.DataFrame) -> pd.DataFrame:
    filtered = summary.copy()
    frequency_ceiling = float(
        filtered["sample_count_total"].quantile(TFIDF_DRIFT_FREQUENCY_QUANTILE)
    )
    filtered["tfidf_high_frequency_excluded"] = (
        filtered["sample_count_total"] > frequency_ceiling
    )
    filtered["tfidf_lexical_excluded"] = filtered["lemma"].isin(
        TFIDF_DRIFT_CANDIDATE_EXCLUDE_LEMMAS
    )
    filtered["drift_candidate_excluded"] = (
        filtered["drift_candidate_excluded"]
        | filtered["tfidf_high_frequency_excluded"]
        | filtered["tfidf_lexical_excluded"]
    )
    filtered.attrs["tfidf_frequency_ceiling"] = frequency_ceiling
    return filtered


def score_tfidf_drift(
    cfg: ExperimentConfig,
    prepared_root: Path,
    tfidf_root: Path,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    started = perf_counter()
    slice_summary = pd.read_parquet(prepared_root / "slice_summary.parquet").sort_values("sort_key")
    slice_order = slice_summary["slice_id"].tolist()
    lemma_slice_stats = pd.read_parquet(prepared_root / "lemma_slice_stats.parquet")

    eligible_vocab = eligible_vocabulary(lemma_slice_stats, cfg, total_slices=len(slice_order))
    write_dataframe(tfidf_root / "eligible_vocabulary.parquet", eligible_vocab)

    eligible_words = set(eligible_vocab.loc[eligible_vocab["eligible"], "lemma"].tolist())
    if not eligible_words:
        raise ValueError("No eligible vocabulary survived the slice-level selection filters")

    slice_term_counts, slice_totals = _slice_term_counts(
        prepared_root,
        cfg.model.text_view,
        slice_order,
        eligible_words,
    )
    if slice_term_counts.empty:
        raise ValueError("TF-IDF drift scoring found no eligible terms in the prepared text view")

    per_slice = slice_term_counts.merge(slice_totals, on="slice_id", how="left")
    document_frequency = (
        per_slice.groupby("lemma")["slice_id"].nunique().rename("document_frequency").reset_index()
    )
    n_slices = len(slice_order)
    document_frequency["idf"] = (
        np.log((1.0 + n_slices) / (1.0 + document_frequency["document_frequency"])) + 1.0
    )

    per_slice = per_slice.merge(document_frequency, on="lemma", how="left")
    per_slice["tf"] = per_slice["frequency"] / per_slice["slice_token_count"].clip(lower=1)
    per_slice["tfidf"] = per_slice["tf"] * per_slice["idf"]

    weight_map = {
        (str(row.slice_id), str(row.lemma)): float(row.tfidf)
        for row in per_slice.itertuples(index=False)
    }

    summary_rows: list[dict[str, object]] = []
    trajectory_rows: list[dict[str, object]] = []
    for word in sorted(eligible_words):
        weights = [weight_map.get((slice_id, word), 0.0) for slice_id in slice_order]
        consecutive_drift = [
            abs(right - left) for left, right in zip(weights[:-1], weights[1:], strict=True)
        ]
        for left_slice, right_slice, left_weight, right_weight, drift in zip(
            slice_order[:-1],
            slice_order[1:],
            weights[:-1],
            weights[1:],
            consecutive_drift,
            strict=True,
        ):
            trajectory_rows.append(
                {
                    "method": "tfidf_drift",
                    "lemma": word,
                    "from_slice": left_slice,
                    "to_slice": right_slice,
                    "transition": f"{left_slice}->{right_slice}",
                    "left_weight": left_weight,
                    "right_weight": right_weight,
                    "drift": drift,
                }
            )

        summary_rows.append(
            {
                "lemma": word,
                "method": "tfidf_drift",
                "primary_drift": float(np.mean(consecutive_drift)),
                "first_last_drift": float(abs(weights[-1] - weights[0])),
            }
        )

    summary = pd.DataFrame(summary_rows)
    trajectory = pd.DataFrame(trajectory_rows)
    lemma_pos = lemma_pos_summary(prepared_root, eligible_words)
    runtime_seconds = round(perf_counter() - started, 3)

    summary = summary.merge(
        eligible_vocab[
            [
                "lemma",
                "qualifying_slices",
                "observed_slices",
                "slice_presence_ratio",
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
    summary = summary.rename(
        columns={
            "qualifying_slices": "slice_count",
            "total_frequency": "sample_count_total",
            "min_qualifying_frequency": "sample_count_min",
        }
    )
    summary["sample_count_min"] = summary["sample_count_min"].fillna(summary["min_frequency"])
    summary["runtime_seconds"] = runtime_seconds
    summary = summary.merge(lemma_pos, on="lemma", how="left")
    summary = candidate_exclusion_flags(summary, cfg)
    summary = _apply_tfidf_panel_filters(summary)
    summary = summary.sort_values("primary_drift", ascending=False).reset_index(drop=True)

    candidate_sets = build_candidate_sets(summary, cfg, slice_order, drift_column="primary_drift")
    write_dataframe(tfidf_root / "scores.parquet", summary)
    write_dataframe(tfidf_root / "trajectory.parquet", trajectory)
    write_json(tfidf_root / "candidate_sets.json", candidate_sets)
    write_json(
        tfidf_root / "summary.json",
        {
            "method": "tfidf_drift",
            "text_view": cfg.model.text_view,
            "slice_order": slice_order,
            "scored_terms": int(len(summary)),
            "trajectory_rows": int(len(trajectory)),
            "runtime_seconds": runtime_seconds,
            "tfidf_frequency_ceiling": summary.attrs["tfidf_frequency_ceiling"],
            "tfidf_drift_candidate_exclude_lemmas": list(TFIDF_DRIFT_CANDIDATE_EXCLUDE_LEMMAS),
            "drift_candidates": candidate_sets["drift_candidates"],
            "stable_controls": candidate_sets["stable_controls"],
            "theory_seeds": candidate_sets["theory_seeds"],
        },
    )
    logger.info(
        "Scored TF-IDF drift for %d eligible lemmas across %d slices using %s",
        len(summary),
        len(slice_order),
        cfg.model.text_view,
    )
    return summary, trajectory
