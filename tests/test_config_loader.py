from __future__ import annotations

import os
import subprocess
import sys

import pytest

from stil_semantic_change.utils.config import build_experiment_config
from tests.helpers import make_raw_cfg


def test_build_experiment_config_rejects_invalid_text_view(
    project_root,
    toy_dataset_dir,
    tmp_path,
) -> None:
    raw_cfg = make_raw_cfg(project_root, tmp_path / "outputs", toy_dataset_dir)
    raw_cfg.model.text_view = "not_a_view"

    with pytest.raises(ValueError, match="Invalid model.text_view"):
        build_experiment_config(raw_cfg)


def test_runner_import_does_not_pull_bert_dependencies() -> None:
    repo_root = "/Users/victor/Dropbox/USP/ResearchThesis/Articles/N2"
    command = [
        sys.executable,
        "-c",
        (
            "import sys; "
            "sys.path.insert(0, 'src'); "
            "import stil_semantic_change.runner; "
            "assert 'transformers' not in sys.modules; "
            "assert 'stil_semantic_change.contextual.confirmatory' not in sys.modules; "
            "print('ok')"
        ),
    ]
    completed = subprocess.run(
        command,
        cwd=repo_root,
        env={**os.environ, "PYTHONPATH": "src"},
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0, completed.stderr
    assert completed.stdout.strip() == "ok"
