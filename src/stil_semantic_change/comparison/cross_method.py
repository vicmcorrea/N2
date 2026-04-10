from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd
from scipy.stats import pearsonr, spearmanr

from stil_semantic_change.utils.artifacts import write_dataframe, write_json

DEFAULT_TOP_K_VALUES = (5, 10, 15)
DEFAULT_BERT_PREFERRED_LAYER = -1
FILTERED_BERT_EXCLUDED_BUCKETS = frozenset({"stable_control"})


def _top_k_overlap(frame: pd.DataFrame, rank_col_a: str, rank_col_b: str, k: int) -> int:
    valid = frame.dropna(subset=[rank_col_a, rank_col_b])
    if len(valid) < k:
        return 0
    top_a = set(valid.nsmallest(k, rank_col_a)["lemma"].tolist())
    top_b = set(valid.nsmallest(k, rank_col_b)["lemma"].tolist())
    return len(top_a & top_b)


def _jaccard_from_overlap(overlap: int, k: int) -> float:
    denominator = (2 * k) - overlap
    if denominator <= 0:
        return 0.0
    return float(overlap / denominator)


def _correlation_pair(frame: pd.DataFrame, x: str, y: str) -> dict[str, float | int | None]:
    valid = frame[[x, y]].dropna()
    if len(valid) < 3:
        return {
            "n": int(len(valid)),
            "spearman_r": None,
            "spearman_p": None,
            "pearson_r": None,
            "pearson_p": None,
        }
    spearman_r, spearman_p = spearmanr(valid[x], valid[y])
    pearson_r, pearson_p = pearsonr(valid[x], valid[y])
    return {
        "n": int(len(valid)),
        "spearman_r": float(spearman_r),
        "spearman_p": float(spearman_p),
        "pearson_r": float(pearson_r),
        "pearson_p": float(pearson_p),
    }


def _assign_bert_ranks(frame: pd.DataFrame) -> pd.DataFrame:
    ranked_frames: list[pd.DataFrame] = []
    for _layer, sub in frame.groupby("layer", sort=True):
        ranked = sub.sort_values("primary_drift", ascending=False).reset_index(drop=True).copy()
        ranked["bert_rank"] = ranked.index + 1
        ranked["bert_filtered_candidate"] = ~ranked["bucket"].isin(FILTERED_BERT_EXCLUDED_BUCKETS)
        ranked["bert_filter_reason"] = ranked["bucket"].where(
            ~ranked["bert_filtered_candidate"],
            other="",
        )
        ranked_frames.append(ranked)
    return pd.concat(ranked_frames, ignore_index=True)


def _build_overlap_rows(
    frame: pd.DataFrame,
    *,
    layer: int,
    subset_name: str,
    top_k_values: tuple[int, ...],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for k in top_k_values:
        bert_word2vec_overlap = _top_k_overlap(frame, "bert_rank", "word2vec_rank", k)
        bert_tfidf_overlap = _top_k_overlap(frame, "bert_rank", "tfidf_rank", k)
        word2vec_tfidf_overlap = _top_k_overlap(frame, "word2vec_rank", "tfidf_rank", k)
        rows.append(
            {
                "layer": int(layer),
                "subset": subset_name,
                "k": int(k),
                "bert_word2vec_topk_overlap": bert_word2vec_overlap,
                "bert_word2vec_jaccard": _jaccard_from_overlap(bert_word2vec_overlap, k),
                "bert_tfidf_topk_overlap": bert_tfidf_overlap,
                "bert_tfidf_jaccard": _jaccard_from_overlap(bert_tfidf_overlap, k),
                "word2vec_tfidf_topk_overlap": word2vec_tfidf_overlap,
                "word2vec_tfidf_jaccard": _jaccard_from_overlap(word2vec_tfidf_overlap, k),
            }
        )
    return rows


def _build_correlation_rows(
    frame: pd.DataFrame,
    *,
    layer: int,
    subset_name: str,
) -> list[dict[str, Any]]:
    metric_pairs = {
        "bert_vs_word2vec": ("primary_drift", "word2vec_primary_drift"),
        "bert_vs_tfidf": ("primary_drift", "tfidf_primary_drift"),
        "word2vec_vs_tfidf": ("word2vec_primary_drift", "tfidf_primary_drift"),
    }
    rows: list[dict[str, Any]] = []
    for label, (left, right) in metric_pairs.items():
        stats = _correlation_pair(frame, left, right)
        rows.append(
            {
                "layer": int(layer),
                "subset": subset_name,
                "pair": label,
                **stats,
            }
        )
    return rows


def write_cross_method_agreement(
    scores_root: Path,
    *,
    preferred_layer: int = DEFAULT_BERT_PREFERRED_LAYER,
    top_k_values: tuple[int, ...] = DEFAULT_TOP_K_VALUES,
) -> Path:
    comp_path = scores_root / "bert_confirmatory" / "comparison_with_word2vec.parquet"
    if not comp_path.exists():
        raise FileNotFoundError(f"Missing BERT comparison table: {comp_path}")

    frame = pd.read_parquet(comp_path)
    frame = _assign_bert_ranks(frame)

    out = scores_root / "cross_method_agreement"
    out.mkdir(parents=True, exist_ok=True)

    correlation_rows: list[dict[str, Any]] = []
    overlap_rows: list[dict[str, Any]] = []

    for layer in sorted(frame["layer"].unique()):
        layer_frame = frame.loc[frame["layer"] == layer].copy()
        correlation_rows.extend(
            _build_correlation_rows(layer_frame, layer=int(layer), subset_name="all_panel")
        )
        overlap_rows.extend(
            _build_overlap_rows(
                layer_frame,
                layer=int(layer),
                subset_name="all_panel",
                top_k_values=top_k_values,
            )
        )

        disagreement_frame = layer_frame.loc[
            layer_frame["selected_as_disagreement_case"].fillna(False)
        ].copy()
        if len(disagreement_frame) >= 3:
            correlation_rows.extend(
                _build_correlation_rows(
                    disagreement_frame,
                    layer=int(layer),
                    subset_name="disagreement_cases",
                )
            )
            overlap_rows.extend(
                _build_overlap_rows(
                    disagreement_frame,
                    layer=int(layer),
                    subset_name="disagreement_cases",
                    top_k_values=top_k_values,
                )
            )

    correlation_frame = pd.DataFrame(correlation_rows)
    overlap_frame = pd.DataFrame(overlap_rows)
    write_dataframe(out / "correlations.parquet", correlation_frame)
    write_dataframe(out / "topk_overlap.parquet", overlap_frame)

    ranked_panel = frame.sort_values(["layer", "bert_rank"]).reset_index(drop=True)
    write_dataframe(out / "bert_ranked_panel.parquet", ranked_panel)

    preferred_frame = ranked_panel.loc[ranked_panel["layer"] == preferred_layer].copy()
    if preferred_frame.empty:
        raise ValueError(
            f"Preferred BERT layer {preferred_layer} was not found in the comparison table"
        )

    filtered_panel = preferred_frame.loc[preferred_frame["bert_filtered_candidate"]].copy()
    filtered_panel = filtered_panel.sort_values("bert_rank").reset_index(drop=True)
    write_dataframe(out / "bert_filtered_panel.parquet", filtered_panel)

    stable_leakage = preferred_frame.loc[
        preferred_frame["selected_as_stable_control"].fillna(False)
    ].copy()
    stable_leakage = stable_leakage.sort_values("bert_rank").reset_index(drop=True)
    write_dataframe(out / "bert_stable_control_leakage.parquet", stable_leakage)

    largest_word2vec_gap = preferred_frame.copy()
    largest_word2vec_gap["abs_bert_word2vec_gap"] = largest_word2vec_gap["bert_word2vec_gap"].abs()
    largest_word2vec_gap = largest_word2vec_gap.sort_values(
        "abs_bert_word2vec_gap", ascending=False
    )
    write_dataframe(out / "largest_bert_word2vec_gap.parquet", largest_word2vec_gap.head(24))

    largest_tfidf_gap = preferred_frame.copy()
    largest_tfidf_gap["abs_bert_tfidf_gap"] = largest_tfidf_gap["bert_tfidf_gap"].abs()
    largest_tfidf_gap = largest_tfidf_gap.sort_values("abs_bert_tfidf_gap", ascending=False)
    write_dataframe(out / "largest_bert_tfidf_gap.parquet", largest_tfidf_gap.head(24))

    filtered_candidates = filtered_panel["lemma"].tolist()
    stable_controls = stable_leakage["lemma"].tolist()
    theory_seeds = preferred_frame.loc[
        preferred_frame["selected_as_theory_seed"].fillna(False),
        "lemma",
    ].tolist()
    summary: dict[str, Any] = {
        "comparison_source": str(comp_path),
        "preferred_layer": int(preferred_layer),
        "top_k_values": [int(k) for k in top_k_values],
        "panel_lemmas": int(preferred_frame["lemma"].nunique()),
        "layers": [int(x) for x in sorted(frame["layer"].unique())],
        "filtered_bert_candidate_count": int(len(filtered_panel)),
        "stable_control_leakage_count": int(len(stable_leakage)),
        "filtered_bert_top_terms": filtered_candidates[:15],
        "stable_control_leakage_top_terms": stable_controls[:10],
        "theory_seed_terms": theory_seeds,
    }
    write_json(out / "summary.json", summary)
    write_json(
        out / "bert_candidate_sets.json",
        {
            "preferred_layer": int(preferred_layer),
            "drift_candidates": filtered_candidates[:15],
            "stable_controls": stable_controls[:10],
            "theory_seeds": theory_seeds,
        },
    )
    return out
