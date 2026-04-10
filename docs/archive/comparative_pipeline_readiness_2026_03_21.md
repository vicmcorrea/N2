# Comparative Pipeline Readiness Audit

Date: 2026-03-21

## Purpose

This note records the current N2 pipeline state after verifying:

- the local Hydra + `uv` experiment package
- the preserved `BrPoliCorpus floor` run artifacts
- the local `PTPARL-V` organization
- the paper-facing comparative direction

It is meant to answer one practical question:

> What is the highest-value next implementation step for turning the current
> Word2Vec-first pipeline into a comparative drift pipeline that is useful for
> the paper?

## Executive Summary

The N2 codebase is now in **good shape as a reusable Word2Vec baseline pipeline**,
but it is **not yet in good comparative shape** for the current paper framing.

Current status:

1. A clean completed yearly `BrPoliCorpus floor` baseline run now exists at:
   - `run/outputs/experiments/brpolicorpus_floor_yearly/2cf8a857028c`
2. The shared preparation layer is reusable for additional methods because it already writes:
   - slice summaries
   - lemma-by-slice statistics
   - raw text shards
   - multiple processed text views
3. The code is still centered on a **Word2Vec -> report -> optional BERT confirmatory** story.
4. The most important missing comparative component is still a **first-class TF-IDF drift arm**.
5. `PTPARL-V` should be integrated as a **separate validation-oriented dataset path**, not pooled into the main `BrPoliCorpus` timeline.

## Verified Local Findings

## 1. The clean Word2Vec baseline is real

The preserved baseline at `2cf8a857028c` completed all expected stages:

- `prepare_corpus`
- `train_word2vec`
- `align_embeddings`
- `score_candidates`
- `report_candidates`

The stage manifests exist and the artifact package is complete.

Key counts from the preserved run:

- 24 yearly slices from `2000` to `2023`
- 48 trained slice models (`24 slices x 2 replicates`)
- 3,225 scored lemmas
- 148,338 trajectory rows
- alignment anchors between `8,938` and `18,331`

This means the current pipeline is already strong enough to serve as the frozen
Word2Vec arm of the comparative paper.

## 2. The quicklook is no longer the best reference run

The earlier quicklook remains useful as an exploratory milestone:

- `run/outputs/experiments/brpolicorpus_floor_yearly/ae5022228b99/quicklook/yearly_2003_2023_r1`

But it should no longer be treated as the main implementation reference, because
the clean completed baseline is now `2cf8a857028c`.

Also, the previously mentioned rerun path:

- `run/outputs/experiments/brpolicorpus_floor_yearly/c5437a2643c5`

is not present in the current workspace snapshot.

## 3. The reusable parts are already the right ones

Reusable immediately:

- `src/stil_semantic_change/data/loaders.py`
- `src/stil_semantic_change/preprocessing/text.py`
- `src/stil_semantic_change/preprocessing/views.py`
- `src/stil_semantic_change/utils/config/*`
- `src/stil_semantic_change/utils/artifacts.py`
- `src/stil_semantic_change/word2vec/*`

These components already give us the parts a comparative pipeline needs:

- one shared preparation stage
- one reproducible config hash per experiment
- one stable artifact layout
- one reusable eligibility table based on slice-level counts

This matches the comparative literature well: use one shared corpus contract,
then compare methods under the same data conditions instead of letting each
method silently redefine the task setup.

## 4. The pipeline is still structurally tied to the old paper framing

The main comparative gaps are still architectural, not just computational:

### Default task graph is Word2Vec-first

The default task remains:

1. `prepare_corpus`
2. `train_word2vec`
3. `align_embeddings`
4. `score_candidates`
5. `report_candidates`

This is still a good baseline pipeline, but it is not yet a multi-method
comparison workflow.

### BERT is still confirmatory, not peer-level

The current contextual path:

- reads `candidate_sets.json`
- samples only terms selected by the Word2Vec stage
- writes `comparison_with_word2vec.parquet`

So it still behaves as a downstream appendage to Word2Vec rather than as a
first-class method scored on a shared panel.

### Reporting and readiness remain single-method oriented

The current reports and readiness heuristics are still mostly about:

- Word2Vec drift rankings
- Word2Vec stable controls
- Procrustes anchor health

That is useful for baseline quality control, but not yet enough for the paper's
current questions about:

- agreement across methods
- disagreement structure
- cost versus signal
- validation-oriented usefulness

## 5. `PTPARL-V` is ready for a validation track, not as a pooled corpus

The local `PTPARL-V` organization is already strong:

- canonical processed layer: `RawDatasets/PTPARL-V/exports/V0-1/csv`
- inventory layer: `RawDatasets/PTPARL-V/inventory`
- exact publication-date coverage from `1995-11-23` to `2022-04-30`

Important local validation findings:

- `out_with_text_processed.csv` has `10,068` rows
- `5,713` rows have `text_process_label == 1`
- initiative keys based only on `ini_num + ini_leg` are unsafe
- `ini_num + ini_leg + ini_type` is the safer simple key

For a quick initiative-party aggregation audit on the processed rows:

- usable text-labeled rows with non-null votes: `5,713`
- initiative-party groups using `ini_num + ini_leg + ini_type`: `3,816`
- clean single-label initiative-party groups: `3,501`
- conflicted initiative-party groups: `315`
- clean group ratio: about `91.75%`

So `PTPARL-V` is already strong enough to support a separate validation table if
we:

1. restrict to processed usable text
2. aggregate at the initiative-party level
3. use `ini_num + ini_leg + ini_type`
4. drop conflicted groups

This is good enough for a validation-oriented paper companion, but it should not
be described as direct semantic-change ground truth.

## Highest-Value Next Implementation Step

Implement a first-class `tfidf_drift` stage that writes standardized method
artifacts over the same prepared yearly slices already used by Word2Vec.

Why this is the right next step:

1. It directly answers the advisor's cheap-versus-expensive comparison question.
2. It is the largest missing method family in the current pipeline.
3. It reuses the existing preparation outputs with minimal new infrastructure.
4. It creates the first real need for a shared comparison schema, which is the
   architectural pivot the rest of the comparative paper depends on.

### Minimal design for this step

Add a first implementation that:

- consumes `prepared/lemma_slice_stats.parquet`
- consumes one declared prepared text view
- uses the same slice order and eligibility logic as Word2Vec
- writes method-local outputs under `scores/tfidf_drift/`

Minimum artifacts:

- `scores/tfidf_drift/scores.parquet`
- `scores/tfidf_drift/trajectory.parquet`
- `scores/tfidf_drift/summary.json`

Required schema alignment:

- `lemma`
- `method`
- `primary_drift`
- `first_last_drift`
- `slice_count`
- `sample_count_total`
- `sample_count_min`
- `runtime_seconds`

After that, the immediate follow-up should be a small comparison-stage artifact,
not another Word2Vec rerun.

## Why TF-IDF First Is Methodologically Sound

The literature supports keeping the first comparative expansion simple and
controlled.

- Hamilton, Leskovec, and Jurafsky (2016) established aligned SGNS as a standard
  diachronic baseline for slice-specific semantic change analysis.
- Shoemark et al. (2019) compared semantic-change approaches systematically and
  showed that setup choices matter enough that side-by-side baselines are worth
  preserving rather than assuming one embedding pipeline is definitive.
- Schlechtweg et al. (2020) framed graded lexical semantic change as a ranking
  problem and evaluated systems through rank correlation, which fits the current
  paper's agreement/disagreement framing.
- Kutuzov, Velldal, and Ovrelid (2022) showed that contextualized methods are
  useful but can produce method-specific errors, which supports keeping BERT as a
  later peer arm rather than treating it as automatic truth.
- Periti and Tahmasebi (2024) argue that comparisons across contextualized
  semantic-change systems are often misleading unless the evaluation setup is
  controlled, which is another reason to build the cheap baseline and shared
  comparison contract before expanding contextual work.
- Sousa and Lopes Cardoso (2024) introduced `PTPARL-V` specifically as a
  Portuguese parliamentary resource aligned with voting behaviour, which supports
  using it as a validation-oriented external political signal instead of trying
  to force `BrPoliCorpus` alone into a validation story.

## Recommended Practical Order

1. Freeze `2cf8a857028c` as the Word2Vec baseline reference.
2. Implement `tfidf_drift` with a method-neutral score schema.
3. Build a shared comparison panel from Word2Vec + TF-IDF + controls + theory seeds.
4. Refactor contextual BERT to read from that panel instead of `candidate_sets.json`.
5. Add a small comparison stage for correlations, overlaps, and runtime summaries.
6. Add the `PTPARL-V` validation-table build as a separate pipeline path.

## Sources

- Hamilton, William L., Jure Leskovec, and Dan Jurafsky. 2016. *Diachronic Word Embeddings Reveal Statistical Laws of Semantic Change*. ACL.
  - https://aclanthology.org/P16-1141/
- Shoemark, Philippa, Farhana Ferdousi Liza, Dong Nguyen, Scott Hale, and Barbara McGillivray. 2019. *Room to Glo: A Systematic Comparison of Semantic Change Detection Approaches with Word Embeddings*. EMNLP-IJCNLP.
  - https://aclanthology.org/D19-1008/
- Schlechtweg, Dominik, Barbara McGillivray, Simon Hengchen, Haim Dubossarsky, and Nina Tahmasebi. 2020. *SemEval-2020 Task 1: Unsupervised Lexical Semantic Change Detection*. SemEval.
  - https://aclanthology.org/2020.semeval-1.1/
- Kutuzov, Andrey, Erik Velldal, and Lilja Øvrelid. 2022. *Contextualized embeddings for semantic change detection: Lessons learned*.
  - https://doi.org/10.3384/nejlt.2000-1533.2022.3478
- Periti, Francesco, and Nina Tahmasebi. 2024. *A Systematic Comparison of Contextualized Word Embeddings for Lexical Semantic Change*. NAACL.
  - https://doi.org/10.18653/v1/2024.naacl-long.240
- Sousa, Afonso, and Henrique Lopes Cardoso. 2024. *PTPARL-V: Portuguese Parliamentary Debates for Voting Behaviour Study*. ParlaCLARIN @ LREC-COLING.
  - https://aclanthology.org/2024.parlaclarin-1.6/
