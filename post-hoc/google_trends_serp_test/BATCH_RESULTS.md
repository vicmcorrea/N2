# Batch Results

## Latest full run

- Run directory
  - `outputs/batch_20260406T020524Z`
- Terms requested
  - 55 unique terms
- Parameters
  - `date_from=2004-01-01`
  - `date_to=2023-12-31`
  - `geo_location=BR`
  - `max_workers=3`

## Outcome

- 55 terms succeeded
- 0 terms failed
- every term returned 240 monthly `interest_over_time` rows
- every term produced 20 yearly rows covering 2004 to 2023
- every term returned `related_queries`
- no term returned non-empty `related_topics` in this run

## Main artifacts

- batch summary
  - `outputs/batch_20260406T020524Z/summary.json`
- per-term status table
  - `outputs/batch_20260406T020524Z/tables/term_results.csv`
- group summary
  - `outputs/batch_20260406T020524Z/tables/group_summary.csv`
- yearly long table
  - `outputs/batch_20260406T020524Z/tables/yearly_interest_long.csv`
- yearly wide matrix
  - `outputs/batch_20260406T020524Z/tables/yearly_interest_wide.csv`

## Caution

- Oxylabs documents that `google_trends_explore` may differ from direct Google
  Trends browser output.
- `breakdown_by_region` should be interpreted carefully because earlier smoke
  tests suggested geography results may not strictly match the requested
  `geo_location`.
