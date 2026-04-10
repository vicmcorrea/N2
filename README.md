# N2 Overview

This folder is the self-contained workspace for the current STIL paper direction.

It contains both:

- a config-driven comparative experiment package for Portuguese political diachronic NLP
- the active manuscript draft and paper-figure package for the STIL submission

The project is now framed as an exploratory comparison of drift signals in Brazilian
Portuguese political discourse, not as a validation-heavy claim that one method has
solved semantic-change detection.

## Main folders

- `2026S1_STIL_conceptDrift/`
  - cleaned LaTeX STIL template
  - active manuscript draft in `main.tex`
  - paper figure package in `figs/paper/`
- `RawDatasets/`
  - organized local copies of the datasets for the paper
  - `BrPoliCorpus-Dataset/`
  - `Roda-Viva-Dataset/`
  - `PTPARL-V/`
- `docs/`
  - project notes, dataset readiness, literature notes, and handoff material
- `run/`
  - pipeline entrypoints, Hydra configs, and experiment outputs
- `src/stil_semantic_change/`
  - comparative drift pipeline implementation

## Start here

- `docs/README.md`
- `docs/chat_handoff.md`
- `docs/project_overview.md`
- `docs/advisor_feedback_2026_03_20.md`
- `docs/paper_writing_status_2026_03_23.md`
- `docs/cross_method_agreement_2026_03_23.md`
- `docs/comparison_panel_2026_03_22.md`
- `docs/tfidf_drift_baseline_2026_03_22.md`
- `docs/word2vec_baseline_freeze_2026_03_21.md`
- `docs/ptparl_v_vote_label_note.md`
- `docs/paper-submission-guidelines-STIL.md`
- `2026S1_STIL_conceptDrift/main.tex`
- `2026S1_STIL_conceptDrift/figs/paper/figure_inventory.md`

## Experiment Quickstart

Install dependencies with `uv`:

```bash
uv sync --group dev
```

The prepared-corpus layout, frozen baselines, and paper-facing comparison layers are documented here:

- `docs/prepared_artifact_layout_2026_03_21.md`
- `docs/runtime_config_cleanup_2026_03_21.md`
- `docs/word2vec_baseline_freeze_2026_03_21.md`
- `docs/candidate_panel_filter_2026_03_21.md`
- `docs/tfidf_drift_baseline_2026_03_22.md`
- `docs/comparison_panel_2026_03_22.md`
- `docs/cross_method_agreement_2026_03_23.md`
- `docs/paper_writing_status_2026_03_23.md`

Older planning and transition notes that were superseded by the frozen comparative
baseline or the current manuscript have been moved into `docs/archive/`.

Run the toy end-to-end smoke pipeline:

```bash
uv run python run/pipeline/main.py dataset=toy_brpolicorpus_yearly task=run_yearly_core \
  model.vector_size=40 model.window=3 model.negative=3 model.min_count=1 model.epochs=20 model.replicates=1 \
  alignment.min_anchor_words=2 \
  selection.min_occurrences_per_slice=2 selection.min_documents_per_slice=1 selection.min_slice_presence_ratio=0.66
```

Run the main yearly core:

```bash
uv run python run/pipeline/main.py task=run_yearly_core dataset=brpolicorpus_floor_yearly
```

Outputs are written under `run/outputs/`.

Full-tree backup of the frozen baseline run `ba65fe5b9cce` (Word2Vec, TF-IDF, panel, BERT, prepared corpus):

- `run/outputs/backups/ba65fe5b9cce_word2vec_bert_20260322.tar.gz`

## Frozen Comparative Baseline

The current source of truth is:

- `run/outputs/experiments/brpolicorpus_floor_yearly/ba65fe5b9cce`

That frozen run now anchors:

- the cleaned `Word2Vec` baseline
- the cleaned `TF-IDF` baseline
- the shared `comparison_panel`
- contextual `BERT`
- the `cross_method_agreement` layer
- the paper figure package in `2026S1_STIL_conceptDrift/figs/paper/`

Do not use `8e15dc2372c5` as the immutable prepared-artifact source because its
prepared root was touched by an aborted forced rerun after completion.

## Important Runtime Notes

- `model.text_view` is validated at config-load time
  - valid values: `normalized_surface`, `content_surface`, `content_lemma`
- the default `Word2Vec` training representation is `content_lemma`
- `preprocess.preserve_accents` is active
  - `true` keeps accented forms such as `corrupção`
  - `false` normalizes them to forms such as `corrupcao`
- contextual `BERT` dependencies are lazy-loaded and should only be paid for when the `bert_confirmatory` stage actually runs
- candidate-panel selection is stricter than the raw drift ranking
  - dominant POS gating for drift/stable panels
  - centralized lexical exclusions in `src/stil_semantic_change/selection/lexicons.py`
  - validated preview on frozen run `ba65fe5b9cce`
- the clean `TF-IDF` baseline is attached to frozen run `ba65fe5b9cce`
- the first shared `comparison_panel` also exists under frozen run `ba65fe5b9cce`
  - current panel size: `55`
  - current shared drift overlap: `0`
  - current disagreement cases: `30`
- contextual `BERT` now prefers the shared `comparison_panel` as its candidate universe
  - it falls back to legacy `candidate_sets.json` only if the shared panel is absent
- a cross-method agreement layer now exists on the same frozen run under `scores/cross_method_agreement`
  - it provides rank correlations, top-k overlap tables, a filtered BERT panel, and a stable-control leakage table
  - the current preferred contextual layer is `-1`

## Current Comparative Snapshot

Current shared-panel summary on frozen run `ba65fe5b9cce`:

- panel size: `55`
- `Word2Vec` drift terms: `15`
- `TF-IDF` drift terms: `15`
- stable controls: `20`
- theory seeds: `5`
- cheap-method top-15 overlap: `0`

Current cross-method summary:

- `Word2Vec` vs `TF-IDF` Spearman: `-0.540`
- `BERT(-1)` vs `Word2Vec` Spearman: `0.208`
- `BERT(-1)` vs `TF-IDF` Spearman: `0.125`
- `BERT` layer agreement Spearman: `0.858`

Current filtered contextual top terms:

- `bloqueio`, `típico`, `exposição`, `salário`, `mínimo`
- `troca`, `preço`, `voto`, `real`, `intervenção`
- `excepcional`, `renovação`, `eleição`, `crítico`, `político`

## Most important current decision

The current plan is:

- main corpus: `RawDatasets/BrPoliCorpus-Dataset/exports/floor`
- complementary corpus: `RawDatasets/Roda-Viva-Dataset/exports/V0-2/csv`
- main method: Word2Vec Skip-Gram 300d by time slice + Orthogonal Procrustes
- cheap baseline: `TF-IDF` drift on the same prepared view
- contextual method: `rufimelo/bert-large-portuguese-cased-sts`
- comparative readout: shared panel + cross-method agreement layer on frozen run `ba65fe5b9cce`

## Dataset references

- `RawDatasets/BrPoliCorpus-Dataset/inventory/`
- `RawDatasets/Roda-Viva-Dataset/inventory/`

## Writing references

- `2026S1_STIL_conceptDrift/main.tex`
- `2026S1_STIL_conceptDrift/figs/paper/figure_inventory.md`
- `docs/semantic_change_literature_guide.md`
- `docs/word_selection_protocol.md`
- `docs/paper_writing_status_2026_03_23.md`
