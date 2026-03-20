from __future__ import annotations

from pathlib import Path

import pytest

from stil_semantic_change.utils.config import build_experiment_config
from tests.helpers import make_raw_cfg


@pytest.fixture()
def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


@pytest.fixture()
def toy_dataset_dir(project_root: Path) -> Path:
    return project_root / "tests" / "fixtures" / "toy_brpolicorpus_floor"
@pytest.fixture()
def built_cfg(project_root: Path, toy_dataset_dir: Path, tmp_path: Path):
    raw_cfg = make_raw_cfg(project_root, tmp_path / "outputs", toy_dataset_dir)
    return raw_cfg, build_experiment_config(raw_cfg)
