# Test Results

## Verdict

The Oxylabs-based method used in `how-to-scrape-google-trends/` works at the
request and parsing level when valid credentials are supplied.

## What was tested

- exact endpoint used by the cloned repo
- exact source used by the cloned repo, `google_trends_explore`
- credentials loaded from `../how-to-scrape-google-trends/SERP-API-CREDENTIALS.txt`
- normalized CSV export for the four sections expected by the repo

## Key findings

1. The original `scraper.py` does not work as-is because it still contains
   placeholder credentials.
2. The same method works through the isolated harness and returns structured
   Google Trends data with these sections:
   - `interest_over_time`
   - `breakdown_by_region`
   - `related_topics`
   - `related_queries`
3. A default query such as `democracia` returns a weekly series over roughly the
   last 12 months.
4. When `date_from`, `date_to`, and `geo_location` are passed, the endpoint can
   return a longer historical series. In the smoke test with `2004-01-01` to
   `2023-12-31`, it returned 240 monthly points.
5. `related_topics` may legitimately come back empty for a query.
6. `breakdown_by_region` should be treated carefully. Even with
   `geo_location=BR`, the returned geography output did not look Brazil-only in
   the smoke test.

## Important caution

The official Oxylabs documentation for `google_trends_explore` warns that the
scraped data may not be fully accurate relative to direct Google Trends usage.

Official doc checked during this test

- `https://developers.oxylabs.io/scraping-solutions/web-scraper-api/targets/google/trends-explore`

## Useful runs

- `outputs/smoke_20260406T015746Z_democracia`
  - default request
  - 53 weekly `interest_over_time` rows
- `outputs/smoke_20260406T015920Z_democracia`
  - `date_from=2004-01-01`
  - `date_to=2023-12-31`
  - `geo_location=BR`
  - 240 monthly `interest_over_time` rows
