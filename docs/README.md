# Docs Guide

This folder was consolidated on 2026-03-24 so that the live documentation set
matches the current frozen experiment and the current STIL draft.

## Read first

These are the main active docs for future work:

1. `chat_handoff.md`
2. `project_overview.md`
3. `advisor_feedback_2026_03_20.md`
4. `paper_writing_status_2026_03_23.md`
5. `cross_method_agreement_2026_03_23.md`
6. `comparison_panel_2026_03_22.md`
7. `tfidf_drift_baseline_2026_03_22.md`
8. `word2vec_baseline_freeze_2026_03_21.md`
9. `ptparl_v_vote_label_note.md`
10. `paper-submission-guidelines-STIL.md`

## What each live doc is for

- `chat_handoff.md`
  - quickest orientation for a new chat
  - current paper framing, frozen run, active figures, and likely next work
- `project_overview.md`
  - stable project-level summary
  - corpora, method families, frozen source of truth, and current interpretation
- `paper_writing_status_2026_03_23.md`
  - current manuscript status
  - paper structure, figure/table package, compile state, and writing priorities
- `word2vec_baseline_freeze_2026_03_21.md`
  - frozen static-embedding baseline details
- `tfidf_drift_baseline_2026_03_22.md`
  - frozen lexical baseline details
- `comparison_panel_2026_03_22.md`
  - shared 55-lemma panel construction and composition
- `cross_method_agreement_2026_03_23.md`
  - frozen cross-method correlations, overlap, filtered contextual layer, and diagnostics
- `ptparl_v_vote_label_note.md`
  - current rules and caveats for using `PTPARL-V` as a later validation-oriented source
- `prepared_artifact_layout_2026_03_21.md`
  - frozen prepared-artifact contract and multi-view layout
- `runtime_config_cleanup_2026_03_21.md`
  - implementation-level cleanup notes that still affect reproducibility
- `semantic_change_literature_guide.md`
  - literature helper for writing
- `word_selection_protocol.md`
  - term-selection rationale and panel terminology

## Current source of truth

Use this frozen experiment root unless there is an explicit reason not to:

- `run/outputs/experiments/brpolicorpus_floor_yearly/ba65fe5b9cce`

Do not use:

- `run/outputs/experiments/brpolicorpus_floor_yearly/8e15dc2372c5`

Its prepared root was touched after completion by an aborted forced rerun.

## Current manuscript assets

- manuscript: `2026S1_STIL_conceptDrift/main.tex`
- compiled PDF: `2026S1_STIL_conceptDrift/main.pdf`
- figure package: `2026S1_STIL_conceptDrift/figs/paper/`
- figure inventory: `2026S1_STIL_conceptDrift/figs/paper/figure_inventory.md`

Current paper-facing figures in the manuscript:

- `figure_05_study_design`
- `figure_02_method_agreement`
- `figure_03_overlap_and_rank_statistics`
- `figure_04_representative_trajectories`

Archived but still reproducible:

- `figure_01_corpus_profile`

## Archive policy

Files in `docs/archive/` are kept for project memory, but they should not be read
before active work unless there is a specific historical question.
