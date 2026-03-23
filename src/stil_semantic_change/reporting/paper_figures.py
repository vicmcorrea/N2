from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from string import ascii_uppercase

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy.stats import mannwhitneyu, spearmanr

from stil_semantic_change.utils.artifacts import read_json

OKABE_ITO = {
    "blue": "#0072B2",
    "orange": "#D55E00",
    "green": "#009E73",
    "yellow": "#F0E442",
    "sky": "#56B4E9",
    "purple": "#CC79A7",
    "grey": "#7F7F7F",
    "black": "#000000",
}

BUCKET_LABELS = {
    "word2vec_only_drift": "Word2Vec drift",
    "tfidf_only_drift": "TF-IDF drift",
    "stable_control": "Stable control",
    "theory_seed": "Theory seed",
}

BUCKET_COLORS = {
    "word2vec_only_drift": OKABE_ITO["blue"],
    "tfidf_only_drift": OKABE_ITO["orange"],
    "stable_control": OKABE_ITO["grey"],
    "theory_seed": OKABE_ITO["purple"],
}

METHOD_COLORS = {
    "Word2Vec": OKABE_ITO["blue"],
    "TF-IDF": OKABE_ITO["orange"],
    "BERT": OKABE_ITO["green"],
}

PAIR_COLORS = {
    "BERT vs Word2Vec": OKABE_ITO["green"],
    "BERT vs TF-IDF": OKABE_ITO["orange"],
    "Word2Vec vs TF-IDF": OKABE_ITO["blue"],
}

SELECTED_TRAJECTORY_TERMS = {
    "bloqueio": "Strong contextual support for a Word2Vec-led term",
    "salário": "Strong contextual support for a TF-IDF-led term",
    "reforma": "Theory seed with elevated contextual rank",
    "trabalho": "Stable-control leakage diagnostic",
}

EXPORT_SUFFIXES = {
    "pdf": {"dpi": None},
    "eps": {"dpi": None},
    "png": {"dpi": 600},
    "tiff": {"dpi": 600},
}


@dataclass(frozen=True)
class PaperFigurePaths:
    experiment_root: Path
    output_dir: Path


def generate_paper_figures(experiment_root: Path, output_dir: Path) -> dict[str, object]:
    _ = PaperFigurePaths(experiment_root=experiment_root, output_dir=output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    _apply_publication_style()

    slice_summary = pd.read_parquet(experiment_root / "prepared" / "slice_summary.parquet")
    lemma_slice_stats = pd.read_parquet(experiment_root / "prepared" / "lemma_slice_stats.parquet")
    comparison_panel = pd.read_parquet(
        experiment_root / "scores" / "comparison_panel" / "comparison_panel.parquet"
    )
    bert_comparison = pd.read_parquet(
        experiment_root / "scores" / "bert_confirmatory" / "comparison_with_word2vec.parquet"
    )
    cross_summary = read_json(
        experiment_root / "scores" / "cross_method_agreement" / "summary.json"
    )
    topk_overlap = pd.read_parquet(
        experiment_root / "scores" / "cross_method_agreement" / "topk_overlap.parquet"
    )
    word2vec_trajectory = pd.read_parquet(experiment_root / "scores" / "trajectory.parquet")
    tfidf_trajectory = pd.read_parquet(
        experiment_root / "scores" / "tfidf_drift" / "trajectory.parquet"
    )
    bert_trajectory = pd.read_parquet(
        experiment_root / "scores" / "bert_confirmatory" / "trajectory.parquet"
    )

    preferred_layer = int(cross_summary["preferred_layer"])

    figure_manifest: dict[str, object] = {
        "experiment_root": str(experiment_root),
        "preferred_layer": preferred_layer,
        "figures": [],
    }

    corpus_path = output_dir / "figure_01_corpus_profile"
    _plot_corpus_profile(slice_summary, lemma_slice_stats, corpus_path)
    figure_manifest["figures"].append(
        {
            "id": "figure_01",
            "stem": str(corpus_path),
            "caption": (
                "Corpus profile for the frozen BrPoliCorpus floor baseline. Panel (A) shows the "
                "number of floor speeches per yearly slice, panel (B) the retained token volume, "
                "and panel (C) the number of unique lemmas observed after preprocessing."
            ),
        }
    )

    agreement_path = output_dir / "figure_02_method_agreement"
    agreement_metrics = _plot_method_agreement(
        comparison_panel=comparison_panel,
        bert_comparison=bert_comparison,
        preferred_layer=preferred_layer,
        output_stem=agreement_path,
    )
    figure_manifest["figures"].append(
        {
            "id": "figure_02",
            "stem": str(agreement_path),
            "caption": (
                "Pairwise agreement across drift methods on the shared comparison panel. Panels "
                "(A) through (C) show percentile-rank agreement between the preferred BERT layer, "
                "Word2Vec, and TF-IDF, while panel (D) compares the two contextual layers. "
                "Annotations report Spearman correlation and two-sided p-values."
            ),
            "stats": agreement_metrics,
        }
    )

    overlap_path = output_dir / "figure_03_overlap_and_rank_statistics"
    overlap_metrics = _plot_overlap_and_rank_statistics(
        comparison_panel=comparison_panel,
        bert_comparison=bert_comparison,
        topk_overlap=topk_overlap,
        preferred_layer=preferred_layer,
        output_stem=overlap_path,
    )
    figure_manifest["figures"].append(
        {
            "id": "figure_03",
            "stem": str(overlap_path),
            "caption": (
                "Overlap and rank-distribution summaries on the shared comparison panel. Panel "
                "(A) traces top-k overlap for the preferred BERT layer. Panels (B) through (D) "
                "show rank-percentile distributions by bucket for Word2Vec, TF-IDF, and BERT. "
                "Points show individual terms, large markers show means, error bars show 95% "
                "bootstrap confidence intervals, and brackets report one-sided Mann-Whitney tests "
                "for selected drift terms versus stable controls."
            ),
            "stats": overlap_metrics,
        }
    )

    trajectory_path = output_dir / "figure_04_representative_trajectories"
    _plot_representative_trajectories(
        word2vec_trajectory=word2vec_trajectory,
        tfidf_trajectory=tfidf_trajectory,
        bert_trajectory=bert_trajectory,
        preferred_layer=preferred_layer,
        output_stem=trajectory_path,
    )
    figure_manifest["figures"].append(
        {
            "id": "figure_04",
            "stem": str(trajectory_path),
            "caption": (
                "Representative term trajectories across methods. Each panel shows "
                "transition-level scores standardized within term and method to "
                "emphasize temporal shape rather than absolute scale. Word2Vec "
                "ribbons denote replicate variability; TF-IDF and BERT are "
                "single-series estimates."
            ),
        }
    )

    manifest_path = output_dir / "figure_manifest.json"
    manifest_path.write_text(
        json.dumps(figure_manifest, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    _write_inventory_markdown(output_dir / "figure_inventory.md", figure_manifest)
    return figure_manifest


def _apply_publication_style() -> None:
    sns.set_theme(style="ticks", context="paper", font_scale=1.05)
    plt.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
            "font.size": 8,
            "axes.labelsize": 9,
            "axes.titlesize": 9,
            "xtick.labelsize": 7,
            "ytick.labelsize": 7,
            "legend.fontsize": 7,
            "figure.titlesize": 10,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
        }
    )


def _save_bundle(fig: plt.Figure, output_stem: Path) -> None:
    output_stem.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    for suffix, kwargs in EXPORT_SUFFIXES.items():
        path = output_stem.with_suffix(f".{suffix}")
        save_kwargs = {"bbox_inches": "tight"}
        if kwargs["dpi"] is not None:
            save_kwargs["dpi"] = kwargs["dpi"]
        fig.savefig(path, **save_kwargs)
    plt.close(fig)


def _add_panel_labels(axes: list[plt.Axes], *, x: float = -0.14, y: float = 1.05) -> None:
    for index, axis in enumerate(axes):
        axis.text(
            x,
            y,
            ascii_uppercase[index],
            transform=axis.transAxes,
            fontsize=11,
            fontweight="bold",
            va="top",
            ha="left",
        )


def _rank_to_percentile(rank: pd.Series) -> pd.Series:
    if rank.nunique(dropna=True) <= 1:
        return pd.Series(np.ones(len(rank)), index=rank.index, dtype=float)
    maximum = float(rank.max())
    return 1.0 - ((rank.astype(float) - 1.0) / (maximum - 1.0))


def _format_p_value(value: float) -> str:
    if value < 0.001:
        return "p < .001"
    return f"p = {value:.3f}"


def _significance_stars(value: float) -> str:
    if value < 0.001:
        return "***"
    if value < 0.01:
        return "**"
    if value < 0.05:
        return "*"
    return "ns"


def _bootstrap_ci(
    values: np.ndarray,
    *,
    seed: int = 13,
    n_boot: int = 4000,
) -> tuple[float, float, float]:
    if len(values) == 0:
        return (np.nan, np.nan, np.nan)
    rng = np.random.default_rng(seed)
    if len(values) == 1:
        return (float(values[0]), float(values[0]), float(values[0]))
    draws = rng.choice(values, size=(n_boot, len(values)), replace=True)
    means = draws.mean(axis=1)
    return (
        float(values.mean()),
        float(np.quantile(means, 0.025)),
        float(np.quantile(means, 0.975)),
    )


def _plot_corpus_profile(
    slice_summary: pd.DataFrame,
    lemma_slice_stats: pd.DataFrame,
    output_stem: Path,
) -> None:
    summary = slice_summary.sort_values("sort_key").copy()
    summary["year"] = summary["slice_id"].astype(int)
    vocab = (
        lemma_slice_stats.groupby("slice_id")["lemma"]
        .nunique()
        .rename("vocab_size")
        .reset_index()
    )
    vocab["slice_id"] = vocab["slice_id"].astype(str)
    summary = summary.merge(vocab, on="slice_id", how="left")

    fig, axes = plt.subplots(3, 1, figsize=(7.2, 7.8), sharex=True)
    years = summary["year"].to_numpy()

    axes[0].bar(years, summary["document_count"], color=OKABE_ITO["blue"], width=0.8)
    axes[0].set_ylabel("Documents")
    axes[0].set_title("Floor speeches by year")

    axes[1].plot(
        years,
        summary["token_count"] / 1_000_000,
        color=OKABE_ITO["orange"],
        marker="o",
        linewidth=2,
    )
    axes[1].fill_between(
        years,
        np.zeros_like(years, dtype=float),
        summary["token_count"] / 1_000_000,
        color=OKABE_ITO["orange"],
        alpha=0.15,
    )
    axes[1].set_ylabel("Tokens (millions)")
    axes[1].set_title("Retained token volume by year")

    axes[2].plot(years, summary["vocab_size"], color=OKABE_ITO["green"], marker="s", linewidth=2)
    axes[2].set_ylabel("Unique lemmas")
    axes[2].set_xlabel("Year")
    axes[2].set_title("Vocabulary size by year")

    for axis in axes:
        axis.grid(axis="y", alpha=0.25)
        axis.set_xlim(years.min() - 0.5, years.max() + 0.5)

    axes[2].set_xticks(years[::2])
    _add_panel_labels(list(axes))
    _save_bundle(fig, output_stem)


def _plot_method_agreement(
    comparison_panel: pd.DataFrame,
    bert_comparison: pd.DataFrame,
    preferred_layer: int,
    output_stem: Path,
) -> dict[str, dict[str, float]]:
    panel = comparison_panel.copy()
    panel["word2vec_pct"] = _rank_to_percentile(panel["word2vec_rank"])
    panel["tfidf_pct"] = _rank_to_percentile(panel["tfidf_rank"])

    bert = bert_comparison.loc[bert_comparison["layer"] == preferred_layer].copy()
    bert["bert_rank"] = bert["primary_drift"].rank(method="first", ascending=False)
    bert["bert_pct"] = _rank_to_percentile(bert["bert_rank"])
    bert = bert.merge(
        panel[["lemma", "word2vec_pct", "tfidf_pct"]],
        on="lemma",
        how="left",
    )

    layer_pivot = bert_comparison.pivot_table(
        index="lemma",
        columns="layer",
        values="primary_drift",
        aggfunc="first",
    ).reset_index()
    layer_pivot["bert_minus4_rank"] = layer_pivot[-4].rank(method="first", ascending=False)
    layer_pivot["bert_minus1_rank"] = layer_pivot[-1].rank(method="first", ascending=False)
    layer_pivot["bert_minus4_pct"] = _rank_to_percentile(layer_pivot["bert_minus4_rank"])
    layer_pivot["bert_minus1_pct"] = _rank_to_percentile(layer_pivot["bert_minus1_rank"])
    layer_pivot = layer_pivot.merge(
        bert[["lemma", "bucket"]],
        on="lemma",
        how="left",
    )

    fig, axes = plt.subplots(2, 2, figsize=(7.2, 6.8))
    highlight_terms = {"bloqueio", "salário", "reforma", "trabalho"}

    metrics: dict[str, dict[str, float]] = {}
    panel_specs = [
        ("BERT vs Word2Vec", bert, "word2vec_pct", "bert_pct", axes[0, 0]),
        ("BERT vs TF-IDF", bert, "tfidf_pct", "bert_pct", axes[0, 1]),
        ("Word2Vec vs TF-IDF", bert, "word2vec_pct", "tfidf_pct", axes[1, 0]),
        ("BERT layer agreement", layer_pivot, "bert_minus4_pct", "bert_minus1_pct", axes[1, 1]),
    ]

    for title, frame, x_col, y_col, axis in panel_specs:
        rho, p_value = spearmanr(frame[x_col], frame[y_col])
        metrics[title] = {"spearman_r": float(rho), "p_value": float(p_value)}
        for bucket, bucket_frame in frame.groupby("bucket", sort=False):
            axis.scatter(
                bucket_frame[x_col],
                bucket_frame[y_col],
                s=42,
                alpha=0.9,
                color=BUCKET_COLORS.get(bucket, OKABE_ITO["black"]),
                marker=_marker_for_bucket(bucket),
                linewidth=0.5,
                edgecolor="white",
                label=BUCKET_LABELS.get(bucket, bucket),
            )
        axis.plot([0, 1], [0, 1], color=OKABE_ITO["grey"], linestyle="--", linewidth=1)
        axis.set_xlim(-0.02, 1.02)
        axis.set_ylim(-0.02, 1.02)
        axis.grid(alpha=0.2)
        axis.set_title(title)
        axis.text(
            0.03,
            0.05,
            f"$\\rho$ = {rho:.2f}\n{_format_p_value(float(p_value))}",
            transform=axis.transAxes,
            ha="left",
            va="bottom",
            bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.9},
        )
        for _, row in frame.loc[frame["lemma"].isin(highlight_terms)].iterrows():
            axis.annotate(
                row["lemma"],
                (row[x_col], row[y_col]),
                textcoords="offset points",
                xytext=(4, 4),
                fontsize=6.5,
            )

    axes[0, 0].set_xlabel("Word2Vec rank percentile")
    axes[0, 0].set_ylabel("BERT rank percentile")
    axes[0, 1].set_xlabel("TF-IDF rank percentile")
    axes[0, 1].set_ylabel("BERT rank percentile")
    axes[1, 0].set_xlabel("Word2Vec rank percentile")
    axes[1, 0].set_ylabel("TF-IDF rank percentile")
    axes[1, 1].set_xlabel("BERT layer -4 rank percentile")
    axes[1, 1].set_ylabel("BERT layer -1 rank percentile")

    handles, labels = axes[0, 0].get_legend_handles_labels()
    unique = dict(zip(labels, handles, strict=False))
    fig.legend(
        unique.values(),
        unique.keys(),
        loc="upper center",
        ncol=4,
        frameon=False,
        bbox_to_anchor=(0.5, 1.02),
    )
    _add_panel_labels([axes[0, 0], axes[0, 1], axes[1, 0], axes[1, 1]], x=-0.13, y=1.04)
    fig.subplots_adjust(top=0.88)
    _save_bundle(fig, output_stem)
    return metrics


def _plot_overlap_and_rank_statistics(
    comparison_panel: pd.DataFrame,
    bert_comparison: pd.DataFrame,
    topk_overlap: pd.DataFrame,
    preferred_layer: int,
    output_stem: Path,
) -> dict[str, object]:
    fig, axes = plt.subplots(2, 2, figsize=(7.2, 6.8))

    overlap = topk_overlap.loc[
        (topk_overlap["layer"] == preferred_layer) & (topk_overlap["subset"] == "all_panel")
    ].copy()
    overlap = overlap.sort_values("k")
    pair_columns = [
        ("BERT vs Word2Vec", "bert_word2vec_topk_overlap"),
        ("BERT vs TF-IDF", "bert_tfidf_topk_overlap"),
        ("Word2Vec vs TF-IDF", "word2vec_tfidf_topk_overlap"),
    ]
    for label, column in pair_columns:
        axes[0, 0].plot(
            overlap["k"],
            overlap[column],
            marker="o",
            linewidth=2,
            color=PAIR_COLORS[label],
            label=label,
        )
        for _, row in overlap.iterrows():
            axes[0, 0].annotate(
                f"{int(row[column])}",
                (row["k"], row[column]),
                textcoords="offset points",
                xytext=(0, 5),
                ha="center",
                fontsize=6.5,
            )
    axes[0, 0].set_xlabel("Top-k threshold")
    axes[0, 0].set_ylabel("Shared terms")
    axes[0, 0].set_title("Top-k overlap on the shared panel")
    axes[0, 0].set_xticks(overlap["k"])
    axes[0, 0].grid(alpha=0.2)
    axes[0, 0].legend(frameon=False, loc="upper left")

    preferred = bert_comparison.loc[bert_comparison["layer"] == preferred_layer].copy()
    panel = comparison_panel.copy()
    preferred["bert_rank"] = preferred["primary_drift"].rank(method="first", ascending=False)
    method_frames = {
        "Word2Vec": panel[["lemma", "bucket", "word2vec_rank"]].rename(
            columns={"word2vec_rank": "rank"}
        ),
        "TF-IDF": panel[["lemma", "bucket", "tfidf_rank"]].rename(
            columns={"tfidf_rank": "rank"}
        ),
        "BERT": preferred[["lemma", "bucket", "bert_rank"]].rename(
            columns={"bert_rank": "rank"}
        ),
    }

    stats_summary: dict[str, object] = {
        "overlap": overlap.to_dict(orient="records"),
        "bucket_tests": {},
    }
    bucket_order = ["Selected drift", "Theory seed", "Stable control"]
    bucket_palette = {
        "Selected drift": OKABE_ITO["yellow"],
        "Theory seed": OKABE_ITO["purple"],
        "Stable control": OKABE_ITO["grey"],
    }

    for axis, (method_label, frame) in zip(
        [axes[0, 1], axes[1, 0], axes[1, 1]],
        method_frames.items(),
        strict=False,
    ):
        stats_summary["bucket_tests"][method_label] = _plot_bucket_rank_panel(
            axis=axis,
            method_label=method_label,
            frame=frame,
            bucket_order=bucket_order,
            bucket_palette=bucket_palette,
        )

    _add_panel_labels([axes[0, 0], axes[0, 1], axes[1, 0], axes[1, 1]], x=-0.13, y=1.04)
    _save_bundle(fig, output_stem)
    return stats_summary


def _plot_bucket_rank_panel(
    axis: plt.Axes,
    method_label: str,
    frame: pd.DataFrame,
    bucket_order: list[str],
    bucket_palette: dict[str, str],
) -> dict[str, float]:
    plot_frame = frame.copy()
    plot_frame["bucket_group"] = plot_frame["bucket"].map(_bucket_group)
    plot_frame["rank_pct"] = _rank_to_percentile(plot_frame["rank"])

    jitter_rng = np.random.default_rng(13)
    stats: list[tuple[str, float, float, float]] = []
    for index, bucket_group in enumerate(bucket_order):
        values = plot_frame.loc[plot_frame["bucket_group"] == bucket_group, "rank_pct"].to_numpy()
        if len(values) == 0:
            continue
        x = np.full(len(values), float(index)) + jitter_rng.uniform(-0.08, 0.08, size=len(values))
        axis.scatter(
            x,
            values,
            s=16,
            color=bucket_palette[bucket_group],
            alpha=0.35,
            linewidth=0.0,
        )
        mean_value, ci_low, ci_high = _bootstrap_ci(values)
        stats.append((bucket_group, mean_value, ci_low, ci_high))
        axis.errorbar(
            index,
            mean_value,
            yerr=np.array([[mean_value - ci_low], [ci_high - mean_value]]),
            color=METHOD_COLORS[method_label],
            marker="o",
            markersize=5,
            linewidth=1.5,
            capsize=3,
            zorder=4,
        )

    axis.set_xticks(range(len(bucket_order)))
    axis.set_xticklabels(bucket_order, rotation=18, ha="right")
    axis.set_ylim(-0.02, 1.05)
    axis.set_ylabel("Rank percentile")
    axis.set_title(method_label)
    axis.grid(axis="y", alpha=0.2)

    drift_values = plot_frame.loc[
        plot_frame["bucket_group"] == "Selected drift",
        "rank_pct",
    ].to_numpy()
    stable_values = plot_frame.loc[
        plot_frame["bucket_group"] == "Stable control",
        "rank_pct",
    ].to_numpy()
    statistic, p_value = mannwhitneyu(drift_values, stable_values, alternative="greater")
    _add_significance_bracket(
        axis=axis,
        x_left=0,
        x_right=2,
        y=1.0,
        label=f"{_significance_stars(float(p_value))} ({_format_p_value(float(p_value))})",
    )
    return {
        "u_statistic": float(statistic),
        "p_value": float(p_value),
        "drift_mean": float(drift_values.mean()),
        "stable_mean": float(stable_values.mean()),
    }


def _add_significance_bracket(
    axis: plt.Axes,
    x_left: float,
    x_right: float,
    y: float,
    label: str,
) -> None:
    axis.plot(
        [x_left, x_left, x_right, x_right],
        [y - 0.015, y, y, y - 0.015],
        color=OKABE_ITO["black"],
        linewidth=0.8,
    )
    axis.text((x_left + x_right) / 2, y + 0.015, label, ha="center", va="bottom", fontsize=6.5)


def _plot_representative_trajectories(
    word2vec_trajectory: pd.DataFrame,
    tfidf_trajectory: pd.DataFrame,
    bert_trajectory: pd.DataFrame,
    preferred_layer: int,
    output_stem: Path,
) -> None:
    fig, axes = plt.subplots(2, 2, figsize=(7.2, 6.8), sharex=True, sharey=True)
    flat_axes = [axes[0, 0], axes[0, 1], axes[1, 0], axes[1, 1]]

    for axis, (term, subtitle) in zip(flat_axes, SELECTED_TRAJECTORY_TERMS.items(), strict=False):
        w_frame = (
            word2vec_trajectory.loc[word2vec_trajectory["lemma"] == term]
            .groupby(["to_slice", "transition"])
            .agg(mean_drift=("drift", "mean"), std_drift=("drift", "std"))
            .reset_index()
            .sort_values("to_slice")
        )
        t_frame = (
            tfidf_trajectory.loc[tfidf_trajectory["lemma"] == term]
            .sort_values("to_slice")
            .reset_index(drop=True)
        )
        b_frame = (
            bert_trajectory.loc[
                (bert_trajectory["lemma"] == term) & (bert_trajectory["layer"] == preferred_layer)
            ]
            .sort_values("to_slice")
            .reset_index(drop=True)
        )

        years = w_frame["to_slice"].astype(int).to_numpy()
        w_mean = _zscore(w_frame["mean_drift"].to_numpy())
        w_std = w_frame["std_drift"].fillna(0.0).to_numpy()
        w_scale = float(w_frame["mean_drift"].std(ddof=0))
        w_std = w_std / w_scale if w_scale > 0 else np.zeros_like(w_std)

        axis.plot(
            years,
            w_mean,
            color=METHOD_COLORS["Word2Vec"],
            linewidth=2,
            marker="o",
            label="Word2Vec",
        )
        axis.fill_between(
            years,
            w_mean - w_std,
            w_mean + w_std,
            color=METHOD_COLORS["Word2Vec"],
            alpha=0.18,
        )
        axis.plot(
            t_frame["to_slice"].astype(int),
            _zscore(t_frame["drift"].to_numpy()),
            color=METHOD_COLORS["TF-IDF"],
            linewidth=1.8,
            marker="s",
            label="TF-IDF",
        )
        axis.plot(
            b_frame["to_slice"].astype(int),
            _zscore(b_frame["drift"].to_numpy()),
            color=METHOD_COLORS["BERT"],
            linewidth=1.8,
            marker="^",
            label="BERT",
        )
        axis.axhline(0.0, color=OKABE_ITO["grey"], linewidth=0.8, linestyle="--", alpha=0.8)
        axis.set_title(f"{term}\n{subtitle}", fontsize=8.5)
        axis.grid(alpha=0.2)
        axis.set_xlim(years.min() - 0.2, years.max() + 0.2)
        axis.set_xticks(years[::4])

    for axis in flat_axes[2:]:
        axis.set_xlabel("Right-hand slice year")
    for axis in [axes[0, 0], axes[1, 0]]:
        axis.set_ylabel("Within-term standardized drift")

    handles, labels = flat_axes[0].get_legend_handles_labels()
    fig.legend(
        handles,
        labels,
        loc="upper center",
        ncol=3,
        frameon=False,
        bbox_to_anchor=(0.5, 1.02),
    )
    _add_panel_labels(flat_axes, x=-0.13, y=1.06)
    fig.subplots_adjust(top=0.9)
    _save_bundle(fig, output_stem)


def _marker_for_bucket(bucket: str) -> str:
    return {
        "word2vec_only_drift": "o",
        "tfidf_only_drift": "s",
        "stable_control": "D",
        "theory_seed": "^",
    }.get(bucket, "o")


def _bucket_group(bucket: str) -> str:
    if bucket in {"word2vec_only_drift", "tfidf_only_drift"}:
        return "Selected drift"
    if bucket == "stable_control":
        return "Stable control"
    return "Theory seed"


def _zscore(values: np.ndarray) -> np.ndarray:
    values = values.astype(float)
    std = float(values.std(ddof=0))
    if std == 0.0:
        return np.zeros_like(values)
    return (values - float(values.mean())) / std


def _write_inventory_markdown(path: Path, manifest: dict[str, object]) -> None:
    lines = [
        "# Paper Figure Inventory",
        "",
        f"Experiment root: `{manifest['experiment_root']}`",
        f"Preferred BERT layer: `{manifest['preferred_layer']}`",
        "",
    ]
    for figure in manifest["figures"]:
        lines.extend(
            [
                f"## {figure['id']}",
                "",
                f"Stem: `{figure['stem']}`",
                "",
                figure["caption"],
                "",
            ]
        )
    path.write_text("\n".join(lines), encoding="utf-8")
