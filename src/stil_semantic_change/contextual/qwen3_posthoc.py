"""Post-hoc Qwen3 token-level comparator on frozen shared-panel contexts.

This module reuses the frozen BERT confirmatory sample set and token-aligned
window logic, but swaps in Qwen3 hidden-state extraction. The goal is a
supplementary off-tree run that mirrors the frozen BERT protocol as closely as
possible without mutating the original Hydra experiment outputs.
"""

from __future__ import annotations

import json
import logging
from collections.abc import Iterable
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from omegaconf import OmegaConf
from scipy.stats import mannwhitneyu, pearsonr, spearmanr
from transformers import AutoModel, AutoTokenizer

from stil_semantic_change.contextual.confirmatory import (
    CONTEXT_WINDOW_TOKENS,
    MAX_SEQUENCE_LENGTH,
    ContextExample,
    _build_prototypes,
    _load_document_texts,
    _resolve_device,
    score_prototype_distances,
)
from stil_semantic_change.preprocessing.text import PortuguesePreprocessor
from stil_semantic_change.utils.config.schema import PreprocessConfig

logger = logging.getLogger(__name__)

DEFAULT_MODEL_ID = "Qwen/Qwen3-Embedding-0.6B"
DEFAULT_LOCAL_MODEL_PATH = Path(
    "/Users/victor/.cache/huggingface/hub/models--Qwen--Qwen3-Embedding-0.6B/"
    "snapshots/c54f2e6e80b2d7b7de06f51cec4959f6b3e03418"
)
DEFAULT_LAYERS = (-1, -4)
DEFAULT_BATCH_SIZE = 8
DEFAULT_PREFERRED_LAYER = -1
DEFAULT_TOP_K_VALUES = (5, 10, 15)
DEFAULT_SUMMARY_TOP_K = 15
DEFAULT_LEAKAGE_TOP_K = 20
DEFAULT_BUCKET_ORDER = (
    "word2vec_only_drift",
    "tfidf_only_drift",
    "stable_control",
    "theory_seed",
)


def _load_preprocess_config(project_root: Path) -> PreprocessConfig:
    raw_cfg = OmegaConf.load(project_root / "run" / "conf" / "preprocess" / "default.yaml")
    return PreprocessConfig(
        spacy_model=str(raw_cfg.spacy_model),
        fallback_to_blank=bool(raw_cfg.fallback_to_blank),
        lowercase=bool(raw_cfg.lowercase),
        preserve_accents=bool(raw_cfg.preserve_accents),
        keep_pos=tuple(str(value) for value in raw_cfg.keep_pos),
        exclude_pos=tuple(str(value) for value in raw_cfg.exclude_pos),
        remove_stopwords=bool(raw_cfg.remove_stopwords),
        remove_punctuation=bool(raw_cfg.remove_punctuation),
        remove_numeric=bool(raw_cfg.remove_numeric),
        min_token_length=int(raw_cfg.min_token_length),
        batch_size=int(raw_cfg.batch_size),
        n_process=int(raw_cfg.get("n_process", 6)),
    )


def _validate_output_root(frozen_run_root: Path, output_root: Path) -> None:
    frozen_resolved = frozen_run_root.resolve()
    output_resolved = output_root.resolve()
    if frozen_resolved == output_resolved or frozen_resolved in output_resolved.parents:
        raise ValueError("Qwen3 post-hoc outputs must not be written inside the frozen run root")


def _load_frozen_inputs(
    frozen_run_root: Path,
    embeddinggemma_root: Path,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, dict, list[str]]:
    scores_root = frozen_run_root / "scores"
    bert_root = scores_root / "bert_confirmatory"
    panel_root = scores_root / "comparison_panel"

    samples = pd.read_parquet(bert_root / "sampled_occurrences.parquet")
    panel = pd.read_parquet(panel_root / "comparison_panel.parquet")
    bert_scores = pd.read_parquet(bert_root / "scores.parquet")
    embeddinggemma_comparison = pd.read_parquet(embeddinggemma_root / "comparison.parquet")
    bert_summary = json.loads((bert_root / "summary.json").read_text(encoding="utf-8"))
    panel_summary = json.loads((panel_root / "summary.json").read_text(encoding="utf-8"))
    slice_order = [str(slice_id) for slice_id in panel_summary["slice_order"]]
    return (
        samples,
        panel,
        bert_scores,
        embeddinggemma_comparison,
        bert_summary,
        slice_order,
    )


def _build_context_examples_from_frozen_samples(
    *,
    frozen_run_root: Path,
    samples: pd.DataFrame,
    project_root: Path,
) -> list[ContextExample]:
    prepared_root = frozen_run_root / "prepared"
    logger.info("Loading raw texts for %d sampled occurrences", len(samples))
    raw_texts = _load_document_texts(prepared_root, set(samples["doc_id"].astype(str)))
    logger.info("Loaded %d raw documents for context reconstruction", len(raw_texts))
    preprocessor = PortuguesePreprocessor(_load_preprocess_config(project_root))
    logger.info("Reconstructing token-aligned context windows from frozen samples")

    examples: list[ContextExample] = []
    total_rows = len(samples)
    for index, (doc_id, group) in enumerate(samples.groupby("doc_id", sort=False), start=1):
        words = preprocessor.tokenize_text(raw_texts[str(doc_id)])
        if index % 5000 == 0:
            logger.info("Tokenized %d documents while rebuilding contexts", index)
        for row in group.itertuples(index=False):
            token_index = int(row.token_index)
            if token_index >= len(words):
                continue
            start = max(0, token_index - CONTEXT_WINDOW_TOKENS)
            end = min(len(words), token_index + CONTEXT_WINDOW_TOKENS + 1)
            context_words = words[start:end]
            target_index = token_index - start
            if not context_words or not (0 <= target_index < len(context_words)):
                continue
            examples.append(
                ContextExample(
                    occurrence_id=int(row.occurrence_id),
                    lemma=str(row.lemma),
                    slice_id=str(row.slice_id),
                    doc_id=str(doc_id),
                    token_index=token_index,
                    context_words=context_words,
                    target_index=target_index,
                    source_file=str(row.source_file) if pd.notna(row.source_file) else None,
                )
            )
        if len(examples) % 10000 == 0 and examples:
            logger.info("Prepared %d / %d context examples", len(examples), total_rows)

    if not examples:
        raise ValueError("Could not reconstruct any token-level context windows")
    logger.info("Built %d token-aligned context examples", len(examples))
    return examples


def _batched(values: Iterable[ContextExample], batch_size: int) -> Iterable[list[ContextExample]]:
    batch: list[ContextExample] = []
    for value in values:
        batch.append(value)
        if len(batch) >= batch_size:
            yield batch
            batch = []
    if batch:
        yield batch


def _embed_occurrences(
    *,
    examples: list[ContextExample],
    tokenizer,
    model,
    layers: tuple[int, ...],
    batch_size: int,
    device: str,
) -> tuple[pd.DataFrame, dict[int, np.ndarray]]:
    occurrence_rows: list[dict[str, object]] = []
    layer_vectors: dict[int, list[np.ndarray]] = {int(layer): [] for layer in layers}
    layer_stack = getattr(model, "layers", None)
    if layer_stack is None:
        layer_stack = getattr(getattr(model, "model", None), "layers", None)
    if layer_stack is None:
        raise ValueError("Could not locate transformer layers for Qwen3 hook-based extraction")

    resolved_layers = {
        int(layer): (
            int(layer)
            if int(layer) >= 0
            else int(model.config.num_hidden_layers) + int(layer)
        )
        for layer in layers
    }
    last_layer_index = int(model.config.num_hidden_layers) - 1

    total_batches = (len(examples) + max(1, batch_size) - 1) // max(1, batch_size)
    for batch_index, batch in enumerate(_batched(examples, max(1, batch_size)), start=1):
        batch_encoding = tokenizer(
            [item.context_words for item in batch],
            is_split_into_words=True,
            padding=True,
            truncation=True,
            max_length=MAX_SEQUENCE_LENGTH,
            return_tensors="pt",
        )
        encoded = {key: value.to(device) for key, value in batch_encoding.items()}
        captured_layers: dict[int, torch.Tensor] = {}
        handles = []

        def _hook_factory(
            layer_alias: int,
            layer_store: dict[int, torch.Tensor],
        ):
            def _hook(_module, _inputs, output):
                tensor = output[0] if isinstance(output, tuple) else output
                layer_store[layer_alias] = tensor

            return _hook

        for layer_alias, resolved_index in resolved_layers.items():
            if resolved_index == last_layer_index:
                continue
            handles.append(
                layer_stack[resolved_index].register_forward_hook(
                    _hook_factory(layer_alias, captured_layers)
                )
            )
        with torch.inference_mode():
            outputs = model(**encoded, output_hidden_states=False)
        for handle in handles:
            handle.remove()
        for layer_alias, resolved_index in resolved_layers.items():
            if resolved_index == last_layer_index:
                captured_layers[layer_alias] = outputs.last_hidden_state
        if set(captured_layers) != set(resolved_layers):
            raise ValueError("Did not capture every requested Qwen3 layer")

        for item_index, item in enumerate(batch):
            token_word_ids = batch_encoding.word_ids(batch_index=item_index)
            positions = [
                idx
                for idx, word_id in enumerate(token_word_ids)
                if word_id == item.target_index
            ]
            if not positions:
                continue

            row = {
                "occurrence_id": item.occurrence_id,
                "lemma": item.lemma,
                "slice_id": item.slice_id,
                "doc_id": item.doc_id,
                "token_index": item.token_index,
                "source_file": item.source_file,
                "subword_count": len(positions),
            }
            for layer in layers:
                vector = (
                    captured_layers[int(layer)][item_index, positions, :]
                    .mean(dim=0)
                    .to(torch.float32)
                    .detach()
                    .cpu()
                    .numpy()
                    .astype(np.float32)
                )
                layer_vectors[int(layer)].append(vector)
            occurrence_rows.append(row)

        if batch_index == 1 or batch_index % 10 == 0 or batch_index == total_batches:
            logger.info("Embedded %d / %d batches", batch_index, total_batches)

    occurrence_meta = pd.DataFrame(occurrence_rows)
    stacked_layers = {
        layer: np.stack(vectors, axis=0)
        if vectors
        else np.empty((0, model.config.hidden_size), dtype=np.float32)
        for layer, vectors in layer_vectors.items()
    }
    return occurrence_meta, stacked_layers


def _rank_within_layer(frame: pd.DataFrame, value_col: str, rank_col: str) -> pd.DataFrame:
    ranked_frames: list[pd.DataFrame] = []
    for _layer, sub in frame.groupby("layer", sort=True):
        ranked = sub.sort_values(value_col, ascending=False).reset_index(drop=True).copy()
        ranked[rank_col] = ranked.index + 1
        ranked_frames.append(ranked)
    return pd.concat(ranked_frames, ignore_index=True)


def _top_k_overlap(frame: pd.DataFrame, left_rank: str, right_rank: str, k: int) -> int:
    valid = frame.dropna(subset=[left_rank, right_rank])
    if len(valid) < k:
        return 0
    top_left = set(valid.nsmallest(k, left_rank)["lemma"].tolist())
    top_right = set(valid.nsmallest(k, right_rank)["lemma"].tolist())
    return len(top_left & top_right)


def _correlation_row(frame: pd.DataFrame, left: str, right: str) -> dict[str, object]:
    valid = frame[[left, right]].dropna()
    if len(valid) < 3:
        return {
            "n": int(len(valid)),
            "spearman_r": None,
            "spearman_p": None,
            "pearson_r": None,
            "pearson_p": None,
        }
    spearman_r, spearman_p = spearmanr(valid[left], valid[right])
    pearson_r, pearson_p = pearsonr(valid[left], valid[right])
    return {
        "n": int(len(valid)),
        "spearman_r": float(spearman_r),
        "spearman_p": float(spearman_p),
        "pearson_r": float(pearson_r),
        "pearson_p": float(pearson_p),
    }


def _bert_layer_frame(bert_scores: pd.DataFrame, layer: int) -> pd.DataFrame:
    frame = bert_scores.loc[bert_scores["layer"] == layer].copy()
    frame = frame.sort_values("primary_drift", ascending=False).reset_index(drop=True)
    frame["bert_rank"] = frame.index + 1
    return frame.rename(
        columns={
            "primary_drift": "bert_primary_drift",
            "first_last_drift": "bert_first_last_drift",
            "sample_count_total": "bert_sample_count_total",
            "sample_count_min": "bert_sample_count_min",
        }
    )


def _build_comparison_frame(
    *,
    qwen_scores: pd.DataFrame,
    panel: pd.DataFrame,
    bert_scores: pd.DataFrame,
    embeddinggemma_comparison: pd.DataFrame,
    preferred_bert_layer: int,
) -> pd.DataFrame:
    panel_columns = [
        "lemma",
        "bucket",
        "word2vec_rank",
        "word2vec_primary_drift",
        "word2vec_first_last_drift",
        "tfidf_rank",
        "tfidf_primary_drift",
        "tfidf_first_last_drift",
        "selected_by_word2vec",
        "selected_by_tfidf",
        "selected_as_stable_control",
        "selected_as_theory_seed",
        "selected_as_disagreement_case",
        "slice_count",
        "total_frequency",
        "slice_presence_ratio",
        "dominant_pos",
    ]
    comparison = _rank_within_layer(qwen_scores, "primary_drift", "qwen_rank")
    comparison = comparison.rename(
        columns={
            "primary_drift": "qwen_primary_drift",
            "first_last_drift": "qwen_first_last_drift",
            "sample_count_total": "qwen_sample_count_total",
            "sample_count_min": "qwen_sample_count_min",
        }
    )
    comparison = comparison.merge(panel[panel_columns], on="lemma", how="left")

    bert_preferred = _bert_layer_frame(bert_scores, preferred_bert_layer)
    comparison = comparison.merge(
        bert_preferred[
            [
                "lemma",
                "bert_rank",
                "bert_primary_drift",
                "bert_first_last_drift",
                "bert_sample_count_total",
                "bert_sample_count_min",
            ]
        ],
        on="lemma",
        how="left",
    )

    gemma = embeddinggemma_comparison[
        [
            "lemma",
            "embeddinggemma_rank",
            "embeddinggemma_primary_drift",
            "embeddinggemma_first_last_drift",
        ]
    ].copy()
    comparison = comparison.merge(gemma, on="lemma", how="left")
    return comparison


def _build_agreement_frame(comparison: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    metric_pairs = {
        "qwen_vs_word2vec": (
            "qwen_primary_drift",
            "word2vec_primary_drift",
            "qwen_rank",
            "word2vec_rank",
        ),
        "qwen_vs_tfidf": (
            "qwen_primary_drift",
            "tfidf_primary_drift",
            "qwen_rank",
            "tfidf_rank",
        ),
        "qwen_vs_bert": (
            "qwen_primary_drift",
            "bert_primary_drift",
            "qwen_rank",
            "bert_rank",
        ),
        "qwen_vs_embeddinggemma": (
            "qwen_primary_drift",
            "embeddinggemma_primary_drift",
            "qwen_rank",
            "embeddinggemma_rank",
        ),
    }
    for layer, layer_frame in comparison.groupby("layer", sort=True):
        for label, (left, right, left_rank, right_rank) in metric_pairs.items():
            rows.append(
                {
                    "layer": int(layer),
                    "pair": label,
                    **_correlation_row(layer_frame, left, right),
                }
            )
            for k in DEFAULT_TOP_K_VALUES:
                rows.append(
                    {
                        "layer": int(layer),
                        "pair": label,
                        "metric": f"top_{k}_overlap",
                        "k": int(k),
                        "value": int(_top_k_overlap(layer_frame, left_rank, right_rank, k)),
                    }
                )
    return pd.DataFrame(rows)


def _build_raw_top_terms_frame(comparison: pd.DataFrame, top_k: int) -> pd.DataFrame:
    ranked_frames: list[pd.DataFrame] = []
    for _layer, layer_frame in comparison.groupby("layer", sort=True):
        ranked = layer_frame.sort_values("qwen_rank").head(top_k).copy()
        ranked.insert(1, "raw_rank", ranked["qwen_rank"])
        ranked_frames.append(ranked)
    return pd.concat(ranked_frames, ignore_index=True)


def _bucket_summary(layer_frame: pd.DataFrame, top_k: int) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    top = layer_frame.loc[layer_frame["qwen_rank"] <= top_k].copy()
    for bucket in DEFAULT_BUCKET_ORDER:
        bucket_frame = layer_frame.loc[layer_frame["bucket"] == bucket].copy()
        if bucket_frame.empty:
            continue
        top_bucket = top.loc[top["bucket"] == bucket]
        rows.append(
            {
                "bucket": bucket,
                "count": int(len(bucket_frame)),
                "mean_drift": float(bucket_frame["qwen_primary_drift"].mean()),
                "median_rank": float(bucket_frame["qwen_rank"].median()),
                "top_k_count": int(len(top_bucket)),
                "top_k_share_within_bucket": float(len(top_bucket) / len(bucket_frame)),
            }
        )
    return pd.DataFrame(rows)


def _build_bucket_summary_frame(comparison: pd.DataFrame, top_k: int) -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    for layer, layer_frame in comparison.groupby("layer", sort=True):
        frame = _bucket_summary(layer_frame, top_k)
        frame.insert(0, "layer", int(layer))
        frames.append(frame)
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


def _build_stable_control_leakage_frame(comparison: pd.DataFrame, top_k: int) -> pd.DataFrame:
    leakage_frames: list[pd.DataFrame] = []
    for layer, layer_frame in comparison.groupby("layer", sort=True):
        stable = layer_frame.loc[layer_frame["selected_as_stable_control"].fillna(False)].copy()
        stable = stable.sort_values("qwen_rank").reset_index(drop=True)
        stable["leaks_into_top_k"] = stable["qwen_rank"] <= top_k
        stable["layer"] = int(layer)
        leakage_frames.append(stable)
    return pd.concat(leakage_frames, ignore_index=True)


def _build_theory_seed_frame(comparison: pd.DataFrame) -> pd.DataFrame:
    seed_frames: list[pd.DataFrame] = []
    for layer, layer_frame in comparison.groupby("layer", sort=True):
        seeds = layer_frame.loc[layer_frame["selected_as_theory_seed"].fillna(False)].copy()
        seeds = seeds.sort_values("qwen_rank").reset_index(drop=True)
        seeds["layer"] = int(layer)
        seed_frames.append(seeds)
    return pd.concat(seed_frames, ignore_index=True)


def _frequency_row(frame: pd.DataFrame, layer: int, subset: str) -> dict[str, object]:
    valid = frame[["qwen_primary_drift", "total_frequency"]].dropna()
    if len(valid) < 3:
        return {
            "layer": int(layer),
            "subset": subset,
            "n": int(len(valid)),
            "spearman_total_frequency": None,
            "pearson_total_frequency": None,
            "spearman_log_total_frequency": None,
            "pearson_log_total_frequency": None,
        }
    logged = np.log1p(valid["total_frequency"])
    spearman_freq, _ = spearmanr(valid["qwen_primary_drift"], valid["total_frequency"])
    pearson_freq, _ = pearsonr(valid["qwen_primary_drift"], valid["total_frequency"])
    spearman_log, _ = spearmanr(valid["qwen_primary_drift"], logged)
    pearson_log, _ = pearsonr(valid["qwen_primary_drift"], logged)
    return {
        "layer": int(layer),
        "subset": subset,
        "n": int(len(valid)),
        "spearman_total_frequency": float(spearman_freq),
        "pearson_total_frequency": float(pearson_freq),
        "spearman_log_total_frequency": float(spearman_log),
        "pearson_log_total_frequency": float(pearson_log),
    }


def _build_frequency_sensitivity_frame(comparison: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for layer, layer_frame in comparison.groupby("layer", sort=True):
        rows.append(_frequency_row(layer_frame, int(layer), "all_panel"))
        for bucket in DEFAULT_BUCKET_ORDER:
            bucket_frame = layer_frame.loc[layer_frame["bucket"] == bucket].copy()
            if not bucket_frame.empty:
                rows.append(_frequency_row(bucket_frame, int(layer), bucket))
    return pd.DataFrame(rows)


def _bucket_separation_row(layer_frame: pd.DataFrame, layer: int) -> dict[str, object]:
    drift = layer_frame.loc[
        layer_frame["bucket"].isin({"word2vec_only_drift", "tfidf_only_drift"}),
        "qwen_primary_drift",
    ].dropna()
    stable = layer_frame.loc[
        layer_frame["bucket"] == "stable_control",
        "qwen_primary_drift",
    ].dropna()
    if len(drift) < 3 or len(stable) < 3:
        return {
            "layer": int(layer),
            "drift_mean": None,
            "stable_mean": None,
            "mannwhitney_u": None,
            "mannwhitney_p": None,
        }
    stat, p_value = mannwhitneyu(drift, stable, alternative="two-sided")
    return {
        "layer": int(layer),
        "drift_mean": float(drift.mean()),
        "stable_mean": float(stable.mean()),
        "mannwhitney_u": float(stat),
        "mannwhitney_p": float(p_value),
    }


def _build_bucket_separation_frame(comparison: pd.DataFrame) -> pd.DataFrame:
    rows = [
        _bucket_separation_row(layer_frame, int(layer))
        for layer, layer_frame in comparison.groupby("layer", sort=True)
    ]
    return pd.DataFrame(rows)


def _compare_against_embeddinggemma(comparison: pd.DataFrame, layer: int) -> str:
    layer_frame = comparison.loc[comparison["layer"] == layer].copy()
    row = _correlation_row(
        layer_frame,
        "qwen_primary_drift",
        "embeddinggemma_primary_drift",
    )
    if row["spearman_r"] is None:
        return "Not enough overlapping rows for Qwen vs EmbeddingGemma correlation."
    return (
        f"Layer {layer}: Spearman rho = {row['spearman_r']:.3f}, "
        f"Pearson r = {row['pearson_r']:.3f}."
    )


def _summary_lines(
    *,
    comparison: pd.DataFrame,
    agreement: pd.DataFrame,
    raw_top_terms: pd.DataFrame,
    bucket_summary: pd.DataFrame,
    stable_control_leakage: pd.DataFrame,
    theory_seed_behavior: pd.DataFrame,
    frequency_sensitivity: pd.DataFrame,
    bucket_separation: pd.DataFrame,
    summary: dict[str, object],
) -> str:
    preferred_layer = int(summary["preferred_layer"])
    top_terms = raw_top_terms.loc[
        raw_top_terms["layer"] == preferred_layer
    ].head(DEFAULT_SUMMARY_TOP_K)
    leakage = stable_control_leakage.loc[
        (stable_control_leakage["layer"] == preferred_layer)
        & (stable_control_leakage["leaks_into_top_k"])
    ]
    seeds = theory_seed_behavior.loc[theory_seed_behavior["layer"] == preferred_layer].copy()
    freq = frequency_sensitivity.loc[
        (frequency_sensitivity["layer"] == preferred_layer)
        & (frequency_sensitivity["subset"] == "all_panel")
    ]
    separation = bucket_separation.loc[bucket_separation["layer"] == preferred_layer]
    corr_rows = agreement.loc[
        (agreement["layer"] == preferred_layer) & agreement["metric"].isna()
    ].set_index("pair")

    bucket_counts = bucket_summary.loc[bucket_summary["layer"] == preferred_layer]
    bucket_lines = [
        f"- `{row.bucket}`: {int(row.top_k_count)} in top-{DEFAULT_SUMMARY_TOP_K} "
        f"({int(row.count)} total, mean drift {row.mean_drift:.4f})"
        for row in bucket_counts.itertuples(index=False)
    ]
    top_lines = [
        f"{int(row.qwen_rank)}. `{row.lemma}` ({row.bucket}, drift {row.qwen_primary_drift:.5f})"
        for row in top_terms.itertuples(index=False)
    ]
    leakage_lines = [
        f"- rank {int(row.qwen_rank)}: `{row.lemma}`"
        for row in leakage.itertuples(index=False)
    ] or ["- none in the inspected raw top-k"]
    seed_lines = [
        f"- `{row.lemma}` rank {int(row.qwen_rank)} drift {row.qwen_primary_drift:.5f}"
        for row in seeds.itertuples(index=False)
    ]

    freq_line = "Frequency sensitivity unavailable."
    if not freq.empty:
        row = freq.iloc[0]
        freq_line = (
            f"Layer {preferred_layer}: Spearman(total_frequency) = "
            f"{row['spearman_total_frequency']:.3f}, "
            f"Spearman(log total_frequency) = {row['spearman_log_total_frequency']:.3f}."
        )

    separation_line = "Bucket separation unavailable."
    if not separation.empty and pd.notna(separation.iloc[0]["mannwhitney_p"]):
        row = separation.iloc[0]
        separation_line = (
            f"Drift mean {row['drift_mean']:.5f} vs stable mean {row['stable_mean']:.5f}; "
            f"Mann-Whitney p = {row['mannwhitney_p']:.4f}."
        )

    def corr_text(pair: str) -> str:
        row = corr_rows.loc[pair]
        return (
            f"Spearman rho = {row['spearman_r']:.3f}, "
            f"Pearson r = {row['pearson_r']:.3f}"
        )

    lines = [
        "# Qwen3 Token-Level Post-Hoc Summary",
        "",
        f"- Model id: `{summary['model_id']}`",
        f"- Local snapshot: `{summary['model_path']}`",
        f"- Device: `{summary['device']}`",
        f"- Layers: `{summary['layers']}`",
        f"- Frozen run root: `{summary['frozen_run_root']}`",
        "",
        "## Agreement",
        f"- vs Word2Vec: {corr_text('qwen_vs_word2vec')}",
        f"- vs TF-IDF: {corr_text('qwen_vs_tfidf')}",
        f"- vs frozen BERT layer {preferred_layer}: {corr_text('qwen_vs_bert')}",
        f"- vs EmbeddingGemma: {corr_text('qwen_vs_embeddinggemma')}",
        "",
        "## Top-ranked Terms",
        *top_lines,
        "",
        f"## Bucket Composition in Raw Top-{DEFAULT_SUMMARY_TOP_K}",
        *bucket_lines,
        "",
        f"## Stable-control Leakage in Raw Top-{DEFAULT_LEAKAGE_TOP_K}",
        *leakage_lines,
        "",
        "## Theory-seed Behavior",
        *seed_lines,
        "",
        "## Frequency Sensitivity",
        freq_line,
        "",
        "## Drift-vs-Stable Separation",
        separation_line,
        "",
        "## Main Caveats",
        (
            "- This mirrors the frozen BERT token-level protocol as closely as possible, "
            "but Qwen3-Embedding is a text-embedding model rather than the exact STS-tuned "
            "encoder used in the frozen run."
        ),
        (
            "- Hidden-state extraction is off-label relative to Qwen3-Embedding's "
            "recommended pooled usage, so interpretability of token-level layer "
            "comparisons is weaker than for frozen BERT."
        ),
        (
            "- Agreement with EmbeddingGemma compares a token-level decoder-state "
            "approximation against a pooled-window embedding comparator; similarity and "
            "disagreement are both method-dependent."
        ),
    ]
    return "\n".join(lines) + "\n"


def run_qwen3_posthoc(
    *,
    frozen_run_root: Path,
    output_root: Path,
    project_root: Path,
    embeddinggemma_root: Path,
    model_id: str = DEFAULT_MODEL_ID,
    model_path: Path = DEFAULT_LOCAL_MODEL_PATH,
    layers: tuple[int, ...] = DEFAULT_LAYERS,
    batch_size: int = DEFAULT_BATCH_SIZE,
    device: str = "cpu",
    preferred_layer: int = DEFAULT_PREFERRED_LAYER,
) -> dict[str, object]:
    _validate_output_root(frozen_run_root, output_root)
    output_root.mkdir(parents=True, exist_ok=True)

    logger.info("Reading frozen artifacts from %s", frozen_run_root)
    (
        samples,
        panel,
        bert_scores,
        embeddinggemma_comparison,
        bert_summary,
        slice_order,
    ) = _load_frozen_inputs(frozen_run_root, embeddinggemma_root)
    logger.info(
        "Loaded frozen inputs: %d sampled occurrences, %d panel terms, %d BERT score rows",
        len(samples),
        panel["lemma"].nunique(),
        len(bert_scores),
    )

    examples = _build_context_examples_from_frozen_samples(
        frozen_run_root=frozen_run_root,
        samples=samples,
        project_root=project_root,
    )

    resolved_device = _resolve_device(device)
    logger.info(
        "Loading Qwen3 model %s from %s on device %s",
        model_id,
        model_path,
        resolved_device,
    )
    tokenizer = AutoTokenizer.from_pretrained(
        model_path,
        use_fast=False,
        trust_remote_code=True,
        padding_side="left",
    )
    model = AutoModel.from_pretrained(model_path, trust_remote_code=True)
    model.to(resolved_device)
    model.eval()

    occurrence_meta, occurrence_layers = _embed_occurrences(
        examples=examples,
        tokenizer=tokenizer,
        model=model,
        layers=layers,
        batch_size=batch_size,
        device=resolved_device,
    )
    if occurrence_meta.empty:
        raise ValueError("Qwen3 post-hoc run produced no valid token embeddings")

    prototypes, prototype_layers = _build_prototypes(occurrence_meta, occurrence_layers)
    qwen_scores, qwen_trajectory = score_prototype_distances(prototypes, slice_order)
    comparison = _build_comparison_frame(
        qwen_scores=qwen_scores,
        panel=panel,
        bert_scores=bert_scores,
        embeddinggemma_comparison=embeddinggemma_comparison,
        preferred_bert_layer=preferred_layer,
    )
    agreement = _build_agreement_frame(comparison)
    raw_top_terms = _build_raw_top_terms_frame(comparison, DEFAULT_LEAKAGE_TOP_K)
    bucket_summary = _build_bucket_summary_frame(comparison, DEFAULT_SUMMARY_TOP_K)
    stable_control_leakage = _build_stable_control_leakage_frame(comparison, DEFAULT_LEAKAGE_TOP_K)
    theory_seed_behavior = _build_theory_seed_frame(comparison)
    frequency_sensitivity = _build_frequency_sensitivity_frame(comparison)
    bucket_separation = _build_bucket_separation_frame(comparison)

    summary = {
        "kind": "supplementary_post_hoc_qwen3_token_comparator",
        "frozen_run_root": str(frozen_run_root),
        "selection_source": bert_summary.get("selection_source", "unknown"),
        "shared_panel_terms": int(panel["lemma"].nunique()),
        "sampled_occurrences_from_frozen_bert": int(len(samples)),
        "embedded_occurrences": int(len(occurrence_meta)),
        "score_rows": int(len(qwen_scores)),
        "trajectory_rows": int(len(qwen_trajectory)),
        "prototype_rows": int(len(prototypes)),
        "model_id": model_id,
        "model_path": str(model_path),
        "device": resolved_device,
        "layers": [int(layer) for layer in layers],
        "batch_size": int(batch_size),
        "preferred_layer": int(preferred_layer),
        "embedding_hidden_size": int(model.config.hidden_size),
        "slice_order": slice_order,
        "methodological_note": (
            "This supplementary run mirrors the frozen BERT token-level confirmatory protocol "
            "on the same sampled occurrences. However, Qwen3-Embedding-0.6B is an embedding model "
            "used off-label here via hidden-state extraction rather than its recommended "
            "pooled output."
        ),
    }

    logger.info("Writing supplementary outputs to %s", output_root)
    occurrence_meta.to_parquet(output_root / "occurrence_embeddings_meta.parquet", index=False)
    for layer, matrix in occurrence_layers.items():
        np.savez_compressed(
            output_root / f"occurrence_embeddings_layer_{layer}.npz",
            embeddings=matrix,
        )
    prototypes.drop(columns=["embedding"]).to_parquet(
        output_root / "prototype_meta.parquet",
        index=False,
    )
    for layer, matrix in prototype_layers.items():
        np.savez_compressed(
            output_root / f"prototype_embeddings_layer_{layer}.npz",
            embeddings=matrix,
        )
    qwen_scores.to_parquet(output_root / "scores.parquet", index=False)
    qwen_trajectory.to_parquet(output_root / "trajectory.parquet", index=False)
    comparison.to_parquet(output_root / "comparison.parquet", index=False)
    agreement.to_parquet(output_root / "agreement.parquet", index=False)
    raw_top_terms.to_parquet(output_root / "raw_top_terms.parquet", index=False)
    bucket_summary.to_parquet(output_root / "bucket_summary.parquet", index=False)
    stable_control_leakage.to_parquet(output_root / "stable_control_leakage.parquet", index=False)
    theory_seed_behavior.to_parquet(output_root / "theory_seed_behavior.parquet", index=False)
    frequency_sensitivity.to_parquet(output_root / "frequency_sensitivity.parquet", index=False)
    bucket_separation.to_parquet(output_root / "bucket_separation.parquet", index=False)
    (output_root / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (output_root / "results_summary.md").write_text(
        _summary_lines(
            comparison=comparison,
            agreement=agreement,
            raw_top_terms=raw_top_terms,
            bucket_summary=bucket_summary,
            stable_control_leakage=stable_control_leakage,
            theory_seed_behavior=theory_seed_behavior,
            frequency_sensitivity=frequency_sensitivity,
            bucket_separation=bucket_separation,
            summary=summary,
        ),
        encoding="utf-8",
    )
    return summary
