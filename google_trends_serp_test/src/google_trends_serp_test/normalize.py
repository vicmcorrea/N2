"""Normalization helpers for the isolated Oxylabs Google Trends smoke test."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

import pandas as pd


def flatten_related_topics(topics_data: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Flatten the nested related-topics structure returned by the API."""
    flattened: list[dict[str, Any]] = []
    if not topics_data:
        return flattened

    for item in topics_data[0].get("items", []):
        topic = item.get("topic", {})
        flattened.append(
            {
                "mid": topic.get("mid"),
                "title": topic.get("title"),
                "type": topic.get("type"),
                "value": item.get("value"),
                "formatted_value": item.get("formatted_value"),
                "link": item.get("link"),
                "keyword": topics_data[0].get("keyword"),
            }
        )

    return flattened


def frame_or_empty(rows: Iterable[dict[str, Any]]) -> pd.DataFrame:
    """Create a dataframe even when a section is empty."""
    return pd.DataFrame(list(rows))


def build_section_frames(trend_data: dict[str, Any]) -> dict[str, pd.DataFrame]:
    """Normalize the main sections expected by the original scraper."""
    interest_series = trend_data.get("interest_over_time", [])
    region_series = trend_data.get("breakdown_by_region", [])
    related_topics = trend_data.get("related_topics", [])
    related_queries = trend_data.get("related_queries", [])

    iot_rows = interest_series[0].get("items", []) if interest_series else []
    bbr_rows = region_series[0].get("items", []) if region_series else []
    rq_rows = related_queries[0].get("items", []) if related_queries else []

    iot_df = frame_or_empty(iot_rows)
    if interest_series and not iot_df.empty:
        iot_df["keyword"] = interest_series[0].get("keyword")

    bbr_df = frame_or_empty(bbr_rows)
    if region_series and not bbr_df.empty:
        bbr_df["keyword"] = region_series[0].get("keyword")

    rt_df = frame_or_empty(flatten_related_topics(related_topics))

    rq_df = frame_or_empty(rq_rows)
    if related_queries and not rq_df.empty:
        rq_df["keyword"] = related_queries[0].get("keyword")

    return {
        "interest_over_time": iot_df,
        "breakdown_by_region": bbr_df,
        "related_topics": rt_df,
        "related_queries": rq_df,
    }
