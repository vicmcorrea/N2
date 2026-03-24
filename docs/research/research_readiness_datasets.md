# Dataset Research Readiness

## Scope

This note compares the two main datasets now organized under `RawDatasets`:

- `BrPoliCorpus-Dataset`
- `Roda-Viva-Dataset`

The goal is to decide which dataset setup is best for the current N2 paper, now framed as an exploratory comparison of drift techniques in Brazilian Portuguese political discourse, and at what temporal granularity each dataset is realistically usable.

## Executive Recommendation

### Best main corpus

Use **BrPoliCorpus floor speeches** as the main corpus.

Why:

- largest usable text volume
- exact date coverage
- strongest year-to-year continuity
- best support for month / quarter / semester / year slicing
- cleanest path to a paper about drift signals in Brazilian Portuguese political discourse

### Best complementary corpus

Use **Roda Viva V0-2** as a complementary corpus, not the only main corpus.

Why:

- interview discourse is richer and more dialogic
- exact date coverage from 1986 to 2009
- useful for qualitative case studies and limited cross-corpus robustness
- smaller than BrPoliCorpus, but still strong enough for targeted comparisons

### Best supporting slice inside BrPoliCorpus

Use **inaugural speeches** only as a historical contrast set, not as the paper core.

Why:

- excellent historical range
- very small number of texts
- better for qualitative examples than for stable year-by-year comparison

## Current Interpretation

Under the current paper framing:

- `BrPoliCorpus floor` should remain the main comparison panel
- `Roda Viva` should remain separate and complementary
- the dataset argument is now about methodological comparison and interpretability, not about proving one gold-standard semantic-change benchmark

## Current Corpus Picture

### BrPoliCorpus

Inventory source:

- `RawDatasets/BrPoliCorpus-Dataset/inventory/`

Useful inventory files:

- `inventory_file_level.csv`
- `inventory_summary_by_category.csv`
- `inventory_year_coverage_by_category.csv`
- `inventory_month_coverage_by_category.csv`
- `inventory_quarter_coverage_by_category.csv`
- `inventory_semester_coverage_by_category.csv`

High-level totals from the inventory:

- 198 CSV files
- 507,213 rows
- 238,457,788 words
- 1,475,601,025 characters

Main subcorpora:

- `floor`
  - 91 files
  - 428,445 rows
  - 184,115,811 words
  - exact dates from `2000-10-10` to `2023-12-21`
- `committees`
  - 16 files
  - 2,577 rows
  - 44,668,908 words
  - exact dates from `2019-02-12` to `2022-12-06`
- `cpi`
  - 3 files
  - 75,182 rows
  - 3,767,972 words
  - exact dates only in 2021
- `programmes`
  - 81 files
  - 590 rows
  - 5,829,214 words
  - only yearly dates (`2014`, `2018`, `2022`)
- `inaugural`
  - 1 file
  - 35 rows
  - 75,883 words
  - exact dates from `1889-11-15` to `2023-01-01`

### Roda Viva

Inventory source:

- `RawDatasets/Roda-Viva-Dataset/inventory/`

Useful inventory files:

- `interview_file_level.csv`
- `inventory_summary_by_primary_category.csv`
- `inventory_summary_by_theme.csv`
- `inventory_year_coverage_overall.csv`
- `inventory_month_coverage_overall.csv`
- `inventory_quarter_coverage_overall.csv`
- `inventory_semester_coverage_overall.csv`

Canonical transcript layer:

- `exports/V0-2/csv`

High-level totals from the inventory:

- 713 interviews
- 172,780 utterance rows
- 9,035,738 words
- 52,438,103 characters
- exact dates from `1986-01-01` to `2009-10-19`

Primary-category breakdown:

- `política`
  - 261 interviews
  - 3,313,475 words
  - 36.67% of words
- `cultura`
  - 218 interviews
  - 2,746,641 words
  - 30.40% of words
- `economia`
  - 108 interviews
  - 1,397,562 words
  - 15.47% of words
- `ciências`
  - 89 interviews
  - 1,058,011 words
  - 11.71% of words
- `esporte`
  - 31 interviews
  - 447,218 words
  - 4.95% of words

## Comparison

### BrPoliCorpus advantages

- Much larger text volume.
- Much stronger support for statistically stable semantic change experiments.
- Better for political vocabulary drift because the discourse domain is more consistent.
- `floor` alone covers 2000-2023 with exact dates and very large yearly volumes.
- Better for fine temporal slicing such as semester, quarter, and month.

### BrPoliCorpus weaknesses

- Mixed subcorpora are not equally useful.
- `committees` is text-rich but time-narrow.
- `cpi` is intense but confined to 2021.
- `programmes` are only election snapshots, not continuous time.
- Genres differ, so corpora should not be merged carelessly.

### Roda Viva advantages

- Exact dates at interview level.
- Dialogic language with rich contextual usage.
- Stronger qualitative interpretability for word meaning in interaction.
- Has topic/category labels.
- Good complement for checking whether drift patterns are corpus-specific or more general.

### Roda Viva weaknesses

- Much smaller than BrPoliCorpus.
- The discourse domain is broader and more heterogeneous.
- The category mix changes over time.
- Many years have modest interview counts, so monthly or quarterly modeling may get sparse fast.

## Recommended Temporal Granularity

### BrPoliCorpus floor

Recommended:

- yearly
- semester
- quarter

Conditionally usable:

- monthly, if restricted to frequent terms or broader bins around events

Not recommended as the only setup:

- daily

Why:

- date coverage is exact and continuous
- yearly volumes are very strong
- quarter and semester should still be dense enough for many vocabulary-level studies
- monthly is possible, but term sparsity must be checked carefully

### BrPoliCorpus committees

Recommended:

- yearly
- semester

Conditionally usable:

- quarter

Not ideal:

- monthly for broad semantic analyses

Why:

- exact dates exist, but the range is only 2019-2022
- texts are extremely long, but there are relatively few rows

### BrPoliCorpus cpi

Recommended:

- month
- quarter

Not useful for long-range semantic change:

- yearly drift across many years

Why:

- all material is in 2021
- better for short-horizon topic/usage dynamics than diachronic change

### BrPoliCorpus programmes

Recommended:

- yearly election-cycle comparison only

Not available:

- semester
- quarter
- month

Why:

- only `Ano` is available
- best treated as snapshots for 2014 / 2018 / 2022

### BrPoliCorpus inaugural

Recommended:

- very long-range historical comparison

Not recommended for main modeling:

- dense year-by-year estimation

Why:

- exact dates exist
- only 35 speeches total

### Roda Viva

Recommended:

- yearly

Conditionally usable:

- semester

Use carefully:

- quarter

Usually too sparse for main analysis:

- month

Why:

- exact dates are excellent
- but interview counts per month are much smaller than in BrPoliCorpus floor
- yearly analysis is safe
- semester may work if terms are common
- quarter or month is better for descriptive coverage or selected case studies, not the main full-corpus experiment

## Best Paper Designs

### Best design

Main corpus:

- BrPoliCorpus `floor`

Support corpora:

- Roda Viva `V0-2`
- BrPoliCorpus `inaugural` for historical examples

Temporal setup:

- main results at yearly or semester level
- robustness checks at quarter level for frequent terms only

Narrative:

- semantic change of political vocabulary in Brazilian Portuguese
- compare institutional parliamentary discourse with interview discourse

### Second-best design

Main corpus:

- Roda Viva

Support corpus:

- BrPoliCorpus floor

Temporal setup:

- yearly only

When to choose this:

- if you want a more interview-centered and linguistically interpretable story
- if you want qualitative case studies to carry more of the paper

## Risks To Control

### Genre effects

Do not pool all corpora into one raw timeline.

Instead:

- compute semantic change inside each corpus separately
- compare resulting drift patterns across corpora

### Sparse time bins

Before monthly or quarterly experiments, require:

- minimum number of documents per bin
- minimum term frequency per bin
- minimum total token volume per bin

### Category imbalance in Roda Viva

Roda Viva is not only political discourse. If you want a political-only subset:

- filter by primary category `política`
- optionally add interviews with multi-label `política`

## Concrete Recommendation For STIL

If the goal is the strongest and safest conference paper:

1. Main experiments on `BrPoliCorpus floor`
2. Yearly bins as default
3. Semester bins as the first finer-grained robustness check
4. Use `Roda Viva` for cross-corpus qualitative validation
5. Use `inaugural` speeches only for historical contrast examples

If the goal is the most elegant linguistic story:

1. Main experiments on `Roda Viva`
2. Yearly bins only
3. Use `BrPoliCorpus floor` as external validation that the drift is not corpus-specific

## Files To Use

For BrPoliCorpus:

- `RawDatasets/BrPoliCorpus-Dataset/exports/`
- `RawDatasets/BrPoliCorpus-Dataset/inventory/`

For Roda Viva:

- `RawDatasets/Roda-Viva-Dataset/exports/V0-2/csv`
- `RawDatasets/Roda-Viva-Dataset/exports/Metadata`
- `RawDatasets/Roda-Viva-Dataset/inventory/`
