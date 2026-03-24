# Chat Handoff

This note is the fastest way to resume work in `Articles/N2`.

## Read first

Use this order unless the task is very narrow:

1. `README.md`
2. `docs/README.md`
3. `docs/project_overview.md`
4. `docs/advisor_feedback_2026_03_20.md`
5. `docs/paper_writing_status_2026_03_23.md`
6. `docs/cross_method_agreement_2026_03_23.md`
7. `docs/comparison_panel_2026_03_22.md`
8. `docs/tfidf_drift_baseline_2026_03_22.md`
9. `docs/word2vec_baseline_freeze_2026_03_21.md`
10. `docs/ptparl_v_vote_label_note.md`
11. `2026S1_STIL_conceptDrift/main.tex`
12. `2026S1_STIL_conceptDrift/figs/paper/figure_inventory.md`

Do not start with files under `docs/archive/` unless you are chasing project history.

## Current paper direction

The paper is now defended as:

- an exploratory comparative study
- on Portuguese political discourse
- using `BrPoliCorpus floor` as the main corpus
- comparing `TF-IDF`, `Word2Vec`, and contextual `BERT`
- with attention to agreement, divergence, interpretability, and cost

Do not write the paper as if we have external semantic ground truth for semantic
change detection. `PTPARL-V` remains a separate noisy supervision source for later
validation-oriented work, not the main discovery corpus.

## Current frozen source of truth

Use:

- `run/outputs/experiments/brpolicorpus_floor_yearly/ba65fe5b9cce`

Do not use:

- `run/outputs/experiments/brpolicorpus_floor_yearly/8e15dc2372c5`

Its prepared root was touched after completion by an aborted forced rerun.

## Current paper-facing results

Corpus summary:

- `24` yearly slices from `2000` to `2023`
- `428,366` speeches
- `63,036,642` retained tokens
- `538,537,771` characters in `content_lemma`

Shared comparison panel:

- `55` lemmas total
- `15` `Word2Vec` drift terms
- `15` `TF-IDF` drift terms
- `20` stable controls
- `5` theory seeds

Cross-method summary:

- `Word2Vec` vs `TF-IDF` Spearman: `-0.540`
- `BERT(-1)` vs `Word2Vec` Spearman: `0.208`
- `BERT(-1)` vs `TF-IDF` Spearman: `0.125`
- `BERT` layer agreement Spearman: `0.858`
- top-15 overlap:
  - `BERT` / `Word2Vec`: `7`
  - `BERT` / `TF-IDF`: `6`
  - `Word2Vec` / `TF-IDF`: `0`

Filtered contextual top terms:

- `bloqueio`, `típico`, `exposição`, `salário`, `mínimo`
- `troca`, `preço`, `voto`, `real`, `intervenção`
- `excepcional`, `renovação`, `eleição`, `crítico`, `político`

## Current manuscript state

Main files:

- `2026S1_STIL_conceptDrift/main.tex`
- `2026S1_STIL_conceptDrift/main.pdf`

Current paper-facing figure package:

- `figure_05_study_design`
- `figure_02_method_agreement`
- `figure_03_overlap_and_rank_statistics`
- `figure_04_representative_trajectories`

Archived but still reproducible:

- `figure_01_corpus_profile`

Current paper-facing tables in the draft:

- dataset summary table built directly in LaTeX
- method scope/runtime table built directly in LaTeX

The manuscript was compiled successfully on `2026-03-24` and currently fits in
`9` total PDF pages.

## What is live vs historical

Treat these as live docs:

- `project_overview.md`
- `paper_writing_status_2026_03_23.md`
- `word2vec_baseline_freeze_2026_03_21.md`
- `tfidf_drift_baseline_2026_03_22.md`
- `comparison_panel_2026_03_22.md`
- `cross_method_agreement_2026_03_23.md`
- `ptparl_v_vote_label_note.md`
- `paper-submission-guidelines-STIL.md`

Treat `docs/archive/` as historical context only.

## Likely next work

The implementation is largely done. The most likely next steps are:

1. final paper polishing in `main.tex`
2. small visualization or table refinements if the draft still looks crowded
3. a separate `PTPARL-V` validation table path with explicit aggregation rules
4. optional symbolic-support analysis described as interpretive future work, not
   as ground truth
