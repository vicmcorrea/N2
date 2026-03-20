from __future__ import annotations

import numpy as np

from stil_semantic_change.word2vec.align import _align_store
from stil_semantic_change.word2vec.vector_store import VectorStore


def test_procrustes_alignment_recovers_rotation(built_cfg) -> None:
    _, cfg = built_cfg
    base_matrix = np.array(
        [
            [1.0, 0.0],
            [0.0, 1.0],
            [1.0, 1.0],
        ]
    )
    rotation = np.array(
        [
            [0.0, -1.0],
            [1.0, 0.0],
        ]
    )
    rotated = base_matrix @ rotation
    previous = VectorStore(words=("a", "b", "c"), matrix=base_matrix, counts=np.array([10, 8, 7]))
    current = VectorStore(words=("a", "b", "c"), matrix=rotated, counts=np.array([9, 7, 6]))
    aligned, anchor_count = _align_store(previous, current, cfg)
    assert anchor_count == 3
    assert np.allclose(aligned.matrix, base_matrix, atol=1e-5)
