# Project Overview

## Purpose

`Articles/N2` is the workspace for the current STIL paper on comparative drift
analysis in Portuguese political discourse. It is separate from the earlier
financial-disclosures paper in `Articles/N1` and should be treated as its own
research line.

## Current advisor-aligned framing

The paper should be written as an exploratory comparative study, not as a claim
that one detector has solved semantic-change detection with external ground truth.

The current contribution is:

- compare `TF-IDF`, `Word2Vec`, and contextual `BERT` on the same political corpus
- show where they agree and where they diverge
- interpret what each method seems to capture
- assess whether the higher-cost contextual layer adds enough value over cheaper methods

This framing is especially useful in Portuguese, where comparable large-scale
political drift studies are still much scarcer than in English-centered work.

## Corpus strategy

Main discovery corpus:

- `BrPoliCorpus floor`

Complementary corpus:

- `Roda Viva`

Validation-oriented later corpus:

- `PTPARL-V`

Constraints that still hold:

- do not merge `BrPoliCorpus` and `Roda Viva` into one uncontrolled timeline
- keep `BrPoliCorpus floor` as the main discovery corpus
- treat `PTPARL-V` as a separate noisy supervision source that requires explicit
  deduplication and aggregation rules

## Current frozen source of truth

The current experiment root for the paper is:

- `run/outputs/experiments/brpolicorpus_floor_yearly/ba65fe5b9cce`

This frozen run anchors:

- the cleaned `Word2Vec` baseline
- the cleaned `TF-IDF` baseline
- the shared `comparison_panel`
- contextual `BERT`
- the `cross_method_agreement` layer
- the paper figure package used by the manuscript

Do not use `8e15dc2372c5` as the immutable prepared-artifact source because its
prepared root was touched after completion by an aborted forced rerun.

## Current comparative findings

Corpus summary:

- `24` yearly slices
- `428,366` speeches
- `63,036,642` retained tokens
- `538,537,771` `content_lemma` characters

Shared comparison panel:

- `55` lemmas
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

## Current interpretation

The main comparative story is now stable:

- `TF-IDF` behaves as the cheap lexical-profile baseline
- `Word2Vec` behaves as the aligned static-embedding baseline
- contextual `BERT` is useful as a higher-cost adjudication layer rather than as
  a replacement for the cheaper methods

The important result is not that one method wins. The important result is that
disagreement itself is informative. The three method families appear sensitive to
different mixtures of lexical salience, neighborhood displacement, and usage-level
variation.

## Current manuscript state

Main manuscript:

- `2026S1_STIL_conceptDrift/main.tex`

Compiled paper:

- `2026S1_STIL_conceptDrift/main.pdf`

Paper-facing figures currently in the manuscript:

- `figure_05_study_design`
- `figure_02_method_agreement`
- `figure_03_overlap_and_rank_statistics`
- `figure_04_representative_trajectories`

The corpus-profile figure `figure_01_corpus_profile` remains in the exported figure
package but is not currently used in the paper.

## Active docs

The main live docs are:

- `README.md`
- `docs/README.md`
- `docs/chat_handoff.md`
- `docs/advisor_feedback_2026_03_20.md`
- `docs/paper_writing_status_2026_03_23.md`
- `docs/word2vec_baseline_freeze_2026_03_21.md`
- `docs/tfidf_drift_baseline_2026_03_22.md`
- `docs/comparison_panel_2026_03_22.md`
- `docs/cross_method_agreement_2026_03_23.md`
- `docs/ptparl_v_vote_label_note.md`
- `docs/paper-submission-guidelines-STIL.md`

Older planning and transition notes were moved to `docs/archive/`.
