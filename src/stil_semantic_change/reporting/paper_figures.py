from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from string import ascii_uppercase

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from adjustText import adjust_text
from matplotlib.colors import to_rgba
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
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
                "use standard boxplots to summarize rank-percentile distributions by bucket "
                "for Word2Vec, TF-IDF, and BERT. "
                "Boxes show medians and interquartile ranges, whiskers extend to 1.5 times the "
                "interquartile range, points show outliers, and brackets report one-sided "
                "Mann-Whitney tests for selected drift terms versus stable controls."
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

    study_design_path = output_dir / "figure_05_study_design"
    _plot_study_design(output_stem=study_design_path)
    figure_manifest["figures"].append(
        {
            "id": "figure_05",
            "stem": str(study_design_path),
            "caption": (
                "Paper-facing comparative workflow. Cheap baselines nominate "
                "candidates; the shared panel combines those candidates with "
                "controls and theory seeds before contextual inspection and "
                "agreement analysis."
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


def _save_individual_panels(
    fig: plt.Figure,
    axes: list[plt.Axes],
    output_stem: Path,
) -> None:
    """Crop and save each axis as a standalone figure file for use with \\subfigure."""
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    output_stem.parent.mkdir(parents=True, exist_ok=True)
    for idx, ax in enumerate(axes):
        letter = ascii_uppercase[idx].lower()
        panel_stem = output_stem.parent / f"{output_stem.name}_panel_{letter}"
        tight_bbox = ax.get_tightbbox(renderer)
        bbox_in = tight_bbox.transformed(fig.dpi_scale_trans.inverted())
        for suffix, kwargs in EXPORT_SUFFIXES.items():
            path = panel_stem.with_suffix(f".{suffix}")
            save_kw: dict[str, object] = {"bbox_inches": bbox_in}
            if kwargs["dpi"] is not None:
                save_kw["dpi"] = kwargs["dpi"]
            fig.savefig(path, **save_kw)


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

    fig, axes = plt.subplots(
        3,
        1,
        figsize=(7.2, 6.4),
        sharex=True,
        gridspec_kw={"hspace": 0.16},
    )
    years = summary["year"].to_numpy()

    series_specs = [
        ("document_count", "Speeches", OKABE_ITO["blue"], "o"),
        ("token_count", "Tokens (M)", OKABE_ITO["orange"], "D"),
        ("vocab_size", "Unique lemmas", OKABE_ITO["green"], "s"),
    ]

    for axis, (column, ylabel, color, marker) in zip(axes, series_specs, strict=False):
        values = summary[column].to_numpy(dtype=float)
        if column == "token_count":
            values = values / 1_000_000
        axis.plot(
            years,
            values,
            color=color,
            linewidth=2.0,
            marker=marker,
            markersize=4.2,
            markerfacecolor="white",
            markeredgewidth=1.1,
        )
        axis.fill_between(years, values, values.min(), color=color, alpha=0.08)
        axis.set_ylabel(ylabel)
        axis.grid(axis="y", alpha=0.18, linewidth=0.7)
        axis.set_xlim(years.min() - 0.5, years.max() + 0.5)

    axes[2].set_xlabel("Year")
    axes[2].set_xticks(years[::3])
    _add_panel_labels(list(axes), x=-0.11, y=1.02)
    fig.subplots_adjust(left=0.11, right=0.98, top=0.98, bottom=0.08)
    _save_bundle(fig, output_stem)


def _plot_study_design(output_stem: Path) -> None:
    fig, ax = plt.subplots(figsize=(6.2, 2.15))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    def add_box(
        x: float,
        y: float,
        w: float,
        h: float,
        text: str,
        *,
        facecolor: str,
        edgecolor: str,
        fontsize: float = 9.0,
    ) -> None:
        patch = FancyBboxPatch(
            (x, y),
            w,
            h,
            boxstyle="round,pad=0.012,rounding_size=0.022",
            linewidth=1.2,
            facecolor=facecolor,
            edgecolor=edgecolor,
        )
        ax.add_patch(patch)
        ax.text(
            x + (w / 2),
            y + (h / 2),
            text,
            ha="center",
            va="center",
            fontsize=fontsize,
            linespacing=1.08,
        )

    def add_arrow(start: tuple[float, float], end: tuple[float, float], *, color: str) -> None:
        arrow = FancyArrowPatch(
            start,
            end,
            arrowstyle="-|>",
            mutation_scale=11,
            linewidth=1.25,
            color=color,
            shrinkA=4,
            shrinkB=4,
            connectionstyle="arc3",
        )
        ax.add_patch(arrow)

    add_box(
        0.02,
        0.35,
        0.18,
        0.30,
        "Diachronic corpus\ntemporal slices\n(preprocessed)",
        facecolor="#F2F2F2",
        edgecolor=OKABE_ITO["grey"],
    )
    add_box(
        0.26,
        0.58,
        0.18,
        0.22,
        "Lexical-statistical\nbaseline",
        facecolor="#FBE5D6",
        edgecolor=OKABE_ITO["orange"],
        fontsize=8.4,
    )
    add_box(
        0.26,
        0.20,
        0.18,
        0.22,
        "Static embedding\nmethod",
        facecolor="#DCEAF6",
        edgecolor=OKABE_ITO["blue"],
        fontsize=8.4,
    )
    add_box(
        0.50,
        0.32,
        0.20,
        0.36,
        "Shared comparison\npanel\ndrift + stable\n+ theory seeds",
        facecolor="#FFF4D0",
        edgecolor="#B79000",
        fontsize=8.2,
    )
    add_box(
        0.76,
        0.56,
        0.20,
        0.24,
        "Contextual\nembedding method",
        facecolor="#DDF1E4",
        edgecolor=OKABE_ITO["green"],
        fontsize=8.2,
    )
    add_box(
        0.76,
        0.18,
        0.20,
        0.24,
        "Agreement layer\ncorrelations, overlap,\ntrajectories, cost",
        facecolor="#F2F2F2",
        edgecolor=OKABE_ITO["grey"],
        fontsize=8.2,
    )

    add_arrow((0.20, 0.56), (0.26, 0.68), color=OKABE_ITO["grey"])
    add_arrow((0.20, 0.44), (0.26, 0.31), color=OKABE_ITO["grey"])
    add_arrow((0.44, 0.68), (0.50, 0.58), color=OKABE_ITO["orange"])
    add_arrow((0.44, 0.31), (0.50, 0.42), color=OKABE_ITO["blue"])
    add_arrow((0.70, 0.58), (0.76, 0.68), color="#B79000")
    add_arrow((0.70, 0.42), (0.76, 0.30), color="#B79000")
    add_arrow((0.86, 0.56), (0.86, 0.42), color=OKABE_ITO["green"])

    _save_bundle(fig, output_stem)


def _draw_agreement_scatter(
    ax: plt.Axes,
    frame: pd.DataFrame,
    x_col: str,
    y_col: str,
    xlabel: str,
    ylabel: str,
    highlight_terms: set[str],
    add_legend: bool = False,
) -> dict[str, float]:
    rho, p_value = spearmanr(frame[x_col], frame[y_col])
    for bucket, bucket_frame in frame.groupby("bucket", sort=False):
        ax.scatter(
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
    ax.plot([0, 1], [0, 1], color=OKABE_ITO["grey"], linestyle="--", linewidth=1)
    ax.set_xlim(-0.02, 1.02)
    ax.set_ylim(-0.02, 1.02)
    ax.grid(alpha=0.2)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.text(
        0.03,
        0.05,
        f"$\\rho$ = {rho:.2f}\n{_format_p_value(float(p_value))}",
        transform=ax.transAxes,
        ha="left",
        va="bottom",
        bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.9},
    )
    subset = frame.loc[frame["lemma"].isin(highlight_terms)]
    texts = [
        ax.text(row[x_col], row[y_col], row["lemma"], fontsize=6.5)
        for _, row in subset.iterrows()
    ]
    adjust_text(
        texts,
        ax=ax,
        arrowprops={"arrowstyle": "-", "color": OKABE_ITO["grey"], "lw": 0.5},
        expand=(1.2, 1.4),
        force_text=(0.3, 0.5),
    )
    if add_legend:
        handles, labels = ax.get_legend_handles_labels()
        unique = dict(zip(labels, handles, strict=False))
        ax.legend(unique.values(), unique.keys(), loc="lower right", frameon=False, fontsize=6, ncol=2)
    return {"spearman_r": float(rho), "p_value": float(p_value)}


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
    bert = bert.merge(panel[["lemma", "word2vec_pct", "tfidf_pct"]], on="lemma", how="left")

    layer_pivot = bert_comparison.pivot_table(
        index="lemma", columns="layer", values="primary_drift", aggfunc="first"
    ).reset_index()
    layer_pivot["bert_minus4_rank"] = layer_pivot[-4].rank(method="first", ascending=False)
    layer_pivot["bert_minus1_rank"] = layer_pivot[-1].rank(method="first", ascending=False)
    layer_pivot["bert_minus4_pct"] = _rank_to_percentile(layer_pivot["bert_minus4_rank"])
    layer_pivot["bert_minus1_pct"] = _rank_to_percentile(layer_pivot["bert_minus1_rank"])
    layer_pivot = layer_pivot.merge(bert[["lemma", "bucket"]], on="lemma", how="left")

    highlight_terms = {"bloqueio", "salário", "reforma", "trabalho"}
    panel_configs = [
        ("BERT vs Word2Vec",    bert,        "word2vec_pct",    "bert_pct",        "Word2Vec rank percentile",    "BERT rank percentile"),
        ("BERT vs TF-IDF",      bert,        "tfidf_pct",       "bert_pct",        "TF-IDF rank percentile",      "BERT rank percentile"),
        ("Word2Vec vs TF-IDF",  bert,        "word2vec_pct",    "tfidf_pct",       "Word2Vec rank percentile",    "TF-IDF rank percentile"),
        ("BERT layer agreement", layer_pivot, "bert_minus4_pct", "bert_minus1_pct", "BERT layer \u22124 rank percentile", "BERT layer \u22121 rank percentile"),
    ]

    metrics: dict[str, dict[str, float]] = {}

    for idx, (name, frame, x_col, y_col, xlabel, ylabel) in enumerate(panel_configs):
        pfig, pax = plt.subplots(1, 1, figsize=(3.3, 3.0))
        metrics[name] = _draw_agreement_scatter(
            pax, frame, x_col, y_col, xlabel, ylabel, highlight_terms, add_legend=(idx == 0)
        )
        letter = ascii_uppercase[idx].lower()
        _save_bundle(pfig, output_stem.parent / f"{output_stem.name}_panel_{letter}")

    fig, axes = plt.subplots(2, 2, figsize=(6.6, 5.9))
    flat_axes = [axes[0, 0], axes[0, 1], axes[1, 0], axes[1, 1]]
    for ax, (name, frame, x_col, y_col, xlabel, ylabel) in zip(flat_axes, panel_configs):
        _draw_agreement_scatter(ax, frame, x_col, y_col, xlabel, ylabel, highlight_terms)

    handles, labels = flat_axes[0].get_legend_handles_labels()
    unique = dict(zip(labels, handles, strict=False))
    fig.legend(unique.values(), unique.keys(), loc="upper center", ncol=4, frameon=False, bbox_to_anchor=(0.5, 1.02))
    _add_panel_labels(flat_axes, x=-0.13, y=1.04)
    fig.subplots_adjust(top=0.85)
    _save_bundle(fig, output_stem)
    return metrics


def _draw_topk_overlap_panel(
    ax: plt.Axes,
    overlap: pd.DataFrame,
    pair_columns: list[tuple[str, str]],
    *,
    panel_label: str | None = None,
) -> None:
    for label, column in pair_columns:
        ax.plot(overlap["k"], overlap[column], marker="o", linewidth=2, color=PAIR_COLORS[label], label=label)
        for _, row in overlap.iterrows():
            ax.annotate(
                f"{int(row[column])}",
                (row["k"], row[column]),
                textcoords="offset points",
                xytext=(0, 5),
                ha="center",
                fontsize=6.5,
            )
    ax.set_xlabel("Top-k threshold")
    ax.set_ylabel("Shared terms")
    ax.set_xticks(overlap["k"])
    ax.grid(alpha=0.2)
    ax.legend(frameon=False, loc="upper left")
    ax.set_title("Top-k overlap")
    if panel_label is not None:
        _add_axis_panel_label(ax, panel_label)


def _plot_overlap_and_rank_statistics(
    comparison_panel: pd.DataFrame,
    bert_comparison: pd.DataFrame,
    topk_overlap: pd.DataFrame,
    preferred_layer: int,
    output_stem: Path,
) -> dict[str, object]:
    overlap = topk_overlap.loc[
        (topk_overlap["layer"] == preferred_layer) & (topk_overlap["subset"] == "all_panel")
    ].copy().sort_values("k")
    pair_columns = [
        ("BERT vs Word2Vec", "bert_word2vec_topk_overlap"),
        ("BERT vs TF-IDF", "bert_tfidf_topk_overlap"),
        ("Word2Vec vs TF-IDF", "word2vec_tfidf_topk_overlap"),
    ]

    preferred = bert_comparison.loc[bert_comparison["layer"] == preferred_layer].copy()
    panel = comparison_panel.copy()
    preferred["bert_rank"] = preferred["primary_drift"].rank(method="first", ascending=False)
    method_frames = {
        "Word2Vec": panel[["lemma", "bucket", "word2vec_rank"]].rename(columns={"word2vec_rank": "rank"}),
        "TF-IDF":   panel[["lemma", "bucket", "tfidf_rank"]].rename(columns={"tfidf_rank": "rank"}),
        "BERT":     preferred[["lemma", "bucket", "bert_rank"]].rename(columns={"bert_rank": "rank"}),
    }
    bucket_order = ["Selected drift", "Theory seed", "Stable control"]
    bucket_palette = {
        "Selected drift": OKABE_ITO["blue"],
        "Theory seed":    OKABE_ITO["purple"],
        "Stable control": OKABE_ITO["black"],
    }

    stats_summary: dict[str, object] = {"overlap": overlap.to_dict(orient="records"), "bucket_tests": {}}

    pfig_a, pax_a = plt.subplots(1, 1, figsize=(3.3, 2.9))
    _draw_topk_overlap_panel(pax_a, overlap, pair_columns, panel_label="A")
    _save_bundle(pfig_a, output_stem.parent / f"{output_stem.name}_panel_a")

    for idx, (method_label, frame) in enumerate(method_frames.items(), start=1):
        pfig, pax = plt.subplots(1, 1, figsize=(3.3, 2.9))
        stats_summary["bucket_tests"][method_label] = _plot_bucket_rank_panel(
            axis=pax, method_label=method_label, frame=frame,
            bucket_order=bucket_order, bucket_palette=bucket_palette,
            panel_label=ascii_uppercase[idx],
        )
        letter = ascii_uppercase[idx].lower()
        _save_bundle(pfig, output_stem.parent / f"{output_stem.name}_panel_{letter}")

    fig, axes = plt.subplots(2, 2, figsize=(6.6, 5.7))
    _draw_topk_overlap_panel(axes[0, 0], overlap, pair_columns, panel_label="A")
    for idx, (axis, (method_label, frame)) in enumerate(
        zip([axes[0, 1], axes[1, 0], axes[1, 1]], method_frames.items(), strict=False),
        start=1,
    ):
        _plot_bucket_rank_panel(axis=axis, method_label=method_label, frame=frame,
                                bucket_order=bucket_order, bucket_palette=bucket_palette,
                                panel_label=ascii_uppercase[idx])

    _save_bundle(fig, output_stem)
    return stats_summary


def _plot_bucket_rank_panel(
    axis: plt.Axes,
    method_label: str,
    frame: pd.DataFrame,
    bucket_order: list[str],
    bucket_palette: dict[str, str],
    panel_label: str | None = None,
) -> dict[str, float]:
    plot_frame = frame.copy()
    plot_frame["bucket_group"] = plot_frame["bucket"].map(_bucket_group)
    plot_frame["rank_pct"] = _rank_to_percentile(plot_frame["rank"])

    values_by_bucket = [
        plot_frame.loc[plot_frame["bucket_group"] == bucket_group, "rank_pct"].to_numpy()
        for bucket_group in bucket_order
    ]
    boxplot = axis.boxplot(
        values_by_bucket,
        positions=np.arange(len(bucket_order), dtype=float),
        widths=0.52,
        patch_artist=True,
        showfliers=True,
        whis=1.5,
        boxprops={"linewidth": 1.2},
        medianprops={"color": OKABE_ITO["black"], "linewidth": 1.8},
        whiskerprops={"color": OKABE_ITO["black"], "linewidth": 1.0},
        capprops={"color": OKABE_ITO["black"], "linewidth": 1.0},
        flierprops={
            "marker": "o",
            "markerfacecolor": OKABE_ITO["black"],
            "markeredgecolor": OKABE_ITO["black"],
            "markersize": 4,
            "alpha": 0.7,
        },
    )
    for index, bucket_group in enumerate(bucket_order):
        box = boxplot["boxes"][index]
        box.set_facecolor(to_rgba(bucket_palette[bucket_group], 0.18))
        box.set_edgecolor(bucket_palette[bucket_group])

    axis.set_xticks(range(len(bucket_order)))
    axis.set_xticklabels(
        [
            f"{bucket_group}\n(n={len(values_by_bucket[index])})"
            for index, bucket_group in enumerate(bucket_order)
        ],
        rotation=18,
        ha="right",
    )
    axis.set_ylim(-0.02, 1.05)
    axis.set_ylabel("Rank percentile")
    axis.grid(axis="y", alpha=0.2)
    axis.set_title(f"{method_label} rank percentiles")
    if panel_label is not None:
        _add_axis_panel_label(axis, panel_label)

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


def _add_axis_panel_label(axis: plt.Axes, label: str) -> None:
    axis.text(
        -0.14,
        1.08,
        label,
        transform=axis.transAxes,
        fontsize=11,
        fontweight="bold",
        va="top",
        ha="left",
    )


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
    term_data: list[tuple[str, pd.DataFrame, pd.DataFrame, pd.DataFrame, np.ndarray, np.ndarray, np.ndarray]] = []
    for term in SELECTED_TRAJECTORY_TERMS:
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
        term_data.append((term, t_frame, b_frame, years, w_mean, w_std))

    def _draw_trajectory_panel(
        ax: plt.Axes,
        term: str,
        t_frame: pd.DataFrame,
        b_frame: pd.DataFrame,
        years: np.ndarray,
        w_mean: np.ndarray,
        w_std: np.ndarray,
        add_legend: bool = False,
    ) -> None:
        ax.plot(years, w_mean, color=METHOD_COLORS["Word2Vec"], linewidth=2, marker="o", label="Word2Vec")
        ax.fill_between(years, w_mean - w_std, w_mean + w_std, color=METHOD_COLORS["Word2Vec"], alpha=0.18)
        ax.plot(t_frame["to_slice"].astype(int), _zscore(t_frame["drift"].to_numpy()),
                color=METHOD_COLORS["TF-IDF"], linewidth=1.8, marker="s", label="TF-IDF")
        ax.plot(b_frame["to_slice"].astype(int), _zscore(b_frame["drift"].to_numpy()),
                color=METHOD_COLORS["BERT"], linewidth=1.8, marker="^", label="BERT")
        ax.axhline(0.0, color=OKABE_ITO["grey"], linewidth=0.8, linestyle="--", alpha=0.8)
        ax.set_title(term, fontsize=8.5)
        ax.grid(alpha=0.2)
        ax.set_xlim(years.min() - 0.2, years.max() + 0.2)
        ax.set_xticks(years[::4])
        ax.set_xlabel("Right-hand slice year")
        ax.set_ylabel("Within-term standardized drift")
        if add_legend:
            handles, labels = ax.get_legend_handles_labels()
            ax.legend(handles, labels, loc="upper right", frameon=False, fontsize=6, ncol=3)

    for idx, (term, t_frame, b_frame, years, w_mean, w_std) in enumerate(term_data):
        pfig, pax = plt.subplots(1, 1, figsize=(3.3, 2.9))
        _draw_trajectory_panel(pax, term, t_frame, b_frame, years, w_mean, w_std, add_legend=(idx == 0))
        letter = ascii_uppercase[idx].lower()
        _save_bundle(pfig, output_stem.parent / f"{output_stem.name}_panel_{letter}")

    fig, axes = plt.subplots(2, 2, figsize=(6.6, 5.7), sharex=True, sharey=True)
    flat_axes = [axes[0, 0], axes[0, 1], axes[1, 0], axes[1, 1]]
    for ax, (term, t_frame, b_frame, years, w_mean, w_std) in zip(flat_axes, term_data):
        _draw_trajectory_panel(ax, term, t_frame, b_frame, years, w_mean, w_std)

    for axis in flat_axes[:2]:
        axis.set_xlabel("")
    for axis in [axes[0, 1], axes[1, 1]]:
        axis.set_ylabel("")

    handles, labels = flat_axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", ncol=3, frameon=False, bbox_to_anchor=(0.5, 1.02))
    _add_panel_labels(flat_axes, x=-0.13, y=1.06)
    fig.subplots_adjust(top=0.87)
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
