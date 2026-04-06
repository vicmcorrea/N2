"""Client helpers for the isolated Oxylabs Google Trends smoke test."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import requests

OXYLABS_URL = "https://realtime.oxylabs.io/v1/queries"
GOOGLE_TRENDS_SOURCE = "google_trends_explore"


@dataclass(frozen=True)
class Credentials:
    """Basic-auth credentials loaded from the local text file."""

    username: str
    password: str


def load_credentials(credentials_path: Path) -> Credentials:
    """Load Oxylabs credentials from the user-provided text file."""
    text = credentials_path.read_text(encoding="utf-8")
    username_match = re.search(r"^username\s*=\s*(.+)$", text, re.MULTILINE)
    password_match = re.search(r"^password\s*=\s*(.+)$", text, re.MULTILINE)
    if username_match is None or password_match is None:
        raise ValueError(f"Could not parse username/password from {credentials_path}")

    return Credentials(
        username=username_match.group(1).strip(),
        password=password_match.group(1).strip(),
    )


def fetch_google_trends_payload(
    credentials: Credentials,
    query: str,
    *,
    date_from: str | None = None,
    date_to: str | None = None,
    geo_location: str | None = None,
    timeout_seconds: int = 180,
) -> dict[str, Any]:
    """Fetch raw Google Trends data using the same source as the cloned repo."""
    context: list[dict[str, str]] = []
    if date_from is not None:
        context.append({"key": "date_from", "value": date_from})
    if date_to is not None:
        context.append({"key": "date_to", "value": date_to})
    if geo_location is not None:
        context.append({"key": "geo_location", "value": geo_location})

    payload: dict[str, Any] = {
        "source": GOOGLE_TRENDS_SOURCE,
        "query": query,
    }
    if context:
        payload["context"] = context

    response = requests.post(
        OXYLABS_URL,
        auth=(credentials.username, credentials.password),
        json=payload,
        timeout=timeout_seconds,
    )
    response.raise_for_status()

    data = response.json()
    content = data["results"][0]["content"]
    return json.loads(content)
