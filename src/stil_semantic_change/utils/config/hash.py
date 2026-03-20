from __future__ import annotations

import hashlib
import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from omegaconf import DictConfig, OmegaConf

from stil_semantic_change.utils.config.schema import ExperimentConfig


def _drop_keys(obj: Any, keys: set[str]) -> Any:
    if isinstance(obj, dict):
        return {key: _drop_keys(value, keys) for key, value in obj.items() if key not in keys}
    if isinstance(obj, list):
        return [_drop_keys(value, keys) for value in obj]
    return obj


def _to_jsonable(obj: Any) -> Any:
    if isinstance(obj, Path):
        return str(obj)
    if isinstance(obj, dict):
        return {key: _to_jsonable(value) for key, value in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_to_jsonable(value) for value in obj]
    return obj


def hash_config(cfg: DictConfig, *, exclude_keys: set[str] | None = None, size: int = 8) -> str:
    exclude = exclude_keys or {"hydra"}
    container = OmegaConf.to_container(cfg, resolve=True)
    container = _drop_keys(container, exclude)
    payload = json.dumps(container, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    digest = hashlib.sha1(payload.encode("utf-8")).hexdigest()
    return digest[: max(1, int(size))]


def hash_experiment_config(cfg: ExperimentConfig, *, size: int = 12) -> str:
    payload = json.dumps(_to_jsonable(asdict(cfg)), sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha1(payload.encode("utf-8")).hexdigest()
    return digest[: max(1, int(size))]
