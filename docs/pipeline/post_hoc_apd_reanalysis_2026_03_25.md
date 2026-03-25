# Post-Hoc APD Reanalysis Pipeline

**Date**: 2026-03-25
**Related to**: Gap Analysis recommendation #1

---

## Purpose

Computes Average Pairwise Distance (APD) scores from frozen BERT occurrence
embeddings, without modifying the frozen run at `ba65fe5b9cce`.

## Architecture

```
Source code:
  src/stil_semantic_change/contextual/apd_reanalysis.py   # Core module
  run/pipeline/apd_reanalysis.py                          # CLI runner

Input (frozen, read-only):
  run/outputs/experiments/brpolicorpus_floor_yearly/ba65fe5b9cce/
    scores/bert_confirmatory/
      occurrence_embeddings_layer_-1.npz   (82,461 × 1024)
      occurrence_embeddings_layer_-4.npz   (82,461 × 1024)
      occurrence_embeddings_meta.parquet
      scores.parquet                       (PRT scores for comparison)
      summary.json

Output (new, separate directory):
  run/outputs/post_hoc/apd_reanalysis/
    apd_scores.parquet                     (110 rows: 55 lemmas × 2 layers)
    apd_trajectory.parquet                 (2,530 rows: per-transition APD)
    apd_vs_prt_comparison.parquet          (merged APD + PRT with ranks)
    apd_vs_prt_agreement.parquet           (Spearman and top-k overlap)
    summary.json                           (run metadata)
```

## Usage

```bash
# Default: reads from ba65fe5b9cce
python run/pipeline/apd_reanalysis.py

# Custom experiment hash
python run/pipeline/apd_reanalysis.py --experiment-hash <hash>
```

## Algorithm

APD with cosine distance between consecutive time slices:

```
APD(T1, T2) = 1 - p̂ · q̂
```

where `p̂ = mean(unit_normalised(embeddings_T1))` and likewise for `q̂`.
This is the closed-form equivalent of the full pairwise computation
(Pranjić et al. 2024), which avoids O(n²) cost while being algebraically
identical.

## Frozen Run Guarantee

The script only calls `np.load()` and `pd.read_parquet()` on the frozen
artifacts. It never opens them for writing. All outputs go to
`run/outputs/post_hoc/apd_reanalysis/`, completely outside the experiment
directory tree.
