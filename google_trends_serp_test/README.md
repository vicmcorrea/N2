# Google Trends SERP Smoke Test

This is an isolated test harness to verify whether the approach in
`how-to-scrape-google-trends/` works with the provided Oxylabs SERP
credentials.

It is intentionally separated from the main STIL pipeline and frozen outputs.

## Layout

- `src/google_trends_serp_test/` contains the reusable test code
- `scripts/run_smoke_test.py` runs a minimal end-to-end check
- `outputs/` stores raw responses, parsed JSON, CSVs, and a summary
- `.venv/` is local to this test project

## What it checks

- reads credentials from `../how-to-scrape-google-trends/SERP-API-CREDENTIALS.txt`
- sends a request to `https://realtime.oxylabs.io/v1/queries`
- uses `source=google_trends_explore`, matching the cloned repo method
- validates that the response includes the expected Google Trends sections
- writes normalized artifacts for inspection

## Run

```bash
cd google_trends_serp_test
uv venv
uv sync
uv run python scripts/run_smoke_test.py --query democracia
```
