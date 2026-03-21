from __future__ import annotations

import logging
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from transformers import AutoModel, AutoTokenizer

from stil_semantic_change.preprocessing.text import PortuguesePreprocessor
from stil_semantic_change.preprocessing.views import (
    prepared_content_tokens_dir,
    prepared_doc_metadata_dir,
    prepared_doc_raw_text_dir,
)
from stil_semantic_change.utils.artifacts import write_dataframe, write_json, write_npz
from stil_semantic_change.utils.config.schema import ExperimentConfig

logger = logging.getLogger(__name__)

CONTEXT_WINDOW_TOKENS = 48
MAX_SEQUENCE_LENGTH = 256


@dataclass(frozen=True)
class ContextExample:
    occurrence_id: int
    lemma: str
    slice_id: str
    doc_id: str
    token_index: int
    context_words: list[str]
    target_index: int
    source_file: str | None


def select_confirmatory_terms(candidate_sets: dict[str, object]) -> list[str]:
    terms: list[str] = []
    for key in ("drift_candidates", "stable_controls", "theory_seeds"):
        for term in candidate_sets.get(key, []):
            normalized = str(term)
            if normalized and normalized not in terms:
                terms.append(normalized)
    return terms


def score_prototype_distances(
    prototypes: pd.DataFrame,
    slice_order: list[str],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    if prototypes.empty:
        raise ValueError("No BERT prototypes were produced")

    score_rows: list[dict[str, object]] = []
    trajectory_rows: list[dict[str, object]] = []

    grouped = prototypes.groupby(["layer", "lemma"])
    for (layer, lemma), group in grouped:
        vectors_by_slice = {
            str(row["slice_id"]): np.asarray(row["embedding"], dtype=np.float32)
            for row in group.to_dict(orient="records")
        }
        counts_by_slice = {
            str(row["slice_id"]): int(row["sample_count"])
            for row in group.to_dict(orient="records")
        }

        distances: list[float] = []
        for left_slice, right_slice in zip(slice_order[:-1], slice_order[1:], strict=True):
            if left_slice not in vectors_by_slice or right_slice not in vectors_by_slice:
                continue
            distance = cosine_distance(vectors_by_slice[left_slice], vectors_by_slice[right_slice])
            distances.append(distance)
            trajectory_rows.append(
                {
                    "layer": int(layer),
                    "lemma": str(lemma),
                    "from_slice": left_slice,
                    "to_slice": right_slice,
                    "transition": f"{left_slice}->{right_slice}",
                    "drift": distance,
                    "left_count": counts_by_slice[left_slice],
                    "right_count": counts_by_slice[right_slice],
                }
            )

        if not distances:
            continue

        present_slices = [slice_id for slice_id in slice_order if slice_id in vectors_by_slice]
        first_last_drift = np.nan
        if len(present_slices) >= 2:
            first_last_drift = cosine_distance(
                vectors_by_slice[present_slices[0]],
                vectors_by_slice[present_slices[-1]],
            )

        score_rows.append(
            {
                "layer": int(layer),
                "lemma": str(lemma),
                "primary_drift": float(np.mean(distances)),
                "first_last_drift": float(first_last_drift),
                "slice_count": len(present_slices),
                "sample_count_total": int(sum(counts_by_slice.values())),
                "sample_count_min": int(min(counts_by_slice.values())),
            }
        )

    return pd.DataFrame(score_rows), pd.DataFrame(trajectory_rows)


def cosine_distance(left: np.ndarray, right: np.ndarray) -> float:
    denominator = np.linalg.norm(left) * np.linalg.norm(right)
    if denominator == 0:
        return 0.0
    return 1.0 - float(np.dot(left, right) / denominator)


def run_bert_confirmatory(
    cfg: ExperimentConfig,
    prepared_root: Path,
    scores_root: Path,
) -> pd.DataFrame:
    bert_root = scores_root / "bert_confirmatory"
    bert_root.mkdir(parents=True, exist_ok=True)

    candidate_sets = _load_candidate_sets(scores_root)
    selected_terms = select_confirmatory_terms(candidate_sets)
    if not selected_terms:
        raise ValueError("No confirmatory terms were found in candidate_sets.json")

    slice_order = [str(slice_id) for slice_id in candidate_sets["slice_order"]]
    samples = _sample_occurrences(
        prepared_root=prepared_root,
        selected_terms=selected_terms,
        max_contexts_per_slice=cfg.model.bert_max_contexts_per_slice,
        seed=cfg.model.seed,
    )
    if samples.empty:
        raise ValueError("No token occurrences were available for confirmatory BERT scoring")
    write_dataframe(bert_root / "sampled_occurrences.parquet", samples)

    doc_texts = _load_document_texts(prepared_root, set(samples["doc_id"].tolist()))
    preprocessor = PortuguesePreprocessor(cfg.preprocess)
    examples = _build_context_examples(samples, doc_texts, preprocessor)
    if not examples:
        raise ValueError("Could not build any token-aligned BERT contexts for sampled occurrences")

    device = _resolve_device()
    logger.info("Running BERT confirmatory analysis on device %s", device)
    tokenizer = AutoTokenizer.from_pretrained(cfg.model.bert_model_name, use_fast=True)
    model = AutoModel.from_pretrained(cfg.model.bert_model_name)
    model.to(device)
    model.eval()

    occurrence_meta, embedding_layers = _embed_occurrences(
        examples=examples,
        tokenizer=tokenizer,
        model=model,
        layers=cfg.model.bert_layers,
        batch_size=cfg.model.bert_batch_size,
        device=device,
    )
    if occurrence_meta.empty:
        raise ValueError("BERT confirmatory run did not yield any valid token embeddings")

    write_dataframe(bert_root / "occurrence_embeddings_meta.parquet", occurrence_meta)
    for layer, matrix in embedding_layers.items():
        write_npz(bert_root / f"occurrence_embeddings_layer_{layer}.npz", embeddings=matrix)

    prototypes, prototype_layers = _build_prototypes(occurrence_meta, embedding_layers)
    write_dataframe(bert_root / "prototype_meta.parquet", prototypes.drop(columns=["embedding"]))
    for layer, matrix in prototype_layers.items():
        write_npz(bert_root / f"prototype_embeddings_layer_{layer}.npz", embeddings=matrix)

    bert_scores, bert_trajectory = score_prototype_distances(prototypes, slice_order)
    word2vec_scores = pd.read_parquet(scores_root / "scores_aggregated.parquet")
    comparison = bert_scores.merge(
        word2vec_scores[["lemma", "primary_drift_mean", "first_last_drift_mean"]],
        on="lemma",
        how="left",
    ).rename(
        columns={
            "primary_drift_mean": "word2vec_primary_drift_mean",
            "first_last_drift_mean": "word2vec_first_last_drift_mean",
        }
    )
    comparison["bert_word2vec_gap"] = (
        comparison["primary_drift"] - comparison["word2vec_primary_drift_mean"]
    )

    write_dataframe(bert_root / "scores.parquet", bert_scores)
    write_dataframe(bert_root / "trajectory.parquet", bert_trajectory)
    write_dataframe(bert_root / "comparison_with_word2vec.parquet", comparison)
    write_json(
        bert_root / "summary.json",
        {
            "model_name": cfg.model.bert_model_name,
            "device": device,
            "layers": list(cfg.model.bert_layers),
            "selected_terms": selected_terms,
            "sampled_occurrences": int(len(samples)),
            "embedded_occurrences": int(len(occurrence_meta)),
            "prototype_rows": int(len(prototypes)),
            "score_rows": int(len(bert_scores)),
        },
    )
    return comparison


def _load_candidate_sets(scores_root: Path) -> dict[str, object]:
    path = scores_root / "candidate_sets.json"
    if not path.exists():
        raise FileNotFoundError(
            "candidate_sets.json was not found. Run the yearly Word2Vec pipeline before "
            "the confirmatory BERT stage."
        )
    return pd.read_json(path, typ="series").to_dict()


def _sample_occurrences(
    prepared_root: Path,
    selected_terms: list[str],
    max_contexts_per_slice: int,
    seed: int,
) -> pd.DataFrame:
    term_set = set(selected_terms)
    token_frames: list[pd.DataFrame] = []
    for shard_path in sorted(prepared_content_tokens_dir(prepared_root).glob("*.parquet")):
        frame = pd.read_parquet(
            shard_path,
            columns=["doc_id", "slice_id", "lemma", "token_index"],
        )
        shard = frame.loc[frame["lemma"].isin(term_set)].copy()
        if not shard.empty:
            token_frames.append(shard)

    if not token_frames:
        return pd.DataFrame()

    occurrences = pd.concat(token_frames, ignore_index=True)
    occurrences = occurrences.sort_values(["lemma", "slice_id", "doc_id", "token_index"])
    sampled_groups: list[pd.DataFrame] = []
    for _, group in occurrences.groupby(["lemma", "slice_id"], sort=True):
        if len(group) <= max_contexts_per_slice:
            sampled = group.copy()
        else:
            sampled = group.sample(
                n=max_contexts_per_slice,
                random_state=seed,
            ).sort_values(["doc_id", "token_index"])
        sampled_groups.append(sampled)

    sampled = pd.concat(sampled_groups, ignore_index=True)
    docs = _load_document_metadata(prepared_root, set(sampled["doc_id"].tolist()))
    sampled = sampled.merge(docs, on="doc_id", how="left")
    sampled.insert(0, "occurrence_id", np.arange(len(sampled), dtype=np.int64))
    return sampled


def _load_document_metadata(prepared_root: Path, doc_ids: set[str]) -> pd.DataFrame:
    rows: list[pd.DataFrame] = []
    for shard_path in sorted(prepared_doc_metadata_dir(prepared_root).glob("*.parquet")):
        frame = pd.read_parquet(shard_path, columns=["doc_id", "date", "source_file"])
        shard = frame.loc[frame["doc_id"].isin(doc_ids)].copy()
        if not shard.empty:
            rows.append(shard)
    if not rows:
        return pd.DataFrame(columns=["doc_id", "date", "source_file"])
    return pd.concat(rows, ignore_index=True).drop_duplicates(subset=["doc_id"])


def _load_document_texts(prepared_root: Path, doc_ids: set[str]) -> dict[str, str]:
    document_texts: dict[str, str] = {}
    for shard_path in sorted(prepared_doc_raw_text_dir(prepared_root).glob("*.parquet")):
        frame = pd.read_parquet(shard_path, columns=["doc_id", "raw_text"])
        shard = frame.loc[frame["doc_id"].isin(doc_ids)]
        for row in shard.itertuples(index=False):
            document_texts[str(row.doc_id)] = str(row.raw_text)
    return document_texts


def _build_context_examples(
    samples: pd.DataFrame,
    document_texts: dict[str, str],
    preprocessor: PortuguesePreprocessor,
) -> list[ContextExample]:
    examples: list[ContextExample] = []
    for row in samples.itertuples(index=False):
        words = preprocessor.tokenize_text(document_texts[str(row.doc_id)])
        if row.token_index >= len(words):
            continue
        start = max(0, int(row.token_index) - CONTEXT_WINDOW_TOKENS)
        end = min(len(words), int(row.token_index) + CONTEXT_WINDOW_TOKENS + 1)
        context_words = words[start:end]
        target_index = int(row.token_index) - start
        if not context_words or not (0 <= target_index < len(context_words)):
            continue
        examples.append(
            ContextExample(
                occurrence_id=int(row.occurrence_id),
                lemma=str(row.lemma),
                slice_id=str(row.slice_id),
                doc_id=str(row.doc_id),
                token_index=int(row.token_index),
                context_words=context_words,
                target_index=target_index,
                source_file=str(row.source_file) if pd.notna(row.source_file) else None,
            )
        )
    return examples


def _resolve_device() -> str:
    if torch.cuda.is_available():
        return "cuda"
    if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        return "mps"
    return "cpu"


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
    examples: list[ContextExample],
    tokenizer,
    model,
    layers: tuple[int, ...],
    batch_size: int,
    device: str,
) -> tuple[pd.DataFrame, dict[int, np.ndarray]]:
    occurrence_rows: list[dict[str, object]] = []
    layer_vectors: dict[int, list[np.ndarray]] = {int(layer): [] for layer in layers}

    for batch in _batched(examples, max(1, batch_size)):
        batch_encoding = tokenizer(
            [item.context_words for item in batch],
            is_split_into_words=True,
            padding=True,
            truncation=True,
            max_length=MAX_SEQUENCE_LENGTH,
            return_tensors="pt",
        )
        encoded = {key: value.to(device) for key, value in batch_encoding.items()}
        with torch.no_grad():
            outputs = model(**encoded, output_hidden_states=True)
        hidden_states = outputs.hidden_states
        if hidden_states is None:
            raise ValueError("Transformer model did not return hidden states")

        for batch_index, item in enumerate(batch):
            token_word_ids = batch_encoding.word_ids(batch_index=batch_index)
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
                    hidden_states[layer][batch_index, positions, :]
                    .mean(dim=0)
                    .detach()
                    .cpu()
                    .numpy()
                    .astype(np.float32)
                )
                layer_vectors[int(layer)].append(vector)
            occurrence_rows.append(row)

    occurrence_meta = pd.DataFrame(occurrence_rows)
    stacked_layers = {
        layer: np.stack(vectors, axis=0) if vectors else np.empty((0, model.config.hidden_size))
        for layer, vectors in layer_vectors.items()
    }
    return occurrence_meta, stacked_layers


def _build_prototypes(
    occurrence_meta: pd.DataFrame,
    embedding_layers: dict[int, np.ndarray],
) -> tuple[pd.DataFrame, dict[int, np.ndarray]]:
    prototype_rows: list[dict[str, object]] = []
    prototype_vectors: dict[int, list[np.ndarray]] = {layer: [] for layer in embedding_layers}

    group_index = occurrence_meta.groupby(["lemma", "slice_id"]).indices
    for layer, matrix in embedding_layers.items():
        for (lemma, slice_id), row_indices in group_index.items():
            vectors = matrix[list(row_indices)]
            if len(vectors) == 0:
                continue
            prototype = vectors.mean(axis=0).astype(np.float32)
            prototype_rows.append(
                {
                    "layer": layer,
                    "lemma": str(lemma),
                    "slice_id": str(slice_id),
                    "sample_count": int(len(row_indices)),
                    "embedding": prototype,
                }
            )
            prototype_vectors[layer].append(prototype)

    prototype_frame = pd.DataFrame(prototype_rows)
    stacked = {
        layer: np.stack(vectors, axis=0) if vectors else np.empty((0, 0), dtype=np.float32)
        for layer, vectors in prototype_vectors.items()
    }
    return prototype_frame, stacked
