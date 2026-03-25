#!/usr/bin/env python3
"""Post-hoc APD reanalysis on frozen BERT artifacts.

This script reads the frozen BERT occurrence embeddings from a completed
experiment run and computes APD (Average Pairwise Distance) scores as an
alternative to the centroid-based PRT metric already stored in
scores.parquet.

Usage
-----
    python run/pipeline/apd_reanalysis.py [--experiment-hash HASH]

The frozen run is never modified. Outputs go to:
    run/outputs/post_hoc/apd_reanalysis/
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from stil_semantic_change.contextual.apd_reanalysis import run_apd_reanalysis

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)s %(levelname)s %(message)s",
)
logger = logging.getLogger(__name__)

DEFAULT_EXPERIMENT_HASH = "ba65fe5b9cce"
DEFAULT_DATASET = "brpolicorpus_floor_yearly"


def main() -> None:
    parser = argparse.ArgumentParser(description="Post-hoc APD reanalysis")
    parser.add_argument(
        "--experiment-hash",
        default=DEFAULT_EXPERIMENT_HASH,
        help="Experiment hash to read frozen artifacts from",
    )
    parser.add_argument(
        "--dataset",
        default=DEFAULT_DATASET,
        help="Dataset name in the experiment path",
    )
    args = parser.parse_args()

    artifacts_root = PROJECT_ROOT / "run" / "outputs"
    frozen_bert_root = (
        artifacts_root
        / "experiments"
        / args.dataset
        / args.experiment_hash
        / "scores"
        / "bert_confirmatory"
    )
    output_root = artifacts_root / "post_hoc" / "apd_reanalysis"

    if not frozen_bert_root.exists():
        logger.error("Frozen BERT root not found: %s", frozen_bert_root)
        sys.exit(1)

    result = run_apd_reanalysis(frozen_bert_root, output_root)

    # Print key findings
    print("\n" + "=" * 70)
    print("APD REANALYSIS COMPLETE")
    print("=" * 70)
    print(f"Lemmas scored: {result['n_lemmas']}")
    print(f"Score rows: {result['n_score_rows']}")
    print(f"Trajectory rows: {result['n_trajectory_rows']}")
    print()
    print("APD vs PRT Agreement:")
    for row in result["agreement"]:
        layer = row["layer"]
        metric = row["metric"]
        value = row["value"]
        if metric == "spearman_rho":
            print(f"  Layer {layer}: Spearman rho = {value:.4f}")
        elif metric == "spearman_pvalue":
            print(f"  Layer {layer}: p-value = {value:.2e}")
        elif metric.startswith("top_"):
            k = metric.split("_")[1]
            print(f"  Layer {layer}: Top-{k} overlap = {int(value)}/{row['max_possible']}")
    print(f"\nOutputs written to: {output_root}")


if __name__ == "__main__":
    main()
