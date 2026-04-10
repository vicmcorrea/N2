"""Load and normalize grouped Google Trends terms from the project markdown file."""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class GroupedTerms:
    """Grouped search terms parsed from the markdown source file."""

    groups: dict[str, list[str]]

    @property
    def unique_terms(self) -> list[str]:
        """Return unique terms while preserving first-seen order."""
        seen: set[str] = set()
        ordered: list[str] = []
        for group_terms in self.groups.values():
            for term in group_terms:
                if term not in seen:
                    seen.add(term)
                    ordered.append(term)
        return ordered

    def memberships(self) -> list[tuple[str, str]]:
        """Return flat group membership rows."""
        rows: list[tuple[str, str]] = []
        for group_name, terms in self.groups.items():
            for term in terms:
                rows.append((group_name, term))
        return rows


def slugify_term(term: str) -> str:
    """Create a filesystem-safe slug while keeping term identity readable."""
    normalized = unicodedata.normalize("NFKD", term).encode("ascii", "ignore").decode("ascii")
    normalized = normalized.lower().strip()
    normalized = re.sub(r"[^a-z0-9]+", "-", normalized).strip("-")
    return normalized or "term"


def load_grouped_terms(markdown_path: Path) -> GroupedTerms:
    """Parse grouped search terms from the project markdown file."""
    text = markdown_path.read_text(encoding="utf-8")

    pattern = re.compile(
        r"^##\s+\d+\.\s+(?P<title>.+?)\n+```text\n(?P<body>.*?)```",
        re.MULTILINE | re.DOTALL,
    )

    groups: dict[str, list[str]] = {}
    for match in pattern.finditer(text):
        title = match.group("title").strip()
        body = match.group("body")
        terms = [line.strip() for line in body.splitlines() if line.strip()]
        groups[title] = terms

    if not groups:
        raise ValueError(f"No grouped terms found in {markdown_path}")

    return GroupedTerms(groups=groups)
