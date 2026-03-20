from __future__ import annotations

import logging
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.linalg import orthogonal_procrustes

from stil_semantic_change.utils.artifacts import write_dataframe, write_json
from stil_semantic_change.utils.config.schema import ExperimentConfig
from stil_semantic_change.utils.periods import slice_sort_key
from stil_semantic_change.word2vec.vector_store import (
    VectorStore,
    load_vector_store,
    save_vector_store,
)

logger = logging.getLogger(__name__)


def _select_anchor_words(
    source: VectorStore,
    target: VectorStore,
    anchor_top_k: int,
) -> list[str]:
    source_counts = dict(zip(source.words, source.counts, strict=True))
    target_counts = dict(zip(target.words, target.counts, strict=True))
    common_words = set(source.words) & set(target.words)
    ranked = sorted(
        common_words,
        key=lambda word: min(int(source_counts[word]), int(target_counts[word])),
        reverse=True,
    )
    return ranked[:anchor_top_k]


def _align_store(
    previous: VectorStore,
    current: VectorStore,
    cfg: ExperimentConfig,
) -> tuple[VectorStore, int]:
    anchor_words = _select_anchor_words(previous, current, cfg.alignment.anchor_top_k)
    if len(anchor_words) < cfg.alignment.min_anchor_words:
        raise ValueError(
            "Not enough common anchor words for Procrustes alignment: "
            f"{len(anchor_words)} < {cfg.alignment.min_anchor_words}"
        )

    prev_index = previous.word_to_index
    curr_index = current.word_to_index
    previous_matrix = np.vstack([previous.matrix[prev_index[word]] for word in anchor_words])
    current_matrix = np.vstack([current.matrix[curr_index[word]] for word in anchor_words])
    rotation, _ = orthogonal_procrustes(current_matrix, previous_matrix)
    aligned_matrix = current.matrix @ rotation
    return (
        VectorStore(words=current.words, matrix=aligned_matrix, counts=current.counts),
        len(anchor_words),
    )


def align_models(cfg: ExperimentConfig, models_root: Path, aligned_root: Path) -> pd.DataFrame:
    slice_order = sorted(
        [path.name for path in (models_root / "replicate_0").iterdir() if path.is_dir()],
        key=slice_sort_key,
    )
    anchor_rows: list[dict[str, object]] = []

    for replicate_dir in sorted(path for path in models_root.iterdir() if path.is_dir()):
        replicate = int(replicate_dir.name.replace("replicate_", ""))
        target_replicate_dir = aligned_root / replicate_dir.name
        target_replicate_dir.mkdir(parents=True, exist_ok=True)

        previous_aligned: VectorStore | None = None
        previous_slice: str | None = None

        for slice_id in slice_order:
            source_prefix = replicate_dir / slice_id / "vectors"
            target_prefix = target_replicate_dir / slice_id / "vectors"
            manifest_path = target_replicate_dir / slice_id / "manifest.json"
            if (
                target_prefix.with_suffix(".npz").exists()
                and manifest_path.exists()
                and not cfg.force
            ):
                previous_aligned = load_vector_store(target_prefix)
                previous_slice = slice_id
                continue

            current_store = load_vector_store(source_prefix)
            if previous_aligned is None:
                aligned_store = current_store
                anchor_count = len(current_store.words)
            else:
                aligned_store, anchor_count = _align_store(previous_aligned, current_store, cfg)

            save_vector_store(target_prefix, aligned_store)
            write_json(
                manifest_path,
                {
                    "slice_id": slice_id,
                    "replicate": replicate,
                    "anchor_count": anchor_count,
                    "aligned_to": previous_slice,
                },
            )
            anchor_rows.append(
                {
                    "replicate": replicate,
                    "slice_id": slice_id,
                    "aligned_to": previous_slice,
                    "anchor_count": anchor_count,
                }
            )
            previous_aligned = aligned_store
            previous_slice = slice_id

    anchor_summary = pd.DataFrame(anchor_rows)
    write_dataframe(aligned_root / "anchor_summary.parquet", anchor_summary)
    return anchor_summary
