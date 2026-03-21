from __future__ import annotations

import pandas as pd

from stil_semantic_change.preprocessing.text import PortuguesePreprocessor
from stil_semantic_change.utils.config.schema import PreprocessConfig


def test_preprocessing_filters_tokens(monkeypatch) -> None:
    import spacy

    monkeypatch.setattr(
        spacy,
        "load",
        lambda *args, **kwargs: (_ for _ in ()).throw(OSError("missing model")),
    )
    cfg = PreprocessConfig(
        spacy_model="pt_core_news_sm",
        fallback_to_blank=True,
        remove_stopwords=True,
        remove_punctuation=True,
        remove_numeric=True,
        min_token_length=2,
    )
    processor = PortuguesePreprocessor(cfg)
    records = pd.DataFrame(
        [
            {
                "doc_id": "doc1",
                "date": pd.Timestamp("2001-01-01"),
                "slice_id": "2001",
                "text": "A democracia reforma a economia e 2024!",
                "source_file": "toy.csv",
            }
        ]
    )
    batch = processor.process_records(records)
    assert batch.documents.loc[0, "token_count"] >= 2
    lemmas = batch.tokens["lemma"].tolist()
    assert "democracia" in lemmas
    assert "economia" in lemmas
    assert "2024" not in lemmas
    assert "a" not in lemmas


def test_lookup_fallback_excludes_obvious_discourse_markers(monkeypatch) -> None:
    import spacy

    monkeypatch.setattr(
        spacy,
        "load",
        lambda *args, **kwargs: (_ for _ in ()).throw(OSError("missing model")),
    )
    cfg = PreprocessConfig(
        spacy_model="pt_lookup",
        fallback_to_blank=True,
        remove_stopwords=True,
        remove_punctuation=True,
        remove_numeric=True,
        min_token_length=2,
    )
    processor = PortuguesePreprocessor(cfg)
    records = pd.DataFrame(
        [
            {
                "doc_id": "doc2",
                "date": pd.Timestamp("2001-01-01"),
                "slice_id": "2001",
                "text": "Obviamente, aliás, a democracia fortalece a economia.",
                "source_file": "toy.csv",
            }
        ]
    )
    batch = processor.process_records(records)
    lemmas = batch.tokens["lemma"].tolist()
    assert "obviamente" not in lemmas
    assert "aliás" not in lemmas
    assert "democracia" in lemmas
    assert "economia" in lemmas


def test_preprocessing_repairs_broken_lemmas_and_pronominal_spacing() -> None:
    cfg = PreprocessConfig(
        spacy_model="pt_lookup",
        fallback_to_blank=True,
        remove_stopwords=False,
        remove_punctuation=True,
        remove_numeric=True,
        min_token_length=2,
    )
    processor = PortuguesePreprocessor(cfg)

    class FakeToken:
        def __init__(self, text: str, lemma: str, pos: str = "VERB") -> None:
            self.text = text
            self.lemma_ = lemma
            self.pos_ = pos
            self.is_punct = False

    fake_doc = [
        FakeToken("digo", "digar"),
        FakeToken("repita", "repitar"),
        FakeToken("trata-se", "tratar se"),
        FakeToken("fazê-lo", "fazer ele"),
        FakeToken("começaremos", "começarer"),
        FakeToken("estaremos", "estarer"),
        FakeToken("veremos", "verer"),
        FakeToken("deveríamos", "deverer"),
        FakeToken("transformou-se", "transformour se"),
        FakeToken("procurem", "procur"),
    ]

    token_rows = processor._extract_tokens(
        fake_doc,
        {
            "doc_id": "doc3",
            "date": pd.Timestamp("2001-01-01"),
            "slice_id": "2001",
        },
    )
    lemmas = [row["lemma"] for row in token_rows]

    assert "dizer" in lemmas
    assert "repetir" in lemmas
    assert "tratar-se" in lemmas
    assert "fazê-lo" in lemmas
    assert "começar" in lemmas
    assert "estar" in lemmas
    assert "ver" in lemmas
    assert "dever" in lemmas
    assert "transformou-se" in lemmas
    assert "procurar" in lemmas
