# Paper Figure Inventory

Experiment root: `run/outputs/experiments/brpolicorpus_floor_yearly/ba65fe5b9cce`
Preferred BERT layer: `-1`

## figure_01

Stem: `2026S1_STIL_conceptDrift (1)/figs/paper/figure_01_corpus_profile`

Corpus profile for the frozen BrPoliCorpus floor baseline. Panel (A) shows the number of floor speeches per yearly slice, panel (B) the retained token volume, and panel (C) the number of unique lemmas observed after preprocessing.

## figure_02

Stem: `2026S1_STIL_conceptDrift (1)/figs/paper/figure_02_method_agreement`

Pairwise agreement across drift methods on the shared comparison panel. Panels (A) through (C) show percentile-rank agreement between the preferred BERT layer, Word2Vec, and TF-IDF, while panel (D) compares the two contextual layers. Annotations report Spearman correlation and two-sided p-values.

## figure_03

Stem: `2026S1_STIL_conceptDrift (1)/figs/paper/figure_03_overlap_and_rank_statistics`

Overlap and rank-distribution summaries on the shared comparison panel. Panel (A) traces top-k overlap for the preferred BERT layer. Panels (B) through (D) show rank-percentile distributions by bucket for Word2Vec, TF-IDF, and BERT. Points show individual terms, large markers show means, error bars show 95% bootstrap confidence intervals, and brackets report one-sided Mann-Whitney tests for selected drift terms versus stable controls.

## figure_04

Stem: `2026S1_STIL_conceptDrift (1)/figs/paper/figure_04_representative_trajectories`

Representative term trajectories across methods. Each panel shows transition-level scores standardized within term and method to emphasize temporal shape rather than absolute scale. Word2Vec ribbons denote replicate variability; TF-IDF and BERT are single-series estimates.

## figure_05

Stem: `2026S1_STIL_conceptDrift (1)/figs/paper/figure_05_study_design`

Paper-facing comparative workflow. Cheap baselines nominate candidates; the shared panel combines those candidates with controls and theory seeds before contextual inspection and agreement analysis.
