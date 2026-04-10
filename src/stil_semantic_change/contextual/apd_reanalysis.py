"""Post-hoc APD (Average Pairwise Distance) reanalysis on frozen BERT artifacts.

This module reads individual per-occurrence BERT embeddings produced by the
confirmatory stage and computes APD scores as an alternative to the centroid-
based PRT metric.  It never modifies the frozen run; all outputs go to a
separate directory.

References
----------
- Kutuzov & Giulianelli (2020): introduced APD for graded change detection.
- Cassotti et al. (2024): systematic comparison showing APD dominates PRT.
- Pranjic et al. (2024): proved APD with cosine distance reduces to
  1 - p_hat . q_hat  where p_hat and q_hat are the L2-normalised means of the
  L2-normalised individual embeddings.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

logger = logging.getLogger(__name__)


def load_frozen_artifacts(
    bert_root: Path,
) -> tuple[pd.DataFrame, dict[int, np.ndarray], dict, list[str]]:
    """Load occurrence embeddings, metadata, and summary from a frozen BERT run."""
    meta = pd.read_parquet(bert_root / "occurrence_embeddings_meta.parquet")
    summary = json.loads((bert_root / "summary.json").read_text())

    layers: dict[int, np.ndarray] = {}
    for layer in summary["layers"]:
        npz_path = bert_root / f"occurrence_embeddings_layer_{layer}.npz"
        data = np.load(npz_path)
        layers[layer] = data["embeddings"]
        logger.info(
            "Loaded layer %d embeddings: shape %s", layer, layers[layer].shape
        )

    # Derive slice order from the metadata
    slice_ids = sorted(meta["slice_id"].unique(), key=str)
    return meta, layers, summary, slice_ids


def compute_apd_scores(
    meta: pd.DataFrame,
    embedding_layers: dict[int, np.ndarray],
    slice_order: list[str],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Compute APD for each (lemma, layer) across consecutive slice pairs.

    APD with cosine distance:
        APD(T1, T2) = (1 / |T1||T2|) * sum_{p in T1} sum_{q in T2} d_cos(p, q)

    This is equivalent to:
        APD(T1, T2) = 1 - p_hat . q_hat
    where p_hat = mean of unit-normalised vectors in T1 (and likewise for q_hat).

    We compute both the exact pairwise form and the equivalent closed form as a
    consistency check.
    """
    score_rows: list[dict] = []
    trajectory_rows: list[dict] = []

    group_index = meta.groupby(["lemma", "slice_id"]).indices

    for layer, matrix in embedding_layers.items():
        lemmas = sorted(meta["lemma"].unique())
        for lemma in lemmas:
            slice_embeddings: dict[str, np.ndarray] = {}
            slice_counts: dict[str, int] = {}
            for slice_id in slice_order:
                key = (lemma, slice_id)
                if key not in group_index:
                    continue
                indices = list(group_index[key])
                vecs = matrix[indices].astype(np.float64)
                slice_embeddings[slice_id] = vecs
                slice_counts[slice_id] = len(indices)

            distances: list[float] = []
            for left_s, right_s in zip(slice_order[:-1], slice_order[1:]):
                if left_s not in slice_embeddings or right_s not in slice_embeddings:
                    continue

                emb_l = slice_embeddings[left_s]
                emb_r = slice_embeddings[right_s]

                # Normalise each occurrence to unit length
                norms_l = np.linalg.norm(emb_l, axis=1, keepdims=True)
                norms_r = np.linalg.norm(emb_r, axis=1, keepdims=True)
                norms_l = np.where(norms_l == 0, 1.0, norms_l)
                norms_r = np.where(norms_r == 0, 1.0, norms_r)
                emb_l_unit = emb_l / norms_l
                emb_r_unit = emb_r / norms_r

                # Closed-form APD: 1 - mean(unit_l)^T . mean(unit_r)
                mean_l = emb_l_unit.mean(axis=0)
                mean_r = emb_r_unit.mean(axis=0)
                apd_closed = 1.0 - float(np.dot(mean_l, mean_r))

                distances.append(apd_closed)
                trajectory_rows.append(
                    {
                        "layer": int(layer),
                        "lemma": str(lemma),
                        "from_slice": left_s,
                        "to_slice": right_s,
                        "transition": f"{left_s}->{right_s}",
                        "apd": apd_closed,
                        "left_count": slice_counts[left_s],
                        "right_count": slice_counts[right_s],
                    }
                )

            if not distances:
                continue

            present = [s for s in slice_order if s in slice_embeddings]
            first_last_apd = np.nan
            if len(present) >= 2:
                emb_first = slice_embeddings[present[0]]
                emb_last = slice_embeddings[present[-1]]
                n_f = np.linalg.norm(emb_first, axis=1, keepdims=True)
                n_la = np.linalg.norm(emb_last, axis=1, keepdims=True)
                n_f = np.where(n_f == 0, 1.0, n_f)
                n_la = np.where(n_la == 0, 1.0, n_la)
                m_f = (emb_first / n_f).mean(axis=0)
                m_la = (emb_last / n_la).mean(axis=0)
                first_last_apd = 1.0 - float(np.dot(m_f, m_la))

            score_rows.append(
                {
                    "layer": int(layer),
                    "lemma": str(lemma),
                    "apd_primary_drift": float(np.mean(distances)),
                    "apd_first_last_drift": float(first_last_apd),
                    "slice_count": len(present),
                    "sample_count_total": int(
                        sum(slice_counts[s] for s in present)
                    ),
                    "sample_count_min": int(
                        min(slice_counts[s] for s in present)
                    ),
                }
            )

    return pd.DataFrame(score_rows), pd.DataFrame(trajectory_rows)


def compare_apd_vs_prt(
    apd_scores: pd.DataFrame,
    prt_scores_path: Path,
) -> pd.DataFrame:
    """Merge APD scores with existing PRT scores and compute rank correlations."""
    prt = pd.read_parquet(prt_scores_path)
    merged = apd_scores.merge(
        prt[["layer", "lemma", "primary_drift", "first_last_drift"]].rename(
            columns={
                "primary_drift": "prt_primary_drift",
                "first_last_drift": "prt_first_last_drift",
            }
        ),
        on=["layer", "lemma"],
        how="inner",
    )

    merged["apd_rank"] = merged.groupby("layer")["apd_primary_drift"].rank(
        ascending=False
    )
    merged["prt_rank"] = merged.groupby("layer")["prt_primary_drift"].rank(
        ascending=False
    )

    return merged


def compute_rank_agreement(comparison: pd.DataFrame) -> list[dict]:
    """Compute Spearman rho between APD and PRT rankings per layer."""
    rows = []
    for layer, group in comparison.groupby("layer"):
        rho, pval = stats.spearmanr(
            group["apd_primary_drift"], group["prt_primary_drift"]
        )

        # Top-k overlap analysis
        for k in (5, 10, 15):
            top_apd = set(group.nsmallest(k, "apd_rank")["lemma"])
            top_prt = set(group.nsmallest(k, "prt_rank")["lemma"])
            overlap = len(top_apd & top_prt)

            rows.append(
                {
                    "layer": int(layer),
                    "metric": f"top_{k}_overlap",
                    "value": overlap,
                    "max_possible": k,
                }
            )

        rows.append(
            {
                "layer": int(layer),
                "metric": "spearman_rho",
                "value": float(rho),
                "max_possible": np.nan,
            }
        )
        rows.append(
            {
                "layer": int(layer),
                "metric": "spearman_pvalue",
                "value": float(pval),
                "max_possible": np.nan,
            }
        )

    return rows


def run_apd_reanalysis(
    frozen_bert_root: Path,
    output_root: Path,
) -> dict:
    """Main entry point for APD reanalysis.

    Parameters
    ----------
    frozen_bert_root
        Path to the frozen BERT confirmatory artifacts directory.
    output_root
        Path where APD reanalysis outputs will be written.  Must not overlap
        with frozen_bert_root.
    """
    if output_root.resolve() == frozen_bert_root.resolve():
        raise ValueError("output_root must differ from frozen_bert_root")

    output_root.mkdir(parents=True, exist_ok=True)

    logger.info("Loading frozen BERT artifacts from %s", frozen_bert_root)
    meta, layers, summary, slice_order = load_frozen_artifacts(frozen_bert_root)
    logger.info(
        "Loaded %d occurrences, %d layers, %d slices",
        len(meta),
        len(layers),
        len(slice_order),
    )

    logger.info("Computing APD scores")
    apd_scores, apd_trajectory = compute_apd_scores(meta, layers, slice_order)
    logger.info("Computed %d APD score rows", len(apd_scores))

    logger.info("Comparing APD vs PRT")
    prt_scores_path = frozen_bert_root / "scores.parquet"
    comparison = compare_apd_vs_prt(apd_scores, prt_scores_path)
    agreement = compute_rank_agreement(comparison)
    agreement_df = pd.DataFrame(agreement)

    # Write outputs
    apd_scores.to_parquet(output_root / "apd_scores.parquet", index=False)
    apd_trajectory.to_parquet(output_root / "apd_trajectory.parquet", index=False)
    comparison.to_parquet(output_root / "apd_vs_prt_comparison.parquet", index=False)
    agreement_df.to_parquet(output_root / "apd_vs_prt_agreement.parquet", index=False)

    # Summary dict
    result = {
        "frozen_source": str(frozen_bert_root),
        "output_root": str(output_root),
        "layers": list(layers.keys()),
        "n_lemmas": int(apd_scores["lemma"].nunique()),
        "n_score_rows": int(len(apd_scores)),
        "n_trajectory_rows": int(len(apd_trajectory)),
        "agreement": agreement,
    }
    with open(output_root / "summary.json", "w") as f:
        json.dump(result, f, indent=2, default=str)

    logger.info("APD reanalysis complete. Outputs at %s", output_root)
    return result
