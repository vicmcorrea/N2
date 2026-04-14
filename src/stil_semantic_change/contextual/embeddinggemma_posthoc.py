"""Post-hoc EmbeddingGemma comparator on frozen shared-panel contexts.

This module reuses the frozen BERT confirmatory sample set and context-window
reconstruction logic, but replaces token-level hidden-state extraction with
whole-window EmbeddingGemma embeddings. The result is a supplementary,
pooled-context sensitivity check that stays outside the Hydra experiment tree.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

import numpy as np
import pandas as pd
from omegaconf import OmegaConf
from scipy.stats import pearsonr, spearmanr

from stil_semantic_change.contextual.confirmatory import (
    CONTEXT_WINDOW_TOKENS,
    _load_document_texts,
    _resolve_device,
    score_prototype_distances,
)
from stil_semantic_change.preprocessing.text import PortuguesePreprocessor
from stil_semantic_change.utils.config.schema import PreprocessConfig

logger = logging.getLogger(__name__)

DEFAULT_MODEL_NAME = "google/embeddinggemma-300m"
DEFAULT_PROMPT_MODE = "clustering"
DEFAULT_TOP_K_VALUES = (5, 10, 15)

PROMPT_PREFIXES = {
    "clustering": "task: clustering | query: ",
    "semantic_similarity": "task: sentence similarity | query: ",
    "retrieval_query": "task: search result | query: ",
}


def variant_name(model_name: str, prompt_mode: str) -> str:
    """Build a filesystem-safe variant label."""
    normalized_model = model_name.replace("/", "__")
    return f"{normalized_model}__{prompt_mode}"


def build_prompted_text(context_text: str, prompt_mode: str) -> str:
    """Apply the official EmbeddingGemma prompt prefix for the chosen use case."""
    try:
        prefix = PROMPT_PREFIXES[prompt_mode]
    except KeyError as exc:
        expected = ", ".join(sorted(PROMPT_PREFIXES))
        raise ValueError(
            f"Unsupported prompt_mode '{prompt_mode}'. Expected one of: {expected}"
        ) from exc
    return f"{prefix}{context_text}"


def _load_preprocess_config(project_root: Path) -> PreprocessConfig:
    """Load the default preprocess config used to reconstruct raw-text windows."""
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
        raise ValueError(
            "EmbeddingGemma post-hoc outputs must not be written inside the frozen run root"
        )


def _load_frozen_inputs(
    frozen_run_root: Path,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, dict, list[str]]:
    scores_root = frozen_run_root / "scores"
    bert_root = scores_root / "bert_confirmatory"
    panel_root = scores_root / "comparison_panel"

    samples = pd.read_parquet(bert_root / "sampled_occurrences.parquet")
    panel = pd.read_parquet(panel_root / "comparison_panel.parquet")
    bert_scores = pd.read_parquet(bert_root / "scores.parquet")
    bert_summary = json.loads((bert_root / "summary.json").read_text(encoding="utf-8"))
    panel_summary = json.loads((panel_root / "summary.json").read_text(encoding="utf-8"))
    slice_order = [str(slice_id) for slice_id in panel_summary["slice_order"]]
    return samples, panel, bert_scores, bert_summary, slice_order


def _build_context_frame(
    frozen_run_root: Path,
    samples: pd.DataFrame,
    project_root: Path,
) -> pd.DataFrame:
    prepared_root = frozen_run_root / "prepared"
    logger.info("Loading raw texts for %d sampled occurrences", len(samples))
    raw_texts = _load_document_texts(prepared_root, set(samples["doc_id"].astype(str)))
    logger.info("Loaded %d raw documents for context reconstruction", len(raw_texts))
    preprocessor = PortuguesePreprocessor(_load_preprocess_config(project_root))
    logger.info("Reconstructing token-aligned context windows from frozen samples")

    rows: list[dict[str, object]] = []
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
            rows.append(
                {
                    "occurrence_id": int(row.occurrence_id),
                    "lemma": str(row.lemma),
                    "slice_id": str(row.slice_id),
                    "doc_id": str(doc_id),
                    "token_index": token_index,
                    "source_file": str(row.source_file) if pd.notna(row.source_file) else None,
                    "target_token": context_words[target_index],
                    "target_index_in_window": target_index,
                    "context_window_tokens": len(context_words),
                    "context_text": " ".join(context_words),
                }
            )
        if len(rows) % 10000 == 0 and rows:
            logger.info("Prepared %d / %d context rows", len(rows), total_rows)

    if not rows:
        raise ValueError("Could not reconstruct any context windows from the frozen sample set")

    logger.info("Built %d context rows; converting them into a dataframe", len(rows))
    return pd.DataFrame(rows)


def _embed_contexts(
    context_frame: pd.DataFrame,
    *,
    model_name: str,
    prompt_mode: str,
    batch_size: int,
    device: str,
) -> np.ndarray:
    prompted_texts = [
        build_prompted_text(str(text), prompt_mode)
        for text in context_frame["context_text"].tolist()
    ]
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError as exc:
        raise ImportError(
            "sentence-transformers is required for EmbeddingGemma post-hoc analysis"
        ) from exc

    logger.info("Loading EmbeddingGemma model %s on device %s", model_name, device)
    try:
        model = SentenceTransformer(model_name, device=device)
    except Exception as exc:  # pragma: no cover - depends on external model access
        raise RuntimeError(
            "Could not load EmbeddingGemma. Make sure Gemma terms are accepted and the "
            "model is accessible through the current Hugging Face credentials."
        ) from exc

    logger.info(
        "Model loaded; starting pooled-context embedding for %d windows with batch_size=%d",
        len(prompted_texts),
        max(1, batch_size),
    )
    embeddings = model.encode(
        prompted_texts,
        batch_size=max(1, batch_size),
        convert_to_numpy=True,
        normalize_embeddings=False,
        show_progress_bar=True,
    )
    logger.info("Finished EmbeddingGemma encoding")
    return np.asarray(embeddings, dtype=np.float32)


def _build_prototypes(
    context_frame: pd.DataFrame,
    occurrence_embeddings: np.ndarray,
) -> tuple[pd.DataFrame, np.ndarray]:
    group_index = context_frame.groupby(["lemma", "slice_id"]).indices
    prototype_rows: list[dict[str, object]] = []
    prototype_vectors: list[np.ndarray] = []

    for (lemma, slice_id), row_indices in group_index.items():
        vectors = occurrence_embeddings[list(row_indices)]
        if len(vectors) == 0:
            continue
        prototype = vectors.mean(axis=0).astype(np.float32)
        prototype_rows.append(
            {
                "layer": 0,
                "lemma": str(lemma),
                "slice_id": str(slice_id),
                "sample_count": int(len(row_indices)),
                "embedding": prototype,
            }
        )
        prototype_vectors.append(prototype)

    prototype_frame = pd.DataFrame(prototype_rows)
    matrix = np.stack(prototype_vectors, axis=0) if prototype_vectors else np.empty((0, 0))
    return prototype_frame, matrix.astype(np.float32)


def _top_k_overlap(frame: pd.DataFrame, left_rank: str, right_rank: str, k: int) -> int:
    valid = frame.dropna(subset=[left_rank, right_rank])
    if len(valid) < k:
        return 0
    top_left = set(valid.nsmallest(k, left_rank)["lemma"].tolist())
    top_right = set(valid.nsmallest(k, right_rank)["lemma"].tolist())
    return len(top_left & top_right)


def _correlation_row(frame: pd.DataFrame, label: str, left: str, right: str) -> dict[str, object]:
    valid = frame[[left, right]].dropna()
    if len(valid) < 3:
        return {
            "pair": label,
            "n": int(len(valid)),
            "spearman_r": None,
            "spearman_p": None,
            "pearson_r": None,
            "pearson_p": None,
        }
    spearman_r, spearman_p = spearmanr(valid[left], valid[right])
    pearson_r, pearson_p = pearsonr(valid[left], valid[right])
    return {
        "pair": label,
        "n": int(len(valid)),
        "spearman_r": float(spearman_r),
        "spearman_p": float(spearman_p),
        "pearson_r": float(pearson_r),
        "pearson_p": float(pearson_p),
    }


def _build_comparison_frame(
    scores: pd.DataFrame,
    panel: pd.DataFrame,
    bert_scores: pd.DataFrame,
) -> pd.DataFrame:
    preferred_bert = bert_scores.loc[bert_scores["layer"] == -1].copy()
    preferred_bert = preferred_bert.rename(
        columns={
            "primary_drift": "bert_primary_drift_layer_minus1",
            "first_last_drift": "bert_first_last_drift_layer_minus1",
        }
    )

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
    ]
    comparison = scores.merge(panel[panel_columns], on="lemma", how="left")
    comparison = comparison.merge(
        preferred_bert[
            [
                "lemma",
                "bert_primary_drift_layer_minus1",
                "bert_first_last_drift_layer_minus1",
            ]
        ],
        on="lemma",
        how="left",
    )
    comparison = comparison.sort_values(
        "embeddinggemma_primary_drift",
        ascending=False,
    ).reset_index(drop=True)
    comparison["embeddinggemma_rank"] = comparison.index + 1
    return comparison


def _build_agreement_frame(comparison: pd.DataFrame) -> pd.DataFrame:
    rows = [
        _correlation_row(
            comparison,
            "embeddinggemma_vs_word2vec",
            "embeddinggemma_primary_drift",
            "word2vec_primary_drift",
        ),
        _correlation_row(
            comparison,
            "embeddinggemma_vs_tfidf",
            "embeddinggemma_primary_drift",
            "tfidf_primary_drift",
        ),
        _correlation_row(
            comparison,
            "embeddinggemma_vs_bert_layer_minus1",
            "embeddinggemma_primary_drift",
            "bert_primary_drift_layer_minus1",
        ),
    ]

    for k in DEFAULT_TOP_K_VALUES:
        rows.extend(
            [
                {
                    "pair": "embeddinggemma_vs_word2vec",
                    "metric": f"top_{k}_overlap",
                    "value": int(
                        _top_k_overlap(comparison, "embeddinggemma_rank", "word2vec_rank", k)
                    ),
                    "k": int(k),
                },
                {
                    "pair": "embeddinggemma_vs_tfidf",
                    "metric": f"top_{k}_overlap",
                    "value": int(
                        _top_k_overlap(comparison, "embeddinggemma_rank", "tfidf_rank", k)
                    ),
                    "k": int(k),
                },
            ]
        )
    return pd.DataFrame(rows)


def run_embeddinggemma_posthoc(
    *,
    frozen_run_root: Path,
    output_root: Path,
    project_root: Path,
    model_name: str = DEFAULT_MODEL_NAME,
    prompt_mode: str = DEFAULT_PROMPT_MODE,
    batch_size: int = 32,
    device: str = "auto",
) -> dict[str, object]:
    """Run the supplementary EmbeddingGemma comparator on frozen panel contexts."""
    _validate_output_root(frozen_run_root, output_root)
    output_root.mkdir(parents=True, exist_ok=True)

    logger.info("Reading frozen artifacts from %s", frozen_run_root)
    samples, panel, bert_scores, bert_summary, slice_order = _load_frozen_inputs(frozen_run_root)
    logger.info(
        "Loaded frozen inputs: %d sampled occurrences, %d panel terms, %d BERT score rows",
        len(samples),
        panel["lemma"].nunique(),
        len(bert_scores),
    )
    context_frame = _build_context_frame(frozen_run_root, samples, project_root)
    resolved_device = _resolve_device(device)
    occurrence_embeddings = _embed_contexts(
        context_frame,
        model_name=model_name,
        prompt_mode=prompt_mode,
        batch_size=batch_size,
        device=resolved_device,
    )
    if len(context_frame) != len(occurrence_embeddings):
        raise ValueError("Occurrence metadata and EmbeddingGemma vectors are misaligned")

    logger.info("Building per-slice prototypes from pooled EmbeddingGemma contexts")
    prototype_frame, prototype_embeddings = _build_prototypes(context_frame, occurrence_embeddings)
    prototype_meta = prototype_frame.drop(columns=["embedding"])
    raw_scores, raw_trajectory = score_prototype_distances(prototype_frame, slice_order)
    scores = raw_scores.drop(columns=["layer"]).rename(
        columns={
            "primary_drift": "embeddinggemma_primary_drift",
            "first_last_drift": "embeddinggemma_first_last_drift",
        }
    )
    trajectory = raw_trajectory.drop(columns=["layer"]).rename(
        columns={"drift": "embeddinggemma_drift"}
    )
    comparison = _build_comparison_frame(scores, panel, bert_scores)
    agreement = _build_agreement_frame(comparison)

    occurrence_meta = context_frame.drop(columns=["context_text"]).copy()
    occurrence_meta["embedding_dim"] = int(occurrence_embeddings.shape[1])
    occurrence_meta["prompt_mode"] = prompt_mode
    occurrence_meta["model_name"] = model_name

    logger.info("Writing supplementary outputs to %s", output_root)
    occurrence_meta.to_parquet(output_root / "occurrence_meta.parquet", index=False)
    prototype_meta.to_parquet(output_root / "prototype_meta.parquet", index=False)
    np.savez_compressed(output_root / "prototype_embeddings.npz", embeddings=prototype_embeddings)
    scores.to_parquet(output_root / "scores.parquet", index=False)
    trajectory.to_parquet(output_root / "trajectory.parquet", index=False)
    comparison.to_parquet(output_root / "comparison.parquet", index=False)
    agreement.to_parquet(output_root / "agreement.parquet", index=False)

    summary = {
        "kind": "supplementary_post_hoc_embeddinggemma_comparator",
        "frozen_run_root": str(frozen_run_root),
        "selection_source": bert_summary.get("selection_source", "unknown"),
        "shared_panel_terms": int(panel["lemma"].nunique()),
        "sampled_occurrences_from_frozen_bert": int(len(samples)),
        "embedded_occurrences": int(len(context_frame)),
        "score_rows": int(len(scores)),
        "trajectory_rows": int(len(trajectory)),
        "prototype_rows": int(len(prototype_meta)),
        "model_name": model_name,
        "prompt_mode": prompt_mode,
        "device": resolved_device,
        "embedding_dim": int(occurrence_embeddings.shape[1]),
        "slice_order": slice_order,
        "methodological_note": (
            "This is a pooled context-window comparator over the frozen 55-lemma panel. "
            "It does not reproduce token-level hidden-state extraction or layer-specific "
            "BERT analysis."
        ),
    }
    (output_root / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return summary
