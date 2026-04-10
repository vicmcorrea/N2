# N2 Progress Status

Date: 2026-03-20

## Update: 2026-03-23

Since the 2026-03-22 update:

- the contextual run was analyzed and folded into a paper-facing `cross_method_agreement` layer
- a filtered contextual panel and stable-control leakage diagnostics were frozen on top of `ba65fe5b9cce`
- a publication-oriented figure package was generated directly from the frozen baseline under:
  - `Articles/N2/2026S1_STIL_conceptDrift/figs/paper`
- the active manuscript draft in:
  - `Articles/N2/2026S1_STIL_conceptDrift/main.tex`
  was updated to include:
  - a concrete paper title
  - an abstract
  - working prose for introduction, methods, results, and conclusion
  - figure environments wired to the new paper figures

Current figure package:

- `figure_01_corpus_profile`
- `figure_02_method_agreement`
- `figure_03_overlap_and_rank_statistics`
- `figure_04_representative_trajectories`

Each figure now exists as:

- `PDF`
- `EPS`
- `PNG`
- `TIFF`

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
- contextual `BERT` was refactored to use that shared panel by default instead of the older Word2Vec-only candidate set
- contextual `BERT` was then run successfully on that shared panel
- a post-run `cross_method_agreement` layer was generated on the same frozen baseline under:
  - `Articles/N2/run/outputs/experiments/brpolicorpus_floor_yearly/ba65fe5b9cce/scores/cross_method_agreement`

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
- `bert_confirmatory`
- `cross_method_agreement`
- `run_yearly_core`

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

### 5. BERT support in code and outputs

The codebase already includes a confirmatory contextual path:

- `Articles/N2/src/stil_semantic_change/contextual/confirmatory.py`
- `Articles/N2/src/stil_semantic_change/runner.py`

That contextual path has now been run successfully on the frozen baseline and attached to
the shared comparison panel.

Current contextual artifacts on frozen run `ba65fe5b9cce`:

- `scores/bert_confirmatory`
- `scores/cross_method_agreement`

Current high-level result:

- BERT is moderately closer to `Word2Vec` than to `TF-IDF`
- raw contextual top ranks still leak stable controls
- a filtered contextual panel now exists for paper-facing comparison

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

### 7. Paper-facing comparative results snapshot

Current shared-panel summary on frozen run `ba65fe5b9cce`:

- `55` lemmas total
- `15` `Word2Vec` drift terms
- `15` `TF-IDF` drift terms
- `20` stable controls
- `5` theory seeds

Current cross-method result snapshot:

- `Word2Vec` vs `TF-IDF` Spearman: `-0.540`
- `BERT(-1)` vs `Word2Vec` Spearman: `0.208`
- `BERT(-1)` vs `TF-IDF` Spearman: `0.125`
- `BERT` layer agreement Spearman: `0.858`
- top-15 overlap:
  - `BERT` / `Word2Vec`: `7`
  - `BERT` / `TF-IDF`: `6`
  - `Word2Vec` / `TF-IDF`: `0`

Current filtered contextual top terms:

- `bloqueio`, `típico`, `exposição`, `salário`, `mínimo`
- `troca`, `preço`, `voto`, `real`, `intervenção`
- `excepcional`, `renovação`, `eleição`, `crítico`, `político`

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

- the cheap lexical and contextual baselines now exist
- cross-method correlation analysis now exists
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

This reframing is already implemented in both code and manuscript direction.

Current state:

- the frozen baseline is comparative rather than single-method
- the article draft already treats agreement and disagreement as the core result
- the remaining work is paper assembly, not conceptual reframing

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

This step is now implemented at a first useful level.

Current outputs on frozen run `ba65fe5b9cce`:

- `scores/cross_method_agreement/correlations.parquet`
- `scores/cross_method_agreement/topk_overlap.parquet`
- `scores/cross_method_agreement/bert_filtered_panel.parquet`
- `scores/cross_method_agreement/bert_stable_control_leakage.parquet`
- `scores/cross_method_agreement/summary.json`

Still useful to add next:

- runtime/cost comparison
- qualitative agreement packets with neighbors and contexts
- a final decision on whether the paper-facing BERT list needs only stable-control filtering or one extra lexical cleanup pass

### 5. Add symbolic analysis

This should be treated as a support layer, not necessarily as the main detector.

Most useful likely role:

- distinguish semantic/contextual change from rhetoric, topicality, or style
- use selected `NILC-Metrix` features or simple rule-based lexical measures

### 6. Contextual BERT in the new comparative setup

BERT is now being used as:

- the expensive contextual comparison method
- not the only “confirmatory truth” layer
- with the shared `comparison_panel` as its default candidate universe
- with a post-run `cross_method_agreement` layer that filters stable-control leakage from the paper-facing contextual top list

### 7. Rebuild the paper figures

Need final paper-facing visuals for:

- method correlation
- top-k overlap
- representative agreement cases
- representative disagreement cases
- cost vs signal tradeoff

This step is now implemented for the current frozen comparative package. The figures
exist under:

- `Articles/N2/2026S1_STIL_conceptDrift/figs/paper`

and are already integrated into:

- `Articles/N2/2026S1_STIL_conceptDrift/main.tex`

## Recommended Next Order

1. continue writing and tightening `2026S1_STIL_conceptDrift/main.tex`
2. produce qualitative agreement/disagreement packets from the frozen comparison artifacts
3. add a runtime/cost comparison table across `TF-IDF`, `Word2Vec`, and `BERT`
4. add symbolic support features if feasible
5. decide how to position `PTPARL-V` in limitations or future work

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

- symbolic support analysis
- runtime/cost reporting
- qualitative agreement/disagreement packets
- citation-grounded related work and final prose polish
