from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from time import perf_counter

import pandas as pd
from omegaconf import DictConfig, OmegaConf

from stil_semantic_change.comparison.panel import build_comparison_panel
from stil_semantic_change.data.loaders import iter_dataset_batches
from stil_semantic_change.preprocessing.text import PortuguesePreprocessor
from stil_semantic_change.preprocessing.views import (
    TEXT_VIEW_NAMES,
    TEXT_VIEW_TO_COLUMN,
    prepared_content_tokens_dir,
    prepared_doc_metadata_dir,
    prepared_doc_raw_text_dir,
    prepared_text_view_by_slice_dir,
    prepared_text_views_by_doc_dir,
)
from stil_semantic_change.tfidf.score import score_tfidf_drift
from stil_semantic_change.utils.artifacts import (
    ArtifactPaths,
    build_artifact_paths,
    ensure_directories,
    reset_stage_root,
    stage_complete,
    stage_manifest_path,
    update_stage_manifest,
    write_dataframe,
    write_json,
)
from stil_semantic_change.utils.config.schema import ExperimentConfig
from stil_semantic_change.utils.logging import setup_logging
from stil_semantic_change.utils.periods import slice_sort_key
from stil_semantic_change.word2vec.align import align_models
from stil_semantic_change.word2vec.score import score_candidates
from stil_semantic_change.word2vec.train import train_word2vec_models

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ExperimentContext:
    cfg: ExperimentConfig
    raw_cfg: DictConfig
    paths: ArtifactPaths


def run_experiment(cfg: ExperimentConfig, raw_cfg: DictConfig) -> None:
    paths = build_artifact_paths(cfg, raw_cfg)
    ensure_directories(paths)
    setup_logging(cfg.logging, log_file=paths.logs_root / f"{cfg.task.name}.log")
    context = ExperimentContext(cfg=cfg, raw_cfg=raw_cfg, paths=paths)

    if "print_config" in cfg.task.pipeline:
        logger.info("\n%s", OmegaConf.to_yaml(raw_cfg, resolve=True))
        return

    stage_functions = {
        "prepare_corpus": _prepare_corpus,
        "train_word2vec": _train_word2vec,
        "align_embeddings": _align_embeddings,
        "score_candidates": _score_candidates,
        "report_candidates": _report_candidates,
        "tfidf_drift": _tfidf_drift,
        "comparison_panel": _comparison_panel,
        "bert_confirmatory": _bert_confirmatory,
    }

    for stage_name in cfg.task.pipeline:
        if stage_name not in stage_functions:
            raise ValueError(f"Unknown stage: {stage_name}")
        stage_root = _stage_root(context.paths, stage_name)
        skip_existing = stage_complete(stage_root, stage_name) and not cfg.force
        started_at = datetime.now(UTC)
        started_perf = perf_counter()
        stage_functions[stage_name](context)
        if skip_existing:
            continue
        completed_at = datetime.now(UTC)
        update_stage_manifest(
            stage_root,
            stage_name,
            {
                "stage_name": stage_name,
                "task_name": cfg.task.name,
                "dataset_name": cfg.dataset.name,
                "started_at": started_at.isoformat(),
                "completed_at": completed_at.isoformat(),
                "duration_seconds": round(perf_counter() - started_perf, 3),
            },
        )


def _stage_root(paths: ArtifactPaths, stage_name: str) -> Path:
    stage_roots = {
        "prepare_corpus": paths.prepared_root,
        "train_word2vec": paths.models_root,
        "align_embeddings": paths.aligned_root,
        "score_candidates": paths.scores_root,
        "report_candidates": paths.reports_root,
        "tfidf_drift": paths.scores_root / "tfidf_drift",
        "comparison_panel": paths.scores_root / "comparison_panel",
        "bert_confirmatory": paths.scores_root,
    }
    try:
        return stage_roots[stage_name]
    except KeyError as exc:
        raise ValueError(f"Unknown stage root for {stage_name}") from exc


def _reset_stage_if_incomplete(stage_root: Path, stage_name: str) -> None:
    if stage_complete(stage_root, stage_name):
        return
    if any(stage_root.iterdir()):
        logger.info(
            "Resetting incomplete outputs under %s before rerunning stage %s",
            stage_root,
            stage_name,
        )
        reset_stage_root(stage_root)


def _prepare_corpus(context: ExperimentContext) -> None:
    stage_name = "prepare_corpus"
    if stage_complete(context.paths.prepared_root, stage_name) and not context.cfg.force:
        logger.info("Skipping corpus preparation because outputs already exist")
        return
    _reset_stage_if_incomplete(context.paths.prepared_root, stage_name)

    metadata_dir = prepared_doc_metadata_dir(context.paths.prepared_root)
    raw_text_dir = prepared_doc_raw_text_dir(context.paths.prepared_root)
    text_views_dir = prepared_text_views_by_doc_dir(context.paths.prepared_root)
    tokens_dir = prepared_content_tokens_dir(context.paths.prepared_root)
    slice_text_dirs = {
        view_name: prepared_text_view_by_slice_dir(context.paths.prepared_root, view_name)
        for view_name in TEXT_VIEW_NAMES
    }
    metadata_dir.mkdir(parents=True, exist_ok=True)
    raw_text_dir.mkdir(parents=True, exist_ok=True)
    text_views_dir.mkdir(parents=True, exist_ok=True)
    tokens_dir.mkdir(parents=True, exist_ok=True)
    for directory in slice_text_dirs.values():
        directory.mkdir(parents=True, exist_ok=True)

    preprocessor = PortuguesePreprocessor(context.cfg.preprocess)
    slice_stats: dict[str, dict[str, int]] = {}
    lemma_slice_stats: dict[tuple[str, str], dict[str, int]] = {}
    shard_rows: list[dict[str, object]] = []

    for batch_index, frame in enumerate(iter_dataset_batches(context.cfg.dataset), start=1):
        processed = preprocessor.process_records(frame)
        documents = processed.documents.loc[processed.documents["token_count"] > 0].copy()
        tokens = processed.tokens.copy()
        if documents.empty or tokens.empty:
            continue

        shard_name = f"batch_{batch_index:04d}.parquet"
        metadata_output = documents[
            [
                "doc_id",
                "date",
                "slice_id",
                "source_file",
                "normalized_token_count",
                "token_count",
            ]
        ].copy()
        raw_text_output = documents[["doc_id", "slice_id", "raw_text"]].copy()
        text_views_output = documents[
            [
                "doc_id",
                "slice_id",
                "normalized_surface_text",
                "content_surface_text",
                "content_lemma_text",
            ]
        ].copy()
        tokens_output = tokens[
            ["doc_id", "slice_id", "token_index", "token", "lemma", "pos"]
        ].copy()
        write_dataframe(metadata_dir / shard_name, metadata_output)
        write_dataframe(raw_text_dir / shard_name, raw_text_output)
        write_dataframe(text_views_dir / shard_name, text_views_output)
        write_dataframe(tokens_dir / shard_name, tokens_output)
        shard_rows.append(
            {
                "shard_name": shard_name,
                "document_count": int(len(metadata_output)),
                "normalized_token_count": int(metadata_output["normalized_token_count"].sum()),
                "content_token_count": int(metadata_output["token_count"].sum()),
                "slice_count": int(metadata_output["slice_id"].nunique()),
            }
        )

        for slice_id, slice_documents in documents.groupby("slice_id", sort=False):
            for view_name, column_name in TEXT_VIEW_TO_COLUMN.items():
                texts = [text for text in slice_documents[column_name].tolist() if text]
                if not texts:
                    continue
                sentence_file = slice_text_dirs[view_name] / f"{slice_id}.txt"
                with sentence_file.open("a", encoding="utf-8") as handle:
                    handle.write("\n".join(texts))
                    handle.write("\n")

        for slice_id, doc_count, token_count in (
            documents.groupby("slice_id")
            .agg(document_count=("doc_id", "nunique"), token_count=("token_count", "sum"))
            .reset_index()
            .itertuples(index=False, name=None)
        ):
            current = slice_stats.setdefault(str(slice_id), {"document_count": 0, "token_count": 0})
            current["document_count"] += int(doc_count)
            current["token_count"] += int(token_count)

        grouped = (
            tokens_output.groupby(["slice_id", "lemma"])
            .agg(frequency=("lemma", "size"), document_count=("doc_id", "nunique"))
            .reset_index()
        )
        for slice_id, lemma, frequency, document_count in grouped.itertuples(
            index=False,
            name=None,
        ):
            key = (str(slice_id), str(lemma))
            current = lemma_slice_stats.setdefault(key, {"frequency": 0, "document_count": 0})
            current["frequency"] += int(frequency)
            current["document_count"] += int(document_count)

        logger.info(
            "Prepared batch %d with %d documents and %d tokens",
            batch_index,
            len(documents),
            len(tokens),
        )

    if not shard_rows:
        raise ValueError("Corpus preparation produced no usable shards")

    slice_summary = pd.DataFrame(
        [
            {
                "slice_id": slice_id,
                "document_count": values["document_count"],
                "token_count": values["token_count"],
                "sort_key": f"{slice_sort_key(slice_id)[0]:04d}-{slice_sort_key(slice_id)[1]:02d}",
            }
            for slice_id, values in slice_stats.items()
        ]
    ).sort_values("sort_key")
    lemma_stats_frame = pd.DataFrame(
        [
            {
                "slice_id": slice_id,
                "lemma": lemma,
                "frequency": values["frequency"],
                "document_count": values["document_count"],
            }
            for (slice_id, lemma), values in lemma_slice_stats.items()
        ]
    )

    write_dataframe(context.paths.prepared_root / "slice_summary.parquet", slice_summary)
    write_dataframe(context.paths.prepared_root / "lemma_slice_stats.parquet", lemma_stats_frame)
    write_dataframe(context.paths.prepared_root / "doc_shards.parquet", pd.DataFrame(shard_rows))
    write_json(
        stage_manifest_path(context.paths.prepared_root, stage_name),
        {
            "dataset": context.cfg.dataset.name,
            "shard_count": len(shard_rows),
            "slice_count": int(len(slice_summary)),
            "text_views": list(TEXT_VIEW_TO_COLUMN),
            "slice_text_file_counts": {
                view_name: int(len(list(directory.glob("*.txt"))))
                for view_name, directory in slice_text_dirs.items()
            },
            "token_rows": int(lemma_stats_frame["frequency"].sum()),
        },
    )


def _train_word2vec(context: ExperimentContext) -> None:
    stage_name = "train_word2vec"
    if stage_complete(context.paths.models_root, stage_name) and not context.cfg.force:
        logger.info("Skipping Word2Vec training because outputs already exist")
        return
    _reset_stage_if_incomplete(context.paths.models_root, stage_name)

    outputs = train_word2vec_models(
        context.cfg,
        context.paths.prepared_root,
        context.paths.models_root,
    )
    write_json(
        stage_manifest_path(context.paths.models_root, stage_name),
        {
            "slice_order": outputs.slice_order,
            "model_count": len(outputs.model_paths),
            "replicates": context.cfg.model.replicates,
        },
    )


def _align_embeddings(context: ExperimentContext) -> None:
    stage_name = "align_embeddings"
    if stage_complete(context.paths.aligned_root, stage_name) and not context.cfg.force:
        logger.info("Skipping alignment because outputs already exist")
        return
    _reset_stage_if_incomplete(context.paths.aligned_root, stage_name)

    anchor_summary = align_models(
        context.cfg,
        context.paths.models_root,
        context.paths.aligned_root,
    )
    write_json(
        stage_manifest_path(context.paths.aligned_root, stage_name),
        {
            "rows": int(len(anchor_summary)),
            "replicates": context.cfg.model.replicates,
        },
    )


def _score_candidates(context: ExperimentContext) -> None:
    stage_name = "score_candidates"
    if stage_complete(context.paths.scores_root, stage_name) and not context.cfg.force:
        logger.info("Skipping candidate scoring because outputs already exist")
        return
    _reset_stage_if_incomplete(context.paths.scores_root, stage_name)

    summary, trajectory = score_candidates(
        context.cfg,
        context.paths.prepared_root,
        context.paths.aligned_root,
        context.paths.scores_root,
    )
    write_json(
        stage_manifest_path(context.paths.scores_root, stage_name),
        {
            "scored_terms": int(len(summary)),
            "trajectory_rows": int(len(trajectory)),
        },
    )


def _report_candidates(context: ExperimentContext) -> None:
    stage_name = "report_candidates"
    if stage_complete(context.paths.reports_root, stage_name) and not context.cfg.force:
        logger.info("Skipping reporting because outputs already exist")
        return
    _reset_stage_if_incomplete(context.paths.reports_root, stage_name)

    from stil_semantic_change.reporting.plots import generate_reports

    generate_reports(
        context.cfg,
        context.paths.prepared_root,
        context.paths.aligned_root,
        context.paths.scores_root,
        context.paths.reports_root,
    )
    write_json(
        stage_manifest_path(context.paths.reports_root, stage_name),
        {
            "report_root": str(context.paths.reports_root),
        },
    )


def _tfidf_drift(context: ExperimentContext) -> None:
    stage_name = "tfidf_drift"
    tfidf_root = context.paths.scores_root / "tfidf_drift"
    if stage_complete(tfidf_root, stage_name) and not context.cfg.force:
        logger.info("Skipping TF-IDF drift scoring because outputs already exist")
        return
    if tfidf_root.exists() and not stage_complete(tfidf_root, stage_name):
        logger.info("Resetting incomplete TF-IDF drift outputs under %s", tfidf_root)
        reset_stage_root(tfidf_root)

    summary, trajectory = score_tfidf_drift(
        context.cfg,
        context.paths.prepared_root,
        tfidf_root,
    )
    write_json(
        stage_manifest_path(tfidf_root, stage_name),
        {
            "scored_terms": int(len(summary)),
            "trajectory_rows": int(len(trajectory)),
            "tfidf_root": str(tfidf_root),
            "text_view": context.cfg.model.text_view,
        },
    )


def _comparison_panel(context: ExperimentContext) -> None:
    stage_name = "comparison_panel"
    panel_root = context.paths.scores_root / "comparison_panel"
    if stage_complete(panel_root, stage_name) and not context.cfg.force:
        logger.info("Skipping comparison-panel build because outputs already exist")
        return
    if panel_root.exists() and not stage_complete(panel_root, stage_name):
        logger.info("Resetting incomplete comparison-panel outputs under %s", panel_root)
        reset_stage_root(panel_root)

    panel = build_comparison_panel(
        context.cfg,
        context.paths.scores_root,
        panel_root,
    )
    write_json(
        stage_manifest_path(panel_root, stage_name),
        {
            "row_count": int(len(panel)),
            "panel_root": str(panel_root),
        },
    )


def _bert_confirmatory(context: ExperimentContext) -> None:
    stage_name = "bert_confirmatory"
    if stage_complete(context.paths.scores_root, stage_name) and not context.cfg.force:
        logger.info("Skipping confirmatory BERT analysis because outputs already exist")
        return
    bert_root = context.paths.scores_root / "bert_confirmatory"
    if bert_root.exists() and not stage_complete(context.paths.scores_root, stage_name):
        logger.info("Resetting incomplete BERT confirmatory outputs under %s", bert_root)
        reset_stage_root(bert_root)

    from stil_semantic_change.contextual.confirmatory import run_bert_confirmatory

    comparison = run_bert_confirmatory(
        context.cfg,
        context.paths.prepared_root,
        context.paths.scores_root,
    )
    write_json(
        stage_manifest_path(context.paths.scores_root, stage_name),
        {
            "rows": int(len(comparison)),
            "bert_root": str(context.paths.scores_root / "bert_confirmatory"),
        },
    )
