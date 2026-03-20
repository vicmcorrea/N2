from __future__ import annotations

import json
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from omegaconf import DictConfig

from stil_semantic_change.utils.config.hash import hash_config
from stil_semantic_change.utils.config.schema import ExperimentConfig


@dataclass(frozen=True)
class ArtifactPaths:
    experiment_root: Path
    prepared_root: Path
    models_root: Path
    aligned_root: Path
    scores_root: Path
    reports_root: Path
    logs_root: Path


def build_artifact_paths(cfg: ExperimentConfig, raw_cfg: DictConfig) -> ArtifactPaths:
    experiment_hash = hash_config(
        raw_cfg,
        exclude_keys={"force", "hydra", "task"},
        size=12,
    )
    root = cfg.io.artifacts_root / "experiments" / cfg.dataset.name / experiment_hash
    return ArtifactPaths(
        experiment_root=root,
        prepared_root=root / "prepared",
        models_root=root / "models",
        aligned_root=root / "aligned",
        scores_root=root / "scores",
        reports_root=root / "reports",
        logs_root=root / "logs",
    )


def ensure_directories(paths: ArtifactPaths) -> None:
    for path in (
        paths.experiment_root,
        paths.prepared_root,
        paths.models_root,
        paths.aligned_root,
        paths.scores_root,
        paths.reports_root,
        paths.logs_root,
    ):
        path.mkdir(parents=True, exist_ok=True)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_dataframe(path: Path, frame: pd.DataFrame) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_parquet(path, index=False)


def read_dataframe(path: Path) -> pd.DataFrame:
    return pd.read_parquet(path)


def write_npz(path: Path, **arrays: np.ndarray) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(path, **arrays)


def stage_manifest_path(stage_root: Path, stage_name: str) -> Path:
    return stage_root / f"{stage_name}_manifest.json"


def stage_complete(stage_root: Path, stage_name: str) -> bool:
    return stage_manifest_path(stage_root, stage_name).exists()


def reset_stage_root(stage_root: Path) -> None:
    if not stage_root.exists():
        return
    for child in stage_root.iterdir():
        if child.is_dir():
            shutil.rmtree(child)
        else:
            child.unlink()
