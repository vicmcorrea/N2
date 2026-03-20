# N2 Progress Status

Date: 2026-03-20

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

### 2. Implement the `TF-IDF` drift baseline

This is the most important missing method family.

Needed outputs:

- per-term `TF-IDF` drift score
- top-k drift ranking
- comparison with `Word2Vec` and later `BERT`

### 3. Finish the clean yearly `Word2Vec` run

We still need a cleaner main yearly run on `BrPoliCorpus floor` to avoid carrying obvious preprocessing noise into the comparative analysis.

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

1. implement the `TF-IDF` baseline
2. define the shared candidate panel
3. complete a cleaner yearly `Word2Vec` run
4. run cross-method correlation analysis
5. add symbolic support features if feasible
6. run `BERT` on the filtered comparison panel
7. draft the exploratory comparative paper

## Practical Summary

What exists now:

- organized corpora
- working N2 experiment code
- one completed exploratory `Word2Vec` quicklook
- partial later reruns
- a preliminary advisor memo

What is still missing for the actual paper:

- `TF-IDF` comparison
- clean cross-method comparison tables
- symbolic support analysis
- final paper figures
- the new comparative draft itself
