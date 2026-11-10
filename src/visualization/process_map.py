"""
Process Map Visualization Module
Generates high-resolution publication-quality process maps and charts using Matplotlib and NetworkX.
Runs standalone without external Graphviz system dependencies.
Author: Madhura (Member 2 - Process Mining)
"""

from pathlib import Path
from typing import Dict, Any, Union
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend for headless execution
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import networkx as nx
import numpy as np
import pandas as pd


# Categorization of clinical activities with healthcare semantic colors
ACTIVITY_CLINICAL_ROLES = {
    "ER Registration": {"stage": "1. Intake", "color": "#2b5c8f"},
    "ER Triage": {"stage": "1. Intake", "color": "#3498db"},
    "ER Sepsis Triage": {"stage": "1. Intake", "color": "#1abc9c"},
    "CRP": {"stage": "2. Diagnostics", "color": "#8e44ad"},
    "Leucocytes": {"stage": "2. Diagnostics", "color": "#9b59b6"},
    "LacticAcid": {"stage": "2. Diagnostics", "color": "#6c5ce7"},
    "IV Liquid": {"stage": "3. Treatment", "color": "#16a085"},
    "IV Antibiotics": {"stage": "3. Treatment", "color": "#27ae60"},
    "Admission NC": {"stage": "4. Inpatient", "color": "#d35400"},
    "Admission IC": {"stage": "4. Inpatient", "color": "#c0392b"},
    "Release A": {"stage": "5. Disposition", "color": "#2ecc71"},
    "Release B": {"stage": "5. Disposition", "color": "#27ae60"},
    "Release C": {"stage": "5. Disposition", "color": "#7f8c8d"},
    "Release D": {"stage": "5. Disposition", "color": "#95a5a6"},
    "Release E": {"stage": "5. Disposition", "color": "#bdc3c7"},
    "Return ER": {"stage": "5. Disposition", "color": "#e74c3c"},
}

# Clinical flow positioning for clean left-to-right pathway layout
CLINICAL_COORDINATES = {
    "ER Registration": (0.0, 1.0),
    "ER Triage": (1.2, 1.8),
    "ER Sepsis Triage": (1.2, 0.2),
    "IV Liquid": (2.8, 2.0),
    "IV Antibiotics": (2.8, 1.2),
    "LacticAcid": (2.8, 0.4),
    "Leucocytes": (4.2, 1.8),
    "CRP": (4.2, 0.6),
    "Admission NC": (5.8, 1.6),
    "Admission IC": (5.8, 0.4),
    "Release A": (7.5, 2.2),
    "Release B": (7.5, 1.6),
    "Release C": (7.5, 1.0),
    "Release D": (7.5, 0.4),
    "Release E": (7.5, -0.2),
    "Return ER": (7.5, -0.8),
}


def plot_frequency_dfg(
    freq_df: pd.DataFrame,
    output_path: Union[str, Path],
    min_frequency: int = 50
) -> Path:
    """
    Renders the Directly-Follows Graph weighted by activity transition frequencies.
    Filters minor noise transitions below min_frequency for clinical clarity.
    """
    save_file = Path(output_path)
    save_file.parent.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(16, 10), dpi=300)
    fig.patch.set_facecolor("#fdfefe")
    ax.set_facecolor("#fdfefe")

    G = nx.DiGraph()

    # Filter transitions for visual clarity
    filtered_df = freq_df[freq_df["transition_count"] >= min_frequency].copy()

    for _, row in filtered_df.iterrows():
        G.add_edge(
            row["source_activity"],
            row["target_activity"],
            weight=row["transition_count"]
        )

    # Use clinical layout
    pos = {node: CLINICAL_COORDINATES.get(node, (3.0, 1.0)) for node in G.nodes()}

    # Draw nodes
    for node in G.nodes():
        x, y = pos[node]
        color = ACTIVITY_CLINICAL_ROLES.get(node, {}).get("color", "#34495e")
        box = patches.FancyBboxPatch(
            (x - 0.45, y - 0.2),
            0.9,
            0.4,
            boxstyle="round,pad=0.08,rounding_size=0.15",
            facecolor=color,
            edgecolor="#1a252f",
            linewidth=1.2,
            zorder=3
        )
        ax.add_patch(box)
        ax.text(
            x, y,
            node,
            ha="center", va="center",
            fontsize=9.5, fontweight="bold", color="white",
            zorder=4
        )

    # Draw edges with scaled thickness
    max_weight = max(G[u][v]["weight"] for u, v in G.edges())
    for u, v in G.edges():
        weight = G[u][v]["weight"]
        x1, y1 = pos[u]
        x2, y2 = pos[v]

        # Arrow width proportional to volume
        width = 1.0 + 3.5 * (weight / max_weight)
        alpha = 0.55 + 0.4 * (weight / max_weight)

        # Draw curved arc if bidirectional or self-loop
        rad = 0.18 if (v, u) in G.edges() and u != v else 0.08
        if u == v:
            rad = 0.35

        ax.annotate(
            "",
            xy=(x2, y2),
            xytext=(x1, y1),
            arrowprops=dict(
                arrowstyle="-|>",
                color="#2c3e50",
                lw=width,
                alpha=alpha,
                shrinkA=22,
                shrinkB=22,
                connectionstyle=f"arc3,rad={rad}"
            ),
            zorder=2
        )

        # Label prominent edges
        if weight >= 150:
            mid_x = (x1 + x2) / 2.0
            mid_y = (y1 + y2) / 2.0 + (0.1 if rad >= 0 else -0.1)
            ax.text(
                mid_x, mid_y,
                f"{weight:,}",
                fontsize=7.5,
                fontweight="bold",
                color="#1b2631",
                ha="center",
                va="center",
                bbox=dict(boxstyle="round,pad=0.15", facecolor="#ffffff", edgecolor="#bdc3c7", lw=0.6, alpha=0.9),
                zorder=5
            )

    ax.set_xlim(-0.8, 8.5)
    ax.set_ylim(-1.3, 2.7)
    ax.axis("off")

    plt.title(
        f"CareFlow: Clinical Pathway Process Map (Directly-Follows Graph)\n"
        f"Showing Primary Transitions (≥ {min_frequency} events) Across 1,050 Sepsis Patient Journeys",
        fontsize=14, fontweight="bold", pad=20, color="#1a252f"
    )

    # Stage Legend
    legend_elements = [
        patches.Patch(facecolor="#2b5c8f", label="Intake / Triage"),
        patches.Patch(facecolor="#8e44ad", label="Diagnostics / Lab"),
        patches.Patch(facecolor="#27ae60", label="Medical Treatments"),
        patches.Patch(facecolor="#d35400", label="Inpatient Hospitalization"),
        patches.Patch(facecolor="#7f8c8d", label="Discharge / Adverse Disposition")
    ]
    ax.legend(
        handles=legend_elements,
        loc="lower center",
        ncol=5,
        frameon=True,
        facecolor="#ffffff",
        edgecolor="#d5dbdb",
        fontsize=9
    )

    plt.tight_layout()
    plt.savefig(save_file, dpi=300, bbox_inches="tight")
    plt.close()

    print(f"[Visualizer] Frequency DFG map saved to: {save_file}")
    return save_file


def plot_performance_dfg(
    perf_df: pd.DataFrame,
    output_path: Union[str, Path],
    min_cases: int = 30
) -> Path:
    """
    Renders the Performance Directly-Follows Graph highlighting clinical bottlenecks
    and recorded time gaps between consecutive activities.
    """
    save_file = Path(output_path)
    save_file.parent.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(16, 10), dpi=300)
    fig.patch.set_facecolor("#fdfefe")
    ax.set_facecolor("#fdfefe")

    G = nx.DiGraph()

    filtered_df = perf_df[perf_df["transition_count"] >= min_cases].copy()

    for _, row in filtered_df.iterrows():
        G.add_edge(
            row["source_activity"],
            row["target_activity"],
            hours=row["mean_duration_hours"],
            count=row["transition_count"]
        )

    pos = {node: CLINICAL_COORDINATES.get(node, (3.0, 1.0)) for node in G.nodes()}

    # Draw nodes
    for node in G.nodes():
        x, y = pos[node]
        color = ACTIVITY_CLINICAL_ROLES.get(node, {}).get("color", "#34495e")
        box = patches.FancyBboxPatch(
            (x - 0.45, y - 0.2),
            0.9,
            0.4,
            boxstyle="round,pad=0.08,rounding_size=0.15",
            facecolor=color,
            edgecolor="#1a252f",
            linewidth=1.2,
            zorder=3
        )
        ax.add_patch(box)
        ax.text(
            x, y,
            node,
            ha="center", va="center",
            fontsize=9.5, fontweight="bold", color="white",
            zorder=4
        )

    # Bottleneck color scale: < 2 hrs (green), 2-12 hrs (orange), > 12 hrs (dark red)
    for u, v in G.edges():
        hours = G[u][v]["hours"]
        x1, y1 = pos[u]
        x2, y2 = pos[v]

        if hours > 24:
            edge_color = "#c0392b"
            width = 3.2
        elif hours > 6:
            edge_color = "#e67e22"
            width = 2.2
        else:
            edge_color = "#27ae60"
            width = 1.2

        rad = 0.18 if (v, u) in G.edges() and u != v else 0.08

        ax.annotate(
            "",
            xy=(x2, y2),
            xytext=(x1, y1),
            arrowprops=dict(
                arrowstyle="-|>",
                color=edge_color,
                lw=width,
                shrinkA=22,
                shrinkB=22,
                connectionstyle=f"arc3,rad={rad}"
            ),
            zorder=2
        )

        mid_x = (x1 + x2) / 2.0
        mid_y = (y1 + y2) / 2.0 + (0.12 if rad >= 0 else -0.12)
        ax.text(
            mid_x, mid_y,
            f"{hours:.1f}h",
            fontsize=8,
            fontweight="bold",
            color="#922b21" if hours > 24 else "#1b2631",
            ha="center",
            va="center",
            bbox=dict(boxstyle="round,pad=0.15", facecolor="#fff9e6" if hours > 24 else "#ffffff", edgecolor=edge_color, lw=0.8, alpha=0.9),
            zorder=5
        )

    ax.set_xlim(-0.8, 8.5)
    ax.set_ylim(-1.3, 2.7)
    ax.axis("off")

    plt.title(
        f"CareFlow: Performance & Bottleneck Analysis (Mean Waiting Time in Hours)\n"
        f"Highlighting High-Latency Clinical Transitions (≥ {min_cases} cases)",
        fontsize=14, fontweight="bold", pad=20, color="#1a252f"
    )

    # Legend
    legend_elements = [
        patches.Patch(facecolor="#27ae60", label="Rapid Transition (< 6 hours)"),
        patches.Patch(facecolor="#e67e22", label="Moderate Waiting Interval (6 - 24 hours)"),
        patches.Patch(facecolor="#c0392b", label="Critical Delay / Inpatient Interval (> 24 hours)")
    ]
    ax.legend(
        handles=legend_elements,
        loc="lower center",
        ncol=3,
        frameon=True,
        facecolor="#ffffff",
        edgecolor="#d5dbdb",
        fontsize=9
    )

    plt.tight_layout()
    plt.savefig(save_file, dpi=300, bbox_inches="tight")
    plt.close()

    print(f"[Visualizer] Performance DFG map saved to: {save_file}")
    return save_file


def plot_variants_distribution(
    variants_df: pd.DataFrame,
    output_path: Union[str, Path],
    top_k: int = 12
) -> Path:
    """
    Renders the Pareto distribution of patient journey variants.
    """
    save_file = Path(output_path)
    save_file.parent.mkdir(parents=True, exist_ok=True)

    fig, ax1 = plt.subplots(figsize=(13, 7), dpi=300)
    fig.patch.set_facecolor("#ffffff")
    ax1.set_facecolor("#ffffff")

    top_variants = variants_df.iloc[:top_k].copy()
    y_pos = np.arange(len(top_variants))

    # Horizontal bars for case frequencies
    bars = ax1.barh(
        y_pos,
        top_variants["case_frequency"],
        color="#2980b9",
        edgecolor="#1a5276",
        height=0.6,
        alpha=0.85,
        label="Case Frequency"
    )

    ax1.set_yticks(y_pos)
    ax1.set_yticklabels(
        [f"{row['variant_id']} ({row['pathway_length']} steps)" for _, row in top_variants.iterrows()],
        fontsize=9, fontweight="bold"
    )
    ax1.invert_yaxis()  # Top variant on top
    ax1.set_xlabel("Number of Patient Cases", fontsize=10, fontweight="bold", color="#1a252f")
    ax1.grid(axis="x", linestyle="--", alpha=0.4)

    # Bar value labels
    for bar in bars:
        w = bar.get_width()
        ax1.text(
            w + 1.2,
            bar.get_y() + bar.get_height() / 2,
            f"{int(w)} cases",
            va="center", fontsize=8.5, color="#1a252f"
        )

    # Cumulative Pareto line on secondary axis
    ax2 = ax1.twiny()
    ax2.plot(
        top_variants["cumulative_coverage_pct"],
        y_pos,
        color="#e74c3c",
        marker="o",
        linewidth=2,
        label="Cumulative Coverage %"
    )
    ax2.set_xlabel("Cumulative Patient Coverage (%)", fontsize=10, fontweight="bold", color="#c0392b")
    ax2.set_xlim(0, 100)

    for i, txt in enumerate(top_variants["cumulative_coverage_pct"]):
        ax2.annotate(
            f"{txt:.1f}%",
            (txt, y_pos[i]),
            textcoords="offset points",
            xytext=(7, -4),
            fontsize=8,
            color="#c0392b",
            fontweight="bold"
        )

    plt.title(
        f"CareFlow: Top {top_k} Patient Pathway Variants & Pareto Case Coverage\n"
        f"Showing High Pathway Variability (846 Total Unique Variants Across 1,050 Cases)",
        fontsize=12, fontweight="bold", pad=15, color="#1a252f"
    )

    plt.tight_layout()
    plt.savefig(save_file, dpi=300, bbox_inches="tight")
    plt.close()

    print(f"[Visualizer] Variants distribution chart saved to: {save_file}")
    return save_file


if __name__ == "__main__":
    project_root = Path(__file__).resolve().parents[2]
    tables_dir = project_root / "outputs" / "tables"
    figures_dir = project_root / "outputs" / "figures"

    freq_csv = tables_dir / "dfg_frequency_table.csv"
    perf_csv = tables_dir / "dfg_performance_table.csv"
    var_csv = tables_dir / "process_variants_summary.csv"

    if freq_csv.exists():
        plot_frequency_dfg(pd.read_csv(freq_csv), figures_dir / "dfg_frequency_process_map.png")
    if perf_csv.exists():
        plot_performance_dfg(pd.read_csv(perf_csv), figures_dir / "dfg_performance_bottleneck_map.png")
    if var_csv.exists():
        plot_variants_distribution(pd.read_csv(var_csv), figures_dir / "top_variants_distribution.png")
