# Notes

## Current State

This folder now reflects the current STIL preparation state after the dataset organization and inventory work.

The working direction is:

- semantic change in Brazilian Portuguese
- main corpus: `BrPoliCorpus floor`
- complementary corpus: `Roda Viva V0-2`

## Canonical Dataset Locations

### BrPoliCorpus

- data: `Articles/N2/RawDatasets/BrPoliCorpus-Dataset/exports`
- inventories: `Articles/N2/RawDatasets/BrPoliCorpus-Dataset/inventory`
- local scripts: `Articles/N2/RawDatasets/BrPoliCorpus-Dataset/scripts`

Key inventory files:

- `inventory_file_level.csv`
- `inventory_summary_by_category.csv`
- `inventory_year_coverage_by_category.csv`
- `inventory_month_coverage_by_category.csv`
- `inventory_quarter_coverage_by_category.csv`
- `inventory_semester_coverage_by_category.csv`

### Roda Viva

- data: `Articles/N2/RawDatasets/Roda-Viva-Dataset/exports`
- inventories: `Articles/N2/RawDatasets/Roda-Viva-Dataset/inventory`
- local scripts: `Articles/N2/RawDatasets/Roda-Viva-Dataset/scripts`

Key inventory files:

- `interview_file_level.csv`
- `inventory_summary_by_primary_category.csv`
- `inventory_summary_by_theme.csv`
- `inventory_year_coverage_overall.csv`
- `inventory_month_coverage_overall.csv`
- `inventory_quarter_coverage_overall.csv`
- `inventory_semester_coverage_overall.csv`

## Most Important Dataset Findings

### BrPoliCorpus

- `floor` is the strongest main corpus.
- `floor` supports exact-date slicing and has the best overall text volume.
- `committees` is useful but time-narrow.
- `cpi` is useful for short-horizon analysis, not long-range diachrony.
- `programmes` supports only yearly election-cycle comparisons.
- `inaugural` is best used as a small historical contrast set.

### Roda Viva

- `V0-2` is the canonical transcript layer for analysis.
- `713` interviews are available with exact dates.
- The corpus supports yearly analysis safely.
- Semester analysis may be usable.
- Monthly and quarterly analysis are better treated as descriptive or selective, not the main default.

## Practical Recommendation

Use:

1. `BrPoliCorpus floor` for the main results
2. yearly bins as the default
3. semester bins as the first robustness check
4. `Roda Viva V0-2` for complementary validation and qualitative examples

## Key Documents In This Folder

- `project_overview.md`
- `stil_plan_recommendation.md`
- `research_readiness_datasets.md`
- `word_selection_protocol.md`
