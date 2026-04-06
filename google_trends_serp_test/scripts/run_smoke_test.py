"""Run a contained end-to-end smoke test against the Oxylabs Google Trends API."""

from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from google_trends_serp_test.client import fetch_google_trends_payload, load_credentials
from google_trends_serp_test.normalize import build_section_frames


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser for the smoke test."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--query", default="democracia")
    parser.add_argument("--date-from")
    parser.add_argument("--date-to")
    parser.add_argument("--geo-location")
    parser.add_argument(
        "--credentials-file",
        type=Path,
        default=Path("../how-to-scrape-google-trends/SERP-API-CREDENTIALS.txt"),
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=Path("outputs"),
    )
    return parser


def write_json(path: Path, payload: dict[str, Any]) -> None:
    """Write JSON with UTF-8 and stable indentation."""
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> None:
    """Execute the smoke test and persist a compact artifact bundle."""
    args = build_parser().parse_args()
    credentials = load_credentials(args.credentials_file)

    timestamp = datetime.now(tz=UTC).strftime("%Y%m%dT%H%M%SZ")
    run_dir = args.output_root / f"smoke_{timestamp}_{args.query}"
    raw_dir = run_dir / "raw"
    normalized_dir = run_dir / "normalized"
    raw_dir.mkdir(parents=True, exist_ok=True)
    normalized_dir.mkdir(parents=True, exist_ok=True)

    payload = fetch_google_trends_payload(
        credentials,
        args.query,
        date_from=args.date_from,
        date_to=args.date_to,
        geo_location=args.geo_location,
    )
    write_json(raw_dir / "google_trends_payload.json", payload)

    frames = build_section_frames(payload)
    for name, frame in frames.items():
        frame.to_csv(normalized_dir / f"{name}.csv", index=False)

    summary = {
        "query": args.query,
        "credentials_file": str(args.credentials_file),
        "run_dir": str(run_dir),
        "date_from": args.date_from,
        "date_to": args.date_to,
        "geo_location": args.geo_location,
        "sections_present": sorted(payload.keys()),
        "row_counts": {name: int(len(frame)) for name, frame in frames.items()},
        "works_like_repo_method": all(
            key in payload
            for key in (
                "interest_over_time",
                "breakdown_by_region",
                "related_topics",
                "related_queries",
            )
        ),
    }
    write_json(run_dir / "summary.json", summary)

    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
