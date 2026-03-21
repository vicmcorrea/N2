from __future__ import annotations

import logging
import re
import unicodedata
from dataclasses import dataclass

import pandas as pd
import spacy
from spacy.lang.pt.stop_words import STOP_WORDS

from stil_semantic_change.utils.config.schema import PreprocessConfig

logger = logging.getLogger(__name__)

TOKEN_RE = re.compile(r"\w+", flags=re.UNICODE)
VERB_SUFFIXES = ("ar", "er", "ir", "ado", "ido", "ando", "endo", "indo", "ava", "ia")
ADV_SUFFIXES = ("mente",)
ADJ_SUFFIXES = (
    "al",
    "ais",
    "vel",
    "veis",
    "ico",
    "ica",
    "icos",
    "icas",
    "oso",
    "osa",
    "ivo",
    "iva",
)
FUNCTION_WORD_POS = {
    "afinal": "ADV",
    "aliás": "ADV",
    "daí": "ADV",
    "daquelas": "PRON",
    "entretanto": "CCONJ",
    "evidentemente": "ADV",
    "felizmente": "ADV",
    "geralmente": "ADV",
    "igualmente": "ADV",
    "lamentavelmente": "ADV",
    "naqueles": "PRON",
    "naturalmente": "ADV",
    "nele": "PRON",
    "obviamente": "ADV",
    "perfeitamente": "ADV",
    "posteriormente": "ADV",
    "provavelmente": "ADV",
    "seguramente": "ADV",
    "simplesmente": "ADV",
    "senão": "SCONJ",
    "tampouco": "ADV",
    "v.exa": "PRON",
    "verdadeiramente": "ADV",
    "àquele": "PRON",
}


@dataclass(frozen=True)
class ProcessedBatch:
    documents: pd.DataFrame
    tokens: pd.DataFrame


class PortuguesePreprocessor:
    def __init__(self, cfg: PreprocessConfig) -> None:
        self.cfg = cfg
        self.stopwords = set(STOP_WORDS)
        self._nlp = self._load_nlp()

    def _load_nlp(self):  # type: ignore[no-untyped-def]
        if self.cfg.spacy_model in {"pt_lookup", "pt_blank_lookup"}:
            logger.info("Using spaCy Portuguese lookup lemmatizer pipeline")
            return self._build_lookup_nlp()
        try:
            return spacy.load(self.cfg.spacy_model, disable=["ner", "parser"])
        except Exception as exc:
            if not self.cfg.fallback_to_blank:
                raise
            logger.warning(
                "Could not load spaCy model %s (%s). Falling back to a blank Portuguese "
                "lookup lemmatizer.",
                self.cfg.spacy_model,
                exc,
            )
            return self._build_lookup_nlp()

    def _build_lookup_nlp(self):  # type: ignore[no-untyped-def]
        nlp = spacy.blank("pt")
        nlp.add_pipe("lemmatizer", config={"mode": "lookup"})
        nlp.initialize()
        return nlp

    def process_records(self, records: pd.DataFrame) -> ProcessedBatch:
        documents: list[dict[str, object]] = []
        tokens: list[dict[str, object]] = []

        meta_records = records.to_dict(orient="records")
        text_values = records["text"].fillna("").astype(str).tolist()
        docs = self._nlp.pipe(
            text_values,
            batch_size=self.cfg.batch_size,
            n_process=max(1, self.cfg.n_process),
        )

        for meta, doc in zip(meta_records, docs, strict=True):
            token_rows = self._extract_tokens(doc, meta)
            documents.append(
                {
                    **meta,
                    "clean_text": " ".join(row["lemma"] for row in token_rows),
                    "token_count": len(token_rows),
                }
            )
            tokens.extend(token_rows)

        documents_df = pd.DataFrame(documents)
        tokens_df = pd.DataFrame(tokens)
        return ProcessedBatch(documents=documents_df, tokens=tokens_df)

    def tokenize_text(self, text: str) -> list[str]:
        return [str(token.text) for token in self._nlp(text)]

    def _extract_tokens(self, doc, meta: dict[str, object]) -> list[dict[str, object]]:  # type: ignore[no-untyped-def]
        token_rows: list[dict[str, object]] = []

        for index, token in enumerate(doc):
            original_text = str(token.text)
            if self.cfg.remove_punctuation and (
                token.is_punct or not TOKEN_RE.search(original_text)
            ):
                continue
            if self.cfg.remove_numeric and any(char.isdigit() for char in original_text):
                continue

            normalized = self._normalize_text(original_text)
            if not normalized:
                continue

            lemma = token.lemma_ if getattr(token, "lemma_", "") else normalized
            lemma = self._normalize_text(lemma)
            if not lemma:
                continue

            if self.cfg.remove_stopwords and lemma in self.stopwords:
                continue
            if len(lemma) < self.cfg.min_token_length:
                continue

            pos = token.pos_ or self._guess_pos(original_text)
            if self.cfg.exclude_pos and pos in self.cfg.exclude_pos:
                continue
            if self.cfg.keep_pos and pos not in self.cfg.keep_pos:
                continue

            token_rows.append(
                {
                    "doc_id": meta["doc_id"],
                    "date": meta["date"],
                    "slice_id": meta["slice_id"],
                    "token_index": index,
                    "lemma": lemma,
                    "pos": pos,
                }
            )

        return token_rows

    def _normalize_text(self, value: str) -> str:
        text = unicodedata.normalize("NFC", value.strip())
        if self.cfg.lowercase:
            text = text.lower()
        return text

    def _guess_pos(self, token: str) -> str:
        if token[:1].isupper() and token[1:].islower():
            return "PROPN"
        lowered = token.lower()
        if lowered in FUNCTION_WORD_POS:
            return FUNCTION_WORD_POS[lowered]
        if lowered.endswith(ADV_SUFFIXES):
            return "ADV"
        if lowered.endswith(VERB_SUFFIXES):
            return "VERB"
        if lowered.endswith(ADJ_SUFFIXES):
            return "ADJ"
        return "NOUN"
