from __future__ import annotations

from pathlib import Path

DOCS_DIRNAME = "docs"
DOC_METADATA_DIRNAME = "metadata"
DOC_RAW_TEXT_DIRNAME = "raw_text"
TOKENS_DIRNAME = "tokens"
CONTENT_TOKENS_DIRNAME = "content"
TEXT_VIEWS_DIRNAME = "text_views"
BY_DOC_DIRNAME = "by_doc"
BY_SLICE_DIRNAME = "by_slice"

NORMALIZED_SURFACE_VIEW = "normalized_surface"
CONTENT_SURFACE_VIEW = "content_surface"
CONTENT_LEMMA_VIEW = "content_lemma"
TEXT_VIEW_NAMES = (
    NORMALIZED_SURFACE_VIEW,
    CONTENT_SURFACE_VIEW,
    CONTENT_LEMMA_VIEW,
)

TEXT_VIEW_TO_COLUMN = {
    NORMALIZED_SURFACE_VIEW: "normalized_surface_text",
    CONTENT_SURFACE_VIEW: "content_surface_text",
    CONTENT_LEMMA_VIEW: "content_lemma_text",
}


def prepared_doc_metadata_dir(prepared_root: Path) -> Path:
    return prepared_root / DOCS_DIRNAME / DOC_METADATA_DIRNAME


def prepared_doc_raw_text_dir(prepared_root: Path) -> Path:
    return prepared_root / DOCS_DIRNAME / DOC_RAW_TEXT_DIRNAME


def prepared_content_tokens_dir(prepared_root: Path) -> Path:
    return prepared_root / TOKENS_DIRNAME / CONTENT_TOKENS_DIRNAME


def prepared_text_views_by_doc_dir(prepared_root: Path) -> Path:
    return prepared_root / TEXT_VIEWS_DIRNAME / BY_DOC_DIRNAME


def prepared_text_view_by_slice_dir(prepared_root: Path, view_name: str) -> Path:
    return prepared_root / TEXT_VIEWS_DIRNAME / BY_SLICE_DIRNAME / view_name
