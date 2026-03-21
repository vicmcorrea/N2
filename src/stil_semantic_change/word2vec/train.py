from __future__ import annotations

import logging
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path

import pandas as pd
from gensim.models import Word2Vec

from stil_semantic_change.preprocessing.views import (
    TEXT_VIEW_TO_COLUMN,
    prepared_text_view_by_slice_dir,
    prepared_text_views_by_doc_dir,
)
from stil_semantic_change.utils.artifacts import write_dataframe, write_json
from stil_semantic_change.utils.config.schema import ExperimentConfig
from stil_semantic_change.word2vec.vector_store import save_vector_store, vector_store_from_model

logger = logging.getLogger(__name__)


class SliceSentenceFileIterable:
    def __init__(self, sentence_file: Path) -> None:
        self.sentence_file = sentence_file

    def __iter__(self) -> Iterator[list[str]]:
        with self.sentence_file.open(encoding="utf-8") as handle:
            for line in handle:
                clean_text = line.strip()
                if not clean_text:
                    continue
                yield [token for token in clean_text.split(" ") if token]


class SliceSentenceShardIterable:
    def __init__(self, doc_shards: list[Path], slice_id: str, text_column: str) -> None:
        self.doc_shards = doc_shards
        self.slice_id = slice_id
        self.text_column = text_column

    def __iter__(self) -> Iterator[list[str]]:
        for shard_path in self.doc_shards:
            frame = pd.read_parquet(shard_path, columns=["slice_id", self.text_column])
            shard = frame.loc[frame["slice_id"] == self.slice_id]
            for clean_text in shard[self.text_column].tolist():
                if not clean_text:
                    continue
                yield [token for token in clean_text.split(" ") if token]


@dataclass(frozen=True)
class TrainingOutputs:
    slice_order: list[str]
    model_paths: list[Path]


def train_word2vec_models(
    cfg: ExperimentConfig,
    prepared_root: Path,
    models_root: Path,
) -> TrainingOutputs:
    text_column = TEXT_VIEW_TO_COLUMN[cfg.model.text_view]
    sentence_dir = prepared_text_view_by_slice_dir(prepared_root, cfg.model.text_view)
    doc_shards = sorted(prepared_text_views_by_doc_dir(prepared_root).glob("*.parquet"))
    if not sentence_dir.exists() and not doc_shards:
        raise FileNotFoundError(
            "No prepared slice text files or text view shards found under "
            f"{sentence_dir} or {prepared_text_views_by_doc_dir(prepared_root)}"
        )

    slice_summary = pd.read_parquet(prepared_root / "slice_summary.parquet").sort_values("sort_key")
    slice_order = slice_summary["slice_id"].tolist()
    model_paths: list[Path] = []

    for replicate in range(cfg.model.replicates):
        for slice_id in slice_order:
            replicate_seed = cfg.model.seed + replicate
            target_dir = models_root / f"replicate_{replicate}" / slice_id
            model_path = target_dir / "word2vec.model"
            manifest_path = target_dir / "manifest.json"
            if model_path.exists() and manifest_path.exists() and not cfg.force:
                logger.info(
                    "Skipping existing Word2Vec model for %s replicate %d",
                    slice_id,
                    replicate,
                )
                model_paths.append(model_path)
                continue

            target_dir.mkdir(parents=True, exist_ok=True)
            sentence_file = sentence_dir / f"{slice_id}.txt"
            if sentence_file.exists():
                sentences: Iterator[list[str]] = SliceSentenceFileIterable(sentence_file)
            else:
                logger.warning(
                    "Falling back to shard scan for slice %s because %s is missing",
                    slice_id,
                    sentence_file,
                )
                sentences = SliceSentenceShardIterable(doc_shards, slice_id, text_column)
            total_examples = int(
                slice_summary.loc[slice_summary["slice_id"] == slice_id, "document_count"].iloc[0]
            )
            model = Word2Vec(
                sentences=sentences,
                vector_size=cfg.model.vector_size,
                window=cfg.model.window,
                negative=cfg.model.negative,
                min_count=cfg.model.min_count,
                epochs=cfg.model.epochs,
                sg=cfg.model.sg,
                workers=cfg.model.workers,
                seed=replicate_seed,
            )
            model.save(str(model_path))
            store = vector_store_from_model(model)
            save_vector_store(target_dir / "vectors", store)

            vocab_stats = pd.DataFrame(
                {
                    "lemma": list(store.words),
                    "training_count": store.counts,
                }
            )
            write_dataframe(target_dir / "vocab_stats.parquet", vocab_stats)
            write_json(
                manifest_path,
                {
                    "slice_id": slice_id,
                    "replicate": replicate,
                    "seed": replicate_seed,
                    "text_view": cfg.model.text_view,
                    "vector_size": cfg.model.vector_size,
                    "vocabulary_size": len(store.words),
                    "total_examples": total_examples,
                },
            )
            logger.info(
                "Trained Word2Vec for slice %s replicate %d with %d words",
                slice_id,
                replicate,
                len(store.words),
            )
            model_paths.append(model_path)

    return TrainingOutputs(slice_order=slice_order, model_paths=model_paths)
