# Exploratory Drift Comparison Plan

## Goal

Turn N2 into an exploratory paper about how different drift techniques behave on Portuguese political discourse, using `BrPoliCorpus floor` as the main corpus.

## Core Paper Claim

The paper should claim something like:

> Different drift-detection families show partly overlapping but not identical signals in Brazilian Portuguese political discourse, and the agreement structure itself is informative for method choice and interpretation.

This framing is strong even without external labeled ground truth.

## Main Research Questions

### RQ1

How strongly do drift rankings correlate across `TF-IDF`, `Word2Vec`, and contextual `BERT` on `BrPoliCorpus floor`?

### RQ2

Which terms are consistently ranked as high-drift across methods, and which appear only in specific method families?

### RQ3

Does contextual `BERT` provide enough additional signal to justify its cost relative to lighter alternatives?

### RQ4

Can symbolic or lexical-feature analysis help distinguish semantic change from topical, rhetorical, or stylistic change?

## Corpus Design

### Main corpus

- `RawDatasets/BrPoliCorpus-Dataset/exports/floor`

### Complementary corpus

- `RawDatasets/Roda-Viva-Dataset/exports/V0-2/csv`

### Main temporal granularity

- yearly

### First robustness check

- semester

## Technique Matrix

### 1. TF-IDF profile drift

Possible implementations:

- compare slice-level context vectors for each lemma
- use term-context matrices with cosine drift across periods

Why it matters:

- cheap baseline
- easy to scale
- may capture topical and framing shifts surprisingly well

### 2. Word2Vec drift

Current main embedding pipeline:

- Skip-Gram 300d per slice
- Orthogonal Procrustes alignment

Why it matters:

- already implemented in N2
- good balance of interpretability and cost

### 3. Contextual BERT drift

Use:

- contextual embeddings on sampled occurrences of selected terms
- period-level prototype comparisons or clustering-based diagnostics

Why it matters:

- usage-sensitive
- expensive
- useful as the high-cost comparison point

### 4. Symbolic analysis

Possible sources:

- selected `NILC-Metrix` measures
- simpler rule-based lexical statistics

Use it for:

- emotiveness
- lexical density or complexity
- discourse-connective or cohesion-related changes
- separating style/rhetoric effects from semantic-style claims

## Evaluation Without Gold Labels

Because the corpus has no external ground-truth labels, the paper should rely on comparison-based evaluation:

- rank correlation across methods
- top-k overlap
- stability across reruns
- stability across yearly vs semester slicing
- qualitative case analysis
- runtime/cost comparison

This is not a weakness if it is presented explicitly as the paper design.

## What Counts As A Useful Result

Any of these outcomes is publishable if well analyzed:

- high agreement across methods
- low agreement across methods
- evidence that cheap baselines approximate expensive models
- evidence that certain drift types are method-specific
- evidence that some “drift” is mostly rhetorical or stylistic rather than semantic

## Immediate Implementation Priorities

1. Implement the `TF-IDF` drift baseline in N2.
2. Define a shared comparison vocabulary panel.
3. Reuse the existing `Word2Vec` pipeline as the main embedding baseline.
4. Run `BERT` only on the shared candidate panel.
5. Decide which symbolic features are realistic to add in the first paper version.

## Proposed Comparison Outputs

The paper should aim to produce:

- method-by-method drift rankings
- pairwise rank-correlation table
- top-k overlap table
- cost/runtime comparison table
- multi-method case studies for selected terms
- agreement vs disagreement visualizations

## Minimal Paper Package

At a minimum, the paper should include:

1. one clear corpus/setup figure
2. one method-comparison table
3. one agreement/correlation figure
4. one disagreement or case-study figure
5. one cost/runtime comparison table
6. a short qualitative section explaining what kinds of drift each method appears to recover

## Recommendation On Symbolic Layer

Treat `NILC-Metrix` as an interpretive companion layer, not as the sole drift detector.

Best use:

- slice-level discourse diagnostics
- context-style interpretation for selected words
- separation of semantic, topical, and rhetorical signals

## Final Practical Position

Do not try to prove that one method is universally correct.

Instead, show:

- what each method recovers
- when they agree
- when they disagree
- what that means for Portuguese political discourse analysis
