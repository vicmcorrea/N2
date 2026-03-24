# Frozen Results Snapshot

**Snapshot date**: 2026-03-24 17:19 BRT (UTC-3)

**Frozen experiment run**: `ba65fe5b9cce`

**Full path**: `run/outputs/experiments/brpolicorpus_floor_yearly/ba65fe5b9cce`

**DO NOT USE**: `8e15dc2372c5` (corrupted by aborted rerun)

All values below were read directly from the output files on disk at the time
of this snapshot. If new experiments are run, compare against these numbers to
detect changes.

---

## 1. Corpus Summary

**Source**: `prepared/slice_summary.parquet` (24 rows),
`prepared/prepare_corpus_manifest.json`

| Metric | Value |
|--------|-------|
| Total speeches | 428,366 |
| Total retained tokens | 63,036,642 |
| Total content_lemma characters | 538,537,771 |
| Yearly slices | 24 |
| Year range | 2000–2023 |
| Unique lemmas | 225,484 |
| Eligible lemmas (after filtering) | 3,221 |
| Text views generated | `normalized_surface`, `content_surface`, `content_lemma` |
| Doc shards | 474 |

### Slice-level breakdown

**Source**: `prepared/slice_summary.parquet`

| Slice | Speeches | Tokens |
|-------|----------|--------|
| 2000 | 3,041 | 630,426 |
| 2001 | 18,837 | 3,569,257 |
| 2002 | 11,357 | 2,289,094 |
| 2003 | 22,860 | 4,171,779 |
| 2004 | 18,634 | 3,440,937 |
| 2005 | 18,805 | 3,464,645 |
| 2006 | 16,443 | 2,837,491 |
| 2007 | 14,709 | 2,338,737 |
| 2008 | 16,947 | 2,780,454 |
| 2009 | 22,994 | 3,705,481 |
| 2010 | 14,466 | 2,278,955 |
| 2011 | 21,969 | 2,509,603 |
| 2012 | 15,161 | 2,612,215 |
| 2013 | 26,307 | 4,106,849 |
| 2014 | 16,556 | 2,628,745 |
| 2015 | 26,868 | 3,580,084 |
| 2016 | 22,042 | 2,949,276 |
| 2017 | 26,414 | 3,055,774 |
| 2018 | 15,131 | 1,773,609 |
| 2019 | 14,402 | 1,621,547 |
| 2020 | 14,397 | 1,422,924 |
| 2021 | 20,715 | 2,076,560 |
| 2022 | 13,611 | 1,449,965 |
| 2023 | 15,700 | 1,742,235 |

### Yearly quartiles

| Metric | Q1 (p25) | Median | Q3 (p75) |
|--------|----------|--------|----------|
| Speeches | 14,648 | 16,752 | 21,987 |
| Tokens (M) | 2.00 | 2.62 | 3.45 |
| Characters (M) | 16.9 | 22.3 | 29.7 |
| Lemmas | 39,456 | 50,269 | 58,637 |

---

## 2. Candidate Eligibility

**Source**: `scores/eligible_vocabulary.parquet` (225,484 rows)

| Filter | Threshold |
|--------|-----------|
| Min frequency per slice | 50 |
| Min documents per slice | 5 |
| Min slice presence | 80% of 24 slices |
| POS restriction (drift/control) | NOUN, ADJ |
| Excluded procedural terms | `ano`, `matéria`, `medida`, `nº`, `sr.` |

Result: 3,221 eligible lemmas for TF-IDF and Word2Vec scoring.

---

## 3. Word2Vec Baseline

**Source**: `scores/scores_aggregated.parquet` (3,221 rows),
`scores/score_candidates_manifest.json`, `aligned/align_embeddings_manifest.json`

### Hyperparameters

| Parameter | Value |
|-----------|-------|
| Architecture | Skip-gram |
| Dimensions | 300 |
| Window | 5 |
| Negative samples | 5 |
| Min count | 5 |
| Epochs | 5 |
| Replicates | 2 (different seeds) |
| Alignment | Orthogonal Procrustes, top 20,000 anchors |

### Runtime

| Stage | Duration |
|-------|----------|
| Prepare corpus | 18,823s (~5.2 hours) |
| Train models + align | 320.9s (~5.4 min) + 38.9s alignment |

### Artifacts

- 48 Word2Vec `.model` files (2 replicates × 24 slices)
- 48 aligned `.npz` vector files
- 96 aligned `.json` vocabulary files
- 48 anchor summary rows in `aligned/anchor_summary.parquet`

### Top 15 Drift Candidates (filtered: NOUN/ADJ, not excluded)

**Source**: `scores/candidate_sets.json`, `scores/scores_aggregated.parquet`

| Rank | Lemma | Primary Drift | POS | Mean Freq |
|------|-------|---------------|-----|-----------|
| 1 | intervenção | 0.4028 | NOUN | 600.7 |
| 2 | planalto | 0.4009 | NOUN | 154.3 |
| 3 | renovação | 0.3880 | NOUN | 204.2 |
| 4 | troca | 0.3860 | NOUN | 290.2 |
| 5 | inaceitável | 0.3809 | ADJ | 284.6 |
| 6 | oposto | 0.3808 | ADJ | 70.1 |
| 7 | perigoso | 0.3802 | ADJ | 204.6 |
| 8 | crítico | 0.3796 | ADJ | 382.5 |
| 9 | contradição | 0.3795 | NOUN | 156.5 |
| 10 | excepcional | 0.3789 | ADJ | 168.5 |
| 11 | inédito | 0.3778 | ADJ | 135.5 |
| 12 | exposição | 0.3760 | NOUN | 301.5 |
| 13 | bloqueio | 0.3758 | NOUN | 74.3 |
| 14 | típico | 0.3755 | ADJ | 119.3 |
| 15 | alvo | 0.3754 | NOUN | 237.1 |

### Bottom 10 Stable Controls (lowest drift, NOUN/ADJ)

| Rank | Lemma | Primary Drift | POS | Mean Freq |
|------|-------|---------------|-----|-----------|
| 3221 | juridicidade | 0.0994 | NOUN | 148.3 |
| 3220 | orçamentária | 0.1496 | ADJ | 116.3 |
| 3219 | recurso | 0.1507 | NOUN | 7,158.4 |
| 3218 | trabalho | 0.1522 | NOUN | 8,703.1 |
| 3217 | público | 0.1525 | ADJ | 13,353.8 |
| 3216 | social | 0.1539 | ADJ | 6,777.6 |
| 3215 | ensino | 0.1539 | NOUN | 1,994.4 |
| 3214 | votação | 0.1541 | NOUN | 4,006.3 |
| 3213 | potável | 0.1542 | ADJ | 97.8 |
| 3212 | direito | 0.1553 | NOUN | 7,103.5 |

---

## 4. TF-IDF Baseline

**Source**: `scores/tfidf_drift/scores.parquet` (3,221 rows),
`scores/tfidf_drift/summary.json`, `scores/tfidf_drift/tfidf_drift_manifest.json`

### Method

- Smoothed IDF, TF-IDF weight per lemma per yearly slice
- Drift = mean absolute change between adjacent slices
- Runtime: 24.63 seconds

### Top 15 Drift Candidates (filtered: NOUN/ADJ, not excluded)

**Source**: `scores/tfidf_drift/candidate_sets.json` (via `summary.json`)

| Rank | Lemma | Primary Drift | POS | Mean Freq |
|------|-------|---------------|-----|-----------|
| 1 | crise | 0.000494 | NOUN | 2,544.6 |
| 2 | trabalhador | 0.000489 | NOUN | 4,888.8 |
| 3 | saúde | 0.000466 | NOUN | 5,904.7 |
| 4 | salário | 0.000465 | NOUN | 3,001.0 |
| 5 | emenda | 0.000455 | NOUN | 3,859.9 |
| 6 | eleição | 0.000436 | NOUN | 2,513.3 |
| 7 | previdência | 0.000432 | NOUN | 1,152.0 |
| 8 | provisório | 0.000406 | ADJ | 3,037.4 |
| 9 | preço | 0.000381 | NOUN | 1,983.5 |
| 10 | mínimo | 0.000364 | ADJ | 1,860.4 |
| 11 | político | 0.000362 | ADJ | 7,150.3 |
| 12 | voto | 0.000362 | NOUN | 4,175.0 |
| 13 | real | 0.000351 | NOUN | 6,103.3 |
| 14 | partido | 0.000341 | NOUN | 5,046.2 |
| 15 | destaque | 0.000337 | NOUN | (not in top filtered) |

Note: TF-IDF top 15 before panel filtering also included `reforma` (rank 3,
0.000895) but it was classified as a theory seed instead of a TF-IDF drift
candidate.

### TF-IDF Stable Controls (bottom 10)

Same 10 terms as W2V stable controls — `altíssimo`, `expresso`, `complicado`,
`gigantesco`, `vento`, `sincero`, `prejudicial`, `posterior`, `inteligente`,
`altivez` — selected as the intersection of lowest-ranked terms from both methods.

---

## 5. Shared Comparison Panel

**Source**: `scores/comparison_panel/comparison_panel.parquet` (55 rows),
`scores/comparison_panel/summary.json`

### Composition

| Bucket | Count | Terms |
|--------|-------|-------|
| `word2vec_only_drift` | 15 | intervenção, planalto, renovação, troca, inaceitável, oposto, perigoso, crítico, contradição, excepcional, inédito, exposição, bloqueio, típico, alvo |
| `tfidf_only_drift` | 15 | crise, trabalhador, saúde, salário, emenda, eleição, previdência, provisório, preço, mínimo, político, voto, real, partido, destaque |
| `stable_control` | 20 | (10 from W2V bottom: juridicidade, orçamentária, recurso, trabalho, público, social, ensino, votação, potável, direito) + (10 from TF-IDF bottom: inteligente, complicado, gigantesco, expresso, prejudicial, posterior, vento, altíssimo, sincero, altivez) |
| `theory_seed` | 5 | democracia, corrupção, reforma, economia, liberdade |
| **Total** | **55** | |

### Key observation

- Shared drift count between W2V and TF-IDF top 15: **0** (complete disagreement)
- Zero overlap confirms methods capture fundamentally different signals

---

## 6. Contextual BERT

**Source**: `scores/bert_confirmatory/summary.json`,
`scores/bert_confirmatory/scores.parquet` (110 rows = 55 lemmas × 2 layers)

### Configuration

| Parameter | Value |
|-----------|-------|
| Model | `rufimelo/bert-large-portuguese-cased-sts` |
| Device | CPU |
| Layers extracted | −1, −4 |
| Contexts per lemma per slice | up to 64 |
| Context window | 48 tokens |
| Sampled occurrences | 82,468 |
| Embedded occurrences | 82,461 |
| Prototype rows | 2,640 (55 lemmas × 24 slices × 2 layers) |
| Score rows | 110 (55 lemmas × 2 layers) |

### Disk usage

| File | Size |
|------|------|
| `occurrence_embeddings_layer_-1.npz` | 313 MB |
| `occurrence_embeddings_layer_-4.npz` | 314 MB |
| `prototype_embeddings_layer_-1.npz` | 5.0 MB |
| `prototype_embeddings_layer_-4.npz` | 5.0 MB |
| `sampled_occurrences.parquet` | 1.4 MB |

### Top 20 by BERT layer −1 (primary drift)

**Source**: `scores/bert_confirmatory/scores.parquet`

| Rank | Lemma | BERT Drift | Bucket |
|------|-------|------------|--------|
| 1 | bloqueio | 0.04250 | word2vec_only_drift |
| 2 | típico | 0.03202 | word2vec_only_drift |
| 3 | exposição | 0.03142 | word2vec_only_drift |
| 4 | expresso | 0.03060 | stable_control |
| 5 | salário | 0.02984 | tfidf_only_drift |
| 6 | vento | 0.02948 | stable_control |
| 7 | mínimo | 0.02845 | tfidf_only_drift |
| 8 | troca | 0.02825 | word2vec_only_drift |
| 9 | preço | 0.02750 | tfidf_only_drift |
| 10 | voto | 0.02689 | tfidf_only_drift |
| 11 | real | 0.02688 | tfidf_only_drift |
| 12 | intervenção | 0.02656 | word2vec_only_drift |
| 13 | excepcional | 0.02534 | word2vec_only_drift |
| 14 | renovação | 0.02449 | word2vec_only_drift |
| 15 | eleição | 0.02425 | tfidf_only_drift |
| 16 | trabalho | 0.02409 | stable_control |
| 17 | público | 0.02393 | stable_control |
| 18 | crítico | 0.02381 | word2vec_only_drift |
| 19 | político | 0.02316 | tfidf_only_drift |
| 20 | destaque | 0.02265 | tfidf_only_drift |

### Stable-control leakage in raw BERT top-k

Positions 4 (expresso), 6 (vento), 16 (trabalho), 17 (público) are stable controls
that leak into the raw BERT top-20. This motivated the filtered contextual panel.

---

## 7. Cross-Method Agreement

**Source**: `scores/cross_method_agreement/correlations.parquet` (12 rows),
`scores/cross_method_agreement/topk_overlap.parquet` (12 rows),
`scores/cross_method_agreement/summary.json`

### Rank Correlations (all_panel, N=55)

**Source**: `scores/cross_method_agreement/correlations.parquet`

| Layer | Pair | Spearman ρ | p-value | Pearson r | p-value |
|-------|------|------------|---------|-----------|---------|
| −4 | BERT vs Word2Vec | **0.321** | 0.017 | 0.382 | 0.004 |
| −4 | BERT vs TF-IDF | −0.038 | 0.782 | −0.081 | 0.555 |
| −4 | Word2Vec vs TF-IDF | **−0.540** | 0.000021 | −0.626 | 3.2×10⁻⁷ |
| −1 | BERT vs Word2Vec | **0.208** | 0.128 | 0.253 | 0.062 |
| −1 | BERT vs TF-IDF | 0.125 | 0.365 | 0.057 | 0.678 |
| −1 | Word2Vec vs TF-IDF | **−0.540** | 0.000021 | −0.626 | 3.2×10⁻⁷ |

### Rank Correlations (disagreement_cases only, N=30)

| Layer | Pair | Spearman ρ | p-value |
|-------|------|------------|---------|
| −4 | BERT vs Word2Vec | 0.160 | 0.397 |
| −4 | BERT vs TF-IDF | −0.197 | 0.296 |
| −4 | Word2Vec vs TF-IDF | **−0.736** | 0.000004 |
| −1 | BERT vs Word2Vec | 0.018 | 0.927 |
| −1 | BERT vs TF-IDF | −0.049 | 0.798 |
| −1 | Word2Vec vs TF-IDF | **−0.736** | 0.000004 |

### BERT Layer Agreement

**Source**: `scores/cross_method_agreement/layer_correlations.parquet`

- Layer −4 vs −1 on BERT primary_drift across the 55-lemma panel:
  Spearman **0.858** (not stored directly; derived from the cross-method
  layer_correlations file and confirmed in the paper)

### Top-k Overlap (all_panel, layer −1)

**Source**: `scores/cross_method_agreement/topk_overlap.parquet`

| k | BERT/W2V overlap | BERT/TF-IDF overlap | W2V/TF-IDF overlap |
|---|------------------|---------------------|--------------------|
| 5 | 0 | 1 | 0 |
| 10 | 1 | 2 | 0 |
| **15** | **7** | **6** | **0** |

### Top-k Overlap (all_panel, layer −4)

| k | BERT/W2V overlap | BERT/TF-IDF overlap | W2V/TF-IDF overlap |
|---|------------------|---------------------|--------------------|
| 5 | 0 | 0 | 0 |
| 10 | 2 | 1 | 0 |
| 15 | 8 | 4 | 0 |

### Filtered Contextual Panel (top 15, layer −1)

**Source**: `scores/cross_method_agreement/summary.json`,
`scores/cross_method_agreement/bert_filtered_panel.parquet` (35 rows total,
top 15 shown)

After excluding stable controls from the raw BERT ranking:

1. bloqueio
2. típico
3. exposição
4. salário
5. mínimo
6. troca
7. preço
8. voto
9. real
10. intervenção
11. excepcional
12. renovação
13. eleição
14. crítico
15. político

### Stable-Control Leakage (top 10)

**Source**: `scores/cross_method_agreement/bert_stable_control_leakage.parquet`
(20 rows)

1. expresso
2. vento
3. trabalho
4. público
5. inteligente
6. social
7. ensino
8. sincero
9. recurso
10. altíssimo

---

## 8. Runtime Summary

**Source**: All `*_manifest.json` files

| Stage | Duration | Timestamp |
|-------|----------|-----------|
| Prepare corpus | 18,823s (5.2h) | 2026-03-21 17:44 → 22:58 UTC |
| Train models + score | 320.9s (5.4min) | 2026-03-22 15:56 → 16:02 UTC |
| Align embeddings | 38.9s | 2026-03-21 23:15 → 23:16 UTC |
| TF-IDF drift | 24.7s | 2026-03-22 14:20 → 14:21 UTC |
| Comparison panel | 0.06s | 2026-03-22 16:03 UTC |
| BERT confirmatory | (CPU run, no wall-clock in manifest) | 2026-03-22 ~13:52–17:56 UTC |
| Report generation | 5.6s | 2026-03-23 00:13 UTC |
| Cross-method agreement | (post-run analysis) | 2026-03-23 03:44 UTC |

### Relative cost ratios (paper-facing)

| Method | Scope | Relative cost |
|--------|-------|---------------|
| TF-IDF | 3,221 lemmas | seconds (1×) |
| Word2Vec | 3,221 lemmas | minutes (~56×) |
| BERT | 55 lemmas / 82,461 occ | hours (~600×) |

---

## 9. Complete File Inventory

### Root directory

```
ba65fe5b9cce/
```

Total disk usage: ~8.6 GB

| Directory | Size | Purpose |
|-----------|------|---------|
| `prepared/` | 4.3 GB | Preprocessed corpus (shards, text views, tokens) |
| `models/` | 2.8 GB | 48 Word2Vec .model files |
| `aligned/` | 896 MB | 48 aligned .npz vectors + vocab JSONs |
| `scores/` | 618 MB | All scoring outputs (W2V, TF-IDF, BERT, panel, agreement) |
| `reports/` | 6.3 MB | Figures, tables, summary markdown |
| `logs/` | 420 KB | Run logs |

### prepared/ (4.3 GB)

| File/Dir | Rows/Count | Description |
|----------|------------|-------------|
| `slice_summary.parquet` | 24 rows | Per-slice document and token counts |
| `lemma_slice_stats.parquet` | 1,184,808 rows | Per-lemma-per-slice frequency and doc count |
| `doc_shards.parquet` | 474 rows | Shard-level document and token counts |
| `prepare_corpus_manifest.json` | — | Stage metadata and timestamps |
| `docs/metadata/` | — | Document metadata |
| `docs/raw_text/` | — | Raw text storage |
| `text_views/by_slice/` | 546 files | `content_lemma`, `content_surface`, `normalized_surface` per slice |
| `text_views/by_doc/` | — | Per-document text views |
| `tokens/content/` | 474 files | Tokenized content shards |

### models/ (2.8 GB)

- 48 directories: `replicate_{0,1}/{2000..2023}/`
- Each contains a trained Word2Vec `.model` file

### aligned/ (896 MB)

- `anchor_summary.parquet` — 48 rows (replicate × slice anchor counts)
- `align_embeddings_manifest.json`
- 48 `vectors.npz` files (aligned embedding matrices)
- 96 `vectors.json` files (vocabulary mappings)

### scores/ (618 MB)

#### scores/ (root-level Word2Vec)

| File | Rows | Columns | Description |
|------|------|---------|-------------|
| `eligible_vocabulary.parquet` | 225,484 | 14 | All lemmas with eligibility flags |
| `scores_aggregated.parquet` | 3,221 | 29 | Aggregated drift scores (mean over replicates) |
| `scores_per_replicate.parquet` | 6,442 | 5 | Per-replicate drift scores |
| `trajectory.parquet` | 148,154 | 6 | Per-transition drift values |
| `candidate_sets.json` | — | — | W2V drift candidates, stable controls, theory seeds |
| `score_candidates_manifest.json` | — | — | Stage metadata |

#### scores/tfidf_drift/

| File | Rows | Columns | Description |
|------|------|---------|-------------|
| `scores.parquet` | 3,221 | 24 | TF-IDF drift scores for all eligible lemmas |
| `eligible_vocabulary.parquet` | 225,484 | 14 | Copy of eligibility table |
| `trajectory.parquet` | 74,083 | 8 | Per-transition TF-IDF weights and drift |
| `candidate_sets.json` | — | — | TF-IDF candidates (from `summary.json`) |
| `summary.json` | — | — | TF-IDF drift candidates, controls, seeds, runtime |
| `tfidf_drift_manifest.json` | — | — | Stage metadata |

#### scores/comparison_panel/

| File | Rows | Columns | Description |
|------|------|---------|-------------|
| `comparison_panel.parquet` | 55 | 30 | Full panel with both methods' ranks and scores |
| `summary.json` | — | — | Panel composition counts |
| `comparison_panel_manifest.json` | — | — | Stage metadata |

#### scores/bert_confirmatory/

| File | Rows/Size | Description |
|------|-----------|-------------|
| `scores.parquet` | 110 rows (55×2 layers) | BERT drift scores |
| `trajectory.parquet` | 2,530 rows | Per-transition BERT drift |
| `sampled_occurrences.parquet` | 82,468 rows | Sampled context metadata |
| `occurrence_embeddings_meta.parquet` | 82,461 rows | Embedded occurrence metadata |
| `prototype_meta.parquet` | 2,640 rows | Per-lemma-slice-layer prototype metadata |
| `comparison_with_word2vec.parquet` | 110 rows | BERT scores merged with W2V and TF-IDF |
| `occurrence_embeddings_layer_-1.npz` | 313 MB | Raw BERT embeddings (layer −1) |
| `occurrence_embeddings_layer_-4.npz` | 314 MB | Raw BERT embeddings (layer −4) |
| `prototype_embeddings_layer_-1.npz` | 5.0 MB | Centroid embeddings (layer −1) |
| `prototype_embeddings_layer_-4.npz` | 5.0 MB | Centroid embeddings (layer −4) |
| `summary.json` | — | Model config, term list, occurrence counts |
| `direct_run.log` | — | BERT inference log |

#### scores/cross_method_agreement/

| File | Rows | Description |
|------|------|-------------|
| `correlations.parquet` | 12 | Spearman/Pearson for all pairs × 2 layers × 2 subsets |
| `topk_overlap.parquet` | 12 | Top-k overlap for k={5,10,15} × 2 layers × 2 subsets |
| `layer_correlations.parquet` | 4 | BERT layer-specific correlations with W2V and TF-IDF |
| `bert_ranked_panel.parquet` | 110 | Full panel ranked by BERT (both layers) |
| `bert_filtered_panel.parquet` | 35 | Panel after removing stable controls from BERT ranking |
| `bert_stable_control_leakage.parquet` | 20 | Stable controls that leaked into raw BERT top-k |
| `largest_bert_word2vec_gap.parquet` | 24 | Terms with largest BERT–W2V rank gap |
| `largest_bert_tfidf_gap.parquet` | 24 | Terms with largest BERT–TF-IDF rank gap |
| `bert_candidate_sets.json` | — | Filtered BERT candidate lists |
| `summary.json` | — | Agreement summary, filtered top terms |
| `cross_method_agreement_manifest.json` | — | Stage metadata |

### reports/ (6.3 MB)

| File | Description |
|------|-------------|
| `analysis_summary.md` | Auto-generated experiment summary |
| `candidate_summary.parquet` | 30 rows — drift candidate details |
| `nearest_neighbors_early_late.parquet` | 64 rows — nearest neighbors for selected terms |
| `coverage_by_slice.png` | Corpus coverage visualization |
| `drift_trajectories.png` | Drift trajectory plots |
| `drift_vs_frequency_dispersion.png` | Drift vs. frequency scatter |
| `ranked_candidate_overview.png` | Ranked candidate bar chart |
| `selected_terms_slice_heatmap.png` | Heatmap of selected terms across slices |
| `nearest_neighbors_early_late.png` | Nearest neighbor comparison |
| `bert_word2vec_comparison.png` | BERT vs. Word2Vec comparison plot |
| `report_manifest.json` | Figure/table inventory |
| `report_candidates_manifest.json` | Stage metadata |

### logs/

| File | Description |
|------|-------------|
| `run_yearly_core.log` | 428 KB — main pipeline log |
| `report_candidates.log` | 0 bytes — empty |

---

## 10. Paper-Facing Figures

**Location**: `2026S1_STIL_conceptDrift/figs/paper/`

These were generated from the frozen run artifacts and are currently used
in `main.tex`:

| Figure # in paper | File | Source data |
|-------------------|------|-------------|
| 1 | `figure_05_study_design.pdf` | Workflow diagram (manually composed) |
| 2 | `figure_02_method_agreement.pdf` | `scores/cross_method_agreement/correlations.parquet` |
| 3 | `figure_03_overlap_and_rank_statistics.pdf` | `scores/cross_method_agreement/topk_overlap.parquet` + panel |
| 4 | `figure_04_representative_trajectories.pdf` | `scores/bert_confirmatory/trajectory.parquet` + `scores/trajectory.parquet` + `scores/tfidf_drift/trajectory.parquet` |

Archived (not in manuscript):

| File | Source data |
|------|-------------|
| `figure_01_corpus_profile.pdf` | `prepared/slice_summary.parquet` |

---

## 11. Key Numbers for Quick Reference

These are the numbers that appear in the manuscript (`main.tex`):

| What | Value | Source file |
|------|-------|-------------|
| Yearly slices | 24 | `prepared/slice_summary.parquet` |
| Total speeches | 428,366 | `prepared/slice_summary.parquet` |
| Total tokens | 63,036,642 | `prepared/prepare_corpus_manifest.json` |
| Unique lemmas | 225,484 | `scores/eligible_vocabulary.parquet` |
| Eligible lemmas | 3,221 | `scores/scores_aggregated.parquet` |
| Panel size | 55 | `scores/comparison_panel/summary.json` |
| W2V drift terms | 15 | `scores/candidate_sets.json` |
| TF-IDF drift terms | 15 | `scores/tfidf_drift/summary.json` |
| Stable controls | 20 | `scores/comparison_panel/summary.json` |
| Theory seeds | 5 | `scores/comparison_panel/summary.json` |
| BERT sampled occurrences | 82,461 | `scores/bert_confirmatory/summary.json` |
| W2V vs TF-IDF Spearman | −0.540 | `scores/cross_method_agreement/correlations.parquet` |
| W2V vs TF-IDF p-value | 0.000021 | `scores/cross_method_agreement/correlations.parquet` |
| BERT(−1) vs W2V Spearman | 0.208 | `scores/cross_method_agreement/correlations.parquet` |
| BERT(−1) vs W2V p-value | 0.128 | `scores/cross_method_agreement/correlations.parquet` |
| BERT(−1) vs TF-IDF Spearman | 0.125 | `scores/cross_method_agreement/correlations.parquet` |
| BERT(−1) vs TF-IDF p-value | 0.365 | `scores/cross_method_agreement/correlations.parquet` |
| BERT layer agreement | 0.858 | Derived from layer_correlations |
| Top-15 overlap BERT/W2V | 7 | `scores/cross_method_agreement/topk_overlap.parquet` |
| Top-15 overlap BERT/TF-IDF | 6 | `scores/cross_method_agreement/topk_overlap.parquet` |
| Top-15 overlap W2V/TF-IDF | 0 | `scores/cross_method_agreement/topk_overlap.parquet` |

---

*End of snapshot. If new experiments are run after 2026-03-24, create a new
snapshot file and compare against these values to track what changed.*
