# Advisor Comment Fix Plan

This file proposes manuscript edits only. It does not contain a response letter, email text, or short answers to the advisor.

Active paper path checked in this checkout: `2026S1_STIL_conceptDrift/main.tex`.

## 1. Shared Panel Size, 15 + 15 + 20 + 5

Issue in the current paper: Section `Methodology`, subsection `Shared Comparison Panel and the agreement layer`, says the values were chosen empirically and limited by computational cost. That is too vague.

Why the concern is valid: the reader needs to know that these are fixed practical defaults, not tuned after seeing results.

Best fix: replace the weak sentence with a concise explanation of cost and role.

Exact location: `2026S1_STIL_conceptDrift/main.tex`, subsection `Shared Comparison Panel and the agreement layer`.

Replacement text:

```latex
These counts were fixed before contextual scoring as practical defaults rather than tuned to favor any method. Fifteen candidates per cheaper tier capture the top region of each method-specific ranking while keeping the contextual stage tractable, since each additional lemma can require up to 64 sampled contexts per yearly slice. The 20 stable controls balance the panel with low-drift terms from the cheaper rankings, and the 5 theory seeds keep a small interpretive anchor without turning the seed list into a third candidate source.
```

Citations needed: optional. If cited, use the already verified `schlechtweg-etal-2020-semeval` for small curated LSC target sets. I would not add a citation only for the numeric split.

## 2. Source of Theory Seeds

Issue in the current paper: the paper says the seeds are drawn from prior work on Brazilian political vocabulary, but the internal docs show they were selected by domain motivated inspection, not copied from a published seed list.

Why the concern is valid: the current wording overclaims.

Best fix: be honest and cite corpus and resource context, not a nonexistent seed source.

Exact location: `2026S1_STIL_conceptDrift/main.tex`, subsection `Shared Comparison Panel and the agreement layer`.

Replacement text:

```latex
The theory seeds (\textit{democracia}, \textit{corrup\c{c}\~ao}, \textit{reforma}, \textit{economia}, and \textit{liberdade}) were selected by manual inspection as recurring, politically central lemmas in Brazilian parliamentary discourse, informed by the BrPoliCorpus resource~\cite{lima-lopes-2025-brpolicorpus} and by the broader survey of Portuguese diachronic resources in~\cite{osorio-cardoso-2025-historical}. They are used as interpretive anchors, not as supervised labels or as a gold standard.
```

Citations needed: yes, but use existing verified keys only: `lima-lopes-2025-brpolicorpus`, `osorio-cardoso-2025-historical`.

## 3. Missing Methodological Details About Panel

Issue in the current paper: Section 4 omits key construction details: dominant POS gate, lexical exclusions, and how stable controls are drawn.

Why the concern is valid: without these details, the panel looks hand picked.

Best fix: add one sentence after the first panel composition sentence.

Exact location: `2026S1_STIL_conceptDrift/main.tex`, subsection `Shared Comparison Panel and the agreement layer`.

Insertion text:

```latex
Drift candidates and stable controls are further restricted to lemmas whose dominant POS is \texttt{NOUN} or \texttt{ADJ}, after removing generic discourse terms, broad evaluatives, and parliamentary procedural residue. Stable controls are drawn from the low-drift end of the cheaper rankings, with 10 controls from Word2Vec and 10 from TF-IDF, so leakage diagnostics are not tied to a single low-drift source.
```

Citations needed: not strictly, because this describes the pipeline. If citing POS restricted LSC practice, add verified `schlechtweg-etal-2019-wind`, DOI `10.18653/v1/P19-1072`.

## 4. How To Interpret Figure `fig:method_agreement`

Issue in the current paper: the results jump from naming Figure `fig:method_agreement` to conclusions without teaching the reader how to read rank scatterplots.

Why the concern is valid: the plot is not self explanatory to readers unfamiliar with rank agreement diagnostics.

Best fix: insert a short interpretation paragraph before Figure `fig:method_agreement`.

Figure: `Figure fig:method_agreement (figs/paper/figure_02_method_agreement_panel_a.pdf, figs/paper/figure_02_method_agreement_panel_b.pdf, figs/paper/figure_02_method_agreement_panel_c.pdf, figs/paper/figure_02_method_agreement_panel_d.pdf)`.

Insertion text:

```latex
Each panel in Figure~\ref{fig:method_agreement} compares the ranks assigned to the same 55 lemmas by two scoring views. Points close to a rising diagonal indicate similar rankings, points close to a falling diagonal indicate inverse rankings, and a diffuse cloud indicates weak association. The annotated Spearman $\rho$ summarizes the rank trend, with the two-sided p-value reported beside it.
```

Citations needed: optional. Spearman rank correlation for LSC rankings is supported by existing `schlechtweg-etal-2020-semeval`.

## 5. Replace `preferred` With `primary`

Issue in the current paper: the paper uses `preferred` in the results for BERT layer `$-1$`, while Section 4 already uses `primary`.

Why the concern is valid: `preferred` sounds subjective. `Primary` names the analytical role.

Best fix: replace all visible uses of `preferred` with `primary`.

Exact locations: Results paragraph introducing Figure `fig:method_agreement`, BERT paragraph, top k paragraph, APD paragraph.

Exact replacements:

```latex
the preferred contextual ranking
```

to

```latex
the primary contextual ranking
```

```latex
On the preferred layer ($-1$)
```

to

```latex
On the primary layer ($-1$)
```

```latex
In the preferred BERT layer ($-1$)
```

to

```latex
In the primary BERT layer ($-1$)
```

```latex
On the preferred layer, APD and centroid rankings
```

to

```latex
On the primary layer, APD and centroid rankings
```

Citations needed: no.

## 6. Caption Confuses Panel And Agreement Layer

Issue in the current paper: the caption says pairwise rank agreement on the shared comparison panel, which is close but underplays that the plotted scores are computed by the agreement analysis layer.

Why the concern is valid: the shared panel is the candidate universe. The agreement layer computes the rank comparisons over it.

Best fix: change the first caption sentence.

Figure: `Figure fig:method_agreement (figs/paper/figure_02_method_agreement_panel_a.pdf, figs/paper/figure_02_method_agreement_panel_b.pdf, figs/paper/figure_02_method_agreement_panel_c.pdf, figs/paper/figure_02_method_agreement_panel_d.pdf)`.

Replacement caption:

```latex
\caption{Pairwise rank agreement computed by the agreement analysis layer over the shared comparison panel. Each scatter compares the drift rankings of two scoring views over the same 55 lemmas: BERT vs.\
Word2Vec (top left), BERT vs.\ TF-IDF (top right), Word2Vec vs.\ TF-IDF (bottom left),
and BERT layers $-4$ vs.\ $-1$ (bottom right). Annotations report Spearman $\bm{\rho}$
and two-sided p-values; the legend in the top-left panel applies throughout.}
```

Citations needed: no.

## 7. Rewrite Agreement Layer Description

Issue in the current paper: the Section 3 agreement layer paragraph lists diagnostics but still reads like a technical inventory.

Why the concern is valid: the reader needs to know which question each diagnostic answers.

Best fix: replace the paragraph beginning with “Finally, the last component”.

Exact location: `2026S1_STIL_conceptDrift/main.tex`, Section `Comparative Drift Framework`.

Replacement text:

```latex
Finally, the framework adds an \textbf{agreement analysis layer}, which compares the rankings produced after all tiers score the same shared panel. This layer asks four practical questions. First, do two methods order the panel similarly overall? Pairwise rank correlations answer this at the level of the full ranking. Second, do the methods agree near the top, where candidate drift terms are selected? Top-$k$ overlap curves track shared high-ranked lemmas as $k$ grows. Third, do stable controls remain low ranked? Stable-control leakage rates identify controls that rise into candidate regions and therefore expose possible method-side noise. Fourth, after leaked controls are removed, which contextual candidates remain most useful for qualitative inspection? The filtered contextual ranking provides that final view.
```

Figures affected: `Figure fig:method_agreement (figs/paper/figure_02_method_agreement_panel_a.pdf, figs/paper/figure_02_method_agreement_panel_b.pdf, figs/paper/figure_02_method_agreement_panel_c.pdf, figs/paper/figure_02_method_agreement_panel_d.pdf)` and `Figure fig:overlap_rank_stats (figs/paper/figure_03_overlap_and_rank_statistics_panel_a.pdf, figs/paper/figure_03_overlap_and_rank_statistics_panel_b.pdf, figs/paper/figure_03_overlap_and_rank_statistics_panel_c.pdf, figs/paper/figure_03_overlap_and_rank_statistics_panel_d.pdf)`.

Citations needed: optional. Existing `schlechtweg-etal-2020-semeval` supports rank evaluation. Verified `dubossarsky-etal-2017-outta` supports control based caution, DOI `10.18653/v1/D17-1118`.

## 8. Group Model Descriptions

Issue in the current paper: there is some repetition between Section 3 and Section 4.

Why the concern is partly valid: the current structure is mostly right. Section 3 defines abstract tiers, while Section 4 instantiates TF-IDF, Word2Vec, and BERTimbau.

Best fix: keep grouped model details in Section 4, but reduce Section 3’s tier paragraph if space is tight. Do not merge everything.

Exact location: `2026S1_STIL_conceptDrift/main.tex`, Section `Comparative Drift Framework`, paragraph beginning “The framework then organizes”; and Section `Methodology`, subsection `Drift detection tiers`.

Suggested Section 3 tightening:

```latex
The framework then organizes lexical semantic change detection into three computational tiers arranged by increasing cost: a lexical-statistical baseline for salience shifts, a static-embedding method for aligned neighborhood displacement, and a contextual-embedding method for token-level usage variation.
```

Citations needed: no beyond existing related work.

## 9. Revise Staged Cost Awareness Paragraph

Issue in the current paper: the current paragraph is directionally right but wordy, and the feed forward phrasing can be tightened.

Why the concern is valid: this paragraph carries the logic of the framework and should read cleanly.

Best fix: replace the staged cost paragraph in Section 3.

Figure: `Figure fig:study_design (figs/paper/figure_05_study_design_v2.pdf)`.

Replacement text:

```latex
The key design principle is \emph{staged cost awareness}. The two cheaper tiers first score the full eligible vocabulary, using their own representations to estimate diachronic drift for each lemma. Their highest-ranked candidates feed into the expensive contextual stage, avoiding BERT inference over every eligible lemma. Cross-method comparison then requires a fixed evaluation set, so no method is judged only on the terms it would naturally select.
```

Citations needed: optional. If you want a literature anchor for vocabulary wide discovery before contextual validation, use verified `kurtyigit-etal-2021-lexical`, DOI `10.18653/v1/2021.acl-long.543`.

## 10. Revise Section 4 Panel Paragraph After Moving Explanations To Section 3

Issue in the current paper: Section 4 should not repeat the whole framework logic, but it currently says too little and uses weak wording.

Why the concern is valid: after explanations moved to Section 3, Section 4 still needs enough concrete implementation detail.

Best fix: replace the whole paragraph in `Shared Comparison Panel and the agreement layer` with an instantiation only paragraph.

Exact location: `2026S1_STIL_conceptDrift/main.tex`, subsection `Shared Comparison Panel and the agreement layer`.

Replacement text:

```latex
Following the framework design (Section~\ref{sec:framework}), we instantiate the shared panel with 55 lemmas: 15 Word2Vec-led drift candidates, 15 TF-IDF-led drift candidates, 20 stable controls, and 5 theory seeds. The Word2Vec and TF-IDF candidate groups are the top-ranked filtered lemmas under each cheaper method, with no overlap between their top-15 lists in the frozen run. Stable controls are drawn from the low-drift end of the cheaper rankings, split evenly between Word2Vec and TF-IDF sources. The theory seeds are \textit{democracia}, \textit{corrup\c{c}\~ao}, \textit{reforma}, \textit{economia}, and \textit{liberdade}. The agreement layer is then instantiated with pairwise Spearman rank correlations, top-$k$ overlap curves for $k=1,\dots,15$, stable-control leakage diagnostics, and a filtered contextual ranking for qualitative inspection.
```

Citations needed: combine with point 2 seed sentence if you do not want this paragraph to become too long.

## 11. Evaluate New Title

Issue in the current paper: the current title is `A Comparative Framework for Diachronic Lexical Semantic Change in Brazilian Portuguese Political Discourse`.

Why the concern is not a problem: the advisor’s change is good. It foregrounds the domain, keeps the framework as the contribution, and avoids making the paper sound like a closed three model benchmark only.

Best fix: keep the current title.

Exact location: title block.

No replacement needed.

Optional shorter title:

```latex
\title{A Comparative Framework for Lexical Semantic Change in Brazilian Portuguese Political Discourse}
```

Recommendation: keep the current title because `Diachronic` helps searchability.

Citations needed: no.

## 12. Revise BERT Inter Layer Paragraph

Issue in the current paper: the paragraph still says `preferred`, does not explicitly state that the two BERT correlations are not significant at conventional levels, and could be more precise about what the layer comparison proves.

Why the concern is valid: the current paragraph can sound stronger than the statistics support.

Best fix: replace the BERT paragraph in Results beginning with “Figure~\ref{fig:method_agreement} also shows”.

Exact location: `2026S1_STIL_conceptDrift/main.tex`, Results section.

Replacement text:

```latex
Figure~\ref{fig:method_agreement} also shows that the contextual tier partly mediates the split between the cheaper baselines without collapsing onto either one. On the primary layer ($-1$), BERT reaches Spearman $\rho = 0.21$ ($p = 0.128$) with Word2Vec and $\rho = 0.12$ ($p = 0.365$) with TF-IDF. Neither association is significant at the conventional $\alpha = 0.05$ level, so contextual BERT should not be treated as a substitute for either cheaper method. Instead, it acts as an intermediate signal that partially aligns with both. The BERT layer comparison shows much stronger agreement between layers $-4$ and $-1$ (Spearman $\rho = 0.858$), indicating that the contextual conclusions are not driven by a single extraction depth. This pattern is consistent with prior findings that mid-to-upper BERT layers carry much of the semantic change signal, while the final layer can encode surface-form information that biases change scores~\cite{laicher-etal-2021-explaining,cassotti-etal-2024-systematic}. In this setting, the agreement between layers $-4$ and $-1$ suggests that orthographic bias does not dominate the contextual ranking, although it cannot be fully ruled out.
```

Citations needed: existing verified `laicher-etal-2021-explaining`, `cassotti-etal-2024-systematic`. I would not add `tenney-etal-2019-bert` unless broader BERT probing support is needed. It was verified via Valyu and Exa as ACL DOI `10.18653/v1/P19-1452`.

## Citation Notes

New citations to consider only if stronger support is needed:

1. `schlechtweg-etal-2019-wind`, verified with Valyu and Exa, DOI `10.18653/v1/P19-1072`.

2. `dubossarsky-etal-2017-outta`, verified with Valyu and Exa, DOI `10.18653/v1/D17-1118`.

3. `kurtyigit-etal-2021-lexical`, verified with Valyu and Exa, DOI `10.18653/v1/2021.acl-long.543`.

I would not use the Silva BRACIS citation for the theory seeds right now. Valyu found it indirectly, but Exa hit a rate limit before secondary verification, and the current paper can solve the advisor’s concern cleanly with existing BrPoliCorpus and Portuguese resource citations.
