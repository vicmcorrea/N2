from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from stil_semantic_change.utils.artifacts import (
    read_dataframe,
    read_json,
    write_json,
)
from stil_semantic_change.utils.config.schema import ExperimentConfig


@dataclass(frozen=True)
class ReadinessMetrics:
    coverage_doc_ratio: float
    coverage_token_ratio: float
    eligible_lemmas: int
    drift_candidate_count: int
    top_presence_avg: float
    top_frequency_median: int
    drift_mean: float
    stable_mean: float
    drift_delta: float
    anchor_mean: float | None
    anchor_min: int | None
    anchor_max: int | None
    slice_count: int
    total_documents: int
    total_tokens: int


def evaluate_run(run_root: Path, cfg: ExperimentConfig | None = None) -> dict[str, Any]:
    prepared_root = run_root / "prepared"
    aligned_root = run_root / "aligned"
    scores_root = run_root / "scores"

    slice_summary = read_dataframe(prepared_root / "slice_summary.parquet")
    slice_summary = slice_summary.sort_values("sort_key")
    doc_counts = slice_summary["document_count"].astype(float)
    token_counts = slice_summary["token_count"].astype(float)

    coverage_doc_ratio = _safe_ratio(doc_counts.min(), doc_counts.max())
    coverage_token_ratio = _safe_ratio(token_counts.min(), token_counts.max())

    eligible_vocab = read_dataframe(scores_root / "eligible_vocabulary.parquet")
    summary = read_dataframe(scores_root / "scores_aggregated.parquet")
    candidate_sets = read_json(scores_root / "candidate_sets.json")

    eligible_count = int(
        eligible_vocab["eligible"].fillna(False).sum()
        if "eligible" in eligible_vocab.columns
        else len(eligible_vocab)
    )

    drift_candidates = candidate_sets.get("drift_candidates", [])
    stable_controls = candidate_sets.get("stable_controls", [])

    top_candidates = summary.loc[summary["lemma"].isin(drift_candidates)].copy()
    top_presence_avg = (
        float(top_candidates["slice_presence_ratio"].mean()) if not top_candidates.empty else 0.0
    )
    top_frequency_median = (
        int(top_candidates["total_frequency"].median()) if not top_candidates.empty else 0
    )
    drift_mean = (
        float(top_candidates["primary_drift_mean"].mean()) if not top_candidates.empty else 0.0
    )

    stable_frame = summary.loc[summary["lemma"].isin(stable_controls)].copy()
    stable_mean = (
        float(stable_frame["primary_drift_mean"].mean()) if not stable_frame.empty else 0.0
    )
    drift_delta = drift_mean - stable_mean

    anchor_stats = _compute_anchor_stats(aligned_root)

    metrics = ReadinessMetrics(
        coverage_doc_ratio=coverage_doc_ratio,
        coverage_token_ratio=coverage_token_ratio,
        eligible_lemmas=eligible_count,
        drift_candidate_count=len(drift_candidates),
        top_presence_avg=round(top_presence_avg, 4),
        top_frequency_median=top_frequency_median,
        drift_mean=round(drift_mean, 4),
        stable_mean=round(stable_mean, 4),
        drift_delta=round(drift_delta, 4),
        anchor_mean=anchor_stats["mean"],
        anchor_min=anchor_stats["min"],
        anchor_max=anchor_stats["max"],
        slice_count=len(slice_summary),
        total_documents=int(slice_summary["document_count"].sum()),
        total_tokens=int(slice_summary["token_count"].sum()),
    )

    status, reasons = _determine_status(metrics)
    result = {
        "status": status,
        "reasons": reasons,
        "metrics": asdict(metrics),
        "metadata": {
            "dataset": cfg.dataset.name if cfg else run_root.name,
            "run_root": str(run_root),
        },
    }
    return result


def write_readiness_reports(run_root: Path, result: dict[str, Any]) -> None:
    reports_root = run_root / "reports"
    reports_root.mkdir(parents=True, exist_ok=True)
    write_json(reports_root / "stil_readiness.json", result)
    (reports_root / "stil_readiness.md").write_text(_format_markdown(result), encoding="utf-8")


def _compute_anchor_stats(aligned_root: Path) -> dict[str, Any]:
    anchor_path = aligned_root / "anchor_summary.parquet"
    if not anchor_path.exists():
        return {"mean": None, "min": None, "max": None}
    anchors = read_dataframe(anchor_path)
    counts = anchors["anchor_count"].astype(int)
    return {"mean": int(counts.mean()), "min": int(counts.min()), "max": int(counts.max())}


def _safe_ratio(numerator: float, denominator: float) -> float:
    if denominator == 0:
        return 0.0
    return float(numerator / denominator)


def _determine_status(metrics: ReadinessMetrics) -> tuple[str, list[str]]:
    reasons: list[str] = []
    score = 0

    if metrics.coverage_doc_ratio >= 0.35:
        score += 1
    else:
        reasons.append(
            "Late or early slices are much thinner than the median, so coverage is uneven."
        )

    if metrics.top_presence_avg >= 0.75:
        score += 1
    else:
        reasons.append("Top drift candidates do not appear consistently across enough slices.")

    if metrics.drift_delta >= 0.015:
        score += 1
    else:
        reasons.append("Drift candidates are not separating cleanly from stable controls yet.")

    if metrics.drift_candidate_count >= 8:
        score += 1
    else:
        reasons.append("Too few drift candidates survived the filters to make a strong story.")

    if metrics.eligible_lemmas >= 1000:
        score += 1
    else:
        reasons.append(
            "The eligible vocabulary is limited, which may mean the filtering thresholds "
            "are too strict."
        )

    if metrics.anchor_mean is not None and metrics.anchor_mean >= 300:
        score += 1
    elif metrics.anchor_mean is not None:
        reasons.append(
            "The alignment anchor set is smaller than preferred, so Procrustes may be "
            "unstable."
        )

    if score >= 4:
        status = "ready"
    elif score >= 2:
        status = "promising_but_needs_iteration"
    else:
        status = "not_ready"
    return status, reasons


def _format_markdown(result: dict[str, Any]) -> str:
    metrics = result["metrics"]
    lines = [f"# STIL Readiness Report — {result['status'].replace('_', ' ').title()}", ""]
    lines.append("## Key Metrics")
    for key, value in metrics.items():
        lines.append(f"- **{key.replace('_', ' ').title()}**: {value}")
    lines.append("\n## Recommendation Reasons")
    if result["reasons"]:
        lines.extend(f"- {reason}" for reason in result["reasons"])
    else:
        lines.append("- No concerns flagged; the current run meets all heuristics.")
    return "\n".join(lines)
