from __future__ import annotations

import logging
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from stil_semantic_change.utils.artifacts import read_json, write_dataframe, write_json
from stil_semantic_change.utils.config.schema import ExperimentConfig
from stil_semantic_change.word2vec.vector_store import load_vector_store, mean_vector_store

logger = logging.getLogger(__name__)


def _save_figure(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(path, dpi=300, bbox_inches="tight")
    plt.close()


def generate_reports(
    cfg: ExperimentConfig,
    prepared_root: Path,
    aligned_root: Path,
    scores_root: Path,
    reports_root: Path,
) -> None:
    sns.set_theme(style=cfg.report.figure_style)
    slice_summary = pd.read_parquet(prepared_root / "slice_summary.parquet").sort_values("sort_key")
    lemma_slice_stats = pd.read_parquet(prepared_root / "lemma_slice_stats.parquet")
    summary = pd.read_parquet(scores_root / "scores_aggregated.parquet")
    trajectory = pd.read_parquet(scores_root / "trajectory.parquet")
    candidate_sets = read_json(scores_root / "candidate_sets.json")

    _plot_coverage(slice_summary, cfg, reports_root / "coverage_by_slice.png")
    _plot_frequency_scatter(
        summary,
        candidate_sets,
        cfg,
        reports_root / "drift_vs_frequency_dispersion.png",
    )
    _plot_small_multiples(trajectory, candidate_sets, cfg, reports_root / "drift_trajectories.png")
    _plot_ranked_terms(summary, candidate_sets, reports_root / "ranked_candidate_overview.png")
    _plot_selected_term_heatmap(
        lemma_slice_stats,
        candidate_sets,
        reports_root / "selected_terms_slice_heatmap.png",
    )
    neighbors = _build_neighbor_report(
        aligned_root=aligned_root,
        slice_order=candidate_sets["slice_order"],
        candidate_sets=candidate_sets,
        cfg=cfg,
    )
    write_dataframe(reports_root / "nearest_neighbors_early_late.parquet", neighbors)
    _plot_neighbor_panels(neighbors, reports_root / "nearest_neighbors_early_late.png")
    candidate_summary = _build_candidate_summary(summary, candidate_sets)
    write_dataframe(reports_root / "candidate_summary.parquet", candidate_summary)
    _write_analysis_summary(
        slice_summary=slice_summary,
        summary=summary,
        candidate_sets=candidate_sets,
        reports_root=reports_root,
        scores_root=scores_root,
    )
    _plot_bert_comparison_if_available(
        scores_root=scores_root,
        candidate_sets=candidate_sets,
        output_path=reports_root / "bert_word2vec_comparison.png",
    )

    write_json(
        reports_root / "report_manifest.json",
        {
            "figures": [
                "coverage_by_slice.png",
                "drift_vs_frequency_dispersion.png",
                "drift_trajectories.png",
                "ranked_candidate_overview.png",
                "selected_terms_slice_heatmap.png",
                "nearest_neighbors_early_late.png",
                "bert_word2vec_comparison.png",
            ],
            "tables": [
                "nearest_neighbors_early_late.parquet",
                "candidate_summary.parquet",
            ],
            "documents": [
                "analysis_summary.md",
            ],
        },
    )


def _plot_coverage(slice_summary: pd.DataFrame, cfg: ExperimentConfig, output_path: Path) -> None:
    fig, axis_left = plt.subplots(figsize=(14, 6))
    axis_right = axis_left.twinx()

    x = np.arange(len(slice_summary))
    axis_left.bar(
        x,
        slice_summary["document_count"],
        color=cfg.report.coverage_palette[0],
        alpha=0.9,
        label="Documents",
    )
    axis_right.plot(
        x,
        slice_summary["token_count"],
        color=cfg.report.coverage_palette[1],
        linewidth=2.5,
        marker="o",
        label="Tokens",
    )

    axis_left.set_xticks(x)
    axis_left.set_xticklabels(slice_summary["slice_id"], rotation=45, ha="right")
    axis_left.set_ylabel("Documents")
    axis_right.set_ylabel("Tokens")
    axis_left.set_title("Corpus Coverage By Time Slice")
    axis_left.grid(axis="y", alpha=0.25)
    _save_figure(output_path)


def _plot_frequency_scatter(
    summary: pd.DataFrame,
    candidate_sets: dict[str, object],
    cfg: ExperimentConfig,
    output_path: Path,
) -> None:
    fig, ax = plt.subplots(figsize=(12, 8))
    scatter = ax.scatter(
        np.log10(summary["total_frequency"] + 1),
        summary["primary_drift_mean"],
        c=summary["slice_presence_ratio"],
        s=50 + summary["mean_document_count"] * 2,
        cmap="viridis",
        alpha=0.75,
        edgecolors="white",
        linewidths=0.5,
    )
    plt.colorbar(scatter, ax=ax, label="Slice presence ratio")

    labels = set(candidate_sets["drift_candidates"][: cfg.report.label_top_n]) | set(
        candidate_sets["theory_seeds"]
    )
    label_frame = summary.loc[summary["lemma"].isin(labels)]
    for _, row in label_frame.iterrows():
        ax.annotate(
            row["lemma"],
            (np.log10(row["total_frequency"] + 1), row["primary_drift_mean"]),
            xytext=(4, 4),
            textcoords="offset points",
            fontsize=9,
        )

    ax.set_xlabel("log10(total frequency + 1)")
    ax.set_ylabel("Mean consecutive drift")
    ax.set_title("Drift vs Frequency and Dispersion")
    ax.grid(alpha=0.25)
    _save_figure(output_path)


def _plot_small_multiples(
    trajectory: pd.DataFrame,
    candidate_sets: dict[str, object],
    cfg: ExperimentConfig,
    output_path: Path,
) -> None:
    selected_terms: list[str] = []
    for term in candidate_sets["drift_candidates"] + candidate_sets["theory_seeds"]:
        if term not in selected_terms:
            selected_terms.append(term)
        if len(selected_terms) >= cfg.report.small_multiple_terms:
            break

    plot_frame = (
        trajectory.loc[trajectory["lemma"].isin(selected_terms)]
        .groupby(["lemma", "transition"])
        .agg(mean_drift=("drift", "mean"), std_drift=("drift", "std"))
        .reset_index()
    )
    if plot_frame.empty:
        return

    columns = 2
    rows = int(np.ceil(len(selected_terms) / columns))
    fig, axes = plt.subplots(rows, columns, figsize=(16, 4 * rows), squeeze=False)
    transitions = list(dict.fromkeys(plot_frame["transition"].tolist()))

    for axis, term in zip(axes.flat, selected_terms, strict=False):
        term_frame = plot_frame.loc[plot_frame["lemma"] == term].copy()
        term_frame["transition"] = pd.Categorical(
            term_frame["transition"],
            categories=transitions,
            ordered=True,
        )
        term_frame = term_frame.sort_values("transition")
        x = np.arange(len(term_frame))
        axis.plot(x, term_frame["mean_drift"], color="#1d3557", linewidth=2.0, marker="o")
        std = term_frame["std_drift"].fillna(0.0)
        axis.fill_between(
            x,
            term_frame["mean_drift"] - std,
            term_frame["mean_drift"] + std,
            color="#a8dadc",
            alpha=0.4,
        )
        axis.set_xticks(x)
        axis.set_xticklabels(term_frame["transition"], rotation=45, ha="right", fontsize=8)
        axis.set_title(term)
        axis.grid(alpha=0.2)

    for axis in axes.flat[len(selected_terms) :]:
        axis.axis("off")

    fig.suptitle("Drift Trajectories With Replicate Variability", fontsize=16, y=1.02)
    _save_figure(output_path)


def _build_candidate_summary(
    summary: pd.DataFrame,
    candidate_sets: dict[str, object],
) -> pd.DataFrame:
    selected_terms: list[tuple[str, str]] = []
    for bucket in ("drift_candidates", "stable_controls", "theory_seeds"):
        for term in candidate_sets.get(bucket, []):
            normalized = str(term)
            if normalized not in {item[0] for item in selected_terms}:
                selected_terms.append((normalized, bucket))

    selected_frame = summary.loc[summary["lemma"].isin([term for term, _ in selected_terms])].copy()
    bucket_map = dict(selected_terms)
    selected_frame["bucket"] = selected_frame["lemma"].map(bucket_map)
    return selected_frame.sort_values(["bucket", "primary_drift_mean"], ascending=[True, False])


def _plot_ranked_terms(
    summary: pd.DataFrame,
    candidate_sets: dict[str, object],
    output_path: Path,
) -> None:
    rows: list[pd.DataFrame] = []
    palettes = {
        "drift_candidate": "#e63946",
        "stable_control": "#457b9d",
        "theory_seed": "#2a9d8f",
    }
    for label, key in [
        ("drift_candidate", "drift_candidates"),
        ("stable_control", "stable_controls"),
        ("theory_seed", "theory_seeds"),
    ]:
        terms = [str(term) for term in candidate_sets.get(key, [])]
        if not terms:
            continue
        frame = summary.loc[summary["lemma"].isin(terms)].copy()
        frame["group"] = label
        rows.append(frame)

    if not rows:
        return

    plot_frame = pd.concat(rows, ignore_index=True)
    plot_frame = plot_frame.sort_values("primary_drift_mean", ascending=True)
    colors = [palettes[group] for group in plot_frame["group"]]

    fig, ax = plt.subplots(figsize=(12, max(6, len(plot_frame) * 0.45)))
    ax.barh(plot_frame["lemma"], plot_frame["primary_drift_mean"], color=colors, alpha=0.9)
    ax.set_xlabel("Mean consecutive drift")
    ax.set_ylabel("Lemma")
    ax.set_title("Selected Terms By Drift Score")
    ax.grid(axis="x", alpha=0.25)
    _save_figure(output_path)


def _plot_selected_term_heatmap(
    lemma_slice_stats: pd.DataFrame,
    candidate_sets: dict[str, object],
    output_path: Path,
) -> None:
    selected_terms: list[str] = []
    for key in ("drift_candidates", "stable_controls", "theory_seeds"):
        for term in candidate_sets.get(key, []):
            normalized = str(term)
            if normalized not in selected_terms:
                selected_terms.append(normalized)

    if not selected_terms:
        return

    plot_frame = lemma_slice_stats.loc[lemma_slice_stats["lemma"].isin(selected_terms)].copy()
    if plot_frame.empty:
        return

    pivot = plot_frame.pivot_table(
        index="lemma",
        columns="slice_id",
        values="frequency",
        aggfunc="sum",
        fill_value=0,
    )
    pivot = np.log10(pivot + 1)
    ordered_terms = [term for term in selected_terms if term in pivot.index]
    pivot = pivot.reindex(index=ordered_terms)
    pivot = pivot.loc[:, sorted(pivot.columns)]

    fig, ax = plt.subplots(figsize=(14, max(6, len(pivot) * 0.5)))
    sns.heatmap(pivot, cmap="mako", linewidths=0.2, linecolor="white", ax=ax)
    ax.set_title("Selected-Term Slice Coverage (log10 frequency + 1)")
    ax.set_xlabel("Slice")
    ax.set_ylabel("Lemma")
    _save_figure(output_path)


def _write_analysis_summary(
    slice_summary: pd.DataFrame,
    summary: pd.DataFrame,
    candidate_sets: dict[str, object],
    reports_root: Path,
    scores_root: Path,
) -> None:
    top_candidates = candidate_sets.get("drift_candidates", [])
    stable_controls = candidate_sets.get("stable_controls", [])
    seeds = candidate_sets.get("theory_seeds", [])
    selected_drift_frame = summary.loc[summary["lemma"].isin(top_candidates)].copy()
    selected_drift_frame = selected_drift_frame.sort_values(
        "primary_drift_mean",
        ascending=False,
    )

    top_frame = summary.head(15)[
        ["lemma", "primary_drift_mean", "slice_presence_ratio", "total_frequency"]
    ]
    lines = [
        "# Experiment Summary",
        "",
        f"- Slices: {len(slice_summary)}",
        f"- Total documents: {int(slice_summary['document_count'].sum())}",
        f"- Total cleaned tokens: {int(slice_summary['token_count'].sum())}",
        f"- Eligible lemmas scored: {int(len(summary))}",
        "",
        "## Drift Candidates",
        "",
    ]
    lines.extend(f"- {term}" for term in top_candidates)
    lines.extend(
        [
            "",
            "## Stable Controls",
            "",
        ]
    )
    lines.extend(f"- {term}" for term in stable_controls)
    lines.extend(
        [
            "",
            "## Theory Seeds Present",
            "",
        ]
    )
    lines.extend(f"- {term}" for term in seeds)
    lines.extend(
        [
            "",
            "## Selected Drift Candidate Panel",
            "",
            "| lemma | primary_drift_mean | slice_presence_ratio | total_frequency |",
            "| --- | ---: | ---: | ---: |",
        ]
    )
    lines.extend(
        f"| {row.lemma} | {row.primary_drift_mean:.4f} | "
        f"{row.slice_presence_ratio:.2f} | {int(row.total_frequency)} |"
        for row in selected_drift_frame.itertuples(index=False)
    )
    lines.extend(
        [
            "",
            "## Raw Top 15 By Word2Vec Drift (Before Candidate-Panel Filtering)",
            "",
            "| lemma | primary_drift_mean | slice_presence_ratio | total_frequency |",
            "| --- | ---: | ---: | ---: |",
        ]
    )
    lines.extend(
        f"| {row.lemma} | {row.primary_drift_mean:.4f} | "
        f"{row.slice_presence_ratio:.2f} | {int(row.total_frequency)} |"
        for row in top_frame.itertuples(index=False)
    )

    bert_path = scores_root / "bert_confirmatory" / "comparison_with_word2vec.parquet"
    if bert_path.exists():
        bert_frame = (
            pd.read_parquet(bert_path)
            .sort_values("primary_drift", ascending=False)
            .head(12)
        )
        lines.extend(
            [
                "",
                "## BERT Confirmatory Snapshot",
                "",
                "| layer | lemma | bert_primary_drift | word2vec_primary_drift | gap |",
                "| ---: | --- | ---: | ---: | ---: |",
            ]
        )
        lines.extend(
            f"| {int(row.layer)} | {row.lemma} | {row.primary_drift:.4f} | "
            f"{row.word2vec_primary_drift:.4f} | {row.bert_word2vec_gap:.4f} |"
            for row in bert_frame.itertuples(index=False)
        )

    (reports_root / "analysis_summary.md").write_text("\n".join(lines), encoding="utf-8")


def _plot_bert_comparison_if_available(
    scores_root: Path,
    candidate_sets: dict[str, object],
    output_path: Path,
) -> None:
    bert_path = scores_root / "bert_confirmatory" / "comparison_with_word2vec.parquet"
    if not bert_path.exists():
        return

    frame = pd.read_parquet(bert_path).copy()
    frame = frame.dropna(subset=["word2vec_primary_drift"])
    if frame.empty:
        return

    highlight_terms = {
        str(term)
        for key in ("drift_candidates", "stable_controls", "theory_seeds")
        for term in candidate_sets.get(key, [])
    }
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.scatterplot(
        data=frame,
        x="word2vec_primary_drift",
        y="primary_drift",
        hue="layer",
        style=frame["lemma"].isin(highlight_terms).map({True: "selected", False: "other"}),
        s=90,
        ax=ax,
    )
    for _, row in frame.loc[frame["lemma"].isin(highlight_terms)].iterrows():
        ax.annotate(
            row["lemma"],
            (row["word2vec_primary_drift"], row["primary_drift"]),
            xytext=(4, 4),
            textcoords="offset points",
            fontsize=8,
        )
    ax.set_xlabel("Word2Vec primary drift")
    ax.set_ylabel("BERT prototype drift")
    ax.set_title("Confirmatory BERT vs Word2Vec Drift")
    ax.grid(alpha=0.25)
    _save_figure(output_path)


def _build_neighbor_report(
    aligned_root: Path,
    slice_order: list[str],
    candidate_sets: dict[str, object],
    cfg: ExperimentConfig,
) -> pd.DataFrame:
    early_slice = slice_order[0]
    late_slice = slice_order[-1]
    replicate_dirs = sorted(
        path
        for path in aligned_root.iterdir()
        if path.is_dir() and path.name.startswith("replicate_")
    )
    early_store = mean_vector_store(
        [load_vector_store(path / early_slice / "vectors") for path in replicate_dirs]
    )
    late_store = mean_vector_store(
        [load_vector_store(path / late_slice / "vectors") for path in replicate_dirs]
    )

    selected_terms = candidate_sets["drift_candidates"][: cfg.report.neighbor_terms]
    rows: list[dict[str, object]] = []
    for term in selected_terms:
        for phase, store in [("early", early_store), ("late", late_store)]:
            index = store.word_to_index
            if term not in index:
                continue
            query_vector = store.matrix[index[term]]
            similarities = []
            for neighbor, neighbor_index in index.items():
                if neighbor == term:
                    continue
                vector = store.matrix[neighbor_index]
                denom = np.linalg.norm(query_vector) * np.linalg.norm(vector)
                similarity = 0.0 if denom == 0 else float(np.dot(query_vector, vector) / denom)
                similarities.append((neighbor, similarity))
            top_neighbors = sorted(
                similarities,
                key=lambda item: item[1],
                reverse=True,
            )[: cfg.selection.neighbor_k]
            for rank, (neighbor, similarity) in enumerate(top_neighbors, start=1):
                rows.append(
                    {
                        "term": term,
                        "phase": phase,
                        "slice_id": early_slice if phase == "early" else late_slice,
                        "rank": rank,
                        "neighbor": neighbor,
                        "similarity": similarity,
                    }
                )
    return pd.DataFrame(rows)


def _plot_neighbor_panels(neighbors: pd.DataFrame, output_path: Path) -> None:
    if neighbors.empty:
        return
    terms = list(dict.fromkeys(neighbors["term"].tolist()))
    fig, axes = plt.subplots(len(terms), 2, figsize=(14, 3.5 * len(terms)), squeeze=False)
    phase_titles = {"early": "Early slice neighbors", "late": "Late slice neighbors"}

    for row_idx, term in enumerate(terms):
        for col_idx, phase in enumerate(["early", "late"]):
            axis = axes[row_idx][col_idx]
            phase_frame = neighbors.loc[(neighbors["term"] == term) & (neighbors["phase"] == phase)]
            axis.axis("off")
            if phase_frame.empty:
                continue
            text = "\n".join(
                f"{int(rank)}. {neighbor} ({similarity:.3f})"
                for rank, neighbor, similarity in phase_frame[
                    ["rank", "neighbor", "similarity"]
                ].itertuples(index=False, name=None)
            )
            axis.text(
                0.0,
                1.0,
                f"{term}\n{phase_titles[phase]}\n\n{text}",
                va="top",
                ha="left",
                fontsize=11,
                family="monospace",
            )

    fig.suptitle("Early vs Late Nearest Neighbors", fontsize=16, y=1.02)
    _save_figure(output_path)
