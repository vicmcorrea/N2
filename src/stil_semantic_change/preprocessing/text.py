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
CLITIC_SUFFIXES = {
    "lhe",
    "lhes",
    "lo",
    "la",
    "los",
    "las",
    "me",
    "se",
    "te",
    "nos",
    "vos",
}
LEMMA_OVERRIDES = {
    "começaremos": "começar",
    "diga": "dizer",
    "diga-se": "dizer-se",
    "digamos": "dizer",
    "digo": "dizer",
    "direi": "dizer",
    "diria": "dizer",
    "dirá": "dizer",
    "dirão": "dizer",
    "diriam": "dizer",
    "procurei": "procurar",
    "procurem": "procurar",
    "procures": "procurar",
    "repita": "repetir",
    "repitam": "repetir",
    "repitamos": "repetir",
    "repito": "repetir",
}
VALID_ARER_ERER_IRER_LEMMAS = {
    "bem-querer",
    "querer",
    "requerer",
}
SURFACE_TO_INFINITIVE_SUFFIXES = (
    ("aríamos", "ar"),
    ("eríamos", "er"),
    ("iríamos", "ir"),
    ("aremos", "ar"),
    ("eremos", "er"),
    ("iremos", "ir"),
    ("ariam", "ar"),
    ("eriam", "er"),
    ("iriam", "ir"),
    ("arei", "ar"),
    ("erei", "er"),
    ("irei", "ir"),
    ("ará", "ar"),
    ("erá", "er"),
    ("irá", "ir"),
    ("arão", "ar"),
    ("erão", "er"),
    ("irão", "ir"),
    ("aria", "ar"),
    ("eria", "er"),
    ("iria", "ir"),
    ("arem", "ar"),
    ("erem", "er"),
    ("irem", "ir"),
)


@dataclass(frozen=True)
class ProcessedBatch:
    documents: pd.DataFrame
    tokens: pd.DataFrame


class PortuguesePreprocessor:
    def __init__(self, cfg: PreprocessConfig) -> None:
        self.cfg = cfg
        self.stopwords = {self._normalize_text(token) for token in STOP_WORDS}
        self.function_word_pos = {
            self._normalize_text(token): pos for token, pos in FUNCTION_WORD_POS.items()
        }
        self.lemma_overrides = {
            self._normalize_text(token): self._normalize_text(lemma)
            for token, lemma in LEMMA_OVERRIDES.items()
        }
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
            document_row, token_rows = self._process_document(doc, meta)
            documents.append(document_row)
            tokens.extend(token_rows)

        documents_df = pd.DataFrame(documents)
        tokens_df = pd.DataFrame(tokens)
        return ProcessedBatch(documents=documents_df, tokens=tokens_df)

    def tokenize_text(self, text: str) -> list[str]:
        return [str(token.text) for token in self._nlp(text)]

    def _process_document(
        self,
        doc,
        meta: dict[str, object],
    ) -> tuple[dict[str, object], list[dict[str, object]]]:  # type: ignore[no-untyped-def]
        token_rows: list[dict[str, object]] = []
        normalized_tokens: list[str] = []
        content_tokens: list[str] = []
        content_lemmas: list[str] = []

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
            normalized_tokens.append(normalized)

            lemma = self._resolve_lemma(token, normalized)
            if not lemma:
                continue

            if self.cfg.remove_stopwords and lemma in self.stopwords:
                continue
            if len(lemma) < self.cfg.min_token_length:
                continue

            pos = token.pos_ or self._guess_pos(normalized)
            if self.cfg.exclude_pos and pos in self.cfg.exclude_pos:
                continue
            if self.cfg.keep_pos and pos not in self.cfg.keep_pos:
                continue

            content_tokens.append(normalized)
            content_lemmas.append(lemma)
            token_rows.append(
                {
                    "doc_id": meta["doc_id"],
                    "date": meta["date"],
                    "slice_id": meta["slice_id"],
                    "token_index": index,
                    "token": normalized,
                    "lemma": lemma,
                    "pos": pos,
                }
            )

        document_row = {
            **meta,
            "raw_text": str(meta.get("text", "")),
            "normalized_surface_text": " ".join(normalized_tokens),
            "content_surface_text": " ".join(content_tokens),
            "content_lemma_text": " ".join(content_lemmas),
            "normalized_token_count": len(normalized_tokens),
            "token_count": len(token_rows),
        }
        return document_row, token_rows

    def _extract_tokens(self, doc, meta: dict[str, object]) -> list[dict[str, object]]:  # type: ignore[no-untyped-def]
        _, token_rows = self._process_document(doc, meta)
        return token_rows

    def _resolve_lemma(self, token, normalized: str) -> str:  # type: ignore[no-untyped-def]
        override = self.lemma_overrides.get(normalized)
        if override is not None:
            return override

        lemma_value = token.lemma_ if getattr(token, "lemma_", "") else normalized
        lemma = self._normalize_text(lemma_value)
        if not lemma:
            return normalized
        if repaired := self._repair_infinitive_from_surface(lemma, normalized):
            return repaired
        if self._looks_like_malformed_infinitive(lemma):
            return normalized
        if " " not in lemma:
            return lemma

        parts = [part for part in lemma.split(" ") if part]
        if len(parts) > 1 and all(part in CLITIC_SUFFIXES for part in parts[1:]):
            if self._looks_like_infinitive(parts[0]):
                return "-".join(parts)
            if repaired := self._repair_infinitive_from_surface(parts[0], normalized):
                return "-".join([repaired, *parts[1:]])
            return normalized
        return normalized

    def _repair_infinitive_from_surface(self, lemma: str, normalized: str) -> str | None:
        if not self._looks_like_malformed_infinitive(lemma):
            return None

        surface = normalized.split("-", maxsplit=1)[0]
        for suffix, infinitive in SURFACE_TO_INFINITIVE_SUFFIXES:
            if surface.endswith(suffix) and len(surface) >= len(suffix):
                return f"{surface[: -len(suffix)]}{infinitive}"
        return None

    def _looks_like_malformed_infinitive(self, lemma: str) -> bool:
        return (
            lemma.endswith(("arer", "erer", "irer"))
            and lemma not in VALID_ARER_ERER_IRER_LEMMAS
        )

    def _looks_like_infinitive(self, lemma: str) -> bool:
        return len(lemma) > 3 and lemma.endswith(("ar", "er", "ir"))

    def _normalize_text(self, value: str) -> str:
        text = unicodedata.normalize("NFC", value.strip())
        if self.cfg.lowercase:
            text = text.lower()
        if not self.cfg.preserve_accents:
            text = "".join(
                char
                for char in unicodedata.normalize("NFD", text)
                if not unicodedata.combining(char)
            )
            text = unicodedata.normalize("NFC", text)
        return text

    def _guess_pos(self, token: str) -> str:
        if token[:1].isupper() and token[1:].islower():
            return "PROPN"
        normalized = self._normalize_text(token)
        if normalized in self.function_word_pos:
            return self.function_word_pos[normalized]
        if normalized.endswith(ADV_SUFFIXES):
            return "ADV"
        if normalized.endswith(VERB_SUFFIXES):
            return "VERB"
        if normalized.endswith(ADJ_SUFFIXES):
            return "ADJ"
        return "NOUN"
