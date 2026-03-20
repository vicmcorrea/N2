from __future__ import annotations

from pathlib import Path
from typing import Any

from omegaconf import DictConfig

from stil_semantic_change.utils.config.schema import (
    AlignmentConfig,
    DatasetConfig,
    ExperimentConfig,
    IOConfig,
    LoggingConfig,
    ModelConfig,
    PreprocessConfig,
    ReportConfig,
    SelectionConfig,
    TaskConfig,
)


def _resolve_path(value: str | Path, project_root: Path) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    return (project_root / path).resolve()


def _tuple_str(values: Any) -> tuple[str, ...]:
    if values is None:
        return ()
    return tuple(str(value) for value in values)


def _tuple_int(values: Any) -> tuple[int, ...]:
    if values is None:
        return ()
    return tuple(int(value) for value in values)


def build_experiment_config(cfg: DictConfig) -> ExperimentConfig:
    project_root = _resolve_path(cfg.io.project_root, Path("."))
    io_cfg = IOConfig(
        project_root=project_root,
        artifacts_root=_resolve_path(cfg.io.artifacts_root, project_root),
        write_resolved_config=bool(cfg.io.write_resolved_config),
    )

    logging_cfg = LoggingConfig(
        level=str(cfg.logging.level),
        format=str(cfg.logging.format),
        log_dir=_resolve_path(cfg.logging.log_dir, io_cfg.project_root),
    )

    dataset_cfg = DatasetConfig(
        kind=str(cfg.dataset.kind),
        name=str(cfg.dataset.name),
        raw_dir=_resolve_path(cfg.dataset.raw_dir, io_cfg.project_root),
        file_glob=str(cfg.dataset.file_glob),
        freq=str(cfg.dataset.freq),
        text_column=str(cfg.dataset.text_column) if cfg.dataset.get("text_column") else None,
        date_column=str(cfg.dataset.date_column) if cfg.dataset.get("date_column") else None,
        metadata_dir=_resolve_path(cfg.dataset.metadata_dir, io_cfg.project_root)
        if cfg.dataset.get("metadata_dir")
        else None,
        category_filter=str(cfg.dataset.category_filter)
        if cfg.dataset.get("category_filter")
        else None,
        limit_files=(
            int(cfg.dataset.limit_files)
            if cfg.dataset.get("limit_files") is not None
            else None
        ),
        limit_rows_per_file=int(cfg.dataset.limit_rows_per_file)
        if cfg.dataset.get("limit_rows_per_file") is not None
        else None,
    )

    preprocess_cfg = PreprocessConfig(
        spacy_model=str(cfg.preprocess.spacy_model),
        fallback_to_blank=bool(cfg.preprocess.fallback_to_blank),
        lowercase=bool(cfg.preprocess.lowercase),
        preserve_accents=bool(cfg.preprocess.preserve_accents),
        keep_pos=_tuple_str(cfg.preprocess.keep_pos),
        exclude_pos=_tuple_str(cfg.preprocess.exclude_pos),
        remove_stopwords=bool(cfg.preprocess.remove_stopwords),
        remove_punctuation=bool(cfg.preprocess.remove_punctuation),
        remove_numeric=bool(cfg.preprocess.remove_numeric),
        min_token_length=int(cfg.preprocess.min_token_length),
        batch_size=int(cfg.preprocess.batch_size),
    )

    model_cfg = ModelConfig(
        kind=str(cfg.model.kind),
        name=str(cfg.model.name),
        vector_size=int(cfg.model.vector_size),
        window=int(cfg.model.window),
        negative=int(cfg.model.negative),
        min_count=int(cfg.model.min_count),
        epochs=int(cfg.model.epochs),
        sg=int(cfg.model.sg),
        workers=int(cfg.model.workers),
        seed=int(cfg.model.seed),
        replicates=int(cfg.model.replicates),
        bert_model_name=str(cfg.model.bert_model_name),
        bert_batch_size=int(cfg.model.bert_batch_size),
        bert_layers=_tuple_int(cfg.model.bert_layers),
        bert_max_contexts_per_slice=int(cfg.model.bert_max_contexts_per_slice),
    )

    alignment_cfg = AlignmentConfig(
        kind=str(cfg.alignment.kind),
        anchor_top_k=int(cfg.alignment.anchor_top_k),
        min_anchor_words=int(cfg.alignment.min_anchor_words),
    )

    selection_cfg = SelectionConfig(
        min_occurrences_per_slice=int(cfg.selection.min_occurrences_per_slice),
        min_documents_per_slice=int(cfg.selection.min_documents_per_slice),
        min_slice_presence_ratio=float(cfg.selection.min_slice_presence_ratio),
        top_drift_candidates=int(cfg.selection.top_drift_candidates),
        top_stable_controls=int(cfg.selection.top_stable_controls),
        top_seed_terms=int(cfg.selection.top_seed_terms),
        theory_seeds=_tuple_str(cfg.selection.theory_seeds),
        neighbor_k=int(cfg.selection.neighbor_k),
    )

    report_cfg = ReportConfig(
        figure_style=str(cfg.report.figure_style),
        coverage_palette=_tuple_str(cfg.report.coverage_palette),
        scatter_palette=_tuple_str(cfg.report.scatter_palette),
        label_top_n=int(cfg.report.label_top_n),
        small_multiple_terms=int(cfg.report.small_multiple_terms),
        neighbor_terms=int(cfg.report.neighbor_terms),
    )

    task_cfg = TaskConfig(
        name=str(cfg.task.name),
        pipeline=_tuple_str(cfg.task.pipeline),
        fail_fast=bool(cfg.task.fail_fast),
    )

    return ExperimentConfig(
        task=task_cfg,
        dataset=dataset_cfg,
        preprocess=preprocess_cfg,
        model=model_cfg,
        alignment=alignment_cfg,
        selection=selection_cfg,
        report=report_cfg,
        logging=logging_cfg,
        io=io_cfg,
        force=bool(cfg.get("force", False)),
    )
