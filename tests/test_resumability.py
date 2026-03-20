from __future__ import annotations

from time import sleep

from stil_semantic_change.runner import run_experiment
from stil_semantic_change.utils.artifacts import build_artifact_paths, stage_manifest_path
from stil_semantic_change.utils.config import build_experiment_config
from tests.helpers import make_raw_cfg


def test_pipeline_skips_existing_outputs(project_root, toy_dataset_dir, tmp_path) -> None:
    artifacts_root = tmp_path / "outputs"
    raw_cfg = make_raw_cfg(project_root, artifacts_root, toy_dataset_dir, force=False)
    cfg = build_experiment_config(raw_cfg)
    run_experiment(cfg, raw_cfg)

    paths = build_artifact_paths(cfg, raw_cfg)
    manifest = stage_manifest_path(paths.prepared_root, "prepare_corpus")
    initial_mtime = manifest.stat().st_mtime

    run_experiment(cfg, raw_cfg)
    assert manifest.stat().st_mtime == initial_mtime

    sleep(1.0)
    forced_raw_cfg = make_raw_cfg(project_root, artifacts_root, toy_dataset_dir, force=True)
    forced_cfg = build_experiment_config(forced_raw_cfg)
    run_experiment(forced_cfg, forced_raw_cfg)
    assert manifest.stat().st_mtime > initial_mtime
