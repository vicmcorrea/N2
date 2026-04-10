# Candidate Selection And Comparison Protocol

This note replaces the earlier “final semantic-change shortlist” framing with a protocol better suited to the current exploratory comparative paper.

## Goal

Build a shared set of candidate terms that lets us compare drift signals across:

- `TF-IDF`
- `Word2Vec`
- `BERT`
- optional symbolic features

The goal is not to create a gold-standard list of “true drift words.” The goal is to build a stable and interpretable comparison panel.

## Shared Vocabulary Panel

Start from lemmas in `BrPoliCorpus floor` and keep a shared analysis panel using:

- content words only by default: `NOUN`, `VERB`, `ADJ`
- minimum frequency threshold per slice
- minimum document-dispersion threshold per slice
- minimum presence across slices

Initial practical defaults:

- at least `50` occurrences per slice
- at least `5` documents per slice
- present in at least `80%` of slices

## Candidate Types To Keep

Build a final comparison panel with several kinds of terms:

1. high-drift candidates from `Word2Vec`
2. high-drift candidates from `TF-IDF`
3. high-drift candidates from `BERT`
4. low-drift stable controls
5. theory-relevant seed terms such as `democracia`, `corrupção`, `golpe`, `previdência`, `cpi`

This avoids overfitting the analysis to only one method.

## Per-Method Use

### TF-IDF

Use `TF-IDF` or similar context-profile representations as a lexical baseline.

Recommended interpretation:

- strong for topic/frame movement
- strong for changes in salient co-occurring vocabulary
- cheap and easy to scale

### Word2Vec

Use yearly or semester slice-specific Skip-Gram embeddings aligned with Orthogonal Procrustes.

Recommended interpretation:

- strong for neighborhood or association change
- practical middle ground between cost and expressiveness

### BERT

Use contextual embeddings only on the shared candidate panel or a filtered subset.

Recommended interpretation:

- strong for usage-level contextual change
- expensive, so it should not be the first screening pass

### Symbolic features

Use only as a support layer, not as the sole drift score.

Possible use:

- distinguish semantic drift from rhetoric/style drift
- track emotiveness, cohesion, complexity, or discourse markers at the slice level

## Comparison Metrics

For the paper, comparison should emphasize:

- rank correlation between methods
- top-k overlap
- agreement on stable controls
- disagreement cases
- computational cost
- qualitative interpretability

Useful statistics:

- Spearman correlation
- Kendall correlation
- Jaccard overlap for top-k lists
- pairwise agreement on manually inspected candidates

## Manual Inspection Protocol

For a selected subset of words:

1. inspect early and late contexts
2. inspect each method's nearest evidence or context signature
3. annotate the likely drift type

Suggested drift-type labels:

- topical/frame drift
- contextual sense drift
- rhetorical/evaluative drift
- style/register drift
- unclear/noisy

This gives the paper a stronger interpretive layer without pretending to have full gold labels.

## Output Panel For The Paper

The final article should include:

- a shared comparison table with scores from all methods
- a stable-controls table
- a method-agreement figure
- a disagreement-case figure or appendix
- selected qualitative context examples

## Practical Rule

Do not let one method define the whole story.

The point of the current paper is to compare methods on the same Portuguese political corpus, not to assume in advance that one method is the truth.
