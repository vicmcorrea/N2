from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class TaskConfig:
    name: str
    pipeline: tuple[str, ...] = ()
    fail_fast: bool = True


@dataclass(frozen=True)
class DatasetConfig:
    kind: str
    name: str
    raw_dir: Path
    file_glob: str
    freq: str
    text_column: str | None = None
    date_column: str | None = None
    metadata_dir: Path | None = None
    category_filter: str | None = None
    limit_files: int | None = None
    limit_rows_per_file: int | None = None


@dataclass(frozen=True)
class PreprocessConfig:
    spacy_model: str
    fallback_to_blank: bool = True
    lowercase: bool = True
    preserve_accents: bool = True
    keep_pos: tuple[str, ...] = ("NOUN", "VERB", "ADJ")
    exclude_pos: tuple[str, ...] = ("PROPN",)
    remove_stopwords: bool = True
    remove_punctuation: bool = True
    remove_numeric: bool = True
    min_token_length: int = 2
    batch_size: int = 128


@dataclass(frozen=True)
class ModelConfig:
    kind: str
    name: str
    vector_size: int = 300
    window: int = 5
    negative: int = 5
    min_count: int = 5
    epochs: int = 5
    sg: int = 1
    workers: int = 6
    seed: int = 13
    replicates: int = 2
    bert_model_name: str = "rufimelo/bert-large-portuguese-cased-sts"
    bert_batch_size: int = 8
    bert_layers: tuple[int, ...] = (-1, -4)
    bert_max_contexts_per_slice: int = 64


@dataclass(frozen=True)
class AlignmentConfig:
    kind: str
    anchor_top_k: int = 20000
    min_anchor_words: int = 50


@dataclass(frozen=True)
class SelectionConfig:
    min_occurrences_per_slice: int = 50
    min_documents_per_slice: int = 5
    min_slice_presence_ratio: float = 0.8
    top_drift_candidates: int = 15
    top_stable_controls: int = 10
    top_seed_terms: int = 5
    theory_seeds: tuple[str, ...] = ("democracia", "corrupção", "reforma", "economia", "liberdade")
    neighbor_k: int = 8


@dataclass(frozen=True)
class ReportConfig:
    figure_style: str = "whitegrid"
    coverage_palette: tuple[str, ...] = ("#2f5d8a", "#e07a5f")
    scatter_palette: tuple[str, ...] = ("#1d3557", "#e63946", "#457b9d")
    label_top_n: int = 12
    small_multiple_terms: int = 8
    neighbor_terms: int = 4


@dataclass(frozen=True)
class LoggingConfig:
    level: str = "INFO"
    format: str = "text"
    log_dir: Path = Path("run/outputs/logs")


@dataclass(frozen=True)
class IOConfig:
    project_root: Path = Path(".")
    artifacts_root: Path = Path("run/outputs")
    write_resolved_config: bool = True


@dataclass(frozen=True)
class ExperimentConfig:
    task: TaskConfig
    dataset: DatasetConfig
    preprocess: PreprocessConfig
    model: ModelConfig
    alignment: AlignmentConfig
    selection: SelectionConfig
    report: ReportConfig
    logging: LoggingConfig
    io: IOConfig
    force: bool = False
