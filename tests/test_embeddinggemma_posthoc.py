from __future__ import annotations

import pytest

from stil_semantic_change.contextual.embeddinggemma_posthoc import (
    build_prompted_text,
    variant_name,
)


def test_variant_name_sanitizes_model_id() -> None:
    assert variant_name("google/embeddinggemma-300m", "clustering") == (
        "google__embeddinggemma-300m__clustering"
    )


def test_build_prompted_text_uses_official_prefix() -> None:
    prompted = build_prompted_text("janela de contexto", "clustering")
    assert prompted == "task: clustering | query: janela de contexto"


def test_build_prompted_text_rejects_unknown_prompt_mode() -> None:
    with pytest.raises(ValueError, match="Unsupported prompt_mode"):
        build_prompted_text("texto", "unknown")
