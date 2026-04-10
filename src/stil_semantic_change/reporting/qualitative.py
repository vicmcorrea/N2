from __future__ import annotations

import hashlib
from collections.abc import Iterable, Sequence
from pathlib import Path

import pandas as pd

from stil_semantic_change.preprocessing.views import (
    prepared_content_tokens_dir,
    prepared_doc_metadata_dir,
)
from stil_semantic_change.utils.artifacts import read_json, write_dataframe


def collect_context_samples(
    run_root: Path,
    terms: Sequence[str] | None = None,
    per_term_per_phase: int = 2,
    context_window: int = 8,
    seed: int = 13,
) -> pd.DataFrame:
    prepared_root = run_root / "prepared"
    scores_root = run_root / "scores"
    candidate_sets = read_json(scores_root / "candidate_sets.json")

    slice_order: list[str] = candidate_sets["slice_order"]
    phases = {
        "early": [slice_order[0]],
        "late": [slice_order[-1]],
    }

    default_terms: list[str] = []
    for bucket in ("drift_candidates", "stable_controls", "theory_seeds"):
        default_terms.extend(candidate_sets.get(bucket, []))
    if terms is None:
        ordered_terms = tuple(dict.fromkeys(default_terms))
    else:
        ordered_terms = tuple(dict.fromkeys(terms))
    if not ordered_terms:
        raise ValueError("No terms were provided or inferred from candidate_sets.json")

    target_slices = {slice_id for ids in phases.values() for slice_id in ids}
    tokens_root = prepared_content_tokens_dir(prepared_root)
    occurrences = _load_occurrences(tokens_root, set(ordered_terms), target_slices)
    contexts: list[dict[str, object]] = []

    if occurrences.empty:
        return pd.DataFrame(
            columns=[
                "term",
                "phase",
                "slice_id",
                "doc_id",
                "date",
                "source_file",
                "token_index",
                "snippet",
            ]
        )

    sampled_docs: set[str] = set()
    for term in ordered_terms:
        for phase, slice_ids in phases.items():
            frame = occurrences[
                (occurrences["lemma"] == term) & occurrences["slice_id"].isin(slice_ids)
            ]
            if frame.empty:
                continue
            count = min(per_term_per_phase, len(frame))
            sub_seed = _term_phase_seed(term, phase, seed)
            if count == len(frame):
                sampled = frame.sort_values(["doc_id", "token_index"])
            else:
                sampled = frame.sample(n=count, random_state=sub_seed)
            sampled_docs.update(sampled["doc_id"].tolist())
            contexts.extend(
                {
                    "term": term,
                    "phase": phase,
                    "slice_id": row.slice_id,
                    "doc_id": row.doc_id,
                    "token_index": int(row.token_index),
                    "lemma": row.lemma,
                }
                for row in sampled.itertuples(index=False)
            )

    if not contexts:
        return pd.DataFrame(
            columns=[
                "term",
                "phase",
                "slice_id",
                "doc_id",
                "date",
                "source_file",
                "token_index",
                "snippet",
            ]
        )

    context_frame = (
        pd.DataFrame(contexts)
        .assign(token_index=lambda df: df["token_index"].astype(int))
        .sort_values(["term", "phase", "doc_id", "token_index"], ignore_index=True)
    )

    doc_tokens = _collect_doc_token_map(tokens_root, sampled_docs)
    doc_metadata = _collect_doc_metadata(prepared_doc_metadata_dir(prepared_root), sampled_docs)

    snippet_rows: list[dict[str, object]] = []
    for row in context_frame.itertuples(index=False):
        snippet = _build_snippet(
            doc_tokens,
            row.doc_id,
            row.token_index,
            context_window,
            row.lemma,
        )
        metadata = doc_metadata.get(row.doc_id, {})
        snippet_rows.append(
            {
                "term": row.term,
                "phase": row.phase,
                "slice_id": row.slice_id,
                "doc_id": row.doc_id,
                "date": metadata.get("date"),
                "source_file": metadata.get("source_file"),
                "token_index": row.token_index,
                "snippet": snippet,
            }
        )

    return pd.DataFrame(snippet_rows)


def write_context_reports(run_root: Path, contexts: pd.DataFrame) -> None:
    reports_root = run_root / "reports"
    reports_root.mkdir(parents=True, exist_ok=True)
    write_dataframe(reports_root / "qualitative_contexts.parquet", contexts)
    (reports_root / "qualitative_contexts.md").write_text(
        _format_markdown(contexts), encoding="utf-8"
    )


def _term_phase_seed(term: str, phase: str, base_seed: int) -> int:
    digest = hashlib.sha1(f"{term}:{phase}".encode()).hexdigest()
    return base_seed + int(digest[:8], 16)


def _load_occurrences(tokens_root: Path, lemmas: set[str], slices: set[str]) -> pd.DataFrame:
    columns = ["doc_id", "slice_id", "lemma", "token_index", "token"]
    frames: list[pd.DataFrame] = []
    for path in sorted(tokens_root.glob("*.parquet")):
        frame = pd.read_parquet(path, columns=columns)
        filtered = frame[
            frame["lemma"].isin(lemmas) & frame["slice_id"].isin(slices)
        ]
        if not filtered.empty:
            frames.append(filtered)
    if not frames:
        return pd.DataFrame(columns=columns)
    return pd.concat(frames, ignore_index=True)


def _collect_doc_token_map(tokens_root: Path, doc_ids: Iterable[str]) -> dict[str, pd.DataFrame]:
    needed = set(doc_ids)
    columns = ["doc_id", "token_index", "token"]
    doc_map: dict[str, pd.DataFrame] = {}
    for path in sorted(tokens_root.glob("*.parquet")):
        frame = pd.read_parquet(path, columns=columns)
        subset = frame.loc[frame["doc_id"].isin(needed)]
        if subset.empty:
            continue
        for doc_id, group in subset.groupby("doc_id"):
            existing = doc_map.get(doc_id)
            ordered = group.sort_values("token_index")
            doc_map[doc_id] = (
                pd.concat([existing, ordered], ignore_index=True)
                .drop_duplicates(subset=["token_index"], keep="first")
                .sort_values("token_index")
            )
    return doc_map


def _collect_doc_metadata(docs_root: Path, doc_ids: Iterable[str]) -> dict[str, dict[str, object]]:
    needed = set(doc_ids)
    columns = ["doc_id", "date", "source_file"]
    meta: dict[str, dict[str, object]] = {}
    for path in sorted(docs_root.glob("*.parquet")):
        frame = pd.read_parquet(path, columns=columns)
        subset = frame.loc[frame["doc_id"].isin(needed)]
        if subset.empty:
            continue
        for row in subset.itertuples(index=False):
            meta[str(row.doc_id)] = {"date": row.date, "source_file": row.source_file}
    return meta


def _build_snippet(
    doc_tokens: dict[str, pd.DataFrame],
    doc_id: str,
    token_index: int,
    window: int,
    lemma: str,
) -> str:
    tokens_frame = doc_tokens.get(doc_id)
    if tokens_frame is None:
        return ""
    lower = token_index - window
    upper = token_index + window
    slice_frame = tokens_frame.loc[
        tokens_frame["token_index"].between(lower, upper)
    ]
    tokens = slice_frame["token"].tolist()
    highlighted = [
        f"**{token}**" if token == lemma else token for token in tokens
    ]
    return " ".join(highlighted).strip()


def _format_markdown(contexts: pd.DataFrame) -> str:
    lines = ["# Qualitative Context Packet", ""]
    if contexts.empty:
        lines.append("No contexts were found for the selected terms.")
        return "\n".join(lines)

    for term in contexts["term"].unique():
        lines.append(f"## {term}")
        term_group = contexts.loc[contexts["term"] == term]
        for phase in ("early", "late"):
            phase_group = term_group.loc[term_group["phase"] == phase]
            if phase_group.empty:
                continue
            lines.append(f"### {phase.title()} slice")
            for row in phase_group.itertuples(index=False):
                lines.append(
                    f"- Slice {row.slice_id}, doc {row.doc_id} ({row.date or 'unknown'})"
                    f"{' from ' + row.source_file if row.source_file else ''}: {row.snippet}"
                )
        lines.append("")
    return "\n".join(lines).strip()
