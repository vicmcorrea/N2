# Chat Handoff

This note is for any future chat using `Articles/N2` as the main workspace.

## Read First

Please read these files before deciding on the next step:

1. `README.md`
2. `docs/project_overview.md`
3. `docs/comparative_pipeline_readiness_2026_03_21.md`
4. `docs/exploratory_drift_comparison_plan.md`
5. `docs/progress_status_2026_03_20.md`
6. `docs/research_readiness_datasets.md`
7. `docs/semantic_change_literature_guide.md`
8. `docs/word_selection_protocol.md`
9. `docs/embedding_strategy_nilc_word2vec.md`
10. `docs/prepared_artifact_layout_2026_03_21.md`
11. `docs/runtime_config_cleanup_2026_03_21.md`
12. `docs/word2vec_baseline_freeze_2026_03_21.md`
13. `docs/candidate_panel_filter_2026_03_21.md`
14. `docs/tfidf_drift_baseline_2026_03_22.md`
15. `docs/comparison_panel_2026_03_22.md`
16. `docs/cross_method_agreement_2026_03_23.md`

## Current Paper Direction

The project is no longer framed as a paper that must prove semantic-change detection with external gold labels.

The current advisor-aligned direction is:

- an exploratory comparison of drift techniques in Portuguese political discourse
- centered on `BrPoliCorpus floor`
- with `Roda Viva` as a complementary corpus

Current method families:

- `TF-IDF` baseline drift
- `Word2Vec` Skip-Gram + Orthogonal Procrustes
- contextual `BERT`
- optional symbolic analysis using selected `NILC-Metrix` or related lexical indicators

## Important Constraints

- do **not** merge `BrPoliCorpus` and `Roda Viva` into one raw timeline without genre control
- keep `BrPoliCorpus floor` as the main experiment
- treat current quicklook results as exploratory, not final evidence
- keep the prepared multi-view artifact contract intact unless there is a deliberate migration plan
- assume `content_lemma` is the default `Word2Vec` representation unless a config explicitly changes `model.text_view`
- when doing citation work, use `valyu` first and `exa` second
- use `ml-paper-writing` when drafting paper-facing planning or writing

## Current Implementation Guardrails

- `model.text_view` is validated at config load time
- `preprocess.preserve_accents` is active and affects normalization
- contextual `BERT` dependencies are lazy-loaded and should not be pulled into non-BERT runs without a good reason
- the cleaned `Word2Vec` baseline is frozen at `ba65fe5b9cce`
- a first-class `tfidf_drift` stage now exists and writes method-local outputs under `scores/tfidf_drift/`
- a first-class `comparison_panel` stage now exists and writes shared outputs under `scores/comparison_panel/`
- contextual `BERT` now prefers the shared `comparison_panel` as its term source
  - fallback to legacy `candidate_sets.json` remains only for backward compatibility
- a first-class `cross_method_agreement` analysis stage now exists and writes:
  - rank correlations
  - top-k overlaps
  - a filtered contextual drift panel
  - a stable-control leakage diagnostic table
- candidate-panel filtering now sits on top of the raw score table rather than mutating the raw ranking
- candidate-panel filtering is now stricter than the earlier lexical-only pass:
  - dominant POS gating for drift/stable panels
  - centralized lexical defaults in `src/stil_semantic_change/selection/lexicons.py`
  - validated preview drift panel documented in `docs/candidate_panel_filter_2026_03_21.md`
- TF-IDF candidate-panel filtering now also applies:
  - a tiny method-local lexical exclusion list for obvious procedural offenders
  - a high-frequency ceiling at the `0.995` quantile for drift-panel selection
- preprocessing now also patches residual malformed lemmas such as `vejar`, `teríar`, `enter`, `mantir`, and `ademal`-type cases

## Most Important Current Outputs

Current clean Word2Vec baseline:

- `run/outputs/experiments/brpolicorpus_floor_yearly/ba65fe5b9cce`
- candidate-panel preview validated on top of that frozen run:
  - see `docs/candidate_panel_filter_2026_03_21.md`
- clean TF-IDF baseline on top of the same frozen run:
  - `run/outputs/experiments/brpolicorpus_floor_yearly/ba65fe5b9cce/scores/tfidf_drift`
  - see `docs/tfidf_drift_baseline_2026_03_22.md`
- shared comparison panel on top of the same frozen run:
  - `run/outputs/experiments/brpolicorpus_floor_yearly/ba65fe5b9cce/scores/comparison_panel`
  - see `docs/comparison_panel_2026_03_22.md`
- cross-method agreement layer on top of the same frozen run:
  - `run/outputs/experiments/brpolicorpus_floor_yearly/ba65fe5b9cce/scores/cross_method_agreement`
  - see `docs/cross_method_agreement_2026_03_23.md`

Important integrity note:

- `run/outputs/experiments/brpolicorpus_floor_yearly/8e15dc2372c5` finished as a clean overnight `Word2Vec` rerun, but its prepared root was later touched by an aborted forced `tfidf_drift` rerun
- do not use `8e15dc2372c5/prepared` as the frozen source of truth for future method runs
- keep `ba65fe5b9cce` as the frozen clean baseline source

Earlier exploratory quicklook:

- `run/outputs/experiments/brpolicorpus_floor_yearly/ae5022228b99/quicklook/yearly_2003_2023_r1`

Advisor memo:

- `2026S1_STIL_conceptDrift/advisor_prelim_report_2026_03_17.tex`
- `2026S1_STIL_conceptDrift/advisor_prelim_report_2026_03_17.pdf`

Progress summary:

- `docs/progress_status_2026_03_20.md`

## Likely Next Tasks

The next useful work usually falls into one of these:

1. produce qualitative agreement/disagreement packets from the frozen comparison artifacts
2. add runtime/cost summary tables across `TF-IDF`, `Word2Vec`, and `BERT`
3. decide whether the contextual paper-facing list should use only stable-control filtering or one additional lexical cleanup layer
4. add the `PTPARL-V` validation-table build as a separate pipeline path
