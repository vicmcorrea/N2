from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from gensim.models import Word2Vec


@dataclass(frozen=True)
class VectorStore:
    words: tuple[str, ...]
    matrix: np.ndarray
    counts: np.ndarray

    @property
    def word_to_index(self) -> dict[str, int]:
        return {word: idx for idx, word in enumerate(self.words)}


def vector_store_from_model(model: Word2Vec) -> VectorStore:
    words = tuple(model.wv.index_to_key)
    matrix = model.wv.vectors.copy()
    counts = np.array([model.wv.get_vecattr(word, "count") for word in words], dtype=np.int64)
    return VectorStore(words=words, matrix=matrix, counts=counts)


def save_vector_store(path_prefix: Path, store: VectorStore) -> None:
    path_prefix.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(path_prefix.with_suffix(".npz"), matrix=store.matrix, counts=store.counts)
    path_prefix.with_suffix(".json").write_text(
        json.dumps({"words": list(store.words)}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def load_vector_store(path_prefix: Path) -> VectorStore:
    payload = np.load(path_prefix.with_suffix(".npz"))
    words_payload = json.loads(path_prefix.with_suffix(".json").read_text(encoding="utf-8"))
    return VectorStore(
        words=tuple(words_payload["words"]),
        matrix=payload["matrix"],
        counts=payload["counts"],
    )


def mean_vector_store(stores: list[VectorStore]) -> VectorStore:
    if not stores:
        raise ValueError("At least one vector store is required")
    common_words = set(stores[0].words)
    for store in stores[1:]:
        common_words &= set(store.words)
    ordered_words = tuple(word for word in stores[0].words if word in common_words)
    if not ordered_words:
        raise ValueError("No common words across vector stores")

    matrices = []
    counts = []
    for store in stores:
        index = store.word_to_index
        matrices.append(np.vstack([store.matrix[index[word]] for word in ordered_words]))
        counts.append(np.vstack([store.counts[index[word]] for word in ordered_words]))

    mean_matrix = np.mean(np.stack(matrices, axis=0), axis=0)
    mean_counts = np.mean(np.stack(counts, axis=0), axis=0).astype(np.int64)
    return VectorStore(words=ordered_words, matrix=mean_matrix, counts=mean_counts)
