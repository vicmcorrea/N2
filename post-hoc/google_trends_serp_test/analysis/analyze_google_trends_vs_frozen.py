#!/usr/bin/env python3
"""Analyze Google Trends signals against the frozen STIL comparison panel."""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import mannwhitneyu, pearsonr, spearmanr

ROOT = Path(__file__).resolve().parents[2]
FROZEN_RUN = ROOT / "run/outputs/experiments/brpolicorpus_floor_yearly/ba65fe5b9cce"
GOOGLE_BATCH = ROOT / "google_trends_serp_test/outputs/batch_20260406T020524Z"
ANALYSIS_DIR = ROOT / "google_trends_serp_test/analysis"

COLOR_MAP = {
    "word2vec_only_drift": "#1f77b4",
    "tfidf_only_drift": "#d55e00",
    "stable_control": "#6c757d",
    "theory_seed": "#2a9d8f",
}
LABEL_MAP = {
    "word2vec_only_drift": "Word2Vec drift",
    "tfidf_only_drift": "TF-IDF drift",
    "stable_control": "Stable controls",
    "theory_seed": "Theory seeds",
}
REPRESENTATIVE_TERMS = [
    "intervenção",
    "inédito",
    "trabalhador",
    "previdência",
    "juridicidade",
    "reforma",
]


@dataclass(frozen=True)
class Paths:
    """Project paths used by the analysis."""

    panel: Path = FROZEN_RUN / "scores/comparison_panel/comparison_panel.parquet"
    word2vec_scores: Path = FROZEN_RUN / "scores/scores_aggregated.parquet"
    word2vec_trajectory: Path = FROZEN_RUN / "scores/trajectory.parquet"
    tfidf_scores: Path = FROZEN_RUN / "scores/tfidf_drift/scores.parquet"
    tfidf_trajectory: Path = FROZEN_RUN / "scores/tfidf_drift/trajectory.parquet"
    bert_panel: Path = FROZEN_RUN / "scores/bert_confirmatory/comparison_with_word2vec.parquet"
    yearly_interest: Path = GOOGLE_BATCH / "tables/yearly_interest_long.csv"
    term_results: Path = GOOGLE_BATCH / "tables/term_results.csv"


def ensure_output_dirs() -> tuple[Path, Path]:
    """Create analysis subdirectories."""
    tables_dir = ANALYSIS_DIR / "tables"
    figures_dir = ANALYSIS_DIR / "figures"
    tables_dir.mkdir(parents=True, exist_ok=True)
    figures_dir.mkdir(parents=True, exist_ok=True)
    return tables_dir, figures_dir


def load_inputs(paths: Paths) -> dict[str, pd.DataFrame]:
    """Load all frozen and Google artifacts needed for the analysis."""
    return {
        "panel": pd.read_parquet(paths.panel),
        "word2vec_scores": pd.read_parquet(paths.word2vec_scores),
        "word2vec_trajectory": pd.read_parquet(paths.word2vec_trajectory),
        "tfidf_scores": pd.read_parquet(paths.tfidf_scores),
        "tfidf_trajectory": pd.read_parquet(paths.tfidf_trajectory),
        "bert_panel": pd.read_parquet(paths.bert_panel),
        "yearly_interest": pd.read_csv(paths.yearly_interest),
        "term_results": pd.read_csv(paths.term_results),
    }


def compute_google_features(yearly_interest: pd.DataFrame) -> pd.DataFrame:
    """Summarize yearly Google Trends movement for each term."""
    rows: list[dict[str, float | int | str]] = []
    for term, frame in yearly_interest.groupby("term", sort=True):
        ordered = frame.sort_values("year").copy()
        values = ordered["mean_value"].astype(float).to_numpy()
        deltas = np.diff(values)
        peak_idx = int(np.argmax(values))
        rows.append(
            {
                "lemma": term,
                "gt_year_min": int(ordered["year"].min()),
                "gt_year_max": int(ordered["year"].max()),
                "gt_mean": float(values.mean()),
                "gt_std": float(values.std(ddof=0)),
                "gt_range": float(values.max() - values.min()),
                "gt_min": float(values.min()),
                "gt_max": float(values.max()),
                "gt_nonzero_share": float((values > 0).mean()),
                "gt_mean_abs_change": float(np.abs(deltas).mean()),
                "gt_rmse_change": float(np.sqrt(np.mean(deltas**2))),
                "gt_net_change": float(values[-1] - values[0]),
                "gt_peak_year": int(ordered.iloc[peak_idx]["year"]),
                "gt_peak_value": float(values[peak_idx]),
            }
        )
    return pd.DataFrame(rows)


def build_panel_table(
    panel: pd.DataFrame,
    google_features: pd.DataFrame,
    term_results: pd.DataFrame,
) -> pd.DataFrame:
    """Join the shared panel to Google-derived features and batch metadata."""
    merged = panel.merge(google_features, on="lemma", how="left").merge(
        term_results[
            [
                "term",
                "related_queries_rows",
                "related_topics_rows",
                "region_rows",
                "interest_rows",
                "year_rows",
            ]
        ],
        left_on="lemma",
        right_on="term",
        how="left",
    )
    merged = merged.drop(columns=["term"])
    merged["bucket_label"] = merged["bucket"].map(LABEL_MAP)
    merged["is_any_drift_candidate"] = merged["bucket"].isin(
        ["word2vec_only_drift", "tfidf_only_drift"]
    )
    return merged.sort_values(["bucket", "lemma"]).reset_index(drop=True)


def cliffs_delta(left: pd.Series, right: pd.Series) -> float:
    """Compute Cliff's delta effect size."""
    left_values = left.to_numpy()
    right_values = right.to_numpy()
    greater = sum(x > y for x in left_values for y in right_values)
    lower = sum(x < y for x in left_values for y in right_values)
    return (greater - lower) / (len(left_values) * len(right_values))


def summarize_groups(panel_table: pd.DataFrame) -> pd.DataFrame:
    """Produce group-level descriptive statistics for external movement."""
    summary = (
        panel_table.groupby(["bucket", "bucket_label"], as_index=False)
        .agg(
            term_count=("lemma", "count"),
            mean_gt_mean_abs_change=("gt_mean_abs_change", "mean"),
            median_gt_mean_abs_change=("gt_mean_abs_change", "median"),
            mean_gt_std=("gt_std", "mean"),
            median_gt_std=("gt_std", "median"),
            mean_gt_range=("gt_range", "mean"),
            median_gt_range=("gt_range", "median"),
            mean_gt_nonzero_share=("gt_nonzero_share", "mean"),
        )
        .sort_values("bucket")
    )
    return summary


def summarize_tests(panel_table: pd.DataFrame) -> pd.DataFrame:
    """Run simple non-parametric comparisons between the main panel buckets."""
    comparisons = [
        ("word2vec_only_drift", "stable_control"),
        ("tfidf_only_drift", "stable_control"),
        ("word2vec_only_drift", "tfidf_only_drift"),
        ("theory_seed", "stable_control"),
        ("drift_any", "stable_control"),
    ]
    metrics = ["gt_mean_abs_change", "gt_std", "gt_range"]
    rows: list[dict[str, float | str]] = []

    for metric in metrics:
        for left_bucket, right_bucket in comparisons:
            if left_bucket == "drift_any":
                left = panel_table.loc[panel_table["is_any_drift_candidate"], metric]
                left_label = "Any drift candidate"
            else:
                left = panel_table.loc[panel_table["bucket"] == left_bucket, metric]
                left_label = LABEL_MAP[left_bucket]

            right = panel_table.loc[panel_table["bucket"] == right_bucket, metric]
            result = mannwhitneyu(left, right, alternative="two-sided")
            rows.append(
                {
                    "metric": metric,
                    "left_group": left_label,
                    "right_group": LABEL_MAP[right_bucket],
                    "left_median": float(left.median()),
                    "right_median": float(right.median()),
                    "left_mean": float(left.mean()),
                    "right_mean": float(right.mean()),
                    "u_statistic": float(result.statistic),
                    "p_value": float(result.pvalue),
                    "cliffs_delta": float(cliffs_delta(left, right)),
                }
            )

    return pd.DataFrame(rows)


def summarize_correlations(
    panel_table: pd.DataFrame,
    bert_panel: pd.DataFrame,
) -> pd.DataFrame:
    """Compute internal/external correlations for the main methods."""
    metric_pairs = [
        ("word2vec_primary_drift", "gt_mean_abs_change", "all_panel", "Word2Vec"),
        ("word2vec_primary_drift", "gt_std", "all_panel", "Word2Vec"),
        ("word2vec_primary_drift", "gt_range", "all_panel", "Word2Vec"),
        ("tfidf_primary_drift", "gt_mean_abs_change", "all_panel", "TF-IDF"),
        ("tfidf_primary_drift", "gt_std", "all_panel", "TF-IDF"),
        ("tfidf_primary_drift", "gt_range", "all_panel", "TF-IDF"),
    ]
    rows: list[dict[str, float | str]] = []

    for internal_metric, external_metric, subset_name, method_label in metric_pairs:
        subset = panel_table.copy()
        spearman = spearmanr(subset[internal_metric], subset[external_metric], nan_policy="omit")
        pearson = pearsonr(subset[internal_metric], subset[external_metric])
        rows.append(
            {
                "method": method_label,
                "subset": subset_name,
                "internal_metric": internal_metric,
                "external_metric": external_metric,
                "spearman_r": float(spearman.statistic),
                "spearman_p": float(spearman.pvalue),
                "pearson_r": float(pearson.statistic),
                "pearson_p": float(pearson.pvalue),
            }
        )

    drift_only = panel_table.loc[panel_table["is_any_drift_candidate"]].copy()
    for internal_metric, method_label in [
        ("word2vec_primary_drift", "Word2Vec"),
        ("tfidf_primary_drift", "TF-IDF"),
    ]:
        for external_metric in ["gt_mean_abs_change", "gt_std", "gt_range"]:
            spearman = spearmanr(
                drift_only[internal_metric],
                drift_only[external_metric],
                nan_policy="omit",
            )
            pearson = pearsonr(drift_only[internal_metric], drift_only[external_metric])
            rows.append(
                {
                    "method": method_label,
                    "subset": "drift_only",
                    "internal_metric": internal_metric,
                    "external_metric": external_metric,
                    "spearman_r": float(spearman.statistic),
                    "spearman_p": float(spearman.pvalue),
                    "pearson_r": float(pearson.statistic),
                    "pearson_p": float(pearson.pvalue),
                }
            )

    bert_joined = bert_panel.loc[bert_panel["layer"] == -1].merge(
        panel_table[["lemma", "gt_mean_abs_change", "gt_std", "gt_range"]],
        on="lemma",
        how="left",
    )
    for external_metric in ["gt_mean_abs_change", "gt_std", "gt_range"]:
        spearman = spearmanr(bert_joined["primary_drift"], bert_joined[external_metric])
        pearson = pearsonr(bert_joined["primary_drift"], bert_joined[external_metric])
        rows.append(
            {
                "method": "BERT(-1)",
                "subset": "all_panel",
                "internal_metric": "primary_drift",
                "external_metric": external_metric,
                "spearman_r": float(spearman.statistic),
                "spearman_p": float(spearman.pvalue),
                "pearson_r": float(pearson.statistic),
                "pearson_p": float(pearson.pvalue),
            }
        )

    return pd.DataFrame(rows)


def prepare_yearly_series(
    yearly_interest: pd.DataFrame,
    word2vec_trajectory: pd.DataFrame,
    tfidf_trajectory: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Prepare year-aligned Google, Word2Vec, and TF-IDF series."""
    google_yearly = yearly_interest.rename(columns={"term": "lemma"}).copy()
    google_yearly["series"] = "Google yearly interest"
    google_yearly["value"] = google_yearly["mean_value"].astype(float)
    google_yearly = google_yearly[["lemma", "year", "series", "value"]]

    w2v_yearly = (
        word2vec_trajectory.assign(year=lambda df: df["to_slice"].astype(int))
        .groupby(["lemma", "year"], as_index=False)
        .agg(value=("drift", "mean"))
    )
    w2v_yearly["series"] = "Word2Vec transition drift"

    tfidf_yearly = (
        tfidf_trajectory.assign(year=lambda df: df["to_slice"].astype(int))
        .groupby(["lemma", "year"], as_index=False)
        .agg(value=("drift", "mean"))
    )
    tfidf_yearly["series"] = "TF-IDF transition drift"
    return google_yearly, w2v_yearly, tfidf_yearly


def zscore_by_term(frame: pd.DataFrame) -> pd.DataFrame:
    """Z-score each series within lemma for legible overlays."""
    standardized = frame.copy()
    grouped = standardized.groupby(["lemma", "series"])["value"]
    means = grouped.transform("mean")
    spreads = grouped.transform(lambda values: float(values.std(ddof=0)))
    standardized["z_value"] = np.where(
        spreads == 0,
        0.0,
        (standardized["value"] - means) / spreads,
    )
    return standardized


def configure_plot_style() -> None:
    """Apply a simple publication-friendly matplotlib style."""
    plt.rcParams.update(
        {
            "font.family": "serif",
            "font.serif": ["DejaVu Serif", "Times New Roman"],
            "font.size": 10,
            "axes.titlesize": 11,
            "axes.labelsize": 10,
            "legend.fontsize": 8.5,
            "axes.grid": True,
            "grid.alpha": 0.18,
            "grid.linestyle": "-",
            "axes.spines.top": False,
            "axes.spines.right": False,
            "savefig.bbox": "tight",
            "figure.dpi": 300,
            "savefig.dpi": 300,
        }
    )


def slugify_term(term: str) -> str:
    """Create a filesystem-safe slug for a panel lemma."""
    normalized = unicodedata.normalize("NFKD", term).encode("ascii", "ignore").decode("ascii")
    normalized = normalized.lower().strip()
    normalized = re.sub(r"[^a-z0-9]+", "-", normalized).strip("-")
    return normalized or "term"


def plot_bucket_external_movement(panel_table: pd.DataFrame, figures_dir: Path) -> None:
    """Plot Google external movement by shared-panel bucket."""
    configure_plot_style()
    order = ["word2vec_only_drift", "tfidf_only_drift", "stable_control", "theory_seed"]
    positions = np.arange(len(order))
    fig, ax = plt.subplots(figsize=(7.0, 3.3))

    for idx, bucket in enumerate(order):
        values = panel_table.loc[panel_table["bucket"] == bucket, "gt_mean_abs_change"].to_numpy()
        ax.boxplot(
            values,
            positions=[idx],
            widths=0.5,
            patch_artist=True,
            boxprops={"facecolor": "#ffffff", "edgecolor": COLOR_MAP[bucket], "linewidth": 1.3},
            medianprops={"color": COLOR_MAP[bucket], "linewidth": 1.5},
            whiskerprops={"color": COLOR_MAP[bucket], "linewidth": 1.1},
            capprops={"color": COLOR_MAP[bucket], "linewidth": 1.1},
        )
        jitter = np.linspace(-0.13, 0.13, len(values))
        ax.scatter(
            np.full(len(values), idx) + jitter,
            values,
            s=28,
            color=COLOR_MAP[bucket],
            alpha=0.8,
            zorder=3,
        )

    ax.set_xticks(positions)
    ax.set_xticklabels([LABEL_MAP[bucket] for bucket in order], rotation=12, ha="right")
    ax.set_ylabel("Google yearly mean absolute change")
    ax.set_title("External Google movement by frozen panel bucket")
    fig.savefig(figures_dir / "figure_bucket_external_movement.pdf")
    fig.savefig(figures_dir / "figure_bucket_external_movement.png")
    plt.close(fig)


def plot_internal_vs_external(panel_table: pd.DataFrame, figures_dir: Path) -> None:
    """Plot internal scores against Google movement for the shared panel."""
    configure_plot_style()
    fig, axes = plt.subplots(1, 2, figsize=(8.4, 3.4), sharey=True)
    scatter_specs = [
        ("word2vec_primary_drift", "Word2Vec primary drift"),
        ("tfidf_primary_drift", "TF-IDF primary drift"),
    ]

    for ax, (metric, xlabel) in zip(axes, scatter_specs, strict=True):
        for bucket, bucket_frame in panel_table.groupby("bucket", sort=False):
            ax.scatter(
                bucket_frame[metric],
                bucket_frame["gt_mean_abs_change"],
                s=34,
                alpha=0.85,
                color=COLOR_MAP[bucket],
                label=LABEL_MAP[bucket],
            )
        spearman = spearmanr(
            panel_table[metric],
            panel_table["gt_mean_abs_change"],
            nan_policy="omit",
        )
        ax.set_xlabel(xlabel)
        ax.set_title(f"{xlabel} vs Google movement\nSpearman ρ = {spearman.statistic:.2f}")

    axes[0].set_ylabel("Google yearly mean absolute change")
    handles, labels = axes[1].get_legend_handles_labels()
    axes[1].legend(handles[:4], labels[:4], loc="upper left", frameon=False)
    fig.savefig(figures_dir / "figure_internal_vs_external_scatter.pdf")
    fig.savefig(figures_dir / "figure_internal_vs_external_scatter.png")
    plt.close(fig)


def plot_representative_trajectories(
    panel_table: pd.DataFrame,
    google_yearly: pd.DataFrame,
    w2v_yearly: pd.DataFrame,
    tfidf_yearly: pd.DataFrame,
    figures_dir: Path,
) -> None:
    """Plot standardized Google and internal trajectories for representative terms."""
    configure_plot_style()
    combined = pd.concat([google_yearly, w2v_yearly, tfidf_yearly], ignore_index=True)
    combined = combined.loc[
        combined["lemma"].isin(REPRESENTATIVE_TERMS) & combined["year"].between(2004, 2023)
    ].copy()
    combined = zscore_by_term(combined)

    bucket_lookup = panel_table.set_index("lemma")["bucket_label"].to_dict()
    line_colors = {
        "Google yearly interest": "#111111",
        "Word2Vec transition drift": "#1f77b4",
        "TF-IDF transition drift": "#d55e00",
    }

    fig, axes = plt.subplots(2, 3, figsize=(10.2, 5.8), sharex=True, sharey=True)
    for ax, lemma in zip(axes.flatten(), REPRESENTATIVE_TERMS, strict=True):
        term_frame = combined.loc[combined["lemma"] == lemma]
        for series, series_frame in term_frame.groupby("series", sort=False):
            ax.plot(
                series_frame["year"],
                series_frame["z_value"],
                color=line_colors[series],
                linewidth=1.8,
                label=series,
            )
        ax.axhline(0.0, color="#999999", linewidth=0.8, alpha=0.6)
        ax.set_title(f"{lemma} ({bucket_lookup[lemma]})")

    for ax in axes[1]:
        ax.set_xlabel("Year")
    for ax in axes[:, 0]:
        ax.set_ylabel("Within-series z-score")

    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(
        handles,
        labels,
        loc="upper center",
        ncol=3,
        frameon=False,
        bbox_to_anchor=(0.5, 1.03),
    )
    fig.savefig(figures_dir / "figure_representative_trajectories.pdf")
    fig.savefig(figures_dir / "figure_representative_trajectories.png")
    plt.close(fig)


def plot_all_word_overlays(
    panel_table: pd.DataFrame,
    google_yearly: pd.DataFrame,
    w2v_yearly: pd.DataFrame,
    tfidf_yearly: pd.DataFrame,
    figures_dir: Path,
) -> pd.DataFrame:
    """Generate one same-graph overlay per panel term."""
    configure_plot_style()
    overlay_dir = figures_dir / "word_overlays"
    overlay_dir.mkdir(parents=True, exist_ok=True)

    combined = pd.concat([google_yearly, w2v_yearly, tfidf_yearly], ignore_index=True)
    combined = combined.loc[combined["year"].between(2004, 2023)].copy()
    combined = zscore_by_term(combined)

    line_colors = {
        "Google yearly interest": "#111111",
        "Word2Vec transition drift": "#1f77b4",
        "TF-IDF transition drift": "#d55e00",
    }
    bucket_lookup = panel_table.set_index("lemma")["bucket_label"].to_dict()
    rows: list[dict[str, str]] = []

    for lemma in panel_table["lemma"].sort_values():
        lemma_frame = combined.loc[combined["lemma"] == lemma].copy()
        if lemma_frame.empty:
            continue

        fig, ax = plt.subplots(figsize=(6.4, 3.2))
        for series, series_frame in lemma_frame.groupby("series", sort=False):
            ax.plot(
                series_frame["year"],
                series_frame["z_value"],
                label=series,
                color=line_colors[series],
                linewidth=1.8,
            )

        ax.axhline(0.0, color="#999999", linewidth=0.8, alpha=0.6)
        ax.set_xlabel("Year")
        ax.set_ylabel("Within-series z-score")
        ax.set_title(f"{lemma} ({bucket_lookup[lemma]})")
        ax.legend(loc="upper left", frameon=False)

        slug = slugify_term(lemma)
        pdf_path = overlay_dir / f"{slug}_google_vs_drift.pdf"
        png_path = overlay_dir / f"{slug}_google_vs_drift.png"
        fig.savefig(pdf_path)
        fig.savefig(png_path)
        plt.close(fig)

        rows.append(
            {
                "lemma": lemma,
                "bucket_label": bucket_lookup[lemma],
                "pdf_path": str(pdf_path),
                "png_path": str(png_path),
            }
        )

    return pd.DataFrame(rows)


def write_outputs(
    panel_table: pd.DataFrame,
    group_summary: pd.DataFrame,
    group_tests: pd.DataFrame,
    correlations: pd.DataFrame,
    representative_terms: pd.DataFrame,
    overlay_index: pd.DataFrame,
    tables_dir: Path,
) -> None:
    """Persist analysis tables for the memo and figures."""
    panel_table.to_csv(tables_dir / "panel_google_joined.csv", index=False)
    group_summary.to_csv(tables_dir / "group_external_movement_summary.csv", index=False)
    group_tests.to_csv(tables_dir / "group_external_movement_tests.csv", index=False)
    correlations.to_csv(tables_dir / "internal_external_correlations.csv", index=False)
    representative_terms.to_csv(tables_dir / "representative_terms.csv", index=False)
    overlay_index.to_csv(tables_dir / "word_overlay_index.csv", index=False)


def main() -> None:
    """Run the full post-hoc Google-vs-frozen analysis."""
    tables_dir, figures_dir = ensure_output_dirs()
    paths = Paths()
    inputs = load_inputs(paths)

    google_features = compute_google_features(inputs["yearly_interest"])
    panel_table = build_panel_table(inputs["panel"], google_features, inputs["term_results"])
    group_summary = summarize_groups(panel_table)
    group_tests = summarize_tests(panel_table)
    correlations = summarize_correlations(panel_table, inputs["bert_panel"])

    google_yearly, w2v_yearly, tfidf_yearly = prepare_yearly_series(
        inputs["yearly_interest"],
        inputs["word2vec_trajectory"],
        inputs["tfidf_trajectory"],
    )

    representative_terms = panel_table.loc[
        panel_table["lemma"].isin(REPRESENTATIVE_TERMS),
        [
            "lemma",
            "bucket",
            "bucket_label",
            "word2vec_rank",
            "tfidf_rank",
            "gt_mean_abs_change",
            "gt_std",
            "gt_range",
            "gt_peak_year",
            "gt_peak_value",
        ],
    ].sort_values(["bucket", "lemma"])

    plot_bucket_external_movement(panel_table, figures_dir)
    plot_internal_vs_external(panel_table, figures_dir)
    plot_representative_trajectories(
        panel_table,
        google_yearly,
        w2v_yearly,
        tfidf_yearly,
        figures_dir,
    )
    overlay_index = plot_all_word_overlays(
        panel_table,
        google_yearly,
        w2v_yearly,
        tfidf_yearly,
        figures_dir,
    )
    write_outputs(
        panel_table,
        group_summary,
        group_tests,
        correlations,
        representative_terms,
        overlay_index,
        tables_dir,
    )


if __name__ == "__main__":
    main()
