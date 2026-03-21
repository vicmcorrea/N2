# Project Overview

## Context

`Articles/N2` supports a new STIL paper direction that is separate from the already submitted financial-disclosures article in:

- `Articles/N1/2026S1_conceptDrift_financialDisclosures`

The main results of that earlier article should not be reused as the core contribution here.

## Current Advisor-Aligned Direction

The project is now framed as an **exploratory comparison of drift techniques in Portuguese political discourse**, not as a paper claiming fully validated semantic-change detection.

The main idea is:

- compare several drift-detection families on the same Portuguese political corpus
- measure how much they agree or disagree
- identify what kinds of change each method seems to capture
- evaluate whether heavier methods add enough value over cheaper ones

This is useful even without labeled ground truth because the contribution becomes comparative and methodological rather than benchmark-style evaluation.

## Current Working Paper Framing

Working framing:

- exploratory analysis of concept and lexical drift in Brazilian Portuguese political discourse
- emphasis on agreement, divergence, interpretability, and computational cost across methods

The paper should answer questions such as:

1. How strongly do different drift techniques correlate on `BrPoliCorpus floor`?
2. Which candidate terms are stable across methods, and which are method-specific?
3. Does contextual BERT add enough value over lighter methods such as TF-IDF or Word2Vec?
4. Can symbolic or rule-based linguistic features help distinguish semantic drift from style, rhetoric, or discourse-structure change?

## Main Corpus Strategy

### Main corpus

Use `BrPoliCorpus floor` as the main corpus.

Why:

- it is the largest and most continuous Portuguese political-discourse panel currently available in N2
- it has exact dates
- it supports yearly and semester slicing
- it stays within a coherent institutional political genre

### Complementary corpus

Use `Roda Viva V0-2` as a complementary corpus.

Why:

- it adds a different but still relevant Portuguese public-discourse genre
- it is useful for qualitative checks and limited cross-corpus comparisons
- it should remain separate from `BrPoliCorpus` unless genre is explicitly controlled

## Method Families To Compare

The new paper should compare at least three families:

1. `TF-IDF`-style contextual/profile drift
2. `Word2Vec` Skip-Gram by slice with Orthogonal Procrustes alignment
3. contextual `BERT` drift on sampled usages

Optional fourth family:

4. symbolic or lexical-feature analysis, potentially using selected `NILC-Metrix` measures

The role of the symbolic layer is different from the embedding methods:

- not necessarily to replace them as the main drift detector
- but to help interpret whether change is more semantic, topical, evaluative, rhetorical, or stylistic

## Current Practical Interpretation Of Methods

- `TF-IDF` is the cheap lexical-profile baseline
- `Word2Vec` is the main static-embedding drift method
- `BERT` is the expensive contextual method
- `NILC-Metrix` or symbolic features are interpretive/supporting signals

The paper does not need one method to “win.” Useful outcomes include:

- high agreement between methods
- low agreement that reveals different drift types
- evidence that cheap methods approximate expensive ones
- evidence that expensive methods detect only a narrower subset of changes

## Current Workflow

1. keep `BrPoliCorpus floor` as the main yearly panel
2. define a shared vocabulary panel across methods
3. compute drift scores for each method family
4. compare rankings, overlaps, and correlations
5. inspect representative stable and divergent cases
6. use symbolic features to interpret change type when useful
7. write the STIL paper as an exploratory comparative study

## Current Implementation Notes

The experiment package now assumes a multi-view prepared-artifact contract instead of a
single universal cleaned-text field.

Important current implementation details:

- `Word2Vec` trains from a configurable prepared text view via `model.text_view`
- the default training view is `content_lemma`
- `model.text_view` is validated at config load time
- `preprocess.preserve_accents` is now an active normalization switch
- contextual `BERT` dependencies are lazy-loaded so non-BERT runs stay lighter

## Active Documentation

The main docs to keep current are:

- `project_overview.md`
- `comparative_pipeline_readiness_2026_03_21.md`
- `exploratory_drift_comparison_plan.md`
- `progress_status_2026_03_20.md`
- `research_readiness_datasets.md`
- `semantic_change_literature_guide.md`
- `word_selection_protocol.md`
- `embedding_strategy_nilc_word2vec.md`
- `chat_handoff.md`
- `prepared_artifact_layout_2026_03_21.md`
- `runtime_config_cleanup_2026_03_21.md`
