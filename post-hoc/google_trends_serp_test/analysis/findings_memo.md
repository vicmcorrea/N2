# Google Trends Post-hoc Analysis Against Frozen STIL Run

## Scope

This memo analyzes whether the existing Google Trends sandbox provides a meaningful external signal for the frozen comparative STIL run [`ba65fe5b9cce`](/Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/run/outputs/experiments/brpolicorpus_floor_yearly/ba65fe5b9cce). The analysis is strictly post hoc: it does not alter the frozen run, does not introduce a new pipeline, and does not modify manuscript-facing figures or result files.

The frozen internal anchor is the shared 55-term comparison panel from [`scores/comparison_panel/comparison_panel.parquet`](/Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/run/outputs/experiments/brpolicorpus_floor_yearly/ba65fe5b9cce/scores/comparison_panel/comparison_panel.parquet), composed of 15 `Word2Vec`-only drift terms, 15 `TF-IDF`-only drift terms, 20 stable controls, and 5 theory seeds. The external anchor is the Oxylabs batch run in [`google_trends_serp_test/outputs/batch_20260406T020524Z`](/Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/google_trends_serp_test/outputs/batch_20260406T020524Z), which returned 20 yearly values per term for 2004 to 2023.

## What the Google Signal Represents

The external signal is best understood as normalized public search interest, not lexical usage. Oxylabs documents `google_trends_explore` as a source that retrieves Google Trends results and explicitly warns that the scraped output may not be fully accurate relative to direct browser use of Google Trends. Oxylabs also exposes this source as a structured wrapper around Google Trends Explore, with support for query string, country-level `geo_location`, date bounds beginning on `2004-01-01`, and search-type selection. See the official documentation: [Oxylabs Trends: Explore](https://developers.oxylabs.io/scraping-solutions/web-scraper-api/targets/google/trends-explore).

Google’s own documentation states that Trends is built from an anonymized, categorized, aggregated sample of Google searches rather than the full search log. Google also states that the plotted values are normalized within the requested geography and time range, then scaled to 0–100, and that Trends is not polling data and should not be treated as a direct mirror of underlying reality. See the official help pages: [FAQ about Google Trends data](https://support.google.com/trends/answer/4365533?hl=en) and [Compare Trends search terms](https://support.google.com/trends/answer/4359550?hl=en).

That distinction matters here. Our frozen STIL outputs measure lexical-semantic movement inside parliamentary speech. Google Trends measures how much the broader public searched for a query relative to all Google searches in Brazil over a requested period. These are different behavioral objects. Any relationship between them should therefore be interpreted as external contextual resonance, not as external ground truth for semantic drift.

## Suitability for the Frozen Yearly Setup

The Google series is only partially suitable for comparison with the frozen yearly slices. The good news is that the sandbox requested `date_from=2004-01-01`, `date_to=2023-12-31`, and `geo_location=BR`, then stored 240 monthly points per term and derived 20 yearly rows covering 2004–2023. That makes the temporal bins broadly compatible with the later portion of the frozen corpus timeline.

The limitation is conceptual rather than purely temporal. The frozen STIL scores summarize adjacent-slice lexical or semantic movement, while the Google series summarizes normalized public search attention. The yearly aggregation in the sandbox is a mean over monthly normalized values, which smooths spikes and further distances the external measure from the transition-based internal drift metrics. It is therefore reasonable to compare coarse temporal movement over 2004–2023, but not to treat the match as a strict validation test.

## Data Used

The key joined analysis table is [`panel_google_joined.csv`](/Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/google_trends_serp_test/analysis/tables/panel_google_joined.csv). It links each of the 55 frozen panel lemmas to Google-derived movement features such as yearly mean absolute change, standard deviation, range, non-zero share, and peak year. Group summaries and tests are in [`group_external_movement_summary.csv`](/Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/google_trends_serp_test/analysis/tables/group_external_movement_summary.csv) and [`group_external_movement_tests.csv`](/Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/google_trends_serp_test/analysis/tables/group_external_movement_tests.csv). Internal-external correlations are in [`internal_external_correlations.csv`](/Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/google_trends_serp_test/analysis/tables/internal_external_correlations.csv).

Figures are stored in [`google_trends_serp_test/analysis/figures`](/Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/google_trends_serp_test/analysis/figures). The most useful ones are:

- [`figure_bucket_external_movement.pdf`](/Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/google_trends_serp_test/analysis/figures/figure_bucket_external_movement.pdf)
- [`figure_internal_vs_external_scatter.pdf`](/Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/google_trends_serp_test/analysis/figures/figure_internal_vs_external_scatter.pdf)
- [`figure_representative_trajectories.pdf`](/Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/google_trends_serp_test/analysis/figures/figure_representative_trajectories.pdf)

## Main Findings

The broad pattern is mixed and method-dependent rather than strongly confirmatory. Across the full 55-term panel, `Word2Vec` drift is moderately positively associated with Google volatility, while `TF-IDF` drift is not. Using yearly mean absolute change as the main external movement measure, the Spearman correlation is `0.298` for `Word2Vec` versus Google movement, but `-0.067` for `TF-IDF` versus Google movement. Using broader volatility measures, `Word2Vec` also correlates positively with Google standard deviation (`ρ = 0.510`) and range (`ρ = 0.499`), while `TF-IDF` correlates negatively with both (`ρ = -0.453` and `ρ = -0.410`). However, these panel-wide relationships weaken once we restrict attention to the 30 drift candidates alone. Inside the drift-only set, the `Word2Vec` correlations become small and statistically weak, while `TF-IDF` remains negatively associated with Google volatility.

This means the apparent external support for `Word2Vec` is real but limited. It mainly comes from separation between `Word2Vec` drift terms and the lower-volatility end of the stable-control set, not from a clean monotonic relationship among the high-drift terms themselves. In other words, Google helps distinguish some `Word2Vec` drift candidates from very flat controls, but it does not strongly rank-order the `Word2Vec` drift list internally.

The group comparisons make the same point. The median Google yearly mean absolute change is `4.76` for the `Word2Vec` drift list, `4.61` for the `TF-IDF` drift list, `3.86` for stable controls, and `4.13` for theory seeds. `Word2Vec` drift exceeds stable controls on this volatility measure with a moderate effect (`p = 0.013`, Cliff’s delta `= 0.50`). The `TF-IDF` list trends in the same direction but more weakly (`p = 0.083`). If the question is whether stable controls are externally flatter than drift candidates, the answer is yes in a limited sense, but the contrast is cleaner for `Word2Vec` than for `TF-IDF`, and several stable controls are not externally flat at all.

## Answers to the Core Questions

### 1. Do high-drift lemmas also show stronger external temporal movement in Google Trends?

Only weakly, and mostly for `Word2Vec` when the whole panel is considered. The strongest positive relationship is between `Word2Vec` drift and Google volatility across all 55 panel terms. That relationship becomes weak inside the drift-only subset, so the evidence is not strong enough to say that higher internal drift reliably implies higher external movement. For `TF-IDF`, the relationship is not positive and is sometimes negative.

### 2. Do Word2Vec-led and TF-IDF-led candidates differ in their Google Trends profiles?

Yes. The `Word2Vec` list is somewhat more externally volatile on average and has a broader upper tail of externally dynamic terms. Its median Google range is `59.08`, compared with `45.92` for the `TF-IDF` list and `38.42` for stable controls. The `TF-IDF` list is much more mixed: some terms are clearly dynamic in Google Trends, but others that are top-ranked internally look relatively smooth externally.

The most externally dynamic `Word2Vec` cases include `inédito`, `alvo`, `planalto`, `perigoso`, `inaceitável`, and `renovação`. The `TF-IDF` list includes some good externally dynamic cases such as `previdência`, `emenda`, `preço`, `saúde`, `salário`, and `partido`, but it also includes relatively flat cases such as `trabalhador`, `eleição`, and `real`. This makes the `TF-IDF` list look more like a mixture of issue salience, topical background frequency, and event response rather than a coherent “more movement externally means more drift internally” profile.

### 3. Do stable controls look flatter externally than drift candidates?

Only partially. The stable bucket contains genuinely flat Google cases such as `juridicidade`, `direito`, `recurso`, and `social`, but it also contains several externally dynamic terms such as `sincero`, `complicado`, `altíssimo`, `altivez`, and `público`. This is a key substantive warning: low internal drift in parliamentary discourse does not imply low public search volatility. Search interest can fluctuate for reasons unrelated to parliamentary semantic displacement, especially for generic adjectives and broad public words.

### 4. Are theory seeds externally more dynamic or more stable than expected?

They are mixed. `reforma` is one of the most externally dynamic terms in the whole 55-term panel, and `corrupção` is also fairly dynamic. `economia` is moderate-to-dynamic depending on the metric. `liberdade` is middling. `democracia` is comparatively flat. As a group, theory seeds are not clearly more dynamic than stable controls and are less volatile than the `Word2Vec` drift bucket on range-based measures. Methodologically, that means theory seeds are useful as substantive anchors, but not as a single coherent “high external movement” benchmark.

### 5. Is the relationship between internal drift and external Google movement strong, weak, mixed, or absent?

The best overall characterization is mixed and weak-to-moderate, not strong. There is some panel-level alignment for `Word2Vec`, little or no positive alignment for `TF-IDF`, and essentially no useful alignment for the contextual `BERT(-1)` scores in this setup. The external Google signal therefore does not function as a robust external validator of internal drift rankings. It functions more as a selective contextual resonance check.

### 6. What kinds of terms look well served by this external signal, and which do not?

The Google signal looks most informative for publicly salient issue terms and event-linked political vocabulary that plausibly produce broad national search attention. The clearest examples are `previdência`, `preço`, `saúde`, `salário`, `partido`, `reforma`, `corrupção`, and some election-cycle-adjacent terms.

The signal looks much less informative for at least four classes of terms. First, rhetorical or evaluative adjectives such as `inaceitável`, `perigoso`, and `excepcional` can show attention spikes, but those spikes do not necessarily diagnose the same phenomenon as parliamentary semantic drift. Second, generic or polysemous terms such as `real`, `alvo`, `público`, and `social` are too broad to map cleanly from lemma to public search intent. Third, legal-bureaucratic terms such as `juridicidade` and `orçamentária` may be too specialized or too low-volume to support stable public-search interpretation. Fourth, semantic-neighborhood shifts that matter inside parliamentary discourse may simply not surface as direct public-search behavior, as illustrated by `intervenção`, which is top-ranked by `Word2Vec` but comparatively flat in Google.

### 7. What methodological caveats matter if this is mentioned in the paper?

Several caveats matter enough to mention explicitly. The first is construct mismatch: Google Trends measures search interest, not lexical usage and not semantic displacement. The second is per-query normalization: because each term’s series is independently normalized to the requested time and geography, cross-term magnitude comparisons are only heuristic. The third is query semantics: this sandbox used raw query strings, not Google “topics,” so the returned signal reflects term matching in Google Trends rather than disambiguated conceptual tracking. Google’s own documentation notes that terms and topics behave differently, and that quoted versus unquoted queries also differ. The fourth is language and lemma mismatch: a Portuguese lemma in the frozen corpus is not the same thing as the set of public queries that Google will match for that term. The fifth is provider reliability: Oxylabs explicitly warns that `google_trends_explore` may differ from direct browser use. The sixth is geography interpretation: the sandbox notes and smoke tests already flagged `breakdown_by_region` as potentially not respecting the requested geography cleanly, so region outputs should not be trusted for validation. The seventh is temporal truncation: Google only permits `2004-01-01` onward, so the first four frozen yearly slices are outside the external window.

## Substantive Interpretation

Substantively, the Google layer supports a restrained story. It does not say that the frozen internal drift findings are wrong. It says that only some of them also resonate as broader public-attention cycles. The strongest externally dynamic cases tend to be terms that could plausibly become objects of national search attention. That is particularly true for politically salient reforms, crisis-linked public issues, and household-salience topics such as prices, wages, health, and pensions.

At the same time, the weakest matches are exactly the kinds of terms for which one would expect parliamentary discourse and public-search behavior to decouple: discourse-internal semantic repositioning, bureaucratic terminology, low-frequency formal words, and generic adjectives. That mismatch is not a failure of the frozen run. It is evidence that Google Trends is probing a different layer of social behavior.

## Recommended Paper Framing

If this external check is mentioned in the paper, it should be framed conservatively as a supplementary contextual probe rather than as external validation in the strong sense. The safest claim is that Google Trends offers limited external resonance for some politically salient lemmas, especially issue-centered terms, but does not provide a uniform benchmark for semantic drift in parliamentary language.

The paper should not imply that Google Trends adjudicates which drift detector is “correct.” The evidence here is too mixed for that. A more defensible claim is that externally normalized search-interest series align only selectively with the frozen panel, and that this selectivity itself is informative: it reinforces the interpretation that the internal methods are sensitive to different phenomena than public search attention.
