from __future__ import annotations

import argparse
import logging
from dataclasses import replace
from pathlib import Path

import pandas as pd
from omegaconf import OmegaConf

from stil_semantic_change.reporting.evaluation import (
    evaluate_run,
    write_readiness_reports,
)
from stil_semantic_change.reporting.plots import generate_reports
from stil_semantic_change.utils.artifacts import (
    reset_stage_root,
    write_dataframe,
    write_json,
)
from stil_semantic_change.utils.config import build_experiment_config
from stil_semantic_change.utils.logging import setup_logging
from stil_semantic_change.word2vec.align import align_models
from stil_semantic_change.word2vec.score import score_candidates
from stil_semantic_change.word2vec.train import train_word2vec_models

logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run a fast Word2Vec quicklook from existing prepared artifacts.",
    )
    parser.add_argument("--resolved-config", type=Path, required=True)
    parser.add_argument("--prepared-root", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--start-year", type=int, default=2003)
    parser.add_argument("--end-year", type=int, default=2023)
    parser.add_argument("--replicates", type=int, default=1)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--epochs", type=int, default=None)
    parser.add_argument("--force", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    raw_cfg = OmegaConf.load(args.resolved_config)
    cfg = build_experiment_config(raw_cfg)
    cfg = replace(
        cfg,
        model=replace(
            cfg.model,
            replicates=args.replicates,
            workers=args.workers,
            epochs=args.epochs if args.epochs is not None else cfg.model.epochs,
        ),
        force=bool(args.force),
    )

    output_root = args.output_root.resolve()
    if args.force and output_root.exists():
        reset_stage_root(output_root)
    output_root.mkdir(parents=True, exist_ok=True)
    setup_logging(cfg.logging, log_file=output_root / "quicklook.log")

    filtered_prepared_root = output_root / "prepared"
    filtered_prepared_root.mkdir(parents=True, exist_ok=True)
    _link_directory(args.prepared_root / "docs", filtered_prepared_root / "docs")
    _link_directory(args.prepared_root / "tokens", filtered_prepared_root / "tokens")

    slice_summary = _load_slice_summary(args.prepared_root, args.start_year, args.end_year)
    lemma_slice_stats = _load_lemma_slice_stats(
        args.prepared_root,
        selected_slices=set(slice_summary["slice_id"].tolist()),
    )
    write_dataframe(filtered_prepared_root / "slice_summary.parquet", slice_summary)
    write_dataframe(filtered_prepared_root / "lemma_slice_stats.parquet", lemma_slice_stats)

    models_root = output_root / "models"
    aligned_root = output_root / "aligned"
    scores_root = output_root / "scores"
    reports_root = output_root / "reports"
    for path in (models_root, aligned_root, scores_root, reports_root):
        path.mkdir(parents=True, exist_ok=True)

    logger.info(
        "Running quicklook from prepared artifacts for yearly slices %d-%d",
        args.start_year,
        args.end_year,
    )
    outputs = train_word2vec_models(cfg, filtered_prepared_root, models_root)
    anchor_summary = align_models(cfg, models_root, aligned_root)
    summary, trajectory = score_candidates(cfg, filtered_prepared_root, aligned_root, scores_root)
    generate_reports(cfg, filtered_prepared_root, aligned_root, scores_root, reports_root)
    readiness = evaluate_run(output_root, cfg)
    write_readiness_reports(output_root, readiness)

    write_json(
        output_root / "quicklook_manifest.json",
        {
            "resolved_config": str(args.resolved_config.resolve()),
            "prepared_root": str(args.prepared_root.resolve()),
            "slice_range": [args.start_year, args.end_year],
            "replicates": args.replicates,
            "workers": args.workers,
            "epochs": cfg.model.epochs,
            "slice_count": int(len(slice_summary)),
            "model_count": int(len(outputs.model_paths)),
            "anchor_rows": int(len(anchor_summary)),
            "scored_terms": int(len(summary)),
            "trajectory_rows": int(len(trajectory)),
            "readiness_status": readiness["status"],
        },
    )


def _link_directory(source: Path, target: Path) -> None:
    if target.is_symlink() or target.exists():
        if target.is_symlink() or target.is_file():
            target.unlink()
        else:
            reset_stage_root(target)
            target.rmdir()
    target.symlink_to(source.resolve(), target_is_directory=True)


def _load_slice_summary(
    prepared_root: Path,
    start_year: int,
    end_year: int,
) -> pd.DataFrame:
    frame = (
        pd.read_parquet(prepared_root / "slice_summary.parquet")
        .assign(year=lambda df: df["slice_id"].astype(int))
        .loc[lambda df: df["year"].between(start_year, end_year)]
        .drop(columns=["year"])
        .reset_index(drop=True)
    )
    if frame.empty:
        raise ValueError("No slices survived the requested year filter")
    return frame


def _load_lemma_slice_stats(
    prepared_root: Path,
    selected_slices: set[str],
) -> pd.DataFrame:
    frame = pd.read_parquet(prepared_root / "lemma_slice_stats.parquet")
    return frame.loc[frame["slice_id"].isin(selected_slices)].reset_index(drop=True)


if __name__ == "__main__":
    main()
