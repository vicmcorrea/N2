# N2 Overview

This folder is the self-contained workspace for the new STIL paper direction.

It now also contains a config-driven experiment package for yearly semantic-change
analysis over Portuguese corpora, centered on `BrPoliCorpus floor`.

## Main folders

- `2026S1_STIL_conceptDrift/`
  - cleaned LaTeX STIL template
  - `main.tex` and compiled `main.pdf`
- `RawDatasets/`
  - organized local copies of the datasets for the paper
  - `BrPoliCorpus-Dataset/`
  - `Roda-Viva-Dataset/`
- `docs/`
  - project notes, dataset readiness, literature notes, and handoff material

## Start here

- `docs/chat_handoff.md`
- `docs/project_overview.md`
- `docs/stil_plan_recommendation.md`
- `docs/research_readiness_datasets.md`
- `docs/prepared_artifact_layout_2026_03_21.md`
- `docs/runtime_config_cleanup_2026_03_21.md`
- `docs/word2vec_baseline_freeze_2026_03_21.md`
- `docs/candidate_panel_filter_2026_03_21.md`
- `docs/tfidf_drift_baseline_2026_03_22.md`
- `docs/comparison_panel_2026_03_22.md`

## Experiment Quickstart

Install dependencies with `uv`:

```bash
uv sync --group dev
```

The prepared-corpus layout and recent runtime/config cleanup are documented here:

- `docs/prepared_artifact_layout_2026_03_21.md`
- `docs/runtime_config_cleanup_2026_03_21.md`
- `docs/word2vec_baseline_freeze_2026_03_21.md`
- `docs/candidate_panel_filter_2026_03_21.md`
- `docs/tfidf_drift_baseline_2026_03_22.md`
- `docs/comparison_panel_2026_03_22.md`

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

## Most important current decision

The current plan is:

- main corpus: `RawDatasets/BrPoliCorpus-Dataset/exports/floor`
- complementary corpus: `RawDatasets/Roda-Viva-Dataset/exports/V0-2/csv`
- main method: Word2Vec Skip-Gram 300d by time slice + Orthogonal Procrustes
- confirmatory method: `rufimelo/bert-large-portuguese-cased-sts`

## Dataset references

- `RawDatasets/BrPoliCorpus-Dataset/inventory/`
- `RawDatasets/Roda-Viva-Dataset/inventory/`

## Writing references

- `2026S1_STIL_conceptDrift/main.tex`
- `docs/semantic_change_literature_guide.md`
- `docs/word_selection_protocol.md`
