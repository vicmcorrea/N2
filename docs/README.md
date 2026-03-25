# Docs Guide

Last reorganized: 2026-03-24

## Folder Structure

```
docs/
  README.md                  ← you are here
  personal-notes-dontTouc.txt
  project/                   ← core project docs
  paper/                     ← manuscript, submission, literature
  experiments/               ← frozen experiment logs and results
  results/                   ← numerical snapshots of all pipeline outputs
  pipeline/                  ← infrastructure and config notes
  research/                  ← background literature and datasets
  archive/                   ← older planning and transition notes
```

## Read First

Start with these in order:

1. `project/chat_handoff.md` — quickest orientation for a new session
2. `project/project_overview.md` — stable project-level summary
3. `project/advisor_feedback_2026_03_20.md` — advisor framing that shaped the paper

## project/

| File | Purpose |
|------|---------|
| `chat_handoff.md` | Quick orientation: framing, frozen run, figures, next work |
| `project_overview.md` | Corpora, method families, frozen source of truth, interpretation |
| `advisor_feedback_2026_03_20.md` | Advisor recommendation to shift to exploratory comparison |

## paper/

| File | Purpose |
|------|---------|
| `paper_writing_status_2026_03_23.md` | Manuscript status, figures, tables, compile state |
| `paper-submission-guidelines-STIL.md` | STIL 2026 submission rules (double-blind, page limits) |
| `literature_comparison_2026_03_24.md` | Systematic comparison of our methodology vs. the field |

## experiments/

| File | Purpose |
|------|---------|
| `word2vec_baseline_freeze_2026_03_21.md` | Frozen Word2Vec baseline: hyperparams, alignment, scores |
| `tfidf_drift_baseline_2026_03_22.md` | Frozen TF-IDF baseline: methodology and scores |
| `comparison_panel_2026_03_22.md` | Shared 55-lemma panel: construction and composition |
| `candidate_panel_filter_2026_03_21.md` | Panel filtering rules and eligibility thresholds |
| `cross_method_agreement_2026_03_23.md` | Cross-method correlations, overlap, filtered BERT panel |

## results/

| File | Purpose |
|------|---------|
| `frozen_results_snapshot_2026_03_24.md` | Complete numerical snapshot of all pipeline outputs from run `ba65fe5b9cce` — corpus totals, candidate lists, correlations, overlaps, file inventory, disk sizes. Timestamped for comparison with future runs. |
| `apd_reanalysis_findings_2026_03_25.md` | APD vs PRT comparison: ρ = 0.79, PRT separates buckets better, robustness validated |

## pipeline/

| File | Purpose |
|------|---------|
| `prepared_artifact_layout_2026_03_21.md` | Frozen prepared-artifact contract and multi-view layout |
| `runtime_config_cleanup_2026_03_21.md` | Implementation cleanup notes affecting reproducibility |
| `gap_analysis_2026_03_24.md` | Literature gap feasibility analysis: APD, layers, clustering, bias — ranked by effort-to-value |
| `post_hoc_apd_reanalysis_2026_03_25.md` | APD reanalysis pipeline: architecture, usage, frozen-run guarantee |

## research/

| File | Purpose |
|------|---------|
| `semantic_change_literature_guide.md` | Literature helper for writing and references |
| `embedding_strategy_nilc_word2vec.md` | Embedding strategy notes (NILC Word2Vec evaluation) |
| `research_readiness_datasets.md` | Dataset readiness assessment (BrPoliCorpus, Roda Viva, etc.) |
| `word_selection_protocol.md` | Term-selection rationale and panel terminology |
| `ptparl_v_vote_label_note.md` | PTPARL-V caveats for potential future validation |

## Current Source of Truth

Frozen experiment root:

- `run/outputs/experiments/brpolicorpus_floor_yearly/ba65fe5b9cce`

Do NOT use `8e15dc2372c5` — its prepared root was corrupted by an aborted rerun.

## Current Manuscript Assets

- Manuscript: `2026S1_STIL_conceptDrift/main.tex`
- Compiled PDF: `2026S1_STIL_conceptDrift/main.pdf`
- Figures: `2026S1_STIL_conceptDrift/figs/paper/`

Paper figures in the manuscript:
- `figure_05_study_design`
- `figure_02_method_agreement`
- `figure_03_overlap_and_rank_statistics`
- `figure_04_representative_trajectories`

Archived (not in manuscript): `figure_01_corpus_profile`

## Archive Policy

Files in `archive/` are kept for project memory. Do not read them before active
docs unless answering a specific historical question.
