# N2 Next Steps Execution Plan

Date: 2026-03-20

## Goal

Lock the project into a clean sequence that produces one trustworthy baseline before the
comparative expansion starts.

## Immediate Plan

### Phase 1. Preserve a clean Word2Vec baseline

Objective:

- produce one completed yearly `BrPoliCorpus floor` baseline run using the clean default
  preprocessing path
- confirm that manifests, scores, and reports are all written
- keep this run as the static baseline for later comparison

Run settings:

- task: `run_yearly_core`
- dataset: `brpolicorpus_floor_yearly`
- preprocess: default `pt_core_news_sm`
- model: `word2vec_skipgram_300d`
- force: `true` for this baseline rebuild

Success criteria:

- `prepared/prepare_corpus_manifest.json` exists
- `models/train_word2vec_manifest.json` exists
- `aligned/align_embeddings_manifest.json` exists
- `scores/score_candidates_manifest.json` exists
- `reports/report_candidates_manifest.json` exists
- `scores/scores_aggregated.parquet` exists
- `reports/analysis_summary.md` exists

Early-run checks:

- first five minutes show successful corpus preparation progress
- first Word2Vec slice training starts without dependency or path errors
- no immediate failures from spaCy model loading, parquet IO, or dataset parsing

### Phase 2. Freeze the baseline artifacts

Objective:

- record the exact run root and resolved config
- update docs with the final baseline path
- use this as the comparison reference for all later methods

Deliverables:

- baseline run path documented in `docs/`
- short note on preprocessing choice and any deviations

### Phase 3. Implement the cheap comparison arm

Objective:

- add a first-class `tfidf_drift` stage over the same prepared yearly slices

Required outputs:

- `scores/tfidf_drift/scores.parquet`
- `scores/tfidf_drift/trajectory.parquet`
- `scores/tfidf_drift/summary.json`

Design constraints:

- same lemma eligibility logic as Word2Vec
- same slice ordering
- same core drift fields for later comparison

### Phase 4. Build the shared comparison panel

Objective:

- create one canonical panel used by every downstream comparison and contextual run

Minimum contents:

- top Word2Vec terms
- top TF-IDF terms
- stable controls
- theory seeds
- metadata columns for frequency and slice coverage

### Phase 5. Promote contextual BERT to a peer stage

Objective:

- reuse the current contextual sampling/prototype code, but run it from the shared panel
  instead of from Word2Vec-only candidate sets

Minimum outputs:

- contextual scores in the same normalized schema as other methods
- runtime and sample metadata

### Phase 6. Add the cross-method comparison stage

Objective:

- produce paper-ready agreement and disagreement artifacts

Minimum outputs:

- Spearman correlation table
- Kendall correlation table
- top-k overlap and Jaccard overlap
- disagreement case packets
- runtime summary by method

## Operating Rules

- do not expand methods until one clean static baseline is preserved
- do not cite a contextual model name different from the one actually run
- keep exploratory outputs separate from clean baseline outputs
- add tests only when implementation changes introduce new behavior worth protecting

## Current Execution Order

1. Start and verify the clean Word2Vec baseline run.
2. Freeze the successful baseline path in docs.
3. Implement `tfidf_drift`.
4. Build `comparison_panel`.
5. Refactor contextual scoring to use the panel.
6. Implement cross-method comparison artifacts.
