# TF-IDF Drift Baseline

Date: 2026-03-22

## What Was Added

A first-class `tfidf_drift` stage now exists in the N2 experiment package.

New code paths:

- `src/stil_semantic_change/tfidf/score.py`
- `src/stil_semantic_change/selection/panel.py`
- `run/conf/task/tfidf_drift.yaml`

The implementation reuses the same prepared yearly slices already used by
`Word2Vec` and writes method-local outputs under:

- `scores/tfidf_drift/scores.parquet`
- `scores/tfidf_drift/trajectory.parquet`
- `scores/tfidf_drift/summary.json`
- `scores/tfidf_drift/candidate_sets.json`
- `scores/tfidf_drift/tfidf_drift_manifest.json`

## Clean Source Run

The clean frozen source run for the TF-IDF baseline is:

- `run/outputs/experiments/brpolicorpus_floor_yearly/ba65fe5b9cce`

The `tfidf_drift` artifacts were generated directly against that completed run's
prepared corpus instead of triggering another full pipeline rerun.

## Important Integrity Note

An overnight rerun also completed at:

- `run/outputs/experiments/brpolicorpus_floor_yearly/8e15dc2372c5`

However, after completion, an aborted forced `tfidf_drift` rerun briefly
re-entered `prepare_corpus` before being stopped. That means `8e15dc2372c5`
should **not** be treated as the immutable prepared-artifact source for future
method runs or paper-facing provenance.

Use `ba65fe5b9cce` as the frozen clean baseline source unless a fresh clean rerun
is completed and explicitly frozen.

## First Clean TF-IDF Result

The clean TF-IDF baseline completed in about `24.7` seconds on the frozen
`BrPoliCorpus floor` yearly prepared corpus.

Method metadata:

- text view: `content_lemma`
- scored terms: `3221`
- trajectory rows: `74083`

## Candidate Panel Status

The raw TF-IDF ranking was initially too procedural and frequency-dominated,
with terms such as `presidente`, `sr.`, `ano`, `medida`, and `nº` dominating the
top list.

To make the first cheap baseline more interpretable, the TF-IDF candidate-panel
selection now adds a method-local gate on top of the shared selection rules:

- exclude a small list of obviously procedural high-noise terms:
  - `ano`
  - `matéria`
  - `medida`
  - `nº`
  - `sr.`
- exclude the extreme global-frequency tail above the `0.995` quantile

This does **not** change the raw TF-IDF score table. It only changes the
candidate panel that would be used for downstream comparison and interpretation.

## Clean TF-IDF Drift Candidate Panel

The current cleaned TF-IDF drift panel on `ba65fe5b9cce` is:

- `crise`
- `trabalhador`
- `saúde`
- `salário`
- `emenda`
- `eleição`
- `previdência`
- `provisório`
- `preço`
- `mínimo`
- `político`
- `voto`
- `real`
- `partido`
- `destaque`

This is substantially more usable than the raw TF-IDF top list, though it still
leans toward lexical salience and institutional vocabulary rather than pure
semantic drift.

## Comparison Signal vs Word2Vec

On the frozen run `ba65fe5b9cce`, the full-vocabulary correlation between the
current `Word2Vec` drift scores and the current `TF-IDF` drift scores is
negative:

- Spearman: about `-0.386`
- Pearson: about `-0.389`

This is useful for the paper because it suggests the cheap lexical-profile
baseline is not simply recovering the same ranking as aligned `Word2Vec`.

## Status After Panel Build

That next step is now complete.

The shared comparison universe built on top of this frozen run is documented in:

- `docs/comparison_panel_2026_03_22.md`

Current result:

- `15` `Word2Vec` drift terms
- `15` `TF-IDF` drift terms
- `0` shared drift terms
- `30` disagreement cases across the two cheap methods

That makes the first comparison panel a strong input for contextual follow-up,
because it concentrates exactly on the terms where the cheap methods disagree.
