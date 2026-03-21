# Prepared Artifact Layout

Date: 2026-03-21

This note defines the organized structure for prepared corpus artifacts under:

`run/outputs/experiments/<dataset>/<hash>/prepared/`

## Goal

We no longer treat one `clean_text` field as the universal representation for every stage.
Instead, we store multiple named text views so different methods can consume the right version.

## Directory Layout

### Document artifacts

- `prepared/docs/metadata/`
  - document metadata shards
  - fields: `doc_id`, `date`, `slice_id`, `source_file`, `normalized_token_count`, `token_count`

- `prepared/docs/raw_text/`
  - raw text shards for context-sensitive methods
  - fields: `doc_id`, `slice_id`, `raw_text`

### Token artifacts

- `prepared/tokens/content/`
  - retained content-token shards after preprocessing filters
  - fields: `doc_id`, `slice_id`, `token_index`, `token`, `lemma`, `pos`

### Text views

- `prepared/text_views/by_doc/`
  - document-level processed text views
  - fields:
    - `normalized_surface_text`
    - `content_surface_text`
    - `content_lemma_text`

- `prepared/text_views/by_slice/normalized_surface/`
  - per-slice text files using normalized surface tokens

- `prepared/text_views/by_slice/content_surface/`
  - per-slice text files using retained surface tokens

- `prepared/text_views/by_slice/content_lemma/`
  - per-slice text files using retained lemmas
  - current default training input for Word2Vec

## Intended Consumers

- Word2Vec:
  - reads `prepared/text_views/by_slice/content_lemma/`
  - configured via `model.text_view`

- BERT confirmatory:
  - reads `prepared/docs/raw_text/` for context reconstruction
  - reads `prepared/tokens/content/` for occurrence targeting

- Qualitative context packet:
  - reads `prepared/tokens/content/`
  - reads `prepared/docs/metadata/`

- Future TF-IDF / lexical baselines:
  - can choose between `normalized_surface`, `content_surface`, or `content_lemma`
  - should declare the chosen representation explicitly in config or stage metadata

## Design Rule

When adding a new method, do not overload an existing text column with a new meaning.
Add a named view if the representation is methodologically distinct.
