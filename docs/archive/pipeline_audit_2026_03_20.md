# N2 Pipeline Audit

Date: 2026-03-20

## Purpose

This note audits the current `Articles/N2` codebase against the updated paper direction:

- exploratory comparison of drift techniques in Portuguese political discourse
- main corpus: `BrPoliCorpus floor`
- minimum comparison set: `TF-IDF`, `Word2Vec`, and contextual `BERT`

The goal is to separate what is reusable from what still reflects the earlier
Word2Vec-first quicklook framing.

## Executive Summary

The current pipeline is a solid base for the `Word2Vec` arm of the paper, but it
is **not yet in good comparative shape** for the new article direction.

Main conclusions:

1. The codebase is structurally reusable and already supports a reproducible
   Hydra + `uv` workflow.
2. The default pipeline is still **Word2Vec-centric**, not comparison-centric.
3. There is currently **no TF-IDF implementation** in the codebase.
4. The contextual path is still implemented as **`bert_confirmatory`**, meaning
   BERT is downstream of Word2Vec candidate selection instead of a first-class
   peer method.
5. The available yearly run artifacts do **not** currently demonstrate one
   completed clean main run with full manifests and preserved outputs.

## What Is Reusable

### 1. Corpus loading and slice preparation

Reusable files:

- `src/stil_semantic_change/data/loaders.py`
- `src/stil_semantic_change/preprocessing/text.py`
- `src/stil_semantic_change/utils/periods.py`

Why they remain useful:

- they already produce slice-aware prepared artifacts
- they work for both `BrPoliCorpus` and `Roda Viva`
- they store document- and lemma-level statistics needed by any method family

### 2. Experiment configuration and artifact hashing

Reusable files:

- `run/conf/config.yaml`
- `src/stil_semantic_change/utils/config/schema.py`
- `src/stil_semantic_change/utils/config/loader.py`
- `src/stil_semantic_change/utils/artifacts.py`

Why they remain useful:

- the experiment hash structure is a good base for method-comparison runs
- configs are already explicit and reproducible
- the artifact layout is understandable and easy to extend

### 3. Word2Vec training and alignment

Reusable files:

- `src/stil_semantic_change/word2vec/train.py`
- `src/stil_semantic_change/word2vec/align.py`
- `src/stil_semantic_change/word2vec/vector_store.py`
- `src/stil_semantic_change/word2vec/score.py`

Why they remain useful:

- this is already the strongest implemented method family
- the per-slice training and Procrustes alignment match the intended static
  embedding baseline
- replicate support is already present

### 4. Qualitative reporting utilities

Reusable files:

- `src/stil_semantic_change/reporting/qualitative.py`
- parts of `src/stil_semantic_change/reporting/plots.py`

Why they remain useful:

- the paper will still need case studies and context packets
- early/late qualitative inspection remains useful across all methods

## What Is Too Tied To The Old Framing

### 1. Default task wiring

Current default:

- `run/conf/config.yaml`
- `run/conf/task/run_yearly_core.yaml`

The default pipeline is:

1. `prepare_corpus`
2. `train_word2vec`
3. `align_embeddings`
4. `score_candidates`
5. `report_candidates`

This means the default experiment is still a **Word2Vec pipeline with reports**,
not a multi-method comparison pipeline.

### 2. BERT is still downstream and confirmatory

Current file:

- `run/conf/task/bert_confirmatory.yaml`
- `src/stil_semantic_change/contextual/confirmatory.py`

Current behavior:

- BERT depends on `candidate_sets.json`
- `candidate_sets.json` is produced by `Word2Vec` scoring
- BERT output is merged back as `comparison_with_word2vec.parquet`

This is useful for a confirmatory follow-up, but it is too tied to the old paper
story. For the new article, BERT should be a peer method scored on a shared
comparison panel, not a subsidiary validator of Word2Vec.

### 3. Reporting is Word2Vec-specific

Current file:

- `src/stil_semantic_change/reporting/plots.py`

Examples of old framing:

- `Top 15 By Word2Vec Drift`
- `Confirmatory BERT vs Word2Vec Drift`
- nearest-neighbor panels are built only from Word2Vec aligned spaces

These remain useful, but they are not yet the central reporting layer the new
paper needs.

### 4. STIL readiness heuristics are single-method heuristics

Current file:

- `src/stil_semantic_change/reporting/evaluation.py`

The readiness logic currently checks:

- Word2Vec candidate counts
- Word2Vec drift vs stable-control separation
- Procrustes anchor counts

That was reasonable for the earlier framing, but it is not enough for the new
paper because it does not evaluate:

- cross-method agreement
- top-k overlap
- rank correlation
- cost/runtime tradeoffs

## Current Default Pipeline Status

## Is the codebase ready for the new comparative direction?

Not yet.

It is **architecturally close**, but still missing the comparative backbone:

- no `TF-IDF` baseline
- no shared method-comparison score table
- no method registry or task graph for multiple scorers
- no correlation or overlap stage
- no runtime/cost artifact table

## Is the current default pipeline the clean full Word2Vec run?

Not in practice.

The code path for a clean run exists, but the preserved artifacts do not show a
completed clean run:

- `ae5022228b99` contains the main `run_yearly_core.log`, but the run does not
  reach alignment, scoring, or reporting manifests
- the log only reaches one completed trained slice (`2000`) before stopping
- `aligned/`, `scores/`, and `reports/` are empty in the preserved artifact tree
- the “quicklook” subdirectory still has its log, but the quicklook outputs are
  not fully preserved there either

This means the repository currently preserves **logs of attempted runs**, not a
fully inspectable final run package.

## Quicklook Versus Clean Path

The current documentation is directionally correct:

- the quicklook was useful
- it was not the final clean run

Evidence in the repo suggests:

- the exploratory path used the fast lookup-only preprocessing route
- `resolved_brpolicorpus_floor_yearly_run_yearly_core_93bb6350.yaml` uses
  `spacy_model: pt_lookup`
- the more linguistically faithful config also exists in
  `resolved_brpolicorpus_floor_yearly_run_yearly_core_414690a5.yaml` with
  `spacy_model: pt_core_news_sm`
- later reruns `4f821f885e1d` and `c5437a2643c5` are incomplete

So the codebase is **not yet at the point where the default preserved outputs
represent one clean finished Word2Vec baseline run**.

## Most Important Gaps For The New Paper

### 1. Missing TF-IDF baseline

This is the largest methodological gap.

Without it, the paper cannot answer the advisor's cheap-versus-expensive
question in a convincing way.

### 2. No shared comparison panel artifact

The project needs a canonical table like:

- one row per lemma
- one column block per method
- shared metadata columns for frequency, slice coverage, and manual labels

Right now each method family does not write into a shared comparison schema.

### 3. No comparison stage

The pipeline needs a dedicated stage for:

- Spearman correlation
- Kendall correlation
- top-k overlap
- Jaccard overlap
- method disagreement cases
- runtime and memory summaries

### 4. BERT candidate selection is too dependent on Word2Vec

BERT currently inherits terms from Word2Vec candidate sets. For the new paper,
candidate selection should come from a shared panel that includes:

- high-drift terms from each method
- stable controls
- theory seeds

### 5. Artifact organization does not yet distinguish exploratory from final runs

Right now the experiment root structure is fine, but the comparative paper will
need clearer naming for:

- exploratory quicklooks
- clean baselines
- method-comparison outputs
- final paper-facing figures and tables

## Recommended Next Implementation Steps

### 1. Add runtime metadata to every stage

Why first:

- the new paper explicitly needs cost comparisons
- this is easy to add without destabilizing the current pipeline

### 2. Introduce a shared comparison-table schema

Recommended output:

- `scores/comparison_panel.parquet`

Minimum columns:

- `lemma`
- `slice_presence_ratio`
- `total_frequency`
- `word2vec_*`
- `tfidf_*`
- `bert_*`
- `is_seed`
- `is_stable_control`
- `manual_drift_type`

### 3. Implement the TF-IDF baseline as a first-class scorer

Recommended shape:

- new lexical module under `src/stil_semantic_change/lexical/`
- new task stage separate from Word2Vec
- output written into `scores/tfidf/`

### 4. Replace the old confirmatory framing with peer-method comparison

Recommended direction:

- keep the existing BERT implementation logic
- stop treating it as confirmatory-only in task naming and reports
- run it on the shared comparison panel

### 5. Add a dedicated method-comparison reporting stage

Recommended outputs:

- correlation table
- top-k overlap table
- cost/runtime table
- agreement/disagreement figure
- method-specific case-study appendix

### 6. Preserve complete run artifacts for at least one clean baseline

Before drafting strong paper claims, the repo should contain at least one
inspectable completed run with:

- manifests present
- score tables present
- reports present
- evaluation report present

## Practical Recommendation

The codebase should now be interpreted as:

- **ready to support Word2Vec baseline development**
- **not yet ready as the full comparative experiment pipeline**

The next development cycle should focus on:

1. stage/runtime instrumentation
2. TF-IDF baseline
3. shared comparison panel
4. comparison reporting
5. one preserved clean yearly baseline run
