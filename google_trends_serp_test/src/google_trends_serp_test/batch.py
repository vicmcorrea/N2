"""Batch execution helpers for the isolated Oxylabs Google Trends test harness."""

from __future__ import annotations

import json
import time
from concurrent.futures import Future, ThreadPoolExecutor, as_completed
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pandas as pd

from google_trends_serp_test.client import Credentials, fetch_google_trends_payload
from google_trends_serp_test.normalize import build_section_frames
from google_trends_serp_test.terms import GroupedTerms, slugify_term


@dataclass(frozen=True)
class BatchConfig:
    """Configuration for a full multi-term Google Trends batch run."""

    query_markdown_path: str
    credentials_file: str
    date_from: str
    date_to: str
    geo_location: str
    max_workers: int
    pause_seconds: float


@dataclass(frozen=True)
class TermResult:
    """Compact result record for one batch term."""

    term: str
    slug: str
    status: str
    error: str | None
    interest_rows: int
    region_rows: int
    related_topics_rows: int
    related_queries_rows: int
    year_rows: int
    term_dir: str


def write_json(path: Path, payload: dict[str, Any]) -> None:
    """Write JSON with UTF-8 and stable indentation."""
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def derive_yearly_interest(interest_frame: pd.DataFrame) -> pd.DataFrame:
    """Derive a yearly series from the monthly/weekly Google Trends output."""
    if interest_frame.empty or "time" not in interest_frame or "value" not in interest_frame:
        return pd.DataFrame(columns=["year", "mean_value", "n_points", "keyword"])

    years = interest_frame["time"].astype(str).str.extract(r"(\d{4})")[0]
    yearly = interest_frame.assign(year=years)
    yearly = yearly.dropna(subset=["year"]).copy()
    if yearly.empty:
        return pd.DataFrame(columns=["year", "mean_value", "n_points", "keyword"])

    yearly["value"] = pd.to_numeric(yearly["value"], errors="coerce")
    grouped = (
        yearly.groupby(["year", "keyword"], as_index=False)
        .agg(mean_value=("value", "mean"), n_points=("value", "count"))
        .sort_values(["year", "keyword"])
    )
    grouped["year"] = grouped["year"].astype(int)
    return grouped


def persist_term_outputs(
    term_dir: Path,
    payload: dict[str, Any],
) -> tuple[dict[str, pd.DataFrame], pd.DataFrame]:
    """Persist raw and normalized artifacts for one term."""
    raw_dir = term_dir / "raw"
    normalized_dir = term_dir / "normalized"
    raw_dir.mkdir(parents=True, exist_ok=True)
    normalized_dir.mkdir(parents=True, exist_ok=True)

    write_json(raw_dir / "google_trends_payload.json", payload)

    frames = build_section_frames(payload)
    for name, frame in frames.items():
        frame.to_csv(normalized_dir / f"{name}.csv", index=False)

    yearly_interest = derive_yearly_interest(frames["interest_over_time"])
    yearly_interest.to_csv(normalized_dir / "interest_over_time_yearly.csv", index=False)
    return frames, yearly_interest


def run_single_term(
    credentials: Credentials,
    term: str,
    term_dir: Path,
    *,
    date_from: str,
    date_to: str,
    geo_location: str,
    pause_seconds: float,
) -> TermResult:
    """Run one term end-to-end and persist artifacts."""
    if pause_seconds > 0:
        time.sleep(pause_seconds)

    slug = term_dir.name
    try:
        payload = fetch_google_trends_payload(
            credentials,
            term,
            date_from=date_from,
            date_to=date_to,
            geo_location=geo_location,
        )
        frames, yearly_interest = persist_term_outputs(term_dir, payload)
        result = TermResult(
            term=term,
            slug=slug,
            status="ok",
            error=None,
            interest_rows=int(len(frames["interest_over_time"])),
            region_rows=int(len(frames["breakdown_by_region"])),
            related_topics_rows=int(len(frames["related_topics"])),
            related_queries_rows=int(len(frames["related_queries"])),
            year_rows=int(len(yearly_interest)),
            term_dir=str(term_dir),
        )
    except Exception as exc:  # noqa: BLE001
        error_payload = {"term": term, "error": repr(exc)}
        write_json(term_dir / "error.json", error_payload)
        result = TermResult(
            term=term,
            slug=slug,
            status="error",
            error=repr(exc),
            interest_rows=0,
            region_rows=0,
            related_topics_rows=0,
            related_queries_rows=0,
            year_rows=0,
            term_dir=str(term_dir),
        )

    write_json(term_dir / "summary.json", asdict(result))
    return result


def build_run_dir(output_root: Path) -> Path:
    """Create a fresh timestamped batch directory."""
    timestamp = datetime.now(tz=UTC).strftime("%Y%m%dT%H%M%SZ")
    run_dir = output_root / f"batch_{timestamp}"
    run_dir.mkdir(parents=True, exist_ok=True)
    return run_dir


def run_batch(
    grouped_terms: GroupedTerms,
    credentials: Credentials,
    output_root: Path,
    config: BatchConfig,
) -> Path:
    """Run the full batch and persist per-term and aggregated outputs."""
    run_dir = build_run_dir(output_root)
    terms_dir = run_dir / "terms"
    tables_dir = run_dir / "tables"
    terms_dir.mkdir(parents=True, exist_ok=True)
    tables_dir.mkdir(parents=True, exist_ok=True)

    write_json(run_dir / "manifest.json", asdict(config))

    membership_rows = [
        {"group": group, "term": term}
        for group, term in grouped_terms.memberships()
    ]
    pd.DataFrame(membership_rows).to_csv(tables_dir / "group_membership.csv", index=False)

    unique_terms = grouped_terms.unique_terms
    futures: dict[Future[TermResult], str] = {}
    results: list[TermResult] = []

    with ThreadPoolExecutor(max_workers=config.max_workers) as executor:
        for term in unique_terms:
            slug = slugify_term(term)
            term_dir = terms_dir / slug
            term_dir.mkdir(parents=True, exist_ok=True)
            future = executor.submit(
                run_single_term,
                credentials,
                term,
                term_dir,
                date_from=config.date_from,
                date_to=config.date_to,
                geo_location=config.geo_location,
                pause_seconds=config.pause_seconds,
            )
            futures[future] = term

        for future in as_completed(futures):
            results.append(future.result())

    results = sorted(results, key=lambda item: item.term)
    results_df = pd.DataFrame(asdict(item) for item in results)
    results_df.to_csv(tables_dir / "term_results.csv", index=False)

    failures_df = results_df[results_df["status"] != "ok"].copy()
    failures_df.to_csv(tables_dir / "failures.csv", index=False)

    yearly_frames: list[pd.DataFrame] = []
    for item in results:
        if item.status != "ok":
            continue
        yearly_path = Path(item.term_dir) / "normalized" / "interest_over_time_yearly.csv"
        if yearly_path.exists():
            frame = pd.read_csv(yearly_path)
            if not frame.empty:
                frame["term"] = item.term
                yearly_frames.append(frame)

    if yearly_frames:
        yearly_long = pd.concat(yearly_frames, ignore_index=True)
        yearly_long.to_csv(tables_dir / "yearly_interest_long.csv", index=False)
        yearly_wide = yearly_long.pivot(
            index="year",
            columns="term",
            values="mean_value",
        ).sort_index()
        yearly_wide.to_csv(tables_dir / "yearly_interest_wide.csv")
    else:
        pd.DataFrame().to_csv(tables_dir / "yearly_interest_long.csv", index=False)
        pd.DataFrame().to_csv(tables_dir / "yearly_interest_wide.csv", index=False)

    group_summary_rows: list[dict[str, Any]] = []
    result_lookup = {item.term: item for item in results}
    for group_name, terms in grouped_terms.groups.items():
        group_results = [result_lookup[term] for term in terms if term in result_lookup]
        total = len(group_results)
        ok_count = sum(1 for item in group_results if item.status == "ok")
        mean_year_rows = (
            sum(item.year_rows for item in group_results if item.status == "ok") / ok_count
            if ok_count
            else 0.0
        )
        group_summary_rows.append(
            {
                "group": group_name,
                "term_count": total,
                "ok_count": ok_count,
                "error_count": total - ok_count,
                "mean_year_rows_ok": mean_year_rows,
            }
        )
    pd.DataFrame(group_summary_rows).to_csv(tables_dir / "group_summary.csv", index=False)

    batch_summary = {
        "run_dir": str(run_dir),
        "total_terms": len(unique_terms),
        "ok_terms": int((results_df["status"] == "ok").sum()) if not results_df.empty else 0,
        "error_terms": int((results_df["status"] != "ok").sum()) if not results_df.empty else 0,
        "date_from": config.date_from,
        "date_to": config.date_to,
        "geo_location": config.geo_location,
        "max_workers": config.max_workers,
        "pause_seconds": config.pause_seconds,
    }
    write_json(run_dir / "summary.json", batch_summary)
    return run_dir
