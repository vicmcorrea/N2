from __future__ import annotations

import argparse
from pathlib import Path

from omegaconf import OmegaConf

from stil_semantic_change.reporting.evaluation import (
    evaluate_run,
    write_readiness_reports,
)
from stil_semantic_change.utils.config import build_experiment_config
from stil_semantic_change.utils.config.schema import LoggingConfig
from stil_semantic_change.utils.logging import setup_logging


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Assess STIL readiness from an existing run.")
    parser.add_argument("--run-root", type=Path, required=True, help="Root directory of the completed run")
    parser.add_argument(
        "--resolved-config",
        type=Path,
        help="Optional resolved Hydra config to reuse for metadata",
    )
    parser.add_argument(
        "--log-dir",
        type=Path,
        default=Path("run/outputs/logs"),
        help="Where to write the evaluation log",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    setup_logging(LoggingConfig(log_dir=args.log_dir), log_file=args.log_dir / "evaluate_run.log")
    cfg = None
    if args.resolved_config:
        raw_cfg = OmegaConf.load(args.resolved_config)
        cfg = build_experiment_config(raw_cfg)

    run_root = args.run_root.resolve()
    result = evaluate_run(run_root, cfg)
    write_readiness_reports(run_root, result)
    print(f"Evaluation finished; status={result['status']}")


if __name__ == "__main__":
    main()
