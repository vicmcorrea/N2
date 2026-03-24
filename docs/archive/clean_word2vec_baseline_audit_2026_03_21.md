# Clean Word2Vec Baseline Audit

Date: 2026-03-21
Run root: `/Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/run/outputs/experiments/brpolicorpus_floor_yearly/2cf8a857028c`

## Status

This baseline completed successfully and is the current clean Word2Vec reference run for the comparative paper direction.

The pipeline finished all core stages:

- `prepare_corpus`
- `train_word2vec`
- `align_embeddings`
- `score_candidates`
- `report_candidates`

## Configuration Summary

- Corpus: `brpolicorpus_floor_yearly`
- Time slices: 24 yearly slices (`2000` to `2023`)
- Model: yearly Word2Vec Skip-Gram
- Vector size: `300`
- Window: `5`
- Negative samples: `5`
- Epochs: `5`
- Workers: `6`
- Replicates: `2`

## Stage Timings

- `prepare_corpus`: 21,160.644 seconds
- `train_word2vec`: 983.010 seconds
- `align_embeddings`: 38.230 seconds
- `score_candidates`: 306.723 seconds
- `report_candidates`: 3.817 seconds

Approximate completion time in Sao Paulo time: 2026-03-21 04:05:55 BRT.

## Artifact Integrity

The run produced the expected core artifacts:

- 48 trained slice models (`24 slices x 2 replicates`)
- 48 aligned slice vector stores
- aggregate score tables
- trajectory table
- candidate sets
- report figures and summaries

Key counts:

- Total documents: `428,366`
- Total cleaned tokens: `63,071,705`
- Eligible lemmas marked in eligibility table: `3,230`
- Lemmas actually scored in aggregate table: `3,225`
- Score rows per replicate table: `6,450`
- Trajectory rows: `148,338`

Alignment anchors look mechanically healthy:

- Anchor rows: `48`
- Minimum anchor count: `8,938`
- Median anchor count: `15,016`
- Maximum anchor count: `18,331`

## Main Audit Findings

### 1. The run is mechanically clean

The baseline completed all expected stages and generated the full artifact package. This means the pipeline is now good enough to serve as the reusable Word2Vec baseline arm in the upcoming comparative study.

### 2. The top-ranked drift list is semantically noisy

Top Word2Vec drift terms include items such as:

- `dir`
- `dito`
- `visto`
- `repito`
- `digo`
- `óbvio`
- `digar`
- `aspa`

Several of these look more like procedural, rhetorical, or formulaic plenary language than substantive conceptual drift. For the comparative paper, this is not fatal, but it means the current ranking is surfacing discourse-style movement and preprocessing artifacts together.

### 3. Lemmatization / normalization quality is a real interpretability bottleneck

The nearest-neighbor outputs contain malformed or suspicious forms such as:

- `digar`
- `repitar`
- `começarer`

This suggests the current preprocessing is still introducing unstable lemma variants. The baseline is therefore useful as a comparison artifact, but not yet strong enough to present top-ranked items as clean lexical evidence without additional filtering.

### 4. Five eligible lemmas were not scored because they are multi-token lemmas

These five lemmas appear in `eligible_vocabulary.parquet` but not in `scores_aggregated.parquet`:

- `encontrar se`
- `fazer ele`
- `parabenizar ele`
- `tornar se`
- `tratar se`

These forms contain spaces, so they are treated inconsistently between lemma statistics and Word2Vec tokenization. They should be excluded earlier from eligibility/scoring or normalized into a representation that the embedding pipeline can actually score consistently.

This is a small edge case, but it should be fixed before the comparative paper to avoid avoidable accounting mismatches.

### 5. Replicate stability is acceptable for the current baseline

For the top-ranked items inspected, replicate disagreement is small. Example cases:

- `dir`: `0.4960` vs `0.4938`
- `dito`: `0.4905` vs `0.4932`
- `repito`: `0.4859` vs `0.4907`
- `digar`: `0.4506` vs `0.4534`

This means the current signal is stable across the two replicates, even when the lexical content is not always theoretically attractive.

## Interpretation

This run should be treated as:

- a clean computational baseline
- a reusable reference artifact for the Word2Vec arm
- not yet a paper-ready lexical ranking without an additional cleanup layer

The stable controls look more plausible than many of the top drift candidates, which reinforces the view that the pipeline is operational but the lexical filtering layer still needs refinement.

## Recommended Next Changes Before Expanding Comparison

1. Exclude multi-token lemmas from eligibility and scoring.
2. Add a lightweight lexical cleanup layer for malformed lemmas and procedural speech markers.
3. Generate a qualitative inspection packet for the top drift candidates before freezing the comparative candidate panel.
4. Keep this run as the current baseline path for Word2Vec while building TF-IDF and contextual comparison arms.

## Baseline Freeze Decision

Decision: keep this run as the current clean Word2Vec baseline for the comparative pipeline, with the explicit caveat that lexical cleanup is still needed before interpreting the top-ranked drift terms as substantive political concepts.
