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
- `docs/next_chat_prompt.md`
- `docs/project_overview.md`
- `docs/stil_plan_recommendation.md`
- `docs/research_readiness_datasets.md`

## Experiment Quickstart

Install dependencies with `uv`:

```bash
uv sync --group dev
```

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
