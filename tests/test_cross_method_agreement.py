from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from stil_semantic_change.comparison.cross_method import write_cross_method_agreement


def test_write_cross_method_agreement_creates_filtered_panel(tmp_path: Path) -> None:
    scores_root = tmp_path / "scores"
    bert_root = scores_root / "bert_confirmatory"
    bert_root.mkdir(parents=True)

    frame = pd.DataFrame(
        [
            {
                "layer": -1,
                "lemma": "bloqueio",
                "primary_drift": 0.40,
                "word2vec_primary_drift": 0.30,
                "tfidf_primary_drift": 0.02,
                "word2vec_rank": 1,
                "tfidf_rank": 8,
                "bucket": "word2vec_only_drift",
                "selected_by_word2vec": True,
                "selected_by_tfidf": False,
                "selected_as_stable_control": False,
                "selected_as_theory_seed": False,
                "selected_as_disagreement_case": True,
                "bert_word2vec_gap": 0.10,
                "bert_tfidf_gap": 0.38,
            },
            {
                "layer": -1,
                "lemma": "expresso",
                "primary_drift": 0.35,
                "word2vec_primary_drift": 0.10,
                "tfidf_primary_drift": 0.01,
                "word2vec_rank": 10,
                "tfidf_rank": 20,
                "bucket": "stable_control",
                "selected_by_word2vec": False,
                "selected_by_tfidf": False,
                "selected_as_stable_control": True,
                "selected_as_theory_seed": False,
                "selected_as_disagreement_case": False,
                "bert_word2vec_gap": 0.25,
                "bert_tfidf_gap": 0.34,
            },
            {
                "layer": -1,
                "lemma": "salário",
                "primary_drift": 0.33,
                "word2vec_primary_drift": 0.04,
                "tfidf_primary_drift": 0.28,
                "word2vec_rank": 18,
                "tfidf_rank": 2,
                "bucket": "tfidf_only_drift",
                "selected_by_word2vec": False,
                "selected_by_tfidf": True,
                "selected_as_stable_control": False,
                "selected_as_theory_seed": False,
                "selected_as_disagreement_case": True,
                "bert_word2vec_gap": 0.29,
                "bert_tfidf_gap": 0.05,
            },
            {
                "layer": -1,
                "lemma": "reforma",
                "primary_drift": 0.22,
                "word2vec_primary_drift": 0.05,
                "tfidf_primary_drift": 0.31,
                "word2vec_rank": 25,
                "tfidf_rank": 1,
                "bucket": "theory_seed",
                "selected_by_word2vec": False,
                "selected_by_tfidf": False,
                "selected_as_stable_control": False,
                "selected_as_theory_seed": True,
                "selected_as_disagreement_case": False,
                "bert_word2vec_gap": 0.17,
                "bert_tfidf_gap": -0.09,
            },
            {
                "layer": -4,
                "lemma": "bloqueio",
                "primary_drift": 0.20,
                "word2vec_primary_drift": 0.30,
                "tfidf_primary_drift": 0.02,
                "word2vec_rank": 1,
                "tfidf_rank": 8,
                "bucket": "word2vec_only_drift",
                "selected_by_word2vec": True,
                "selected_by_tfidf": False,
                "selected_as_stable_control": False,
                "selected_as_theory_seed": False,
                "selected_as_disagreement_case": True,
                "bert_word2vec_gap": -0.10,
                "bert_tfidf_gap": 0.18,
            },
            {
                "layer": -4,
                "lemma": "salário",
                "primary_drift": 0.18,
                "word2vec_primary_drift": 0.04,
                "tfidf_primary_drift": 0.28,
                "word2vec_rank": 18,
                "tfidf_rank": 2,
                "bucket": "tfidf_only_drift",
                "selected_by_word2vec": False,
                "selected_by_tfidf": True,
                "selected_as_stable_control": False,
                "selected_as_theory_seed": False,
                "selected_as_disagreement_case": True,
                "bert_word2vec_gap": 0.14,
                "bert_tfidf_gap": -0.10,
            },
            {
                "layer": -4,
                "lemma": "expresso",
                "primary_drift": 0.17,
                "word2vec_primary_drift": 0.10,
                "tfidf_primary_drift": 0.01,
                "word2vec_rank": 10,
                "tfidf_rank": 20,
                "bucket": "stable_control",
                "selected_by_word2vec": False,
                "selected_by_tfidf": False,
                "selected_as_stable_control": True,
                "selected_as_theory_seed": False,
                "selected_as_disagreement_case": False,
                "bert_word2vec_gap": 0.07,
                "bert_tfidf_gap": 0.16,
            },
            {
                "layer": -4,
                "lemma": "reforma",
                "primary_drift": 0.12,
                "word2vec_primary_drift": 0.05,
                "tfidf_primary_drift": 0.31,
                "word2vec_rank": 25,
                "tfidf_rank": 1,
                "bucket": "theory_seed",
                "selected_by_word2vec": False,
                "selected_by_tfidf": False,
                "selected_as_stable_control": False,
                "selected_as_theory_seed": True,
                "selected_as_disagreement_case": False,
                "bert_word2vec_gap": 0.07,
                "bert_tfidf_gap": -0.19,
            },
        ]
    )
    frame.to_parquet(bert_root / "comparison_with_word2vec.parquet", index=False)

    out_dir = write_cross_method_agreement(scores_root)

    filtered = pd.read_parquet(out_dir / "bert_filtered_panel.parquet")
    assert "expresso" not in filtered["lemma"].tolist()
    assert filtered["lemma"].tolist()[:3] == ["bloqueio", "salário", "reforma"]

    leakage = pd.read_parquet(out_dir / "bert_stable_control_leakage.parquet")
    assert leakage["lemma"].tolist() == ["expresso"]

    summary = json.loads((out_dir / "summary.json").read_text())
    assert summary["preferred_layer"] == -1
    assert summary["filtered_bert_top_terms"][:3] == ["bloqueio", "salário", "reforma"]

    candidate_sets = json.loads((out_dir / "bert_candidate_sets.json").read_text())
    assert candidate_sets["drift_candidates"][:3] == ["bloqueio", "salário", "reforma"]
    assert candidate_sets["stable_controls"] == ["expresso"]
