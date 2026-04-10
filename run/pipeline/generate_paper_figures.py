from __future__ import annotations

import argparse
from pathlib import Path

from stil_semantic_change.reporting.paper_figures import generate_paper_figures


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate paper-ready figures from a frozen run.")
    parser.add_argument(
        "--experiment-root",
        type=Path,
        required=True,
        help="Path to the frozen experiment root.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        required=True,
        help="Directory where the figure bundle should be written.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    manifest = generate_paper_figures(
        experiment_root=args.experiment_root.resolve(),
        output_dir=args.output_dir.resolve(),
    )
    print(f"Wrote {len(manifest['figures'])} figure groups to {args.output_dir.resolve()}")


if __name__ == "__main__":
    main()
