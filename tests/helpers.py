from __future__ import annotations

from pathlib import Path

from omegaconf import OmegaConf


def make_raw_cfg(
    project_root: Path,
    artifacts_root: Path,
    toy_dataset_dir: Path,
    *,
    force: bool = False,
):
    return OmegaConf.create(
        {
            "task": {
                "name": "run_yearly_core",
                "pipeline": [
                    "prepare_corpus",
                    "train_word2vec",
                    "align_embeddings",
                    "score_candidates",
                    "report_candidates",
                ],
                "fail_fast": True,
            },
            "dataset": {
                "kind": "brpolicorpus_floor",
                "name": "toy_brpolicorpus_yearly",
                "raw_dir": str(toy_dataset_dir),
                "file_glob": "*.csv",
                "freq": "yearly",
                "text_column": "Discurso",
                "date_column": "Data",
                "limit_files": None,
                "limit_rows_per_file": None,
            },
            "preprocess": {
                "spacy_model": "pt_core_news_sm",
                "fallback_to_blank": True,
                "lowercase": True,
                "preserve_accents": True,
                "keep_pos": ["NOUN", "VERB", "ADJ"],
                "exclude_pos": ["PROPN"],
                "remove_stopwords": True,
                "remove_punctuation": True,
                "remove_numeric": True,
                "min_token_length": 2,
                "batch_size": 64,
                "n_process": 1,
            },
            "model": {
                "kind": "word2vec",
                "name": "word2vec_skipgram_300d",
                "vector_size": 40,
                "window": 3,
                "negative": 3,
                "min_count": 1,
                "epochs": 25,
                "sg": 1,
                "workers": 1,
                "seed": 13,
                "replicates": 1,
                "bert_model_name": "rufimelo/bert-large-portuguese-cased-sts",
                "bert_batch_size": 4,
                "bert_layers": [-1, -4],
                "bert_max_contexts_per_slice": 8,
            },
            "alignment": {
                "kind": "orthogonal_procrustes",
                "anchor_top_k": 100,
                "min_anchor_words": 2,
            },
            "selection": {
                "min_occurrences_per_slice": 2,
                "min_documents_per_slice": 1,
                "min_slice_presence_ratio": 0.66,
                "top_drift_candidates": 5,
                "top_stable_controls": 3,
                "top_seed_terms": 3,
                "theory_seeds": ["reforma", "economia", "presidente"],
                "neighbor_k": 3,
            },
            "report": {
                "figure_style": "whitegrid",
                "coverage_palette": ["#2f5d8a", "#e07a5f"],
                "scatter_palette": ["#1d3557", "#e63946", "#457b9d"],
                "label_top_n": 6,
                "small_multiple_terms": 4,
                "neighbor_terms": 2,
            },
            "logging": {
                "level": "INFO",
                "format": "text",
                "log_dir": str(artifacts_root / "logs"),
            },
            "io": {
                "project_root": str(project_root),
                "artifacts_root": str(artifacts_root),
                "write_resolved_config": False,
            },
            "force": force,
        }
    )
