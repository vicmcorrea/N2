from __future__ import annotations

import pandas as pd

from stil_semantic_change.contextual.qwen3_posthoc import (
    _build_agreement_frame,
    _build_bucket_summary_frame,
    _build_frequency_sensitivity_frame,
    _build_stable_control_leakage_frame,
)


def _comparison_frame() -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    buckets = [
        "word2vec_only_drift",
        "word2vec_only_drift",
        "tfidf_only_drift",
        "stable_control",
        "stable_control",
        "theory_seed",
    ]
    for layer in (-4, -1):
        for index, bucket in enumerate(buckets, start=1):
            rows.append(
                {
                    "layer": layer,
                    "lemma": f"{bucket}_{index}_{layer}",
                    "qwen_primary_drift": 0.10 - (index * 0.01) + (0.001 * abs(layer)),
                    "qwen_rank": index,
                    "word2vec_primary_drift": 0.20 - (index * 0.01),
                    "word2vec_rank": index,
                    "tfidf_primary_drift": 0.02 + (index * 0.001),
                    "tfidf_rank": len(buckets) - index + 1,
                    "bert_primary_drift": 0.08 - (index * 0.005),
                    "bert_rank": index + 1,
                    "embeddinggemma_primary_drift": 0.03 + (index * 0.002),
                    "embeddinggemma_rank": index + 2,
                    "selected_as_stable_control": bucket == "stable_control",
                    "selected_as_theory_seed": bucket == "theory_seed",
                    "bucket": bucket,
                    "total_frequency": 100 * index,
                }
            )
    return pd.DataFrame(rows)


def test_build_agreement_frame_has_qwen_pairs() -> None:
    frame = _build_agreement_frame(_comparison_frame())
    pairs = set(frame["pair"].dropna().tolist())
    assert "qwen_vs_word2vec" in pairs
    assert "qwen_vs_tfidf" in pairs
    assert "qwen_vs_bert" in pairs
    assert "qwen_vs_embeddinggemma" in pairs


def test_bucket_summary_counts_top_k() -> None:
    frame = _build_bucket_summary_frame(_comparison_frame(), top_k=3)
    preferred = frame.loc[(frame["layer"] == -1) & (frame["bucket"] == "stable_control")].iloc[0]
    assert int(preferred["count"]) == 2
    assert int(preferred["top_k_count"]) == 0


def test_stable_control_leakage_flags_top_k() -> None:
    frame = _build_stable_control_leakage_frame(_comparison_frame(), top_k=4)
    stable = frame.loc[(frame["layer"] == -1) & frame["selected_as_stable_control"]]
    assert stable["leaks_into_top_k"].tolist() == [True, False]


def test_frequency_sensitivity_rows_exist() -> None:
    frame = _build_frequency_sensitivity_frame(_comparison_frame())
    subsets = set(frame["subset"].tolist())
    assert "all_panel" in subsets
    assert "stable_control" in subsets
