from __future__ import annotations

import argparse
from pathlib import Path

from stil_semantic_change.reporting.qualitative import (
    collect_context_samples,
    write_context_reports,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Sample qualitative contexts from an N2 run.")
    parser.add_argument(
        "--run-root",
        type=Path,
        required=True,
        help="Path to the completed run root",
    )
    parser.add_argument(
        "--term",
        dest="terms",
        action="append",
        help=(
            "Add a term to sample (repeat flag to add multiple). "
            "Defaults to drift candidates plus controls/seeds."
        ),
    )
    parser.add_argument(
        "--per-term-per-phase",
        type=int,
        default=2,
        help="Number of contexts to collect per term per phase (early/late).",
    )
    parser.add_argument(
        "--context-window",
        type=int,
        default=8,
        help="Number of tokens to include before/after the target token.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=13,
        help="Deterministic sampling seed.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    run_root = args.run_root.resolve()
    contexts = collect_context_samples(
        run_root,
        terms=args.terms,
        per_term_per_phase=args.per_term_per_phase,
        context_window=args.context_window,
        seed=args.seed,
    )
    write_context_reports(run_root, contexts)
    print(f"Qualitative contexts written for {len(contexts)} samples.")


if __name__ == "__main__":
    main()
