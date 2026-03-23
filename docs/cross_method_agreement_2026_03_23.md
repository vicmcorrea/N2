# Cross-Method Agreement on Frozen Baseline

Date: 2026-03-23

## Purpose

This note records the first cross-method agreement and disagreement analysis built on
top of the frozen comparative baseline run:

- `run/outputs/experiments/brpolicorpus_floor_yearly/ba65fe5b9cce`

The goal is not to create a new experiment root. The goal is to turn the already
completed `Word2Vec` + `TF-IDF` + shared-panel + contextual `BERT` outputs into a
paper-facing comparison layer.

## Provenance

The cross-method artifacts were generated directly from:

- `scores/bert_confirmatory/comparison_with_word2vec.parquet`

within frozen run `ba65fe5b9cce`.

This is best treated as a **post-run analysis layer on the frozen baseline**, not as a
separate long rerun. The frozen source of truth remains:

- `run/outputs/experiments/brpolicorpus_floor_yearly/ba65fe5b9cce`

## New code and task surface

Code:

- `src/stil_semantic_change/comparison/cross_method.py`
- `src/stil_semantic_change/comparison/__init__.py`
- `src/stil_semantic_change/runner.py`
- `run/conf/task/cross_method_agreement.yaml`
- `tests/test_cross_method_agreement.py`

The new stage writes:

- `scores/cross_method_agreement/correlations.parquet`
- `scores/cross_method_agreement/topk_overlap.parquet`
- `scores/cross_method_agreement/bert_ranked_panel.parquet`
- `scores/cross_method_agreement/bert_filtered_panel.parquet`
- `scores/cross_method_agreement/bert_stable_control_leakage.parquet`
- `scores/cross_method_agreement/largest_bert_word2vec_gap.parquet`
- `scores/cross_method_agreement/largest_bert_tfidf_gap.parquet`
- `scores/cross_method_agreement/bert_candidate_sets.json`
- `scores/cross_method_agreement/summary.json`

## What the new layer does

It adds three things on top of the shared panel:

1. rank-correlation summaries across methods
2. top-k overlap summaries across methods
3. a paper-facing contextual panel that excludes stable controls from the raw BERT top
   list while preserving a separate leakage table for diagnostics

The preferred contextual layer is currently:

- `layer = -1`

## Main results

### 1. BERT is informative, but not just a copy of either cheap method

Across the full panel:

- `BERT(-4)` vs `Word2Vec`: Spearman `0.321`
- `BERT(-4)` vs `TF-IDF`: Spearman `-0.038`
- `BERT(-1)` vs `Word2Vec`: Spearman `0.208`
- `BERT(-1)` vs `TF-IDF`: Spearman `0.125`
- `Word2Vec` vs `TF-IDF`: Spearman `-0.540`

Interpretation:

- `Word2Vec` and `TF-IDF` remain strongly divergent on this panel
- contextual `BERT` is somewhat closer to `Word2Vec`, but still materially distinct

### 2. The first shared panel is genuinely disagreement-heavy

At `k = 15` on the full panel:

- `BERT(-1)` / `Word2Vec` overlap: `7`
- `BERT(-1)` / `TF-IDF` overlap: `6`
- `Word2Vec` / `TF-IDF` overlap: `0`

So the panel remains useful as a comparative disagreement set rather than a trivial
consensus set.

### 3. Raw BERT ranks still leak stable controls

Top stable-control leakage terms include:

- `expresso`
- `vento`
- `trabalho`
- `público`
- `inteligente`
- `social`
- `ensino`
- `sincero`
- `recurso`
- `altíssimo`

This confirms that raw contextual top-k should not be used directly as the paper-facing
drift list.

### 4. The filtered BERT panel is substantially cleaner

The preferred contextual drift list after excluding stable controls is:

- `bloqueio`
- `típico`
- `exposição`
- `salário`
- `mínimo`
- `troca`
- `preço`
- `voto`
- `real`
- `intervenção`
- `excepcional`
- `renovação`
- `eleição`
- `crítico`
- `político`

This is not perfect, but it is materially better than the raw contextual ranking for
paper-facing comparison.

## Current interpretation

The comparative pipeline now has three usable layers:

- `Word2Vec` as the aligned static-embedding method
- `TF-IDF` as the cheap lexical baseline
- contextual `BERT` as the expensive adjudication layer over the shared panel

The contextual result should currently be interpreted as:

- useful for agreement/disagreement analysis
- useful for adjudicating method-specific candidates
- not a replacement for the shared candidate panel with an unrestricted raw BERT top-k

## Current recommendation

For the paper-facing comparison section:

1. use the frozen run `ba65fe5b9cce` as the baseline source of truth
2. use `scores/comparison_panel/comparison_panel.parquet` as the common candidate universe
3. use `scores/cross_method_agreement/bert_filtered_panel.parquet` as the contextual
   top-list view
4. keep `scores/cross_method_agreement/bert_stable_control_leakage.parquet` as an
   explicit diagnostic artifact

## Next useful work

- produce a qualitative agreement/disagreement packet with nearest neighbors and contexts
- add a compact runtime/cost comparison table for `TF-IDF`, `Word2Vec`, and `BERT`
- decide whether the paper-facing contextual list should remain stable-control-filtered
  only, or also receive a light lexical exclusion pass
