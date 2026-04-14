#!/usr/bin/env python3
"""Run a supplementary EmbeddingGemma comparator on the frozen contextual sample set."""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from stil_semantic_change.contextual.embeddinggemma_posthoc import (  # noqa: E402
    DEFAULT_MODEL_NAME,
    DEFAULT_PROMPT_MODE,
    run_embeddinggemma_posthoc,
    variant_name,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

DEFAULT_EXPERIMENT_HASH = "ba65fe5b9cce"
DEFAULT_DATASET = "brpolicorpus_floor_yearly"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Post-hoc EmbeddingGemma comparator")
    parser.add_argument(
        "--experiment-hash",
        default=DEFAULT_EXPERIMENT_HASH,
        help="Frozen experiment hash to read from",
    )
    parser.add_argument(
        "--dataset",
        default=DEFAULT_DATASET,
        help="Dataset name under run/outputs/experiments",
    )
    parser.add_argument(
        "--model-name",
        default=DEFAULT_MODEL_NAME,
        help="Embedding model identifier to load from Hugging Face",
    )
    parser.add_argument(
        "--prompt-mode",
        default=DEFAULT_PROMPT_MODE,
        choices=("clustering", "semantic_similarity", "retrieval_query"),
        help="Official EmbeddingGemma prompt family to prepend",
    )
    parser.add_argument("--batch-size", type=int, default=32, help="Embedding batch size")
    parser.add_argument(
        "--device",
        default="auto",
        choices=("auto", "cpu", "cuda", "mps"),
        help="Execution device",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    artifacts_root = PROJECT_ROOT / "run" / "outputs"
    frozen_run_root = artifacts_root / "experiments" / args.dataset / args.experiment_hash
    output_root = (
        artifacts_root
        / "post_hoc"
        / "embeddinggemma_comparator"
        / variant_name(args.model_name, args.prompt_mode)
    )

    if not frozen_run_root.exists():
        logger.error("Frozen run root not found: %s", frozen_run_root)
        sys.exit(1)

    summary = run_embeddinggemma_posthoc(
        frozen_run_root=frozen_run_root,
        output_root=output_root,
        project_root=PROJECT_ROOT,
        model_name=args.model_name,
        prompt_mode=args.prompt_mode,
        batch_size=args.batch_size,
        device=args.device,
    )

    print("\n" + "=" * 72)
    print("EMBEDDINGGEMMA POST-HOC COMPARATOR COMPLETE")
    print("=" * 72)
    print(f"Frozen run: {summary['frozen_run_root']}")
    print(f"Model: {summary['model_name']}")
    print(f"Prompt mode: {summary['prompt_mode']}")
    print(f"Embedded occurrences: {summary['embedded_occurrences']}")
    print(f"Score rows: {summary['score_rows']}")
    print(f"Output root: {output_root}")


if __name__ == "__main__":
    main()
