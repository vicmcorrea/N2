# N2 Progress Status

Date: 2026-03-20

## Update: 2026-03-22

Since this note was first written:

- the clean `Word2Vec` yearly baseline was frozen at:
  - `Articles/N2/run/outputs/experiments/brpolicorpus_floor_yearly/ba65fe5b9cce`
- the strengthened candidate-panel filter was validated and documented
- a first-class `TF-IDF` drift stage was implemented
- clean `TF-IDF` artifacts were generated directly from the frozen baseline under:
  - `Articles/N2/run/outputs/experiments/brpolicorpus_floor_yearly/ba65fe5b9cce/scores/tfidf_drift`
- a first-class shared `comparison_panel` was built directly from the same frozen baseline under:
  - `Articles/N2/run/outputs/experiments/brpolicorpus_floor_yearly/ba65fe5b9cce/scores/comparison_panel`

Important integrity note:

- a later overnight rerun at `8e15dc2372c5` did finish, but its prepared root was
  later touched by an aborted forced rerun attempt
- because of that, `8e15dc2372c5` should not be treated as the immutable
  prepared-artifact source for future method runs
- `ba65fe5b9cce` remains the clean frozen baseline source

## Scope

This note records the current state of `Articles/N2` after the advisor feedback that shifted the paper away from a validation-heavy semantic-change claim and toward an exploratory comparison of drift techniques in Portuguese political discourse.

## Current Paper Direction

The paper should now be framed as:

- an exploratory comparison of drift signals in Brazilian Portuguese political discourse
- centered on `BrPoliCorpus floor`
- comparing cheap and expensive methods rather than trying to prove one gold-standard truth

Current target method families:

- `TF-IDF` or related lexical-profile drift
- `Word2Vec` Skip-Gram + Orthogonal Procrustes
- contextual `BERT`
- optional symbolic support using selected `NILC-Metrix` or related lexical indicators

## What Is Already Done

### 1. N2 experiment package

The N2 codebase already has a structured experiment package under:

- `Articles/N2/run/conf`
- `Articles/N2/run/pipeline`
- `Articles/N2/src/stil_semantic_change`

Existing stages include:

- `prepare_corpus`
- `train_word2vec`
- `align_embeddings`
- `score_candidates`
- `report_candidates`
- `tfidf_drift`
- `comparison_panel`
- `run_yearly_core`
- `bert_confirmatory`

### 2. Corpus organization

The main datasets are already organized and documented:

- `BrPoliCorpus floor` as the main corpus
- `Roda Viva V0-2` as a complementary corpus

Important constraint remains:

- do **not** merge `BrPoliCorpus` and `Roda Viva` into a single raw timeline without explicit genre control

### 3. Preliminary completed run

The main completed preliminary run is:

- `Articles/N2/run/outputs/experiments/brpolicorpus_floor_yearly/ae5022228b99/quicklook/yearly_2003_2023_r1`

This run already produced:

- yearly coverage summaries
- candidate rankings
- drift trajectories
- nearest-neighbor comparisons
- qualitative contexts
- STIL-readiness notes

Important outputs:

- `reports/analysis_summary.md`
- `reports/stil_readiness.md`
- `reports/qualitative_contexts.md`
- `reports/candidate_summary.parquet`

### 4. Advisor memo

A preliminary advisor-facing memo exists at:

- `Articles/N2/2026S1_STIL_conceptDrift/advisor_prelim_report_2026_03_17.tex`
- `Articles/N2/2026S1_STIL_conceptDrift/advisor_prelim_report_2026_03_17.pdf`

This remains useful as a meeting artifact, but it should not be treated as the final paper direction.

### 5. BERT support in code

The codebase already includes a confirmatory contextual path:

- `Articles/N2/src/stil_semantic_change/contextual/confirmatory.py`
- `Articles/N2/src/stil_semantic_change/runner.py`

However, BERT has not yet been used to produce the final comparative outputs needed for the new paper framing.

### 6. Runtime and configuration cleanup

The experiment package has now been tightened in a few important ways:

- prepared artifacts are explicitly multi-view rather than centered on one universal cleaned-text field
- `model.text_view` now validates at config load time
- `preprocess.preserve_accents` now affects normalization behavior instead of remaining unused
- contextual `BERT` dependencies are lazy-loaded so the core non-BERT pipeline starts lighter
- candidate-panel selection now uses dominant POS gating and centralized lexical exclusions
- residual malformed lemma cases such as `vejar`, `teríar`, `enter`, `mantir`, and `ademal` are explicitly patched for future reruns

Reference notes:

- `docs/prepared_artifact_layout_2026_03_21.md`
- `docs/runtime_config_cleanup_2026_03_21.md`
- `docs/word2vec_baseline_freeze_2026_03_21.md`
- `docs/candidate_panel_filter_2026_03_21.md`

## What The Current Results Still Tell Us

Even under the new framing, the completed quicklook remains useful.

It already shows that:

- yearly `BrPoliCorpus floor` slices are dense enough to support diachronic analysis
- politically meaningful candidates such as `golpe`, `corrupção`, `previdência`, and `cpi` emerge from the current pipeline
- a Portuguese political-discourse comparison paper is feasible with the current corpus setup

## Main Limitation Of The Existing Results

The current best run is still an exploratory quicklook, not a final paper run.

Main issue:

- it used the fast lookup-only preprocessing path, so the unrestricted top ranks include noisy lemmas and discourse artifacts

Under the old paper framing, this weakened the semantic-change claim.

Under the new framing, it is still acceptable as a preliminary `Word2Vec` result, but it is not enough because:

- `TF-IDF` comparison is still missing
- cross-method correlation analysis is still missing
- runtime/cost comparison is still missing
- symbolic interpretation is still missing

## Incomplete Or Partial Runs

Two later yearly experiment directories exist but should still be treated as incomplete:

- `Articles/N2/run/outputs/experiments/brpolicorpus_floor_yearly/4f821f885e1d`
- `Articles/N2/run/outputs/experiments/brpolicorpus_floor_yearly/c5437a2643c5`

Observed status:

- `4f821f885e1d` progressed substantially in `prepare_corpus` and its log reaches batch 355, but it has no completed stage manifest
- `c5437a2643c5` appears to have stopped near the beginning of the run

## What Still Needs To Be Done

### 1. Reframe the experiment outputs around comparison

The current article should compare methods rather than defend a single drift detector.

Needed:

- shared comparison vocabulary
- common scoring table across methods
- agreement and disagreement analysis

### 2. Shared comparison panel

This step is now implemented.

Current outputs on frozen run `ba65fe5b9cce`:

- merged `Word2Vec` + `TF-IDF` + seeds + stable-controls panel
- reusable comparison-ready term table
- one common downstream input for contextual scoring

Current summary:

- `55` rows
- `15` `Word2Vec` drift terms
- `15` `TF-IDF` drift terms
- `20` stable controls
- `5` theory seeds
- `0` shared drift terms
- `30` disagreement cases

### 3. Freeze the clean yearly `Word2Vec` baseline and improve the panel filter

The cleaned yearly `Word2Vec` baseline now exists, and the candidate-panel filter has been strengthened and validated on the frozen baseline before the next long rerun.

### 4. Define cross-method evaluation metrics

Needed:

- Spearman or Kendall rank correlation
- top-k overlap
- stable-controls agreement
- disagreement cases
- runtime/cost comparison

### 5. Add symbolic analysis

This should be treated as a support layer, not necessarily as the main detector.

Most useful likely role:

- distinguish semantic/contextual change from rhetoric, topicality, or style
- use selected `NILC-Metrix` features or simple rule-based lexical measures

### 6. Run BERT in the new comparative setup

BERT should now be used as:

- the expensive contextual comparison method
- not the only “confirmatory truth” layer

### 7. Rebuild the paper figures

Need final paper-facing visuals for:

- method correlation
- top-k overlap
- representative agreement cases
- representative disagreement cases
- cost vs signal tradeoff

## Recommended Next Order

1. run `BERT` on the filtered shared comparison panel
2. run cross-method correlation and overlap analysis on top of that panel
3. add symbolic support features if feasible
4. build final paper-facing comparative figures
5. draft the exploratory comparative paper

## Practical Summary

What exists now:

- organized corpora
- working N2 experiment code
- one completed exploratory `Word2Vec` quicklook
- one frozen clean yearly `Word2Vec` baseline at `ba65fe5b9cce`
- one clean first-class `TF-IDF` baseline attached to that frozen run
- one clean first shared comparison panel attached to that frozen run
- partial later reruns
- a preliminary advisor memo
- a cleaner multi-view prepared-artifact contract with stricter runtime validation

What is still missing for the actual paper:

- contextual comparison results on the shared panel
- symbolic support analysis
- final paper figures
- the new comparative draft itself
