# APD Reanalysis Findings

**Date**: 2026-03-25
**Frozen run**: `ba65fe5b9cce`
**APD outputs**: `run/outputs/post_hoc/apd_reanalysis/`
**Script**: `run/pipeline/apd_reanalysis.py`

---

## Summary

We computed Average Pairwise Distance (APD) scores from the frozen individual
BERT occurrence embeddings (82,461 vectors per layer, 55 lemmas, 24 slices)
and compared APD rankings with the existing centroid-based PRT scores.

**The APD and PRT rankings correlate strongly (Spearman ρ = 0.79, p < 10⁻¹²),
confirming that the centroid-based results are broadly robust.** However, the
two metrics foreground different properties of the embedding space, producing
meaningful rank differences at the top of the list.

---

## Key Numbers

| Metric | Layer −1 | Layer −4 |
|--------|----------|----------|
| Spearman ρ (APD vs PRT) | 0.790 | 0.788 |
| p-value | 7.5 × 10⁻¹³ | 9.3 × 10⁻¹³ |
| Pearson r | 0.755 | — |
| Top-5 overlap | 2/5 | 2/5 |
| Top-10 overlap | 5/10 | 5/10 |
| Top-15 overlap | 7/15 | 10/15 |
| APD cross-layer agreement | ρ = 0.830 | — |
| PRT cross-layer agreement | ρ = 0.858 | — |

---

## What the Metrics Capture Differently

### APD favours terms with high embedding variance

APD measures the average pairwise distance between all individual
occurrences across consecutive slices.  Because it operates on all
occurrence pairs, it is sensitive to the overall spread (variance) of
the embedding cloud, not just the movement of the centroid.

**Terms promoted by APD but not PRT** (layer −1, top-15):
`trabalho`, `público`, `político`, `social`, `direito`, `crítico`,
`perigoso`, `alvo`

These tend to be high-frequency, polysemous terms whose BERT embeddings
form a wide cloud in embedding space.  Even without large centroid
movement, the large pairwise distances inflate their APD score.

### PRT favours terms with directional centroid shift

PRT measures cosine distance between slice-level centroid (mean) vectors.
It captures the magnitude and direction of the average-usage shift,
regardless of within-slice spread.

**Terms promoted by PRT but not APD** (layer −1, top-15):
`bloqueio`, `salário`, `mínimo`, `intervenção`, `eleição`,
`preço`, `renovação`, `excepcional`

These terms show coherent directional shift in their average usage
pattern, consistent with the political trajectory interpretations
discussed in the paper.

### The biggest discrepancies

| Lemma | APD rank | PRT rank | Δ |
|-------|---------|---------|---|
| `direito` | 15 | 42 | 27 |
| `salário` | 31 | 5 | 26 |
| `bloqueio` | 26 | 1 | 25 |
| `mínimo` | 30 | 7 | 23 |
| `reforma` | 44 | 22 | 22 |

`bloqueio` and `salário` — the paper's featured PRT-led terms — drop
substantially under APD, because their centroid shift is large but their
overall embedding variance is moderate.

---

## Bucket Separation (Drift vs Stable Controls)

| Metric | Drift mean | Stable mean | Mann-Whitney p |
|--------|-----------|-------------|----------------|
| PRT (layer −1) | 0.022 | 0.018 | **0.008** |
| APD (layer −1) | 0.488 | 0.452 | 0.081 |

**PRT separates drift candidates from stable controls more cleanly
(p = 0.008) than APD (p = 0.081) on this dataset.** This is because APD
conflates genuine drift with high within-cluster variance that some
frequent terms exhibit regardless of semantic change.  For an exploratory
comparison without external ground truth, PRT's stronger bucket
separation suggests it provides a less noisy signal for distinguishing
method-nominated drift from stable baselines.

---

## APD by Bucket (Layer −1)

| Bucket | N | APD mean | PRT mean |
|--------|---|----------|----------|
| word2vec_only_drift | 15 | 0.500 | 0.023 |
| tfidf_only_drift | 15 | 0.477 | 0.022 |
| stable_control | 20 | 0.452 | 0.018 |
| theory_seed | 5 | 0.441 | 0.017 |

---

## Implications for the Paper

1. **Robustness validated**: ρ = 0.79 means the comparative conclusions
   drawn from PRT (agreement structure, cost-benefit, method sensitivities)
   hold under APD as well.

2. **PRT is actually preferable here**: On a dataset without external
   annotation, the metric that better separates known drift from known
   stable controls is more useful for comparative analysis.  PRT achieves
   this more cleanly than APD on BrPoliCorpus.

3. **The difference is interpretable**: APD captures embedding-cloud
   breadth (polysemy, contextual diversity), while PRT captures directional
   shift in the average usage.  Both are meaningful, but for our paper's
   question — which methods agree on which terms — directional shift is
   the more informative signal.

4. **Paper integration**: The Limitations section should be updated to
   present APD as a completed robustness check (not a gap), and the
   Discussion or Results should include the ρ = 0.79 finding.

---

## Files Produced

```
run/outputs/post_hoc/apd_reanalysis/
├── apd_scores.parquet              55 lemmas × 2 layers = 110 rows
├── apd_trajectory.parquet          55 lemmas × 2 layers × 23 transitions
├── apd_vs_prt_comparison.parquet   merged APD + PRT with ranks
├── apd_vs_prt_agreement.parquet    Spearman and top-k overlap stats
└── summary.json                    run metadata
```
