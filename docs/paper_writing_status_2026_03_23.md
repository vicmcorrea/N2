# Paper Writing Status

Last updated: 2026-03-24

## Purpose

This note records the current manuscript state after the comparative pipeline,
shared panel, contextual run, cross-method agreement layer, and paper-facing
figure package were all folded into the STIL draft anchored to the frozen run:

- `run/outputs/experiments/brpolicorpus_floor_yearly/ba65fe5b9cce`

## Current manuscript files

Main manuscript:

- `2026S1_STIL_conceptDrift/main.tex`

Compiled PDF:

- `2026S1_STIL_conceptDrift/main.pdf`

Paper figure package:

- `2026S1_STIL_conceptDrift/figs/paper/figure_inventory.md`
- `2026S1_STIL_conceptDrift/figs/paper/figure_manifest.json`
- `2026S1_STIL_conceptDrift/figs/paper/figure_02_method_agreement.pdf`
- `2026S1_STIL_conceptDrift/figs/paper/figure_03_overlap_and_rank_statistics.pdf`
- `2026S1_STIL_conceptDrift/figs/paper/figure_04_representative_trajectories.pdf`
- `2026S1_STIL_conceptDrift/figs/paper/figure_05_study_design.pdf`

Exported but not currently used in the manuscript:

- `2026S1_STIL_conceptDrift/figs/paper/figure_01_corpus_profile.pdf`

All figures are exported as `PDF`, `EPS`, `PNG`, and `TIFF`.

## Current manuscript state

The manuscript is now well past planning and is in polishing mode.

The draft currently includes:

- title and abstract
- introduction and related work with verified citations
- corpus/setup and methodology sections aligned to the frozen run
- results and discussion organized around the current comparative findings
- conclusion, limitations, and ethics statement
- integrated LaTeX tables for dataset summary and method runtime
- integrated paper-facing figures

The paper compiled successfully on `2026-03-24`.

Current compiled status:

- total PDF pages: `9`
- main content comfortably within the STIL long-paper limit

## Current paper framing

The article should be defended as:

- an exploratory comparative study of drift techniques in Portuguese political discourse
- centered on `BrPoliCorpus floor`
- comparing `TF-IDF`, `Word2Vec`, and contextual `BERT`
- focused on agreement, divergence, interpretability, and computational cost

The paper should not claim externally validated semantic-change detection.

## Frozen results that anchor the draft

Corpus summary:

- `24` yearly slices
- `428,366` speeches
- `63,036,642` retained tokens
- `538,537,771` `content_lemma` characters
- `225,484` unique lemmas overall

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

## Current paper-facing figures and tables

Figure sequence in the manuscript:

1. study-design workflow
2. method agreement
3. overlap and rank summaries
4. representative trajectories

Current table set in the manuscript:

1. corpus summary table with totals and yearly quartiles
2. runtime/method scope table

## Current writing priorities

The highest-value writing work now is:

1. final prose tightening and consistency edits
2. minor layout cleanup when needed
3. cautious discussion polish around method-specific drift interpretations
4. any last citation or wording checks before submission packaging

The main job is no longer rebuilding the pipeline. It is turning the frozen
comparative package into the strongest possible STIL paper.
