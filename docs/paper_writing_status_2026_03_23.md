# Paper Writing Status

Date: 2026-03-23

## Purpose

This note records the current article-writing state after the comparative pipeline,
shared comparison panel, contextual run, cross-method agreement layer, and
paper-facing figure package were all completed on top of the frozen baseline:

- `run/outputs/experiments/brpolicorpus_floor_yearly/ba65fe5b9cce`

The goal is to let a future chat continue writing the paper without re-auditing the
whole pipeline history first.

## Current manuscript files

Main manuscript:

- `2026S1_STIL_conceptDrift/main.tex`

Figure package:

- `2026S1_STIL_conceptDrift/figs/paper/figure_inventory.md`
- `2026S1_STIL_conceptDrift/figs/paper/figure_manifest.json`
- `2026S1_STIL_conceptDrift/figs/paper/figure_01_corpus_profile.pdf`
- `2026S1_STIL_conceptDrift/figs/paper/figure_02_method_agreement.pdf`
- `2026S1_STIL_conceptDrift/figs/paper/figure_03_overlap_and_rank_statistics.pdf`
- `2026S1_STIL_conceptDrift/figs/paper/figure_04_representative_trajectories.pdf`

All figures were exported as:

- `PDF`
- `EPS`
- `PNG`
- `TIFF`

## Current manuscript state

The draft already contains:

- a concrete working title
- a full abstract
- working prose in:
  - introduction
  - related work placeholder text
  - corpus/setup
  - methodology
  - results/discussion
  - conclusion
- integrated figure environments pointing to the paper figure package

The draft is therefore past the planning stage and should now be treated as an
active manuscript that needs refinement, citation support, and table/result polish.

## Current paper framing

The article should be written as:

- an exploratory comparative study of drift signals in Brazilian Portuguese political discourse
- centered on `BrPoliCorpus floor`
- comparing `TF-IDF`, `Word2Vec`, and contextual `BERT`
- focused on agreement, disagreement, interpretability, and computational tradeoffs

It should not be written as:

- a claim that one method definitively detects semantic change with external ground truth

That framing change came directly from advisor feedback and remains the key
motivation behind the current article structure.

## Current results to anchor the paper

Frozen run:

- `ba65fe5b9cce`

Corpus summary:

- 24 yearly slices
- 428,366 prepared speeches
- 63,071,705 retained tokens

Shared comparison panel:

- `55` lemmas total
- `15` `Word2Vec` drift terms
- `15` `TF-IDF` drift terms
- `20` stable controls
- `5` theory seeds

Cross-method summary:

- `Word2Vec` vs `TF-IDF` Spearman: `-0.540`
- `BERT(-1)` vs `Word2Vec` Spearman: `0.208`
- `BERT(-1)` vs `TF-IDF` Spearman: `0.125`
- `BERT` layer agreement Spearman: `0.858`

Top-15 overlap:

- `BERT` / `Word2Vec`: `7`
- `BERT` / `TF-IDF`: `6`
- `Word2Vec` / `TF-IDF`: `0`

Filtered contextual top terms:

- `bloqueio`
- `típico`
- `exposição`
- `salário`
- `mínimo`
- `troca`
- `preço`
- `voto`
- `real`
- `intervenção`
- `excepcional`
- `renovação`
- `eleição`
- `crítico`
- `político`

Important interpretation:

- the cheap methods disagree sharply
- contextual BERT is closer to `Word2Vec` than to `TF-IDF`, but it is not a copy of either
- the comparative story is therefore about complementary drift sensitivities, not winner-take-all benchmarking

## Current figures and what they show

### Figure 1

Corpus size profile over time:

- yearly document volume
- token volume
- vocabulary size

### Figure 2

Pairwise method agreement:

- `BERT` vs `Word2Vec`
- `BERT` vs `TF-IDF`
- `Word2Vec` vs `TF-IDF`
- BERT layer agreement

### Figure 3

Top-k overlap and rank-distribution tests:

- overlap curves
- bootstrap confidence intervals
- Mann-Whitney significance annotations for drift terms vs stable controls

### Figure 4

Representative trajectories:

- `bloqueio`
- `salário`
- `reforma`
- `trabalho`

## Main writing gaps still open

The draft still needs:

- a literature-grounded related-work section with real citations
- a compact methods table or textual summary with runtime/cost information
- a sharper discussion of why disagreement is informative rather than a failure
- one or more concise qualitative agreement/disagreement examples
- a short limitations paragraph about stable-control leakage and the filtered contextual list
- a decision on whether to mention `PTPARL-V` only as future validation or as a short current note

## Recommended next writing order

1. finish the related-work section with real citations
2. tighten the results section around the four figures and the core comparison numbers
3. add one compact table summarizing methods, cost, and output type
4. add a short limitations/future-work paragraph on `PTPARL-V` and symbolic analysis
5. compile and polish the LaTeX manuscript only after the prose is stabilized
