from __future__ import annotations

import argparse
import logging
from pathlib import Path

from stil_semantic_change.contextual.qwen3_posthoc import (
    DEFAULT_BATCH_SIZE,
    DEFAULT_LAYERS,
    DEFAULT_LOCAL_MODEL_PATH,
    DEFAULT_MODEL_ID,
    DEFAULT_PREFERRED_LAYER,
    run_qwen3_posthoc,
)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the post-hoc Qwen3 token-level comparator on frozen BERT samples.",
    )
    parser.add_argument(
        "--frozen-run-root",
        type=Path,
        default=Path(
            "run/outputs/experiments/brpolicorpus_floor_yearly/ba65fe5b9cce"
        ),
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=Path(
            "run/outputs/post_hoc/qwen3_token_comparator/"
            "Qwen__Qwen3-Embedding-0.6B__token_hidden_states"
        ),
    )
    parser.add_argument(
        "--embeddinggemma-root",
        type=Path,
        default=Path(
            "run/outputs/post_hoc/embeddinggemma_comparator/"
            "google__embeddinggemma-300m__clustering"
        ),
    )
    parser.add_argument("--project-root", type=Path, default=Path("."))
    parser.add_argument("--model-id", default=DEFAULT_MODEL_ID)
    parser.add_argument("--model-path", type=Path, default=DEFAULT_LOCAL_MODEL_PATH)
    parser.add_argument("--batch-size", type=int, default=DEFAULT_BATCH_SIZE)
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--preferred-layer", type=int, default=DEFAULT_PREFERRED_LAYER)
    parser.add_argument(
        "--layers",
        type=int,
        nargs="+",
        default=list(DEFAULT_LAYERS),
    )
    return parser.parse_args()


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(name)s %(levelname)s %(message)s",
    )
    args = _parse_args()
    summary = run_qwen3_posthoc(
        frozen_run_root=args.frozen_run_root.resolve(),
        output_root=args.output_root.resolve(),
        project_root=args.project_root.resolve(),
        embeddinggemma_root=args.embeddinggemma_root.resolve(),
        model_id=str(args.model_id),
        model_path=args.model_path.resolve(),
        layers=tuple(int(layer) for layer in args.layers),
        batch_size=int(args.batch_size),
        device=str(args.device),
        preferred_layer=int(args.preferred_layer),
    )

    print()
    print("=" * 72)
    print("QWEN3 POST-HOC TOKEN COMPARATOR COMPLETE")
    print("=" * 72)
    print(f"Frozen run: {summary['frozen_run_root']}")
    print(f"Model: {summary['model_id']}")
    print(f"Layers: {summary['layers']}")
    print(f"Embedded occurrences: {summary['embedded_occurrences']}")
    print(f"Score rows: {summary['score_rows']}")
    print(f"Output root: {args.output_root.resolve()}")


if __name__ == "__main__":
    main()
