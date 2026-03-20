from __future__ import annotations

import logging
import os
from pathlib import Path

os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

import hydra
from omegaconf import DictConfig, OmegaConf

from stil_semantic_change.runner import run_experiment
from stil_semantic_change.utils.config import build_experiment_config, hash_config
from stil_semantic_change.utils.logging import setup_logging

logger = logging.getLogger(__name__)


def _write_resolved_config(raw_cfg: DictConfig, out_dir: Path, stem: str) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{stem}.yaml"
    out_path.write_text(OmegaConf.to_yaml(raw_cfg, resolve=True), encoding="utf-8")
    return out_path


@hydra.main(version_base="1.3", config_path="../conf", config_name="config")
def main(raw_cfg: DictConfig) -> None:
    cfg = build_experiment_config(raw_cfg)
    setup_logging(cfg.logging)

    if cfg.io.write_resolved_config:
        config_hash = hash_config(raw_cfg)
        stem = f"resolved_{cfg.dataset.name}_{cfg.task.name}_{config_hash}"
        path = _write_resolved_config(raw_cfg, cfg.io.artifacts_root / "configs", stem)
        logger.info("Wrote resolved Hydra config to %s", path)

    run_experiment(cfg, raw_cfg)


if __name__ == "__main__":
    main()
