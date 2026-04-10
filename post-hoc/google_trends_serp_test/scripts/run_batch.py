"""Run the isolated Google Trends batch over the project term list."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from google_trends_serp_test.batch import BatchConfig, run_batch
from google_trends_serp_test.client import load_credentials
from google_trends_serp_test.terms import load_grouped_terms


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser for the batch runner."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--terms-markdown",
        type=Path,
        default=Path("../docs/google_trends_search_terms.md"),
    )
    parser.add_argument(
        "--credentials-file",
        type=Path,
        default=Path("../how-to-scrape-google-trends/SERP-API-CREDENTIALS.txt"),
    )
    parser.add_argument("--date-from", default="2004-01-01")
    parser.add_argument("--date-to", default="2023-12-31")
    parser.add_argument("--geo-location", default="BR")
    parser.add_argument("--max-workers", type=int, default=3)
    parser.add_argument("--pause-seconds", type=float, default=0.2)
    parser.add_argument("--output-root", type=Path, default=Path("outputs"))
    return parser


def main() -> None:
    """Execute the full isolated batch run."""
    args = build_parser().parse_args()
    grouped_terms = load_grouped_terms(args.terms_markdown)
    credentials = load_credentials(args.credentials_file)
    config = BatchConfig(
        query_markdown_path=str(args.terms_markdown),
        credentials_file=str(args.credentials_file),
        date_from=args.date_from,
        date_to=args.date_to,
        geo_location=args.geo_location,
        max_workers=args.max_workers,
        pause_seconds=args.pause_seconds,
    )
    run_dir = run_batch(grouped_terms, credentials, args.output_root, config)
    print(json.dumps({"run_dir": str(run_dir)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
