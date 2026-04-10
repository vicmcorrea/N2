# Advisor Feedback: 2026-03-20

## Why The Original Framing Became A Problem

The earlier N2 direction was too close to a paper that claimed meaningful semantic-drift detection without a convincing validation layer.

Main issue raised by the advisor:

- the dataset has no external ground-truth labels for semantic drift
- the current results were mostly unsupervised rankings plus qualitative interpretation
- that makes it hard to defend strong claims that the detected drift is objectively correct

In other words, the problem was not that the project had no interesting signals. The problem was that the article framing depended too much on validation that we do not currently have.

## Main Advisor Recommendation

Shift the paper from:

- a validation-heavy semantic-change article

to:

- an exploratory article about comparing drift techniques in Portuguese political discourse

## New Recommended Direction

The advisor suggested reframing the paper around:

- comparison of multiple drift techniques
- correlation and agreement between methods
- usefulness of cheap versus expensive approaches
- interpretation of what kinds of drift each method appears to capture

This means the paper no longer needs to prove that one method is the true semantic-change detector. Instead, it should compare how different methods behave on the same corpus.

## Specific Suggestions From The Advisor

### 1. Add more than one drift technique

The earlier direction leaned too heavily on embedding-based drift.

The advisor explicitly suggested adding at least:

- `TF-IDF`
- `Word2Vec`
- `BERT`

so the paper can compare their outputs directly.

### 2. Analyze correlation between methods

The paper should ask:

- do the techniques rank similar words as drifting?
- how much overlap do they show?
- where do they disagree?

This is useful even if there is no external label set.

### 3. Compare quality against computational cost

One important practical question is:

- if `TF-IDF`, `Word2Vec`, and `BERT` produce very similar results, is it still worth paying the cost of `BERT`?

This could become one of the main contributions of the paper.

### 4. Consider that different methods may capture different drift types

The advisor highlighted that some techniques may be better for different kinds of change, for example:

- factual or topic drift
- writing-style or rhetorical drift
- more lexical or symbolic shifts
- contextual meaning changes

So disagreement is not automatically failure. It may reveal that methods are sensitive to different kinds of movement.

### 5. Add symbolic or lexical analysis

The advisor suggested exploring a more symbolic layer as well, not only embeddings.

Possible direction:

- `NILC-Metrix`
- dictionary-based or rule-based lexical features
- symbolic indicators such as emotiveness, style, or other lexical variables

This is useful because some apparent “drift” may be more about discourse style, evaluation, or rhetoric than about pure lexical semantics.

Relevant references mentioned during this discussion:

- [NILC-Metrix site](https://pln.venturus.dev.br/nilcmetrix)
- [NILC-Metrix repository](https://github.com/nilc-nlp/nilcmetrix)

## What This Means For N2

The project is still viable, but the contribution has changed.

The paper should now be defended as:

- an exploratory comparative study
- on Portuguese political discourse
- using `BrPoliCorpus floor` as the main corpus
- with multiple drift techniques
- and with attention to agreement, divergence, interpretability, and cost

## Practical Consequences

This feedback implies the following changes:

1. Do not frame the paper as if we already have validated semantic-change detection.
2. Keep the current `Word2Vec` work, but treat it as one method family among others.
3. Add a `TF-IDF` drift baseline.
4. Reuse `BERT` as the expensive contextual comparison method.
5. Consider a symbolic support layer, likely using selected `NILC-Metrix` features or simpler lexical indicators.
6. Build the article around comparison, not around a single-method claim.

## Recommended Working Claim

A safe and useful working claim is:

> Different drift-detection techniques show partly overlapping but not identical signals in Brazilian Portuguese political discourse, and this comparison helps clarify which methods are sufficient, which are expensive, and which kinds of change they appear to capture.

## Status After Feedback

After this advisor feedback, the N2 documentation should be interpreted under the new exploratory-comparison framing.

The current live docs that reflect this updated direction are:

- `docs/project_overview.md`
- `docs/chat_handoff.md`
- `docs/paper_writing_status_2026_03_23.md`

Older planning files from the transition into this framing were moved to
`docs/archive/`.
